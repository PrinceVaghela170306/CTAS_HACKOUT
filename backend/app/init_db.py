#!/usr/bin/env python3
"""
Database initialization script for Coastal Guard API
This script creates all database tables and sets up initial data.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loguru import logger
from datetime import datetime, timezone
import uuid

# Import all models to ensure they are registered
from app.models.monitoring import Base, MonitoringStation, TideData, WeatherData, WaveData, WaterQualityData, SatelliteData
from app.models.environmental_data import EnvironmentalData
from app.models.alert import AlertNotification
from app.config import settings

# Create engine
engine = create_engine(
    settings.database_url or settings.supabase_db_url or "sqlite:///./coastal_guard.db",
    pool_pre_ping=True,
    pool_recycle=300,
    echo=True  # Enable SQL logging for debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    logger.info("Creating database tables...")
    
    try:
        # Create all tables using the shared Base
        Base.metadata.create_all(bind=engine)
        
        logger.success("Database tables created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False

def create_sample_monitoring_stations():
    """Create sample monitoring stations"""
    logger.info("Creating sample monitoring stations...")
    
    db = SessionLocal()
    try:
        # Check if stations already exist
        existing_count = db.query(MonitoringStation).count()
        if existing_count > 0:
            logger.info(f"Found {existing_count} existing monitoring stations, skipping creation")
            return True
        
        sample_stations = [
            {
                "id": "NOAA-8518750",
                "name": "The Battery, NY",
                "station_type": "tide",
                "latitude": 40.7002,
                "longitude": -74.0142,
                "elevation_m": 0.0,
                "water_depth_m": 10.5,
                "operator": "NOAA",
                "station_code": "8518750",
                "description": "Primary tide monitoring station at The Battery, New York",
                "is_active": True,
                "measures_tide": True,
                "measures_waves": False,
                "measures_weather": True,
                "measures_water_quality": False,
                "installation_date": datetime(2020, 1, 1, tzinfo=timezone.utc),
                "last_maintenance": datetime(2024, 6, 1, tzinfo=timezone.utc),
                "next_maintenance": datetime(2024, 12, 1, tzinfo=timezone.utc)
            },
            {
                "id": "NOAA-8516945",
                "name": "Kings Point, NY",
                "station_type": "tide",
                "latitude": 40.8133,
                "longitude": -73.7644,
                "elevation_m": 0.0,
                "water_depth_m": 8.2,
                "operator": "NOAA",
                "station_code": "8516945",
                "description": "Secondary tide monitoring station at Kings Point, New York",
                "is_active": True,
                "measures_tide": True,
                "measures_waves": False,
                "measures_weather": False,
                "measures_water_quality": True,
                "installation_date": datetime(2019, 3, 15, tzinfo=timezone.utc),
                "last_maintenance": datetime(2024, 5, 15, tzinfo=timezone.utc),
                "next_maintenance": datetime(2024, 11, 15, tzinfo=timezone.utc)
            },
            {
                "id": "NOAA-8510560",
                "name": "Montauk, NY",
                "station_type": "wave",
                "latitude": 41.0483,
                "longitude": -71.9600,
                "elevation_m": 0.0,
                "water_depth_m": 15.3,
                "operator": "NOAA",
                "station_code": "8510560",
                "description": "Wave and tide monitoring station at Montauk, New York",
                "is_active": True,
                "measures_tide": True,
                "measures_waves": True,
                "measures_weather": True,
                "measures_water_quality": False,
                "installation_date": datetime(2018, 8, 20, tzinfo=timezone.utc),
                "last_maintenance": datetime(2024, 4, 10, tzinfo=timezone.utc),
                "next_maintenance": datetime(2024, 10, 10, tzinfo=timezone.utc)
            },
            {
                "id": "LOCAL-NYC-001",
                "name": "Brooklyn Bridge Park",
                "station_type": "water_quality",
                "latitude": 40.7024,
                "longitude": -73.9969,
                "elevation_m": 0.0,
                "water_depth_m": 6.8,
                "operator": "NYC Parks",
                "station_code": "BBP001",
                "description": "Water quality monitoring station at Brooklyn Bridge Park",
                "is_active": True,
                "measures_tide": False,
                "measures_waves": False,
                "measures_weather": False,
                "measures_water_quality": True,
                "installation_date": datetime(2021, 5, 1, tzinfo=timezone.utc),
                "last_maintenance": datetime(2024, 7, 1, tzinfo=timezone.utc),
                "next_maintenance": datetime(2025, 1, 1, tzinfo=timezone.utc)
            }
        ]
        
        for station_data in sample_stations:
            station = MonitoringStation(**station_data)
            db.add(station)
        
        db.commit()
        logger.success(f"Created {len(sample_stations)} sample monitoring stations")
        return True
        
    except Exception as e:
        logger.error(f"Error creating sample stations: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def create_sample_environmental_data():
    """Create sample environmental data"""
    logger.info("Creating sample environmental data...")
    
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_count = db.query(EnvironmentalData).count()
        if existing_count > 0:
            logger.info(f"Found {existing_count} existing environmental data records, skipping creation")
            return True
        
        # Get existing stations
        stations = db.query(MonitoringStation).all()
        if not stations:
            logger.warning("No monitoring stations found, cannot create environmental data")
            return False
        
        # Create sample data for each station
        current_time = datetime.now(timezone.utc)
        
        for station in stations[:2]:  # Create data for first 2 stations
            sample_data = {
                "id": str(uuid.uuid4()),
                "station_id": station.id,
                "timestamp": current_time,
                
                # Tide and water level data
                "tide_level": 1.2,
                "water_level": 0.8,
                
                # Wave data
                "wave_height": 0.8,
                "wave_period": 6.2,
                "wave_direction": 180.0,
                
                # Wind data
                "wind_speed": 18.7,  # km/h
                "wind_direction": 225.0,
                "wind_gust": 28.1,  # km/h
                
                # Temperature data
                "air_temperature": 18.5,
                "water_temperature": 16.2,
                "feels_like_temperature": 17.8,
                
                # Atmospheric data
                "atmospheric_pressure": 1013.2,
                "humidity": 65.0,
                "visibility": 15.0,
                "uv_index": 3.2,
                
                # Precipitation data
                "precipitation": 0.0,
                "precipitation_probability": 10.0,
                
                # Ocean/Water quality data
                "ph_level": 8.1,
                "dissolved_oxygen": 7.8,
                "turbidity": 2.1,
                "salinity": 32.5,
                
                # Current data
                "current_speed": 0.3,
                "current_direction": 90.0,
                
                # Data quality and metadata
                "data_quality": "good",
                "sensor_status": "operational",
                "battery_level": 85.0,
                "signal_strength": -65.0,
                "data_source": "simulated",
                "processing_notes": "Sample data for testing",
                "is_validated": True
            }
            
            env_data = EnvironmentalData(**sample_data)
            db.add(env_data)
        
        db.commit()
        logger.success("Created sample environmental data")
        return True
        
    except Exception as e:
        logger.error(f"Error creating sample environmental data: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Main initialization function"""
    logger.info("Starting database initialization...")
    
    success = True
    
    # Create tables
    if not create_tables():
        success = False
    
    # Create sample data
    if success and not create_sample_monitoring_stations():
        success = False
    
    if success and not create_sample_environmental_data():
        success = False
    
    if success:
        logger.success("Database initialization completed successfully!")
    else:
        logger.error("Database initialization failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()