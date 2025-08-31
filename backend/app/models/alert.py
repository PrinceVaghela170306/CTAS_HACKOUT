from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, Index
from sqlalchemy.sql import func
from datetime import datetime
from .monitoring import Base

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, index=True)
    
    # Alert classification
    alert_type = Column(String, nullable=False, index=True)  # flood, storm_surge, high_waves, erosion, water_quality
    severity = Column(String, nullable=False, index=True)  # low, medium, high, critical
    priority = Column(String, nullable=False)  # low, medium, high, urgent
    
    # Alert content
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    detailed_message = Column(Text, nullable=True)
    
    # Location information
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String, nullable=False)
    affected_radius_km = Column(Float, default=10.0)
    region = Column(String, nullable=True)
    
    # Timing
    issued_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    effective_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Prediction details
    predicted_peak_time = Column(DateTime(timezone=True), nullable=True)
    expected_duration_hours = Column(Float, nullable=True)
    
    # Impact assessment
    population_at_risk = Column(Integer, nullable=True)
    infrastructure_impact = Column(String, nullable=True)  # minimal, moderate, significant, severe
    economic_impact_estimate = Column(Float, nullable=True)
    affected_area_km2 = Column(Float, nullable=True)
    
    # Alert status
    status = Column(String, default="active", index=True)  # active, acknowledged, resolved, expired, cancelled
    is_active = Column(Boolean, default=True, index=True)
    
    # Source and confidence
    source_system = Column(String, nullable=False)  # ML_model, manual, external_api
    data_sources = Column(JSON, default=list)  # List of data sources used
    confidence_score = Column(Float, nullable=True)  # 0-1 confidence level
    model_version = Column(String, nullable=True)
    
    # Verification
    verification_status = Column(String, default="unverified")  # unverified, verified, false_positive
    verified_by = Column(String, nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # User interaction
    acknowledged_by = Column(String, nullable=True)  # User ID who acknowledged
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledgment_notes = Column(Text, nullable=True)
    
    # Recommendations and actions
    recommendations = Column(JSON, default=list)  # List of recommended actions
    emergency_contacts = Column(JSON, default=list)  # Emergency contact information
    evacuation_zones = Column(JSON, default=list)  # Affected evacuation zones
    
    # Metadata
    tags = Column(JSON, default=list)  # Searchable tags
    external_alert_ids = Column(JSON, default=dict)  # IDs from external systems
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_alert_location_time', 'latitude', 'longitude', 'issued_at'),
        Index('idx_alert_type_severity', 'alert_type', 'severity'),
        Index('idx_alert_status_active', 'status', 'is_active'),
    )
    
    def __repr__(self):
        return f"<Alert(id={self.id}, type={self.alert_type}, severity={self.severity}, status={self.status})>"

class AlertNotification(Base):
    __tablename__ = "alert_notifications"
    
    id = Column(String, primary_key=True, index=True)
    alert_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Notification details
    notification_method = Column(String, nullable=False)  # email, sms, push, webhook
    recipient = Column(String, nullable=False)  # email address, phone number, device token
    
    # Message content
    subject = Column(String, nullable=True)
    message_body = Column(Text, nullable=False)
    message_format = Column(String, default="text")  # text, html, json
    
    # Delivery status
    status = Column(String, default="pending", index=True)  # pending, sent, delivered, failed, bounced
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Delivery attempts
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_code = Column(String, nullable=True)
    
    # Provider details
    provider = Column(String, nullable=True)  # twilio, firebase, sendgrid, etc.
    provider_message_id = Column(String, nullable=True)
    provider_response = Column(JSON, nullable=True)
    
    # User interaction
    opened_at = Column(DateTime(timezone=True), nullable=True)
    clicked_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_notification_alert_user', 'alert_id', 'user_id'),
        Index('idx_notification_status_retry', 'status', 'next_retry_at'),
    )
    
    def __repr__(self):
        return f"<AlertNotification(id={self.id}, alert_id={self.alert_id}, method={self.notification_method}, status={self.status})>"

class AlertSubscription(Base):
    __tablename__ = "alert_subscriptions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Subscription criteria
    alert_types = Column(JSON, default=list)  # Types of alerts to receive
    severity_threshold = Column(String, default="medium")  # Minimum severity level
    
    # Location criteria
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    radius_km = Column(Float, default=50.0)
    location_name = Column(String, nullable=True)
    
    # Notification preferences
    notification_methods = Column(JSON, default=list)  # email, sms, push
    email_address = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    device_tokens = Column(JSON, default=list)  # Push notification tokens
    
    # Timing preferences
    quiet_hours_start = Column(String, nullable=True)  # HH:MM format
    quiet_hours_end = Column(String, nullable=True)
    timezone = Column(String, default="UTC")
    weekend_notifications = Column(Boolean, default=True)
    
    # Subscription status
    is_active = Column(Boolean, default=True, index=True)
    confirmed = Column(Boolean, default=False)
    confirmation_token = Column(String, nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Subscription metadata
    subscription_source = Column(String, default="web")  # web, mobile, api
    tags = Column(JSON, default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_subscription_user_active', 'user_id', 'is_active'),
        Index('idx_subscription_location', 'latitude', 'longitude'),
    )
    
    def __repr__(self):
        return f"<AlertSubscription(id={self.id}, user_id={self.user_id}, active={self.is_active})>"

class AlertHistory(Base):
    __tablename__ = "alert_history"
    
    id = Column(String, primary_key=True, index=True)
    alert_id = Column(String, nullable=False, index=True)
    
    # Change tracking
    action = Column(String, nullable=False)  # created, updated, acknowledged, resolved, cancelled
    field_changed = Column(String, nullable=True)  # Field that was changed
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    # Change metadata
    changed_by = Column(String, nullable=True)  # User ID or system
    change_reason = Column(String, nullable=True)
    change_source = Column(String, default="system")  # system, user, api
    
    # Context
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_alert_history_alert_time', 'alert_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<AlertHistory(id={self.id}, alert_id={self.alert_id}, action={self.action})>"

class AlertMetrics(Base):
    __tablename__ = "alert_metrics"
    
    id = Column(String, primary_key=True, index=True)
    
    # Time period
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    period_type = Column(String, nullable=False)  # hourly, daily, weekly, monthly
    
    # Location (optional - can be global metrics)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    region = Column(String, nullable=True)
    
    # Alert counts
    total_alerts = Column(Integer, default=0)
    alerts_by_type = Column(JSON, default=dict)  # Count by alert type
    alerts_by_severity = Column(JSON, default=dict)  # Count by severity
    
    # Performance metrics
    average_response_time_minutes = Column(Float, nullable=True)
    false_positive_count = Column(Integer, default=0)
    false_positive_rate = Column(Float, nullable=True)
    
    # User engagement
    total_notifications_sent = Column(Integer, default=0)
    notifications_opened = Column(Integer, default=0)
    notifications_clicked = Column(Integer, default=0)
    user_acknowledgments = Column(Integer, default=0)
    
    # System performance
    average_processing_time_ms = Column(Float, nullable=True)
    failed_notifications = Column(Integer, default=0)
    system_uptime_percent = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_metrics_date_period', 'date', 'period_type'),
        Index('idx_metrics_location_date', 'latitude', 'longitude', 'date'),
    )
    
    def __repr__(self):
        return f"<AlertMetrics(date={self.date}, period={self.period_type}, total={self.total_alerts})>"