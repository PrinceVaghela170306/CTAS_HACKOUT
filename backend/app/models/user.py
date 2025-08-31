from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Profile information
    phone_number = Column(String, nullable=True)
    profile_picture_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    
    # Location preferences
    primary_location_lat = Column(Float, nullable=True)
    primary_location_lng = Column(Float, nullable=True)
    primary_location_name = Column(String, nullable=True)
    timezone = Column(String, default="UTC")
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)
    
    # Alert preferences
    alert_types = Column(JSON, default=list)  # List of alert types user wants to receive
    severity_threshold = Column(String, default="medium")  # minimum severity level
    notification_radius_km = Column(Float, default=50.0)  # radius for location-based alerts
    
    # Onboarding status
    onboarding_completed = Column(Boolean, default=False)
    onboarding_step = Column(Integer, default=0)
    
    # User role and permissions
    role = Column(String, default="user")  # user, admin, emergency_manager
    permissions = Column(JSON, default=list)
    
    # Account status
    account_locked = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    last_failed_login = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, full_name={self.full_name})>"

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed = Column(DateTime(timezone=True), server_default=func.now())
    
    # Session metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    device_type = Column(String, nullable=True)
    location = Column(String, nullable=True)
    
    # Session status
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoked_reason = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, active={self.is_active})>"

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True, unique=True)
    
    # Dashboard preferences
    default_map_zoom = Column(Integer, default=10)
    default_map_type = Column(String, default="satellite")  # satellite, terrain, roadmap
    show_monitoring_stations = Column(Boolean, default=True)
    show_weather_overlay = Column(Boolean, default=True)
    show_tide_data = Column(Boolean, default=True)
    show_wave_data = Column(Boolean, default=True)
    
    # Data visualization preferences
    chart_theme = Column(String, default="light")  # light, dark
    time_format = Column(String, default="24h")  # 12h, 24h
    date_format = Column(String, default="MM/DD/YYYY")
    units_system = Column(String, default="metric")  # metric, imperial
    
    # Alert preferences (detailed)
    flood_alerts = Column(Boolean, default=True)
    storm_surge_alerts = Column(Boolean, default=True)
    high_wave_alerts = Column(Boolean, default=True)
    erosion_alerts = Column(Boolean, default=False)
    water_quality_alerts = Column(Boolean, default=False)
    
    # Notification timing
    quiet_hours_start = Column(String, default="22:00")  # HH:MM format
    quiet_hours_end = Column(String, default="07:00")
    weekend_notifications = Column(Boolean, default=True)
    
    # Advanced settings
    data_retention_days = Column(Integer, default=365)
    auto_acknowledge_resolved = Column(Boolean, default=True)
    share_location_data = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserPreferences(user_id={self.user_id})>"

class UserLocation(Base):
    __tablename__ = "user_locations"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Location details
    name = Column(String, nullable=False)  # User-defined name
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String, nullable=True)
    
    # Location metadata
    location_type = Column(String, default="custom")  # home, work, custom, favorite
    is_primary = Column(Boolean, default=False)
    monitoring_radius_km = Column(Float, default=25.0)
    
    # Alert settings for this location
    alerts_enabled = Column(Boolean, default=True)
    alert_types = Column(JSON, default=list)
    severity_threshold = Column(String, default="medium")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserLocation(id={self.id}, name={self.name}, user_id={self.user_id})>"

class UserActivity(Base):
    __tablename__ = "user_activities"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Activity details
    activity_type = Column(String, nullable=False)  # login, logout, alert_view, dashboard_access, etc.
    description = Column(Text, nullable=True)
    activity_metadata = Column(JSON, default=dict)  # Additional activity data
    
    # Context information
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    
    # Timing
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    duration_seconds = Column(Integer, nullable=True)
    
    # Status
    status = Column(String, default="completed")  # completed, failed, in_progress
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<UserActivity(id={self.id}, user_id={self.user_id}, type={self.activity_type})>"