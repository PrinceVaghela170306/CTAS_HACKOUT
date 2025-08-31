from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.routers.auth import get_current_user_dependency
from app.services.notification_service import notification_service
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User, UserPreferences
from app.models.alert import AlertNotification
from pydantic import BaseModel, Field
from loguru import logger
import uuid

router = APIRouter()

# Pydantic models for request/response
class NotificationPreferences(BaseModel):
    email_enabled: bool = Field(True, description="Enable email notifications")
    sms_enabled: bool = Field(False, description="Enable SMS notifications")
    push_enabled: bool = Field(True, description="Enable push notifications")
    phone_number: Optional[str] = Field(None, description="Phone number for SMS")
    device_token: Optional[str] = Field(None, description="Device token for push notifications")
    alert_types: List[str] = Field(["flood", "storm_surge", "high_waves"], description="Alert types to receive")
    severity_threshold: str = Field("medium", description="Minimum severity level")
    quiet_hours_start: Optional[str] = Field(None, description="Quiet hours start (HH:MM)")
    quiet_hours_end: Optional[str] = Field(None, description="Quiet hours end (HH:MM)")

class TestNotificationRequest(BaseModel):
    notification_type: str = Field(..., description="Type: email, sms, push, or all")
    message: Optional[str] = Field("Test notification from Coastal Alert System", description="Custom test message")

class NotificationHistoryResponse(BaseModel):
    id: str
    alert_id: Optional[str]
    notification_method: str
    recipient: str
    subject: Optional[str]
    status: str
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    error_message: Optional[str]

@router.get("/preferences")
async def get_notification_preferences(
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get user's notification preferences"""
    try:
        user_id = current_user["id"]
        
        # Get user preferences
        preferences = db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()
        
        if not preferences:
            # Return default preferences
            return {
                "email_enabled": True,
                "sms_enabled": False,
                "push_enabled": True,
                "phone_number": None,
                "device_token": None,
                "alert_types": ["flood", "storm_surge", "high_waves"],
                "severity_threshold": "medium",
                "quiet_hours_start": None,
                "quiet_hours_end": None
            }
        
        notification_methods = preferences.notification_methods or []
        
        return {
            "email_enabled": "email" in notification_methods,
            "sms_enabled": "sms" in notification_methods,
            "push_enabled": "push" in notification_methods,
            "phone_number": preferences.phone_number,
            "device_token": getattr(preferences, 'device_token', None),
            "alert_types": preferences.alert_types or ["flood", "storm_surge", "high_waves"],
            "severity_threshold": preferences.severity_threshold or "medium",
            "quiet_hours_start": preferences.quiet_hours_start,
            "quiet_hours_end": preferences.quiet_hours_end
        }
        
    except Exception as e:
        logger.error(f"Error getting notification preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to get notification preferences")

@router.put("/preferences")
async def update_notification_preferences(
    preferences: NotificationPreferences,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Update user's notification preferences"""
    try:
        user_id = current_user["id"]
        
        # Get or create user preferences
        user_prefs = db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()
        
        if not user_prefs:
            user_prefs = UserPreferences(
                id=str(uuid.uuid4()),
                user_id=user_id
            )
            db.add(user_prefs)
        
        # Build notification methods list
        notification_methods = []
        if preferences.email_enabled:
            notification_methods.append("email")
        if preferences.sms_enabled:
            notification_methods.append("sms")
        if preferences.push_enabled:
            notification_methods.append("push")
        
        # Update preferences
        user_prefs.notification_methods = notification_methods
        user_prefs.phone_number = preferences.phone_number
        user_prefs.alert_types = preferences.alert_types
        user_prefs.severity_threshold = preferences.severity_threshold
        user_prefs.quiet_hours_start = preferences.quiet_hours_start
        user_prefs.quiet_hours_end = preferences.quiet_hours_end
        user_prefs.updated_at = datetime.utcnow()
        
        # Update device token if provided
        if preferences.device_token:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.device_token = preferences.device_token
        
        db.commit()
        
        return {
            "success": True,
            "message": "Notification preferences updated successfully",
            "preferences": {
                "email_enabled": preferences.email_enabled,
                "sms_enabled": preferences.sms_enabled,
                "push_enabled": preferences.push_enabled,
                "alert_types": preferences.alert_types,
                "severity_threshold": preferences.severity_threshold
            }
        }
        
    except Exception as e:
        logger.error(f"Error updating notification preferences: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update notification preferences")

@router.post("/test")
async def test_notification(
    test_request: TestNotificationRequest,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Send a test notification to verify settings"""
    try:
        user_id = current_user["id"]
        
        # Send test notification
        result = await notification_service.send_test_notification(
            user_id, test_request.notification_type, test_request.message, db
        )
        
        return {
            "success": result.get("success", False),
            "message": "Test notification sent" if result.get("success") else "Test notification failed",
            "details": result
        }
        
    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to send test notification")

@router.get("/history")
async def get_notification_history(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get user's notification history"""
    try:
        user_id = current_user["id"]
        
        # Get notification history
        notifications = db.query(AlertNotification).filter(
            AlertNotification.user_id == user_id
        ).order_by(
            AlertNotification.sent_at.desc()
        ).offset(offset).limit(limit).all()
        
        # Convert to response format
        history = []
        for notification in notifications:
            history.append({
                "id": notification.id,
                "alert_id": notification.alert_id,
                "notification_method": notification.notification_method,
                "recipient": notification.recipient,
                "subject": notification.subject,
                "status": notification.status,
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
                "delivered_at": notification.delivered_at.isoformat() if notification.delivered_at else None,
                "error_message": notification.error_message
            })
        
        # Get total count
        total_count = db.query(AlertNotification).filter(
            AlertNotification.user_id == user_id
        ).count()
        
        return {
            "notifications": history,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting notification history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get notification history")

@router.get("/stats")
async def get_notification_stats(
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get notification statistics for the user"""
    try:
        user_id = current_user["id"]
        
        # Get notification statistics
        total_notifications = db.query(AlertNotification).filter(
            AlertNotification.user_id == user_id
        ).count()
        
        successful_notifications = db.query(AlertNotification).filter(
            AlertNotification.user_id == user_id,
            AlertNotification.status == "sent"
        ).count()
        
        failed_notifications = db.query(AlertNotification).filter(
            AlertNotification.user_id == user_id,
            AlertNotification.status == "failed"
        ).count()
        
        # Get notifications by method
        email_count = db.query(AlertNotification).filter(
            AlertNotification.user_id == user_id,
            AlertNotification.notification_method == "email"
        ).count()
        
        sms_count = db.query(AlertNotification).filter(
            AlertNotification.user_id == user_id,
            AlertNotification.notification_method == "sms"
        ).count()
        
        push_count = db.query(AlertNotification).filter(
            AlertNotification.user_id == user_id,
            AlertNotification.notification_method == "push"
        ).count()
        
        return {
            "total_notifications": total_notifications,
            "successful_notifications": successful_notifications,
            "failed_notifications": failed_notifications,
            "success_rate": (successful_notifications / total_notifications * 100) if total_notifications > 0 else 0,
            "notifications_by_method": {
                "email": email_count,
                "sms": sms_count,
                "push": push_count
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting notification stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get notification statistics")

@router.post("/device-token")
async def register_device_token(
    device_data: Dict[str, str] = Body(...),
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Register device token for push notifications"""
    try:
        user_id = current_user["id"]
        device_token = device_data.get("device_token")
        
        if not device_token:
            raise HTTPException(status_code=400, detail="Device token is required")
        
        # Update user's device token
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.device_token = device_token
        user.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "message": "Device token registered successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering device token: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to register device token")