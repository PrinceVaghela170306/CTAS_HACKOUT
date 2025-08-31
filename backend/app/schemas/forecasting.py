from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class LocationCoordinates(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")

class FloodRiskFactors(BaseModel):
    tide_level: float = Field(..., description="Current tide level in meters")
    wave_height: float = Field(..., description="Wave height in meters")
    storm_surge: float = Field(..., description="Storm surge height in meters")
    rainfall_mm: float = Field(..., description="Rainfall in millimeters")
    wind_speed_kmh: float = Field(..., description="Wind speed in km/h")
    atmospheric_pressure: float = Field(..., description="Atmospheric pressure in hPa")

class RiskMetrics(BaseModel):
    flood_probability: float = Field(..., ge=0, le=1, description="Flood probability (0-1)")
    risk_level: str = Field(..., description="Risk level: low, medium, high, critical")
    confidence_score: float = Field(..., ge=0, le=1, description="Model confidence (0-1)")
    time_to_peak_hours: Optional[float] = Field(None, description="Time to peak flood risk in hours")
    expected_duration_hours: Optional[float] = Field(None, description="Expected flood duration in hours")

class FloodRiskAssessmentResponse(BaseModel):
    location: str = Field(..., description="Location name")
    coordinates: LocationCoordinates
    assessment_time: str = Field(..., description="Assessment timestamp")
    forecast_horizon_hours: int = Field(..., description="Forecast horizon in hours")
    risk_factors: FloodRiskFactors
    risk_metrics: RiskMetrics
    recommendations: List[str] = Field(..., description="Safety recommendations")
    model_version: str = Field(..., description="ML model version used")

class TideForecastPoint(BaseModel):
    timestamp: str = Field(..., description="Forecast timestamp")
    tide_height_m: float = Field(..., description="Predicted tide height in meters")
    tide_type: str = Field(..., description="Tide type: high, low")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence")

class TideForecastResponse(BaseModel):
    location: str = Field(..., description="Location name")
    coordinates: LocationCoordinates
    forecast_generated: str = Field(..., description="Forecast generation time")
    forecast_period_hours: int = Field(..., description="Forecast period in hours")
    predictions: List[TideForecastPoint] = Field(..., description="Tide predictions")
    tidal_range_m: float = Field(..., description="Expected tidal range in meters")
    next_high_tide: Optional[TideForecastPoint] = Field(None, description="Next high tide")
    next_low_tide: Optional[TideForecastPoint] = Field(None, description="Next low tide")
    model_accuracy: float = Field(..., description="Historical model accuracy")

class StormSurgeConditions(BaseModel):
    wind_speed_kmh: float = Field(..., description="Wind speed in km/h")
    wind_direction: str = Field(..., description="Wind direction")
    atmospheric_pressure: float = Field(..., description="Atmospheric pressure in hPa")
    storm_intensity: str = Field(..., description="Storm intensity category")
    distance_to_storm_km: float = Field(..., description="Distance to storm center in km")

class SurgeForecastPoint(BaseModel):
    timestamp: str = Field(..., description="Forecast timestamp")
    surge_height_m: float = Field(..., description="Predicted surge height in meters")
    total_water_level_m: float = Field(..., description="Total water level (tide + surge)")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence")

class StormSurgeForecastResponse(BaseModel):
    location: str = Field(..., description="Location name")
    coordinates: LocationCoordinates
    forecast_generated: str = Field(..., description="Forecast generation time")
    storm_conditions: StormSurgeConditions
    predictions: List[SurgeForecastPoint] = Field(..., description="Storm surge predictions")
    peak_surge_time: Optional[str] = Field(None, description="Expected peak surge time")
    peak_surge_height_m: float = Field(..., description="Expected peak surge height")
    evacuation_recommended: bool = Field(..., description="Whether evacuation is recommended")
    model_version: str = Field(..., description="Model version used")

class WaveConditions(BaseModel):
    wind_speed_kmh: float = Field(..., description="Wind speed in km/h")
    wind_direction: str = Field(..., description="Wind direction")
    fetch_distance_km: float = Field(..., description="Fetch distance in km")
    water_depth_m: float = Field(..., description="Water depth in meters")

class WaveForecastPoint(BaseModel):
    timestamp: str = Field(..., description="Forecast timestamp")
    significant_wave_height_m: float = Field(..., description="Significant wave height in meters")
    peak_wave_period_s: float = Field(..., description="Peak wave period in seconds")
    wave_direction: str = Field(..., description="Wave direction")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence")

class WaveHeightForecastResponse(BaseModel):
    location: str = Field(..., description="Location name")
    coordinates: LocationCoordinates
    forecast_generated: str = Field(..., description="Forecast generation time")
    wave_conditions: WaveConditions
    predictions: List[WaveForecastPoint] = Field(..., description="Wave height predictions")
    max_wave_height_m: float = Field(..., description="Maximum expected wave height")
    hazardous_conditions: bool = Field(..., description="Whether hazardous conditions expected")
    surf_quality_rating: str = Field(..., description="Surf quality rating")
    model_accuracy: float = Field(..., description="Historical model accuracy")

class TrainingMetrics(BaseModel):
    training_samples: int = Field(..., description="Number of training samples")
    validation_accuracy: float = Field(..., description="Validation accuracy")
    training_duration_minutes: int = Field(..., description="Training duration in minutes")
    model_size_mb: float = Field(..., description="Model size in MB")
    feature_importance: Dict[str, float] = Field(..., description="Feature importance scores")

class ModelRetrainingResponse(BaseModel):
    model_type: str = Field(..., description="Type of model retrained")
    retrain_triggered: str = Field(..., description="Retrain trigger timestamp")
    status: str = Field(..., description="Retraining status")
    training_metrics: Optional[TrainingMetrics] = Field(None, description="Training metrics")
    improvement_percentage: Optional[float] = Field(None, description="Performance improvement")
    deployment_time: Optional[str] = Field(None, description="Model deployment time")
    previous_version: str = Field(..., description="Previous model version")
    new_version: str = Field(..., description="New model version")

class ModelPerformanceMetrics(BaseModel):
    accuracy: float = Field(..., description="Model accuracy")
    precision: float = Field(..., description="Model precision")
    recall: float = Field(..., description="Model recall")
    f1_score: float = Field(..., description="F1 score")
    mae: float = Field(..., description="Mean Absolute Error")
    rmse: float = Field(..., description="Root Mean Square Error")
    last_updated: str = Field(..., description="Last metrics update")

class ModelInfo(BaseModel):
    model_name: str = Field(..., description="Model name")
    model_type: str = Field(..., description="Model type (LSTM, GRU, etc.)")
    version: str = Field(..., description="Model version")
    training_date: str = Field(..., description="Last training date")
    performance_metrics: ModelPerformanceMetrics
    prediction_types: List[str] = Field(..., description="Types of predictions")
    data_sources: List[str] = Field(..., description="Data sources used")

class ModelPerformanceResponse(BaseModel):
    summary_generated: str = Field(..., description="Summary generation time")
    total_models: int = Field(..., description="Total number of models")
    models: List[ModelInfo] = Field(..., description="Model information")
    overall_system_health: str = Field(..., description="Overall system health")
    recommendations: List[str] = Field(..., description="Performance recommendations")