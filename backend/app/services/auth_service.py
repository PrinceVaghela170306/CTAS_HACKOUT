from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
import jwt
import bcrypt
import secrets
from supabase import create_client, Client
from fastapi import HTTPException
from app.config import settings
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User, UserSession, UserPreferences, UserLocation
from app.schemas.auth import UserCreate, UserLogin, UserResponse, TokenResponse
import asyncio

class AuthService:
    """Authentication service using Supabase and local database"""
    
    def __init__(self):
        # Initialize Supabase client only if credentials are provided
        if settings.supabase_url and settings.supabase_key:
            self.supabase: Client = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
        else:
            self.supabase = None
            logger.warning("Supabase credentials not provided. Some features may not work.")
        
        self.jwt_secret = settings.jwt_secret_key
        self.jwt_algorithm = "HS256"
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.refresh_token_expire_days = 30
    
    async def register_user(self, user_data: UserCreate, db: Session) -> Dict[str, Any]:
        """Register a new user with Supabase and local database"""
        try:
            # Check if user already exists locally
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                return {
                    "success": False,
                    "error": "User with this email already exists"
                }
            
            # Register with Supabase
            supabase_response = self.supabase.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "full_name": user_data.full_name,
                        "phone": user_data.phone_number
                    }
                }
            })
            
            if supabase_response.user is None:
                return {
                    "success": False,
                    "error": "Failed to create user account"
                }
            
            # Create user in local database
            hashed_password = bcrypt.hashpw(
                user_data.password.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            new_user = User(
                id=supabase_response.user.id,
                email=user_data.email,
                full_name=user_data.full_name,
                hashed_password=hashed_password,
                phone_number=user_data.phone_number,
                is_active=True,
                email_verified=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(new_user)
            
            # Create default user preferences
            preferences = UserPreferences(
                user_id=new_user.id,
                notification_methods=['email'],
                alert_types=['flood', 'storm', 'tide'],
                severity_threshold='medium',
                quiet_hours_start='22:00',
                quiet_hours_end='07:00',
                language='en',
                timezone='UTC',
                created_at=datetime.utcnow()
            )
            
            db.add(preferences)
            db.commit()
            
            # Generate tokens
            access_token = self._create_access_token(new_user.id)
            refresh_token = self._create_refresh_token(new_user.id)
            
            # Create session
            session = UserSession(
                user_id=new_user.id,
                session_token=refresh_token,
                expires_at=datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
                created_at=datetime.utcnow()
            )
            
            db.add(session)
            db.commit()
            
            return {
                "success": True,
                "user": {
                    "id": new_user.id,
                    "email": new_user.email,
                    "full_name": new_user.full_name,
                    "phone_number": new_user.phone_number,
                    "email_verified": new_user.email_verified,
                    "created_at": new_user.created_at.isoformat()
                },
                "tokens": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "expires_in": self.access_token_expire_minutes * 60
                },
                "requires_onboarding": True
            }
            
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            db.rollback()
            return {
                "success": False,
                "error": "Registration failed. Please try again."
            }
    
    async def login_user(self, login_data: UserLogin, db: Session) -> Dict[str, Any]:
        """Authenticate user and return tokens"""
        try:
            # Authenticate with Supabase
            supabase_response = self.supabase.auth.sign_in_with_password({
                "email": login_data.email,
                "password": login_data.password
            })
            
            if supabase_response.user is None:
                return {
                    "success": False,
                    "error": "Invalid email or password"
                }
            
            # Get user from local database
            user = db.query(User).filter(User.email == login_data.email).first()
            
            if not user:
                return {
                    "success": False,
                    "error": "User not found in local database"
                }
            
            if not user.is_active:
                return {
                    "success": False,
                    "error": "Account is deactivated"
                }
            
            # Verify password (additional local check)
            if not bcrypt.checkpw(login_data.password.encode('utf-8'), 
                                user.hashed_password.encode('utf-8')):
                return {
                    "success": False,
                    "error": "Invalid email or password"
                }
            
            # Update last login
            user.last_login = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            
            # Generate new tokens
            access_token = self._create_access_token(user.id)
            refresh_token = self._create_refresh_token(user.id)
            
            # Invalidate old sessions and create new one
            db.query(UserSession).filter(
                UserSession.user_id == user.id,
                UserSession.is_active == True
            ).update({"is_active": False})
            
            new_session = UserSession(
                user_id=user.id,
                session_token=refresh_token,
                expires_at=datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
                created_at=datetime.utcnow(),
                is_active=True
            )
            
            db.add(new_session)
            db.commit()
            
            # Check if user needs onboarding
            preferences = db.query(UserPreferences).filter(
                UserPreferences.user_id == user.id
            ).first()
            
            location = db.query(UserLocation).filter(
                UserLocation.user_id == user.id
            ).first()
            
            requires_onboarding = not (preferences and location)
            
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "phone_number": user.phone_number,
                    "email_verified": user.email_verified,
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "created_at": user.created_at.isoformat()
                },
                "tokens": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "expires_in": self.access_token_expire_minutes * 60
                },
                "requires_onboarding": requires_onboarding
            }
            
        except Exception as e:
            logger.error(f"Error logging in user: {e}")
            return {
                "success": False,
                "error": "Login failed. Please try again."
            }
    
    async def logout_user(self, user_id: str, session_token: str, db: Session) -> Dict[str, Any]:
        """Logout user and invalidate session"""
        try:
            # Logout from Supabase
            self.supabase.auth.sign_out()
            
            # Invalidate local session
            session = db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.session_token == session_token,
                UserSession.is_active == True
            ).first()
            
            if session:
                session.is_active = False
                session.logged_out_at = datetime.utcnow()
                db.commit()
            
            return {
                "success": True,
                "message": "Successfully logged out"
            }
            
        except Exception as e:
            logger.error(f"Error logging out user: {e}")
            return {
                "success": False,
                "error": "Logout failed"
            }
    
    async def refresh_token(self, refresh_token: str, db: Session) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            # Verify refresh token
            payload = jwt.decode(refresh_token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            user_id = payload.get("sub")
            token_type = payload.get("type")
            
            if token_type != "refresh":
                return {
                    "success": False,
                    "error": "Invalid token type"
                }
            
            # Check if session exists and is active
            session = db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.session_token == refresh_token,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            ).first()
            
            if not session:
                return {
                    "success": False,
                    "error": "Invalid or expired refresh token"
                }
            
            # Get user
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                return {
                    "success": False,
                    "error": "User not found or inactive"
                }
            
            # Generate new access token
            new_access_token = self._create_access_token(user_id)
            
            # Update session last used
            session.last_used = datetime.utcnow()
            db.commit()
            
            return {
                "success": True,
                "tokens": {
                    "access_token": new_access_token,
                    "refresh_token": refresh_token,  # Keep same refresh token
                    "token_type": "bearer",
                    "expires_in": self.access_token_expire_minutes * 60
                }
            }
            
        except jwt.ExpiredSignatureError:
            return {
                "success": False,
                "error": "Refresh token expired"
            }
        except jwt.InvalidTokenError:
            return {
                "success": False,
                "error": "Invalid refresh token"
            }
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return {
                "success": False,
                "error": "Token refresh failed"
            }
    
    async def get_current_user(self, access_token: str, db: Session) -> Optional[User]:
        """Get current user from access token"""
        try:
            payload = jwt.decode(access_token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            user_id = payload.get("sub")
            token_type = payload.get("type")
            
            if token_type != "access":
                return None
            
            user = db.query(User).filter(
                User.id == user_id,
                User.is_active == True
            ).first()
            
            return user
            
        except jwt.ExpiredSignatureError:
            logger.warning("Access token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid access token")
            return None
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            return None
    
    async def complete_onboarding(self, user_id: str, onboarding_data: Dict[str, Any], 
                                db: Session) -> Dict[str, Any]:
        """Complete user onboarding process"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Update user preferences
            preferences = db.query(UserPreferences).filter(
                UserPreferences.user_id == user_id
            ).first()
            
            if preferences:
                preferences.notification_methods = onboarding_data.get(
                    'notification_methods', ['email']
                )
                preferences.alert_types = onboarding_data.get(
                    'alert_types', ['flood', 'storm', 'tide']
                )
                preferences.severity_threshold = onboarding_data.get(
                    'severity_threshold', 'medium'
                )
                preferences.phone_number = onboarding_data.get('phone_number')
                preferences.updated_at = datetime.utcnow()
            
            # Create or update user location
            location_data = onboarding_data.get('location', {})
            if location_data:
                existing_location = db.query(UserLocation).filter(
                    UserLocation.user_id == user_id
                ).first()
                
                if existing_location:
                    existing_location.latitude = location_data.get('latitude')
                    existing_location.longitude = location_data.get('longitude')
                    existing_location.address = location_data.get('address')
                    existing_location.city = location_data.get('city')
                    existing_location.state = location_data.get('state')
                    existing_location.country = location_data.get('country')
                    existing_location.postal_code = location_data.get('postal_code')
                    existing_location.updated_at = datetime.utcnow()
                else:
                    new_location = UserLocation(
                        user_id=user_id,
                        latitude=location_data.get('latitude'),
                        longitude=location_data.get('longitude'),
                        address=location_data.get('address'),
                        city=location_data.get('city'),
                        state=location_data.get('state'),
                        country=location_data.get('country'),
                        postal_code=location_data.get('postal_code'),
                        is_primary=True,
                        created_at=datetime.utcnow()
                    )
                    db.add(new_location)
            
            # Mark onboarding as complete
            user.onboarding_completed = True
            user.onboarding_completed_at = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            
            db.commit()
            
            return {
                "success": True,
                "message": "Onboarding completed successfully",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "onboarding_completed": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error completing onboarding: {e}")
            db.rollback()
            return {
                "success": False,
                "error": "Onboarding completion failed"
            }
    
    async def reset_password(self, email: str) -> Dict[str, Any]:
        """Send password reset email"""
        try:
            response = self.supabase.auth.reset_password_email(email)
            
            return {
                "success": True,
                "message": "Password reset email sent"
            }
            
        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
            return {
                "success": False,
                "error": "Failed to send password reset email"
            }
    
    async def verify_email(self, token: str) -> Dict[str, Any]:
        """Verify user email with token"""
        try:
            # This would typically be handled by Supabase webhook
            # For now, we'll simulate email verification
            
            return {
                "success": True,
                "message": "Email verified successfully"
            }
            
        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            return {
                "success": False,
                "error": "Email verification failed"
            }
    
    def _create_access_token(self, user_id: str) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "sub": user_id,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def _create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32)  # Unique token ID
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    async def revoke_all_sessions(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Revoke all active sessions for a user"""
        try:
            # Invalidate all active sessions
            db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            ).update({
                "is_active": False,
                "logged_out_at": datetime.utcnow()
            })
            
            db.commit()
            
            return {
                "success": True,
                "message": "All sessions revoked successfully"
            }
            
        except Exception as e:
            logger.error(f"Error revoking sessions: {e}")
            return {
                "success": False,
                "error": "Failed to revoke sessions"
            }

# Global auth service instance
auth_service = AuthService()

# Dependency function to get Supabase client
def get_supabase() -> Client:
    """Get Supabase client instance"""
    if auth_service.supabase is None:
        raise HTTPException(
            status_code=500,
            detail="Supabase client not initialized. Please check configuration."
        )
    return auth_service.supabase