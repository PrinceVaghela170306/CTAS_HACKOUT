from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Coastal Threat Alert System"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "https://your-frontend-domain.com"
    ]
    
    # Database settings (Supabase)
    SUPABASE_URL: str = "https://your-project.supabase.co"
    SUPABASE_KEY: str = "your-supabase-anon-key"
    SUPABASE_SERVICE_KEY: str = "your-supabase-service-key"
    
    # Database URL for SQLAlchemy
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/ctas_db"
    
    # External API Keys
    OPENWEATHER_API_KEY: str = "your-openweather-api-key"
    NOAA_API_KEY: str = "your-noaa-api-key"
    NASA_API_KEY: str = "your-nasa-api-key"
    SENTINEL_HUB_CLIENT_ID: str = "your-sentinel-hub-client-id"
    SENTINEL_HUB_CLIENT_SECRET: str = "your-sentinel-hub-client-secret"
    
    # Notification services
    TWILIO_ACCOUNT_SID: str = "your-twilio-account-sid"
    TWILIO_AUTH_TOKEN: str = "your-twilio-auth-token"
    TWILIO_PHONE_NUMBER: str = "your-twilio-phone-number"
    
    # Firebase settings
    FIREBASE_CREDENTIALS_PATH: str = "path/to/firebase-credentials.json"
    
    # ML Model settings
    MODEL_PATH: str = "models/"
    RETRAIN_INTERVAL_HOURS: int = 24
    
    # Alert thresholds
    TIDE_ALERT_THRESHOLD: float = 2.5  # meters above normal
    WAVE_HEIGHT_THRESHOLD: float = 4.0  # meters
    STORM_SURGE_THRESHOLD: float = 1.5  # meters
    
    # Data collection intervals
    DATA_COLLECTION_INTERVAL_MINUTES: int = 15
    FORECAST_UPDATE_INTERVAL_HOURS: int = 6
    
    # Redis settings for caching and task queue
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/ctas.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Create logs directory if it doesn't exist
log_dir = Path(settings.LOG_FILE).parent
log_dir.mkdir(exist_ok=True)