from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MonitoringStationResponse(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    location: str
    station_type: str  # coastal, port, offshore
    is_active: bool
    last_updated: datetime
    
    class Config:
        from_attributes = True

class TideDataResponse(BaseModel):
    timestamp: datetime
    tide_level: float  # meters
    predicted_level: Optional[float] = None
    anomaly: float = 0.0  # difference from predicted
    station_id: str
    
    class Config:
        from_attributes = True

class WeatherDataResponse(BaseModel):
    location: str
    temperature: float  # Celsius
    humidity: float  # percentage
    wind_speed: float  # m/s
    wind_direction: float  # degrees
    pressure: float  # hPa
    wave_height: Optional[float] = None  # meters
    wave_period: Optional[float] = None  # seconds
    timestamp: datetime
    
    class Config:
        from_attributes = True

class WaveDataResponse(BaseModel):
    timestamp: datetime
    significant_wave_height: float  # meters
    peak_wave_period: float  # seconds
    wave_direction: float  # degrees
    swell_height: Optional[float] = None
    swell_period: Optional[float] = None
    station_id: str
    
    class Config:
        from_attributes = True

class AlertResponse(BaseModel):
    id: str
    alert_type: str  # flood, storm_surge, high_waves, tsunami, erosion
    severity: str  # low, medium, high, critical
    title: str
    message: str
    location: str
    latitude: float
    longitude: float
    issued_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool
    affected_areas: List[str] = []
    
    class Config:
        from_attributes = True

class DashboardSummary(BaseModel):
    total_stations: int
    active_alerts: int
    risk_level: str  # low, medium, high, critical
    last_updated: datetime
    system_status: str  # operational, maintenance, error
    
class ForecastResponse(BaseModel):
    location: str
    forecast_type: str  # tide, weather, flood_risk
    forecast_hours: int
    generated_at: datetime
    confidence: float  # 0.0 to 1.0
    predictions: List[dict]  # Time series predictions
    
    class Config:
        from_attributes = True

class RiskAssessment(BaseModel):
    location: str
    latitude: float
    longitude: float
    overall_risk: str  # low, medium, high, critical
    flood_probability: float  # 0.0 to 1.0
    storm_surge_risk: float  # 0.0 to 1.0
    wave_risk: float  # 0.0 to 1.0
    assessment_time: datetime
    valid_until: datetime
    contributing_factors: List[str]
    
class HistoricalDataRequest(BaseModel):
    station_id: str
    start_date: datetime
    end_date: datetime
    data_type: str  # tide, weather, wave
    aggregation: Optional[str] = "hourly"  # hourly, daily, weekly
    
class HistoricalDataResponse(BaseModel):
    station_id: str
    data_type: str
    start_date: datetime
    end_date: datetime
    data_points: int
    aggregation: str
    data: List[dict]
    
class RealtimeUpdate(BaseModel):
    station_id: str
    station_name: str
    data_type: str
    value: float
    unit: str
    timestamp: datetime
    status: str  # normal, warning, critical
    
class SystemHealth(BaseModel):
    api_status: str
    database_status: str
    external_apis_status: dict
    last_data_update: datetime
    active_monitoring_stations: int
    system_uptime: str
    
class LocationData(BaseModel):
    name: str
    latitude: float
    longitude: float
    country: str
    state: Optional[str] = None
    coastal_type: str  # beach, port, estuary, bay
    population: Optional[int] = None
    elevation: Optional[float] = None  # meters above sea level