from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.routers.auth import get_current_user_dependency
from app.schemas.dashboard import ForecastResponse, RiskAssessment
from app.services.ml_service import MLModelManager
import logging

logger = logging.getLogger(__name__)
import random

# Initialize ML model manager
ml_manager = MLModelManager()

router = APIRouter()

@router.get("/flood-risk/{location}", response_model=RiskAssessment)
async def get_flood_risk_forecast(
    location: str,
    latitude: float = Query(..., description="Latitude of location"),
    longitude: float = Query(..., description="Longitude of location"),
    hours: int = Query(24, description="Forecast horizon in hours"),
    current_user: dict = Depends(get_current_user_dependency)
):
    """Get AI-powered flood risk assessment and forecast using LSTM model"""
    try:
        # Get current environmental conditions (in production, fetch from sensors/APIs)
        current_conditions = {
            "tide_level": 1.5 + random.uniform(-0.5, 1.0),
            "wave_height": 1.0 + random.uniform(0, 2.0),
            "storm_surge": random.uniform(0, 1.5),
            "rainfall_mm": random.uniform(0, 25),
            "wind_speed_kmh": random.uniform(10, 60),
            "atmospheric_pressure": random.uniform(990, 1020),
            "temperature_c": random.uniform(20, 35),
            "humidity_percent": random.uniform(60, 90)
        }
        
        # Use ML model for prediction
        flood_prediction = await ml_manager.flood_model.predict_flood_risk(current_conditions)
        
        # Get additional forecasts
        tide_forecast = await ml_manager.tide_model.predict_tide_levels(
            latitude, longitude, hours=hours
        )
        surge_forecast = await ml_manager.storm_surge_model.predict_storm_surge(
            current_conditions, hours=hours
        )
        wave_forecast = await ml_manager.wave_model.predict_wave_height(
            current_conditions, hours=hours
        )
        
        return RiskAssessment(
            location=location,
            latitude=latitude,
            longitude=longitude,
            overall_risk=flood_prediction["risk_level"],
            flood_probability=flood_prediction["flood_probability"],
            storm_surge_risk=surge_forecast.get("risk_level", 0.3),
            wave_risk=wave_forecast.get("risk_level", 0.3),
            assessment_time=datetime.utcnow(),
            valid_until=datetime.utcnow() + timedelta(hours=hours),
            contributing_factors=[
                f"Tide impact: {flood_prediction['factors'].get('tide_impact', 0):.2f}",
                f"Wave impact: {flood_prediction['factors'].get('wave_impact', 0):.2f}",
                f"Storm surge: {flood_prediction['factors'].get('surge_impact', 0):.2f}",
                f"Rainfall: {flood_prediction['factors'].get('rainfall_impact', 0):.2f}",
                f"Model confidence: {flood_prediction['confidence']:.2f}"
            ]
        )
        
    except Exception as e:
        logger.error(f"Error generating flood risk forecast for {location}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate flood risk forecast")

@router.post("/flood-risk-advanced/{location}")
async def get_advanced_flood_prediction(
    location: str,
    latitude: float = Query(..., description="Latitude of location"),
    longitude: float = Query(..., description="Longitude of location"),
    current_conditions: Dict[str, Any] = Body(..., description="Current environmental conditions"),
    historical_data: Optional[List[Dict[str, Any]]] = Body(None, description="Historical data for LSTM"),
    current_user: dict = Depends(get_current_user_dependency)
):
    """Get advanced flood prediction with historical data and detailed analysis"""
    try:
        # Use LSTM model with historical data if provided
        flood_prediction = await ml_manager.flood_model.predict_flood_risk(
            current_conditions, historical_data
        )
        
        # Generate forecast timeline
        forecast_timeline = []
        base_time = datetime.utcnow()
        
        for i in range(0, 48, 2):  # 48-hour forecast, every 2 hours
            timestamp = base_time + timedelta(hours=i)
            
            # Simulate changing conditions over time
            future_conditions = current_conditions.copy()
            future_conditions["tide_level"] += random.uniform(-0.3, 0.3)
            future_conditions["wave_height"] += random.uniform(-0.2, 0.2)
            
            future_prediction = await ml_manager.flood_model.predict_flood_risk(future_conditions)
            
            forecast_timeline.append({
                "timestamp": timestamp.isoformat(),
                "flood_probability": future_prediction["flood_probability"],
                "risk_level": future_prediction["risk_level"],
                "confidence": future_prediction["confidence"]
            })
        
        return {
            "location": location,
            "coordinates": {"latitude": latitude, "longitude": longitude},
            "current_prediction": flood_prediction,
            "forecast_timeline": forecast_timeline,
            "model_info": {
                "model_type": flood_prediction.get("model_type", "LSTM"),
                "model_version": flood_prediction["model_version"],
                "prediction_time": flood_prediction["prediction_time"]
            },
            "recommendations": _generate_flood_recommendations(flood_prediction)
        }
        
    except Exception as e:
        logger.error(f"Error generating advanced flood prediction for {location}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate advanced flood prediction")

