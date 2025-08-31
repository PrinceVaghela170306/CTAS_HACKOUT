from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from supabase import create_client, Client
from .config import settings
from loguru import logger
import asyncio

# SQLAlchemy setup
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
metadata = MetaData()

# Supabase client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Supabase dependency
def get_supabase() -> Client:
    return supabase

async def init_db():
    """Initialize database tables"""
    try:
        # Import all models to ensure they are registered
        from app.models import user, monitoring_station, alert, forecast
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Initialize default monitoring stations
        await create_default_stations()
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

async def create_default_stations():
    """Create default monitoring stations for major coastal cities"""
    try:
        db = SessionLocal()
        from app.models.monitoring_station import MonitoringStation
        
        # Check if stations already exist
        existing_stations = db.query(MonitoringStation).count()
        if existing_stations > 0:
            logger.info("Monitoring stations already exist")
            db.close()
            return
        
        default_stations = [
            {
                "name": "Chennai Marina Beach",
                "latitude": 13.0475,
                "longitude": 80.2824,
                "location": "Chennai, Tamil Nadu",
                "station_type": "coastal",
                "is_active": True
            },
            {
                "name": "Mumbai Marine Drive",
                "latitude": 18.9220,
                "longitude": 72.8347,
                "location": "Mumbai, Maharashtra",
                "station_type": "coastal",
                "is_active": True
            },
            {
                "name": "Kochi Port",
                "latitude": 9.9312,
                "longitude": 76.2673,
                "location": "Kochi, Kerala",
                "station_type": "port",
                "is_active": True
            },
            {
                "name": "Visakhapatnam Port",
                "latitude": 17.6868,
                "longitude": 83.2185,
                "location": "Visakhapatnam, Andhra Pradesh",
                "station_type": "port",
                "is_active": True
            },
            {
                "name": "Paradip Port",
                "latitude": 20.2648,
                "longitude": 86.6947,
                "location": "Paradip, Odisha",
                "station_type": "port",
                "is_active": True
            }
        ]
        
        for station_data in default_stations:
            station = MonitoringStation(**station_data)
            db.add(station)
        
        db.commit()
        logger.info(f"Created {len(default_stations)} default monitoring stations")
        db.close()
        
    except Exception as e:
        logger.error(f"Error creating default stations: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()

# Database health check
async def check_db_health() -> bool:
    """Check if database connection is healthy"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False