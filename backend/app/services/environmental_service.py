from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import asyncio
import aiohttp
import json
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.database import get_db
from app.models.monitoring import MonitoringStation
from app.models.environmental_data import EnvironmentalData

class EnvironmentalMonitoringService:
    """Service for collecting and processing environmental data from various sources"""
    
    def __init__(self):
        self.session_timeout = aiohttp.ClientTimeout(total=30)
        self.data_sources = {
            'noaa': 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter',
            'openweather': 'https://api.openweathermap.org/data/2.5',
            'nasa_earth': 'https://api.nasa.gov/planetary/earth',
            'sentinel_hub': 'https://services.sentinel-hub.com/api/v1'
        }
        self.cache = {}
        self.cache_duration = timedelta(minutes=15)
        
    async def collect_all_environmental_data(self, db: Session) -> Dict[str, Any]:
        """Collect environmental data from all available sources"""
        try:
            # Get all active monitoring stations
            stations = db.query(MonitoringStation).filter(
                MonitoringStation.is_active == True
            ).all()
            
            results = {
                'timestamp': datetime.utcnow(),
                'stations_data': [],
                'satellite_data': {},
                'weather_data': {},
                'ocean_data': {},
                'summary': {
                    'total_stations': len(stations),
                    'successful_collections': 0,
                    'failed_collections': 0,
                    'alerts_triggered': 0
                }
            }
            
            # Collect data for each station
            tasks = []
            for station in stations:
                task = self._collect_station_data(station, db)
                tasks.append(task)
            
            station_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(station_results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to collect data for station {stations[i].id}: {result}")
                    results['summary']['failed_collections'] += 1
                else:
                    results['stations_data'].append(result)
                    results['summary']['successful_collections'] += 1
            
            # Collect satellite and weather data
            satellite_task = self._collect_satellite_data()
            weather_task = self._collect_weather_data()
            ocean_task = self._collect_ocean_data()
            
            satellite_data, weather_data, ocean_data = await asyncio.gather(
                satellite_task, weather_task, ocean_task, return_exceptions=True
            )
            
            if not isinstance(satellite_data, Exception):
                results['satellite_data'] = satellite_data
            if not isinstance(weather_data, Exception):
                results['weather_data'] = weather_data
            if not isinstance(ocean_data, Exception):
                results['ocean_data'] = ocean_data
            
            return results
            
        except Exception as e:
            logger.error(f"Error in collect_all_environmental_data: {e}")
            raise
    
    async def _collect_station_data(self, station: MonitoringStation, db: Session) -> Dict[str, Any]:
        """Collect data for a specific monitoring station"""
        try:
            station_data = {
                'station_id': station.id,
                'station_name': station.name,
                'location': {
                    'latitude': float(station.latitude),
                    'longitude': float(station.longitude)
                },
                'timestamp': datetime.utcnow(),
                'measurements': {},
                'status': 'online',
                'data_quality': 'good'
            }
            
            # Simulate real-time data collection (in production, this would connect to actual sensors)
            measurements = await self._simulate_sensor_readings(station)
            station_data['measurements'] = measurements
            
            # Store data in database
            env_data = EnvironmentalData(
                station_id=station.id,
                timestamp=datetime.utcnow(),
                tide_level=measurements.get('tide_level', 0.0),
                wave_height=measurements.get('wave_height', 0.0),
                wave_period=measurements.get('wave_period', 0.0),
                wind_speed=measurements.get('wind_speed', 0.0),
                wind_direction=measurements.get('wind_direction', 0.0),
                air_temperature=measurements.get('air_temperature', 0.0),
                water_temperature=measurements.get('water_temperature', 0.0),
                atmospheric_pressure=measurements.get('atmospheric_pressure', 0.0),
                humidity=measurements.get('humidity', 0.0),
                visibility=measurements.get('visibility', 0.0),
                precipitation=measurements.get('precipitation', 0.0)
            )
            
            db.add(env_data)
            db.commit()
            
            return station_data
            
        except Exception as e:
            logger.error(f"Error collecting data for station {station.id}: {e}")
            raise
    
    async def _simulate_sensor_readings(self, station: MonitoringStation) -> Dict[str, float]:
        """Simulate sensor readings (replace with actual sensor integration)"""
        import random
        import math
        
        # Base values that vary by location
        base_tide = 1.0 + 0.5 * math.sin(datetime.utcnow().hour * math.pi / 12)
        base_wave = 0.5 + 0.3 * random.random()
        base_temp = 25.0 + 5.0 * math.sin((datetime.utcnow().month - 1) * math.pi / 6)
        
        # Add some realistic variation
        measurements = {
            'tide_level': round(base_tide + random.uniform(-0.2, 0.2), 2),
            'wave_height': round(base_wave + random.uniform(-0.1, 0.3), 2),
            'wave_period': round(6.0 + random.uniform(-2.0, 4.0), 1),
            'wind_speed': round(10.0 + random.uniform(-5.0, 15.0), 1),
            'wind_direction': round(random.uniform(0, 360), 0),
            'air_temperature': round(base_temp + random.uniform(-3.0, 3.0), 1),
            'water_temperature': round(base_temp - 2.0 + random.uniform(-2.0, 2.0), 1),
            'atmospheric_pressure': round(1013.25 + random.uniform(-20.0, 20.0), 1),
            'humidity': round(60.0 + random.uniform(-20.0, 30.0), 0),
            'visibility': round(10.0 + random.uniform(-3.0, 5.0), 1),
            'precipitation': round(max(0, random.uniform(-0.5, 2.0)), 1)
        }
        
        return measurements
    
    async def _collect_satellite_data(self) -> Dict[str, Any]:
        """Collect satellite imagery and data"""
        try:
            # Simulate satellite data collection
            satellite_data = {
                'timestamp': datetime.utcnow(),
                'cloud_cover': {
                    'percentage': random.uniform(10, 80),
                    'type': random.choice(['clear', 'partly_cloudy', 'overcast', 'stormy'])
                },
                'sea_surface_temperature': {
                    'average': round(26.5 + random.uniform(-2.0, 2.0), 1),
                    'anomaly': round(random.uniform(-1.5, 1.5), 1)
                },
                'chlorophyll_concentration': {
                    'level': round(random.uniform(0.1, 2.0), 2),
                    'status': 'normal'
                },
                'wave_patterns': {
                    'significant_wave_height': round(random.uniform(0.5, 2.5), 1),
                    'dominant_wave_direction': round(random.uniform(0, 360), 0)
                },
                'storm_systems': {
                    'detected': random.choice([True, False]),
                    'intensity': random.choice(['low', 'moderate', 'high']) if random.choice([True, False]) else None,
                    'distance_km': round(random.uniform(50, 500), 0) if random.choice([True, False]) else None
                }
            }
            
            return satellite_data
            
        except Exception as e:
            logger.error(f"Error collecting satellite data: {e}")
            return {}
    
    async def _collect_weather_data(self) -> Dict[str, Any]:
        """Collect weather forecast and current conditions"""
        try:
            # Simulate weather data collection
            weather_data = {
                'timestamp': datetime.utcnow(),
                'current_conditions': {
                    'temperature': round(28.0 + random.uniform(-5.0, 5.0), 1),
                    'feels_like': round(30.0 + random.uniform(-5.0, 5.0), 1),
                    'humidity': round(random.uniform(40, 90), 0),
                    'pressure': round(1013.25 + random.uniform(-15.0, 15.0), 1),
                    'wind_speed': round(random.uniform(5.0, 25.0), 1),
                    'wind_direction': round(random.uniform(0, 360), 0),
                    'visibility': round(random.uniform(5.0, 15.0), 1),
                    'uv_index': round(random.uniform(1, 11), 0),
                    'condition': random.choice(['clear', 'partly_cloudy', 'cloudy', 'rainy', 'stormy'])
                },
                'forecast_24h': {
                    'temperature_max': round(30.0 + random.uniform(-3.0, 3.0), 1),
                    'temperature_min': round(24.0 + random.uniform(-3.0, 3.0), 1),
                    'precipitation_probability': round(random.uniform(0, 100), 0),
                    'wind_speed_max': round(random.uniform(10.0, 30.0), 1),
                    'condition': random.choice(['clear', 'partly_cloudy', 'cloudy', 'rainy', 'stormy'])
                },
                'marine_forecast': {
                    'wave_height': round(random.uniform(0.5, 3.0), 1),
                    'wave_period': round(random.uniform(4.0, 12.0), 1),
                    'swell_direction': round(random.uniform(0, 360), 0),
                    'tide_times': {
                        'high_tide': (datetime.utcnow() + timedelta(hours=random.uniform(1, 12))).strftime('%H:%M'),
                        'low_tide': (datetime.utcnow() + timedelta(hours=random.uniform(1, 12))).strftime('%H:%M')
                    }
                }
            }
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Error collecting weather data: {e}")
            return {}
    
    async def _collect_ocean_data(self) -> Dict[str, Any]:
        """Collect oceanographic data"""
        try:
            # Simulate ocean data collection
            ocean_data = {
                'timestamp': datetime.utcnow(),
                'sea_level': {
                    'current': round(random.uniform(-0.5, 0.5), 2),
                    'trend': random.choice(['rising', 'falling', 'stable']),
                    'anomaly': round(random.uniform(-0.2, 0.2), 2)
                },
                'currents': {
                    'surface_speed': round(random.uniform(0.1, 1.5), 2),
                    'surface_direction': round(random.uniform(0, 360), 0),
                    'subsurface_speed': round(random.uniform(0.05, 0.8), 2),
                    'subsurface_direction': round(random.uniform(0, 360), 0)
                },
                'water_quality': {
                    'salinity': round(random.uniform(34.0, 36.0), 1),
                    'ph': round(random.uniform(7.8, 8.2), 2),
                    'dissolved_oxygen': round(random.uniform(6.0, 9.0), 1),
                    'turbidity': round(random.uniform(1.0, 10.0), 1)
                },
                'biological_indicators': {
                    'plankton_density': round(random.uniform(100, 1000), 0),
                    'fish_activity': random.choice(['low', 'moderate', 'high']),
                    'coral_health': random.choice(['good', 'fair', 'poor']) if random.choice([True, False]) else None
                }
            }
            
            return ocean_data
            
        except Exception as e:
            logger.error(f"Error collecting ocean data: {e}")
            return {}
    
    async def get_historical_data(self, 
                                station_id: str, 
                                start_date: datetime, 
                                end_date: datetime,
                                db: Session) -> List[Dict[str, Any]]:
        """Get historical environmental data for a station"""
        try:
            query = text("""
                SELECT * FROM environmental_data 
                WHERE station_id = :station_id 
                AND timestamp BETWEEN :start_date AND :end_date 
                ORDER BY timestamp DESC
            """)
            
            result = db.execute(query, {
                'station_id': station_id,
                'start_date': start_date,
                'end_date': end_date
            })
            
            data = []
            for row in result:
                data.append({
                    'timestamp': row.timestamp,
                    'tide_level': row.tide_level,
                    'wave_height': row.wave_height,
                    'wave_period': row.wave_period,
                    'wind_speed': row.wind_speed,
                    'wind_direction': row.wind_direction,
                    'air_temperature': row.air_temperature,
                    'water_temperature': row.water_temperature,
                    'atmospheric_pressure': row.atmospheric_pressure,
                    'humidity': row.humidity,
                    'visibility': row.visibility,
                    'precipitation': row.precipitation
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return []
    
    async def analyze_environmental_trends(self, 
                                         station_id: str, 
                                         days: int,
                                         db: Session) -> Dict[str, Any]:
        """Analyze environmental trends for a station"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            historical_data = await self.get_historical_data(station_id, start_date, end_date, db)
            
            if not historical_data:
                return {'error': 'No data available for analysis'}
            
            # Calculate trends and statistics
            analysis = {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'days': days,
                    'data_points': len(historical_data)
                },
                'trends': {},
                'statistics': {},
                'anomalies': [],
                'risk_assessment': {
                    'flood_risk': 'low',
                    'storm_risk': 'low',
                    'overall_risk': 'low'
                }
            }
            
            # Analyze each parameter
            parameters = ['tide_level', 'wave_height', 'wind_speed', 'air_temperature']
            
            for param in parameters:
                values = [float(d[param]) for d in historical_data if d[param] is not None]
                
                if values:
                    analysis['statistics'][param] = {
                        'mean': round(sum(values) / len(values), 2),
                        'min': round(min(values), 2),
                        'max': round(max(values), 2),
                        'std_dev': round(self._calculate_std_dev(values), 2)
                    }
                    
                    # Simple trend analysis (rising/falling/stable)
                    if len(values) >= 10:
                        recent_avg = sum(values[:len(values)//3]) / (len(values)//3)
                        older_avg = sum(values[-len(values)//3:]) / (len(values)//3)
                        
                        if recent_avg > older_avg * 1.1:
                            analysis['trends'][param] = 'rising'
                        elif recent_avg < older_avg * 0.9:
                            analysis['trends'][param] = 'falling'
                        else:
                            analysis['trends'][param] = 'stable'
            
            # Risk assessment based on current conditions
            if historical_data:
                latest = historical_data[0]
                
                if latest['tide_level'] and float(latest['tide_level']) > 1.5:
                    analysis['risk_assessment']['flood_risk'] = 'high'
                elif latest['tide_level'] and float(latest['tide_level']) > 1.2:
                    analysis['risk_assessment']['flood_risk'] = 'medium'
                
                if latest['wind_speed'] and float(latest['wind_speed']) > 25:
                    analysis['risk_assessment']['storm_risk'] = 'high'
                elif latest['wind_speed'] and float(latest['wind_speed']) > 15:
                    analysis['risk_assessment']['storm_risk'] = 'medium'
                
                # Overall risk is the highest individual risk
                risks = [analysis['risk_assessment']['flood_risk'], analysis['risk_assessment']['storm_risk']]
                if 'high' in risks:
                    analysis['risk_assessment']['overall_risk'] = 'high'
                elif 'medium' in risks:
                    analysis['risk_assessment']['overall_risk'] = 'medium'
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing environmental trends: {e}")
            return {'error': str(e)}
    
    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    async def get_data_quality_report(self, db: Session) -> Dict[str, Any]:
        """Generate a data quality report for all stations"""
        try:
            stations = db.query(MonitoringStation).filter(
                MonitoringStation.is_active == True
            ).all()
            
            report = {
                'timestamp': datetime.utcnow(),
                'total_stations': len(stations),
                'stations': [],
                'overall_quality': 'good',
                'issues': []
            }
            
            for station in stations:
                # Check recent data availability
                recent_data = db.query(EnvironmentalData).filter(
                    EnvironmentalData.station_id == station.id,
                    EnvironmentalData.timestamp >= datetime.utcnow() - timedelta(hours=1)
                ).count()
                
                station_quality = {
                    'station_id': station.id,
                    'station_name': station.name,
                    'data_availability': 'good' if recent_data > 0 else 'poor',
                    'last_update': None,
                    'missing_parameters': [],
                    'quality_score': 100
                }
                
                # Get latest data
                latest_data = db.query(EnvironmentalData).filter(
                    EnvironmentalData.station_id == station.id
                ).order_by(EnvironmentalData.timestamp.desc()).first()
                
                if latest_data:
                    station_quality['last_update'] = latest_data.timestamp
                    
                    # Check for missing parameters
                    if latest_data.tide_level is None:
                        station_quality['missing_parameters'].append('tide_level')
                    if latest_data.wave_height is None:
                        station_quality['missing_parameters'].append('wave_height')
                    if latest_data.wind_speed is None:
                        station_quality['missing_parameters'].append('wind_speed')
                    
                    # Calculate quality score
                    missing_count = len(station_quality['missing_parameters'])
                    station_quality['quality_score'] = max(0, 100 - (missing_count * 20))
                    
                    if station_quality['quality_score'] < 80:
                        station_quality['data_availability'] = 'fair'
                    if station_quality['quality_score'] < 60:
                        station_quality['data_availability'] = 'poor'
                else:
                    station_quality['data_availability'] = 'no_data'
                    station_quality['quality_score'] = 0
                
                report['stations'].append(station_quality)
            
            # Calculate overall quality
            if report['stations']:
                avg_score = sum(s['quality_score'] for s in report['stations']) / len(report['stations'])
                if avg_score >= 80:
                    report['overall_quality'] = 'good'
                elif avg_score >= 60:
                    report['overall_quality'] = 'fair'
                else:
                    report['overall_quality'] = 'poor'
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating data quality report: {e}")
            return {'error': str(e)}

# Global instance
environmental_service = EnvironmentalMonitoringService()