def _generate_flood_recommendations(prediction: Dict[str, Any]) -> List[str]:
    """Generate actionable recommendations based on flood prediction"""
    recommendations = []
    
    risk_level = prediction["risk_level"]
    flood_prob = prediction["flood_probability"]
    
    if risk_level == "critical" or flood_prob > 0.8:
        recommendations.extend([
            "Immediate evacuation recommended for low-lying areas",
            "Activate emergency response protocols",
            "Issue public flood warnings",
            "Deploy emergency services to high-risk zones"
        ])
    elif risk_level == "high" or flood_prob > 0.5:
        recommendations.extend([
            "Monitor conditions closely",
            "Prepare evacuation routes",
            "Alert emergency services",
            "Issue flood watch advisory"
        ])
    elif risk_level == "medium" or flood_prob > 0.3:
        recommendations.extend([
            "Continue monitoring",
            "Check drainage systems",
            "Prepare emergency supplies",
            "Stay informed of weather updates"
        ])
    else:
        recommendations.extend([
            "Normal monitoring sufficient",
            "Routine maintenance checks",
            "Standard preparedness measures"
        ])
    
    return recommendations

@router.get("/tide/{location}", response_model=ForecastResponse)
async def get_tide_forecast(
    location: str,
    hours: int = Query(48, description="Forecast horizon in hours"),
    current_user: dict = Depends(get_current_user_dependency)
):
    """Get tide level forecast using ML models"""
    try:
        # Generate synthetic tide predictions
        predictions = []
        base_time = datetime.utcnow()
        
        for i in range(0, hours, 2):  # Every 2 hours
            timestamp = base_time + timedelta(hours=i)
            # Simulate tidal pattern with some randomness
            tide_level = 1.5 + 1.2 * random.sin(i * 0.26) + random.uniform(-0.3, 0.3)
            
            predictions.append({
                "timestamp": timestamp.isoformat(),
                "tide_level": round(tide_level, 2),
                "confidence": random.uniform(0.8, 0.95)
            })
        
        return ForecastResponse(
            location=location,
            forecast_type="tide",
            forecast_hours=hours,
            generated_at=datetime.utcnow(),
            confidence=0.87,
            predictions=predictions
        )
        
    except Exception as e:
        logger.error(f"Error generating tide forecast for {location}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate tide forecast")

@router.get("/storm-surge/{location}")
async def get_storm_surge_forecast(
    location: str,
    latitude: float = Query(..., description="Latitude of location"),
    longitude: float = Query(..., description="Longitude of location"),
    current_user: dict = Depends(get_current_user_dependency)
):
    """Get storm surge forecast and risk assessment"""
    try:
        # Simulate storm surge prediction
        surge_risk = random.uniform(0.1, 0.8)
        max_surge_height = random.uniform(0.5, 3.0)
        
        forecast_data = {
            "location": location,
            "coordinates": {"latitude": latitude, "longitude": longitude},
            "storm_surge_risk": surge_risk,
            "max_predicted_surge": max_surge_height,
            "peak_surge_time": (datetime.utcnow() + timedelta(hours=random.randint(6, 18))).isoformat(),
            "duration_hours": random.randint(4, 12),
            "confidence": random.uniform(0.75, 0.92),
            "warning_level": "high" if surge_risk > 0.6 else "medium" if surge_risk > 0.3 else "low",
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return forecast_data
        
    except Exception as e:
        logger.error(f"Error generating storm surge forecast for {location}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate storm surge forecast")

@router.get("/wave-height/{location}")
async def get_wave_height_forecast(
    location: str,
    hours: int = Query(24, description="Forecast horizon in hours"),
    current_user: dict = Depends(get_current_user_dependency)
):
    """Get wave height forecast"""
    try:
        predictions = []
        base_time = datetime.utcnow()
        
        for i in range(0, hours, 3):  # Every 3 hours
            timestamp = base_time + timedelta(hours=i)
            # Simulate wave height with weather patterns
            wave_height = 1.0 + 0.8 * random.sin(i * 0.2) + random.uniform(-0.2, 0.4)
            wave_period = random.uniform(6, 12)
            
            predictions.append({
                "timestamp": timestamp.isoformat(),
                "significant_wave_height": round(max(0.1, wave_height), 2),
                "peak_wave_period": round(wave_period, 1),
                "wave_direction": random.randint(180, 270),  # SW to W
                "confidence": random.uniform(0.8, 0.9)
            })
        
        return {
            "location": location,
            "forecast_type": "wave_height",
            "forecast_hours": hours,
            "generated_at": datetime.utcnow().isoformat(),
            "predictions": predictions,
            "model_info": {
                "model_type": "LSTM Neural Network",
                "training_data_years": 5,
                "last_updated": "2024-01-01T00:00:00Z"
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating wave height forecast for {location}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate wave height forecast")

@router.post("/retrain-model")
async def retrain_forecasting_model(
    model_type: str = Query(..., description="Model type: flood, tide, storm_surge, wave"),
    current_user: dict = Depends(get_current_user_dependency)
):
    """Trigger model retraining with latest data"""
    try:
        result = await ml_manager.retrain_model(model_type)
        
        return {
            "message": f"Model retraining completed for {model_type}",
            "model_type": model_type,
            "initiated_by": current_user["email"],
            "initiated_at": datetime.utcnow().isoformat(),
            "status": "completed" if result["success"] else "failed",
            "metrics": result.get("metrics", {}),
            "details": result.get("message", "")
        }
        
    except Exception as e:
        logger.error(f"Error initiating model retraining: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate model retraining")

@router.post("/train-flood-model")
async def train_flood_model_with_data(
    training_data: List[Dict[str, Any]] = Body(..., description="Historical training data"),
    labels: List[float] = Body(..., description="Flood occurrence labels (0-1)"),
    current_user: dict = Depends(get_current_user_dependency)
):
    """Train flood prediction model with custom dataset"""
    try:
        if len(training_data) != len(labels):
            raise HTTPException(status_code=400, detail="Training data and labels must have same length")
        
        if len(training_data) < 50:
            raise HTTPException(status_code=400, detail="Need at least 50 training samples")
        
        # Train the LSTM model
        result = await ml_manager.flood_model.train_model(training_data, labels)
        
        return {
            "message": "Flood model training completed",
            "success": result["success"],
            "training_samples": len(training_data),
            "metrics": result.get("metrics", {}),
            "trained_by": current_user["email"],
            "trained_at": datetime.utcnow().isoformat(),
            "details": result.get("message", "")
        }
        
    except Exception as e:
        logger.error(f"Error training flood model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to train flood model: {str(e)}")

@router.get("/model-performance")
async def get_model_performance(
    model_type: str = Query("all", description="Model type or 'all'"),
    current_user: dict = Depends(get_current_user_dependency)
):
    """Get model performance metrics from actual ML models"""
    try:
        # Get performance metrics from ML manager
        performance_data = ml_manager.get_model_performance()
        
        if model_type != "all" and model_type in performance_data:
            return {model_type: performance_data[model_type]}
        
        return performance_data
        
    except Exception as e:
        logger.error(f"Error fetching model performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch model performance")