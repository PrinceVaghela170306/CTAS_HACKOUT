from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.database import get_db
from app.services.environmental_service import environmental_service
from app.routers.auth import get_current_user_dependency
from loguru import logger

router = APIRouter(tags=["environmental"])

@router.get("/data/current")
async def get_current_environmental_data(
    station_id: Optional[str] = Query(None, description="Specific station ID"),
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get current environmental data from all or specific monitoring stations"""
    try:
        data = await environmental_service.collect_all_environmental_data(db)
        
        if station_id:
            # Filter for specific station
            filtered_data = {
                'timestamp': data['timestamp'],
                'stations_data': [s for s in data['stations_data'] if s['station_id'] == station_id],
                'satellite_data': data.get('satellite_data', {}),
                'weather_data': data.get('weather_data', {}),
                'ocean_data': data.get('ocean_data', {})
            }
            
            if not filtered_data['stations_data']:
                raise HTTPException(status_code=404, detail=f"Station {station_id} not found or no data available")
            
            return filtered_data
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current environmental data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get environmental data")

@router.get("/data/historical")
async def get_historical_environmental_data(
    station_id: str = Query(..., description="Station ID"),
    days: int = Query(7, description="Number of days to look back", ge=1, le=90),
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get historical environmental data for a specific station"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        data = await environmental_service.get_historical_data(
            station_id=station_id,
            start_date=start_date,
            end_date=end_date,
            db=db
        )
        
        if not data:
            raise HTTPException(status_code=404, detail=f"No historical data found for station {station_id}")
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting historical environmental data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get historical data")

@router.get("/analysis/trends")
async def get_environmental_trends(
    station_id: str = Query(..., description="Station ID"),
    days: int = Query(30, description="Number of days to analyze", ge=7, le=365),
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get environmental trend analysis for a specific station"""
    try:
        analysis = await environmental_service.analyze_environmental_trends(
            station_id=station_id,
            days=days,
            db=db
        )
        
        if 'error' in analysis:
            raise HTTPException(status_code=404, detail=analysis['error'])
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting environmental trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze environmental trends")

@router.get("/satellite/current")
async def get_current_satellite_data(
    current_user: dict = Depends(get_current_user_dependency)
) -> Dict[str, Any]:
    """Get current satellite data and imagery information"""
    try:
        satellite_data = await environmental_service._collect_satellite_data()
        
        if not satellite_data:
            raise HTTPException(status_code=503, detail="Satellite data temporarily unavailable")
        
        return satellite_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting satellite data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get satellite data")

@router.get("/weather/current")
async def get_current_weather_data(
    current_user: dict = Depends(get_current_user_dependency)
) -> Dict[str, Any]:
    """Get current weather conditions and marine forecast"""
    try:
        weather_data = await environmental_service._collect_weather_data()
        
        if not weather_data:
            raise HTTPException(status_code=503, detail="Weather data temporarily unavailable")
        
        return weather_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting weather data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get weather data")

@router.get("/ocean/current")
async def get_current_ocean_data(
    current_user: dict = Depends(get_current_user_dependency)
) -> Dict[str, Any]:
    """Get current oceanographic data"""
    try:
        ocean_data = await environmental_service._collect_ocean_data()
        
        if not ocean_data:
            raise HTTPException(status_code=503, detail="Ocean data temporarily unavailable")
        
        return ocean_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ocean data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get ocean data")

@router.get("/quality/report")
async def get_data_quality_report(
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get data quality report for all monitoring stations"""
    try:
        report = await environmental_service.get_data_quality_report(db)
        
        if 'error' in report:
            raise HTTPException(status_code=500, detail=report['error'])
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting data quality report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate data quality report")

@router.post("/data/collect")
async def trigger_data_collection(
    background_tasks: BackgroundTasks,
    station_id: Optional[str] = Query(None, description="Specific station ID to collect data for"),
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Manually trigger environmental data collection"""
    try:
        # Add data collection to background tasks
        background_tasks.add_task(
            environmental_service.collect_all_environmental_data,
            db
        )
        
        return {
            'success': True,
            'message': 'Data collection initiated',
            'triggered_at': datetime.utcnow(),
            'triggered_by': current_user['email'],
            'station_id': station_id
        }
        
    except Exception as e:
        logger.error(f"Error triggering data collection: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger data collection")

@router.get("/summary")
async def get_environmental_summary(
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get comprehensive environmental monitoring summary"""
    try:
        # Collect current data
        current_data = await environmental_service.collect_all_environmental_data(db)
        
        # Get data quality report
        quality_report = await environmental_service.get_data_quality_report(db)
        
        # Compile summary
        summary = {
            'timestamp': datetime.utcnow(),
            'overview': {
                'total_stations': current_data['summary']['total_stations'],
                'active_stations': current_data['summary']['successful_collections'],
                'offline_stations': current_data['summary']['failed_collections'],
                'data_quality': quality_report.get('overall_quality', 'unknown')
            },
            'current_conditions': {
                'weather': current_data.get('weather_data', {}).get('current_conditions', {}),
                'ocean': current_data.get('ocean_data', {}),
                'satellite': current_data.get('satellite_data', {})
            },
            'alerts': {
                'active_count': current_data['summary'].get('alerts_triggered', 0),
                'risk_level': 'low'  # This would be calculated based on current conditions
            },
            'stations_status': []
        }
        
        # Add station status summary
        for station_data in current_data.get('stations_data', []):
            station_summary = {
                'station_id': station_data['station_id'],
                'station_name': station_data['station_name'],
                'status': station_data['status'],
                'last_update': station_data['timestamp'],
                'key_measurements': {
                    'tide_level': station_data['measurements'].get('tide_level'),
                    'wave_height': station_data['measurements'].get('wave_height'),
                    'wind_speed': station_data['measurements'].get('wind_speed'),
                    'temperature': station_data['measurements'].get('air_temperature')
                }
            }
            summary['stations_status'].append(station_summary)
        
        # Determine overall risk level
        high_risk_conditions = 0
        for station in summary['stations_status']:
            measurements = station['key_measurements']
            if measurements.get('tide_level', 0) > 1.5:
                high_risk_conditions += 1
            if measurements.get('wave_height', 0) > 2.0:
                high_risk_conditions += 1
            if measurements.get('wind_speed', 0) > 25:
                high_risk_conditions += 1
        
        if high_risk_conditions >= 3:
            summary['alerts']['risk_level'] = 'high'
        elif high_risk_conditions >= 1:
            summary['alerts']['risk_level'] = 'medium'
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting environmental summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get environmental summary")

@router.get("/stations/{station_id}/status")
async def get_station_status(
    station_id: str,
    current_user: dict = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed status for a specific monitoring station"""
    try:
        # Get current data for the station
        current_data = await environmental_service.collect_all_environmental_data(db)
        
        station_data = None
        for station in current_data.get('stations_data', []):
            if station['station_id'] == station_id:
                station_data = station
                break
        
        if not station_data:
            raise HTTPException(status_code=404, detail=f"Station {station_id} not found")
        
        # Get recent trend analysis
        trends = await environmental_service.analyze_environmental_trends(
            station_id=station_id,
            days=7,
            db=db
        )
        
        # Compile detailed status
        status = {
            'station_info': {
                'id': station_data['station_id'],
                'name': station_data['station_name'],
                'location': station_data['location'],
                'status': station_data['status'],
                'data_quality': station_data['data_quality']
            },
            'current_measurements': station_data['measurements'],
            'last_update': station_data['timestamp'],
            'trends': trends.get('trends', {}),
            'risk_assessment': trends.get('risk_assessment', {}),
            'statistics': trends.get('statistics', {})
        }
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting station status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get station status")