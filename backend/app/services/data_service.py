import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
import random
import json
from app.config import settings

class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API"""
    
    def __init__(self):
        self.api_key = settings.openweather_api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_current_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get current weather data for a location"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "temperature_c": data["main"]["temp"],
                "humidity_percent": data["main"]["humidity"],
                "pressure_hpa": data["main"]["pressure"],
                "wind_speed_kmh": data["wind"]["speed"] * 3.6,  # Convert m/s to km/h
                "wind_direction_deg": data["wind"].get("deg", 0),
                "visibility_km": data.get("visibility", 10000) / 1000,
                "weather_condition": data["weather"][0]["description"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            # Return simulated data as fallback
            return self._simulate_weather_data()
    
    async def get_weather_forecast(self, latitude: float, longitude: float, days: int = 5) -> List[Dict[str, Any]]:
        """Get weather forecast for a location"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            forecast = []
            
            for item in data["list"][:days * 8]:  # 8 forecasts per day (3-hour intervals)
                forecast.append({
                    "timestamp": item["dt_txt"],
                    "temperature_c": item["main"]["temp"],
                    "humidity_percent": item["main"]["humidity"],
                    "pressure_hpa": item["main"]["pressure"],
                    "wind_speed_kmh": item["wind"]["speed"] * 3.6,
                    "wind_direction_deg": item["wind"].get("deg", 0),
                    "precipitation_mm": item.get("rain", {}).get("3h", 0),
                    "weather_condition": item["weather"][0]["description"]
                })
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error fetching weather forecast: {e}")
            return self._simulate_forecast_data(days)
    
    def _simulate_weather_data(self) -> Dict[str, Any]:
        """Simulate weather data when API is unavailable"""
        return {
            "temperature_c": random.uniform(20, 35),
            "humidity_percent": random.uniform(60, 90),
            "pressure_hpa": random.uniform(1000, 1020),
            "wind_speed_kmh": random.uniform(5, 25),
            "wind_direction_deg": random.uniform(0, 360),
            "visibility_km": random.uniform(5, 15),
            "weather_condition": random.choice(["clear sky", "few clouds", "scattered clouds", "overcast"]),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _simulate_forecast_data(self, days: int) -> List[Dict[str, Any]]:
        """Simulate forecast data when API is unavailable"""
        forecast = []
        base_time = datetime.utcnow()
        
        for i in range(days * 8):
            timestamp = base_time + timedelta(hours=i * 3)
            forecast.append({
                "timestamp": timestamp.isoformat(),
                "temperature_c": random.uniform(18, 32),
                "humidity_percent": random.uniform(55, 85),
                "pressure_hpa": random.uniform(995, 1025),
                "wind_speed_kmh": random.uniform(3, 30),
                "wind_direction_deg": random.uniform(0, 360),
                "precipitation_mm": random.uniform(0, 5) if random.random() < 0.3 else 0,
                "weather_condition": random.choice(["clear sky", "few clouds", "light rain", "moderate rain"])
            })
        
        return forecast

class NOAAService:
    """Service for fetching tide and oceanographic data from NOAA"""
    
    def __init__(self):
        self.base_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_tide_data(self, station_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get tide data from NOAA station"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(hours=hours)
            
            params = {
                "product": "water_level",
                "application": "CTAS",
                "begin_date": start_date.strftime("%Y%m%d %H:%M"),
                "end_date": end_date.strftime("%Y%m%d %H:%M"),
                "datum": "MLLW",
                "station": station_id,
                "time_zone": "gmt",
                "units": "metric",
                "format": "json"
            }
            
            response = await self.client.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "data" in data:
                return [
                    {
                        "timestamp": item["t"],
                        "water_level_m": float(item["v"]),
                        "quality": item.get("q", "good")
                    }
                    for item in data["data"]
                ]
            else:
                return self._simulate_tide_data(hours)
                
        except Exception as e:
            logger.error(f"Error fetching NOAA tide data: {e}")
            return self._simulate_tide_data(hours)
    
    async def get_tide_predictions(self, station_id: str, hours: int = 48) -> List[Dict[str, Any]]:
        """Get tide predictions from NOAA"""
        try:
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(hours=hours)
            
            params = {
                "product": "predictions",
                "application": "CTAS",
                "begin_date": start_date.strftime("%Y%m%d %H:%M"),
                "end_date": end_date.strftime("%Y%m%d %H:%M"),
                "datum": "MLLW",
                "station": station_id,
                "time_zone": "gmt",
                "units": "metric",
                "interval": "hilo",
                "format": "json"
            }
            
            response = await self.client.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "predictions" in data:
                return [
                    {
                        "timestamp": item["t"],
                        "water_level_m": float(item["v"]),
                        "tide_type": item["type"]
                    }
                    for item in data["predictions"]
                ]
            else:
                return self._simulate_tide_predictions(hours)
                
        except Exception as e:
            logger.error(f"Error fetching NOAA tide predictions: {e}")
            return self._simulate_tide_predictions(hours)
    
    def _simulate_tide_data(self, hours: int) -> List[Dict[str, Any]]:
        """Simulate tide data when API is unavailable"""
        data = []
        base_time = datetime.utcnow() - timedelta(hours=hours)
        
        for i in range(hours * 6):  # 6 readings per hour (10-minute intervals)
            timestamp = base_time + timedelta(minutes=i * 10)
            # Simulate tidal pattern with some noise
            tide_level = 1.5 * math.sin(2 * math.pi * i / (12.42 * 6)) + random.uniform(-0.2, 0.2)
            
            data.append({
                "timestamp": timestamp.isoformat(),
                "water_level_m": round(tide_level, 2),
                "quality": "simulated"
            })
        
        return data
    
    def _simulate_tide_predictions(self, hours: int) -> List[Dict[str, Any]]:
        """Simulate tide predictions when API is unavailable"""
        predictions = []
        base_time = datetime.utcnow()
        
        # Generate high and low tide predictions
        for i in range(hours // 6):  # Approximately 4 tides per day
            for tide_type in ["H", "L"]:
                timestamp = base_time + timedelta(hours=i * 6 + (3 if tide_type == "L" else 0))
                level = 2.1 if tide_type == "H" else 0.3
                level += random.uniform(-0.3, 0.3)
                
                predictions.append({
                    "timestamp": timestamp.isoformat(),
                    "water_level_m": round(level, 2),
                    "tide_type": tide_type
                })
        
        return sorted(predictions, key=lambda x: x["timestamp"])

class SentinelHubService:
    """Service for fetching satellite imagery from Sentinel Hub"""
    
    def __init__(self):
        self.client_id = settings.sentinel_hub_client_id
        self.client_secret = settings.sentinel_hub_client_secret
        self.base_url = "https://services.sentinel-hub.com"
        self.client = httpx.AsyncClient(timeout=60.0)
        self.access_token = None
    
    async def authenticate(self) -> str:
        """Authenticate with Sentinel Hub and get access token"""
        try:
            url = f"{self.base_url}/oauth/token"
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            
            response = await self.client.post(url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            return self.access_token
            
        except Exception as e:
            logger.error(f"Error authenticating with Sentinel Hub: {e}")
            return None
    
    async def get_satellite_imagery_analysis(self, latitude: float, longitude: float, 
                                           analysis_type: str = "erosion") -> Dict[str, Any]:
        """Get satellite imagery analysis results"""
        try:
            if not self.access_token:
                await self.authenticate()
            
            # For demo purposes, return simulated analysis
            return self._simulate_satellite_analysis(latitude, longitude, analysis_type)
            
        except Exception as e:
            logger.error(f"Error fetching satellite imagery analysis: {e}")
            return self._simulate_satellite_analysis(latitude, longitude, analysis_type)
    
    def _simulate_satellite_analysis(self, latitude: float, longitude: float, 
                                   analysis_type: str) -> Dict[str, Any]:
        """Simulate satellite analysis results"""
        base_analysis = {
            "location": {"latitude": latitude, "longitude": longitude},
            "analysis_date": datetime.utcnow().isoformat(),
            "satellite_source": "Sentinel-2",
            "cloud_cover_percent": random.uniform(0, 30),
            "image_quality": random.choice(["excellent", "good", "fair"])
        }
        
        if analysis_type == "erosion":
            base_analysis.update({
                "shoreline_change_m": random.uniform(-2.5, 0.5),
                "erosion_rate_m_per_year": random.uniform(0.1, 3.0),
                "vegetation_loss_percent": random.uniform(0, 20)
            })
        elif analysis_type == "water_quality":
            base_analysis.update({
                "chlorophyll_concentration": random.uniform(0.5, 15.0),
                "turbidity_estimate": random.uniform(1.0, 8.0),
                "algal_bloom_detected": random.choice([True, False])
            })
        elif analysis_type == "vegetation":
            base_analysis.update({
                "ndvi_average": random.uniform(0.3, 0.8),
                "vegetation_coverage_percent": random.uniform(40, 85),
                "mangrove_area_km2": random.uniform(0, 50)
            })
        
        return base_analysis

class DataCollectionService:
    """Main service for coordinating data collection from all sources"""
    
    def __init__(self):
        self.weather_service = WeatherService()
        self.noaa_service = NOAAService()
        self.sentinel_service = SentinelHubService()
    
    async def collect_all_data(self, latitude: float, longitude: float, 
                             station_id: Optional[str] = None) -> Dict[str, Any]:
        """Collect data from all available sources"""
        tasks = []
        
        # Weather data
        tasks.append(self.weather_service.get_current_weather(latitude, longitude))
        
        # Tide data (if station ID provided)
        if station_id:
            tasks.append(self.noaa_service.get_tide_data(station_id))
            tasks.append(self.noaa_service.get_tide_predictions(station_id))
        
        # Satellite analysis
        tasks.append(self.sentinel_service.get_satellite_imagery_analysis(latitude, longitude))
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            data_collection = {
                "collection_time": datetime.utcnow().isoformat(),
                "location": {"latitude": latitude, "longitude": longitude},
                "weather_data": results[0] if not isinstance(results[0], Exception) else None,
                "satellite_analysis": results[-1] if not isinstance(results[-1], Exception) else None
            }
            
            if station_id and len(results) >= 4:
                data_collection.update({
                    "tide_data": results[1] if not isinstance(results[1], Exception) else None,
                    "tide_predictions": results[2] if not isinstance(results[2], Exception) else None
                })
            
            return data_collection
            
        except Exception as e:
            logger.error(f"Error in data collection: {e}")
            return {
                "collection_time": datetime.utcnow().isoformat(),
                "location": {"latitude": latitude, "longitude": longitude},
                "error": str(e)
            }
    
    async def get_monitoring_stations(self) -> List[Dict[str, Any]]:
        """Get list of available monitoring stations"""
        # Simulate monitoring stations data
        stations = [
            {
                "id": "NOAA-8518750",
                "name": "The Battery, NY",
                "latitude": 40.7002,
                "longitude": -74.0142,
                "station_type": "tide",
                "operator": "NOAA",
                "is_active": True,
                "measures_tide": True,
                "measures_weather": True
            },
            {
                "id": "NOAA-8516945",
                "name": "Kings Point, NY",
                "latitude": 40.8133,
                "longitude": -73.7644,
                "station_type": "tide",
                "operator": "NOAA",
                "is_active": True,
                "measures_tide": True,
                "measures_weather": False
            },
            {
                "id": "NOAA-8510560",
                "name": "Montauk, NY",
                "latitude": 41.0483,
                "longitude": -71.9600,
                "station_type": "tide",
                "operator": "NOAA",
                "is_active": True,
                "measures_tide": True,
                "measures_waves": True
            }
        ]
        
        return stations

# Global service instances
data_service = DataCollectionService()
weather_service = WeatherService()
noaa_service = NOAAService()
sentinel_service = SentinelHubService()