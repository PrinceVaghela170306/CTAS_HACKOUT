from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class AlertLocation(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    location_name: str = Field(..., description="Human-readable location name")
    region: Optional[str] = Field(None, description="Geographic region")

class AlertMetadata(BaseModel):
    source: str = Field(..., description="Alert source system")
    confidence: float = Field(..., ge=0, le=1, description="Alert confidence level (0-1)")
    data_quality: str = Field(..., description="Data quality indicator")
    model_version: Optional[str] = Field(None, description="ML model version if applicable")
    verification_status: str = Field(..., description="Alert verification status")

class AlertDetails(BaseModel):
    predicted_peak_time: Optional[str] = Field(None, description="Predicted peak time")
    expected_duration_hours: Optional[float] = Field(None, description="Expected duration in hours")
    affected_area_km2: Optional[float] = Field(None, description="Affected area in square kilometers")
    population_at_risk: Optional[int] = Field(None, description="Population at risk")
    infrastructure_impact: Optional[str] = Field(None, description="Infrastructure impact assessment")
    economic_impact_estimate: Optional[float] = Field(None, description="Economic impact estimate")

class AlertResponse(BaseModel):
    id: str = Field(..., description="Unique alert identifier")
    alert_type: str = Field(..., description="Type of alert (flood, storm_surge, high_waves, etc.)")
    severity: str = Field(..., description="Alert severity level")
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Detailed alert description")
    location: AlertLocation
    issued_at: str = Field(..., description="Alert issue timestamp")
    expires_at: Optional[str] = Field(None, description="Alert expiration timestamp")
    status: str = Field(..., description="Alert status (active, acknowledged, resolved, expired)")
    priority: str = Field(..., description="Alert priority level")
    alert_metadata: AlertMetadata
    details: AlertDetails
    recommendations: List[str] = Field(..., description="Safety recommendations")
    emergency_contacts: List[str] = Field(..., description="Emergency contact information")
    acknowledged_by: Optional[str] = Field(None, description="User who acknowledged the alert")
    acknowledged_at: Optional[str] = Field(None, description="Acknowledgment timestamp")

class AlertsListResponse(BaseModel):
    total_alerts: int = Field(..., description="Total number of alerts")
    active_alerts: int = Field(..., description="Number of active alerts")
    critical_alerts: int = Field(..., description="Number of critical alerts")
    alerts: List[AlertResponse] = Field(..., description="List of alerts")
    last_updated: str = Field(..., description="Last update timestamp")
    filters_applied: Dict[str, Any] = Field(..., description="Applied filters")

class AlertAcknowledgment(BaseModel):
    alert_id: str = Field(..., description="Alert ID")
    acknowledged_by: str = Field(..., description="User who acknowledged")
    acknowledged_at: str = Field(..., description="Acknowledgment timestamp")
    notes: Optional[str] = Field(None, description="Acknowledgment notes")
    actions_taken: Optional[List[str]] = Field(None, description="Actions taken")

class AlertAcknowledgmentResponse(BaseModel):
    success: bool = Field(..., description="Whether acknowledgment was successful")
    message: str = Field(..., description="Response message")
    acknowledgment: AlertAcknowledgment
    updated_alert: AlertResponse

class HistoricalAlertSummary(BaseModel):
    date: str = Field(..., description="Date of alerts")
    total_alerts: int = Field(..., description="Total alerts for the date")
    alert_types: Dict[str, int] = Field(..., description="Count by alert type")
    severity_breakdown: Dict[str, int] = Field(..., description="Count by severity")
    average_duration_hours: float = Field(..., description="Average alert duration")
    false_positive_rate: float = Field(..., description="False positive rate")

class AlertHistoryResponse(BaseModel):
    location: AlertLocation
    period_start: str = Field(..., description="History period start")
    period_end: str = Field(..., description="History period end")
    total_alerts: int = Field(..., description="Total alerts in period")
    daily_summaries: List[HistoricalAlertSummary] = Field(..., description="Daily alert summaries")
    most_common_alert_type: str = Field(..., description="Most common alert type")
    peak_alert_month: str = Field(..., description="Month with most alerts")
    trends: Dict[str, str] = Field(..., description="Alert trends analysis")
    recommendations: List[str] = Field(..., description="Historical analysis recommendations")

class AlertSubscription(BaseModel):
    user_id: str = Field(..., description="User identifier")
    alert_types: List[str] = Field(..., description="Subscribed alert types")
    locations: List[AlertLocation] = Field(..., description="Subscribed locations")
    severity_threshold: str = Field(..., description="Minimum severity for notifications")
    notification_methods: List[str] = Field(..., description="Notification delivery methods")
    active: bool = Field(..., description="Whether subscription is active")
    created_at: str = Field(..., description="Subscription creation time")
    updated_at: str = Field(..., description="Last update time")

class NotificationDelivery(BaseModel):
    method: str = Field(..., description="Delivery method (email, sms, push)")
    status: str = Field(..., description="Delivery status")
    delivered_at: Optional[str] = Field(None, description="Delivery timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    retry_count: int = Field(0, description="Number of retry attempts")

class AlertNotificationResponse(BaseModel):
    alert_id: str = Field(..., description="Alert identifier")
    notification_id: str = Field(..., description="Notification identifier")
    recipient_count: int = Field(..., description="Number of recipients")
    delivery_status: List[NotificationDelivery] = Field(..., description="Delivery status per method")
    sent_at: str = Field(..., description="Notification send time")
    success_rate: float = Field(..., description="Delivery success rate")

class AlertStatistics(BaseModel):
    period: str = Field(..., description="Statistics period")
    total_alerts: int = Field(..., description="Total alerts issued")
    alerts_by_type: Dict[str, int] = Field(..., description="Alerts count by type")
    alerts_by_severity: Dict[str, int] = Field(..., description="Alerts count by severity")
    average_response_time_minutes: float = Field(..., description="Average response time")
    false_positive_rate: float = Field(..., description="False positive rate")
    user_engagement_rate: float = Field(..., description="User engagement rate")
    most_affected_locations: List[str] = Field(..., description="Most affected locations")
    peak_alert_hours: List[int] = Field(..., description="Peak alert hours of day")

class AlertSystemHealth(BaseModel):
    status: str = Field(..., description="Overall system health status")
    uptime_percentage: float = Field(..., description="System uptime percentage")
    average_processing_time_ms: float = Field(..., description="Average alert processing time")
    queue_size: int = Field(..., description="Current alert queue size")
    failed_notifications: int = Field(..., description="Failed notifications count")
    data_source_status: Dict[str, str] = Field(..., description="Status of data sources")
    last_health_check: str = Field(..., description="Last health check timestamp")