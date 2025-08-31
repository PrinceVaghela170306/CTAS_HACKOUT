from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from app.services.auth_service import get_supabase
from app.schemas.auth import UserCreate, UserLogin, UserResponse, TokenResponse
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    supabase: Client = Depends(get_supabase)
):
    """Register a new user with email confirmation"""
    try:
        # Register user with Supabase Auth
        response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "full_name": user_data.full_name,
                    "phone": user_data.phone
                }
            }
        })
        
        if response.user:
            logger.info(f"User registered successfully: {user_data.email}")
            return UserResponse(
                id=response.user.id,
                email=response.user.email,
                full_name=user_data.full_name,
                phone=user_data.phone,
                is_verified=False,
                created_at=datetime.utcnow()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    user_credentials: UserLogin,
    supabase: Client = Depends(get_supabase)
):
    """Login user with Supabase authentication"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user_credentials.email,
            "password": user_credentials.password
        })
        
        if response.user and response.session:
            logger.info(f"User logged in successfully: {user_credentials.email}")
            return TokenResponse(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                token_type="bearer",
                expires_in=response.session.expires_in,
                user=UserResponse(
                    id=response.user.id,
                    email=response.user.email,
                    full_name=response.user.user_metadata.get("full_name", ""),
                    phone=response.user.user_metadata.get("phone", ""),
                    is_verified=response.user.email_confirmed_at is not None,
                    created_at=datetime.fromisoformat(response.user.created_at.replace('Z', '+00:00'))
                )
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

@router.post("/logout")
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
):
    """Logout user and invalidate token"""
    try:
        # Set the session token
        supabase.auth.set_session(credentials.credentials, None)
        
        # Sign out
        supabase.auth.sign_out()
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logout failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
):
    """Get current user information"""
    try:
        token = credentials.credentials
        
        # Set the session token and get user
        supabase.auth.set_session(token, None)
        user = supabase.auth.get_user()
        
        if user.user:
            return UserResponse(
                id=user.user.id,
                email=user.user.email,
                full_name=user.user.user_metadata.get("full_name", ""),
                phone=user.user.user_metadata.get("phone", ""),
                is_verified=user.user.email_confirmed_at is not None,
                created_at=datetime.fromisoformat(user.user.created_at.replace('Z', '+00:00'))
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
            
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    supabase: Client = Depends(get_supabase)
):
    """Refresh access token"""
    try:
        response = supabase.auth.refresh_session(refresh_token)
        
        if response.session:
            return TokenResponse(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                token_type="bearer",
                expires_in=response.session.expires_in
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
            
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.post("/set-location")
async def set_user_location(
    location_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
):
    """Set user location after onboarding"""
    try:
        # Set the session token
        supabase.auth.set_session(credentials.credentials, None)
        
        # Get user
        user = supabase.auth.get_user()
        
        if not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Store location in user metadata
        # In a real implementation, you'd store this in a separate locations table
        # For now, we'll update the user metadata
        updated_user = supabase.auth.update_user({
            "data": {
                **user.user.user_metadata,
                "location": {
                    "name": location_data.get("name"),
                    "latitude": location_data.get("latitude"),
                    "longitude": location_data.get("longitude"),
                    "is_custom": location_data.get("is_custom", False)
                }
            }
        })
        
        logger.info(f"Location set for user: {user.user.email}")
        return {"message": "Location set successfully"}
        
    except Exception as e:
        logger.error(f"Set location error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to set location"
        )

# Dependency to get current user from token
async def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
) -> dict:
    """Dependency to extract current user from JWT token"""
    try:
        supabase.auth.set_session(credentials.credentials, None)
        user = supabase.auth.get_user()
        
        if user.user:
            return {
                "id": user.user.id,
                "email": user.user.email,
                "full_name": user.user.user_metadata.get("full_name", ""),
                "phone": user.user.user_metadata.get("phone", ""),
                "location": user.user.user_metadata.get("location")
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )