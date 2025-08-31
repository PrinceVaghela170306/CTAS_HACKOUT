from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
from app.routers.auth import get_current_user_dependency
from app.schemas.dashboard import (
    MonitoringStationResponse,
    TideDataResponse,
    WeatherDataResponse,
    DashboardSummary
)
from app.services.data_service import DataCollectionService
# from app.services.weather_service import WeatherService  # TODO: Create weather service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/stations", response_model=List[MonitoringStationResponse])
async def get_monitoring_stations(
    current_user: dict = Depends(get_current_user_dependency),
    active_only: bool = Query(True, description="Return only active stations")
):
    """Get all monitoring stations"""
    try:
        data_service = DataCollectionService()
        stations = await data_service.get_monitoring_stations(active_only=active_only)
        
        return [
            MonitoringStationResponse(
                id=station["id"],
                name=station["name"],
                latitude=station["latitude"],
                longitude=station["longitude"],
                location=station["location"],
                station_type=station["station_type"],
                is_active=station["is_active"],
                last_updated=station.get("last_updated", datetime.utcnow())
            )
            for station in stations
        ]
        
    except Exception as e:
        logger.error(f"Error fetching monitoring stations: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch monitoring stations")

@router.get("/stations/{station_id}/tide-data", response_model=List[TideDataResponse])
async def get_station_tide_data(
    station_id: str,
    hours: int = Query(24, description="Hours of historical data to fetch"),
    current_user: dict = Depends(get_current_user_dependency)
):
    """Get tide data for a specific monitoring station"""
    try:
        data_service = DataCollectionService()
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        tide_data = await data_service.get_tide_data(
            station_id=station_id,
            start_time=start_time,
            end_time=end_time
        )
        
        return [
            TideDataResponse(
                timestamp=data["timestamp"],
                tide_level=data["tide_level"],
                predicted_level=data.get("predicted_level"),
                anomaly=data.get("anomaly", 0.0),
                station_id=station_id
            )
            for data in tide_data
        ]
        
    except Exception as e:
        logger.error(f"Error fetching tide data for station {station_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tide data")

@router.get("/weather/{location}", response_model=WeatherDataResponse)
async def get_weather_data(
    location: str,
    current_user: dict = Depends(get_current_user_dependency)
):
    """Get current weather data for a location"""
    try:
        # weather_service = WeatherService()  # TODO: Create weather service
        # weather_data = await weather_service.get_current_weather(location)
        weather_data = {"message": "Weather service not implemented yet"}
        
        return WeatherDataResponse(
            location=location,
            temperature=weather_data["temperature"],
            humidity=weather_data["humidity"],
            wind_speed=weather_data["wind_speed"],
            wind_direction=weather_data["wind_direction"],
            pressure=weather_data["pressure"],
            wave_height=weather_data.get("wave_height"),
            wave_period=weather_data.get("wave_period"),
            timestamp=weather_data["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Error fetching weather data for {location}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")

@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    current_user: dict = Depends(get_current_user_dependency)
):
    """Get dashboard summary with key metrics"""
    try:
        data_service = DataCollectionService()
        # weather_service = WeatherService()  # TODO: Create weather service
        
        # Get active alerts count
        active_alerts = await data_service.get_active_alerts_count()
        
        # Get total monitoring stations
        stations = await data_service.get_monitoring_stations(active_only=True)
        total_stations = len(stations)
        
        # Get latest data timestamp
        latest_update = await data_service.get_latest_data_timestamp()
        
        # Get current risk level (simplified)
        risk_level = await data_service.calculate_current_risk_level()
        
        return DashboardSummary(
            total_stations=total_stations,
            active_alerts=active_alerts,
            risk_level=risk_level,
            last_updated=latest_update or datetime.utcnow(),
            system_status="operational"
        )
        
    except Exception as e:
        logger.error(f"Error generating dashboard summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate dashboard summary")

@router.get("/historical-data")
async def get_historical_data(
    station_id: str = Query(..., description="Station ID"),
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    data_type: str = Query("tide", description="Data type: tide, weather, wave"),
    current_user: dict = Depends(get_current_user_dependency)
):
    """Get historical data for analysis and replay"""
    try:
        data_service = DataCollectionService()
        
        if data_type == "tide":
            data = await data_service.get_tide_data(station_id, start_date, end_date)
        elif data_type == "weather":
            data = await data_service.get_weather_data(station_id, start_date, end_date)
        elif data_type == "wave":
            data = await data_service.get_wave_data(station_id, start_date, end_date)
        else:
            raise HTTPException(status_code=400, detail="Invalid data type")
        
        return {
            "station_id": station_id,
            "data_type": data_type,
            "start_date": start_date,
            "end_date": end_date,
            "data_points": len(data),
            "data": data
        }
        
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch historical data")

@router.get("/real-time-updates")
async def get_real_time_updates(
    current_user: dict = Depends(get_current_user_dependency)
):
    """Get real-time updates for dashboard (WebSocket alternative)"""
    try:
        data_service = DataCollectionService()
        
        # Get latest data from all active stations
        updates = await data_service.get_latest_updates()
        
        return {
            "timestamp": datetime.utcnow(),
            "updates": updates,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error fetching real-time updates: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch real-time updates")