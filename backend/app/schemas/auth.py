from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters long')
        return v.strip()

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    is_verified: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    user: Optional[UserResponse] = None

class UserPreferences(BaseModel):
    user_id: str
    coastal_location: str
    latitude: float
    longitude: float
    alert_types: list[str] = ["flood", "storm_surge", "high_waves"]
    notification_methods: list[str] = ["push", "email"]
    alert_threshold: str = "medium"  # low, medium, high
    
    @validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v
    
    @validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v
    
    @validator('alert_types')
    def validate_alert_types(cls, v):
        valid_types = ["flood", "storm_surge", "high_waves", "tsunami", "erosion", "algal_bloom"]
        for alert_type in v:
            if alert_type not in valid_types:
                raise ValueError(f'Invalid alert type: {alert_type}')
        return v
    
    @validator('notification_methods')
    def validate_notification_methods(cls, v):
        valid_methods = ["push", "email", "sms"]
        for method in v:
            if method not in valid_methods:
                raise ValueError(f'Invalid notification method: {method}')
        return v

class UserPreferencesResponse(UserPreferences):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OnboardingData(BaseModel):
    coastal_location: str
    latitude: float
    longitude: float
    alert_types: list[str]
    notification_methods: list[str]
    alert_threshold: str = "medium"
    phone_number: Optional[str] = None  # Required for SMS notifications
    
    @validator('phone_number')
    def validate_phone_for_sms(cls, v, values):
        if 'notification_methods' in values and 'sms' in values['notification_methods']:
            if not v:
                raise ValueError('Phone number is required for SMS notifications')
        return v