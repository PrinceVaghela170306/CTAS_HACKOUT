import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import field_validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Application settings
    app_name: str = "Coastal Guard API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    supabase_db_url: Optional[str] = None
    database_url: Optional[str] = None
    
    # Authentication settings
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # External API keys
    openweather_api_key: Optional[str] = None
    noaa_api_key: Optional[str] = None
    sentinel_hub_client_id: Optional[str] = None
    sentinel_hub_client_secret: Optional[str] = None
    
    # Notification services
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: Optional[str] = None
    
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    
    firebase_credentials_path: Optional[str] = None
    firebase_project_id: Optional[str] = None
    
    # ML/AI settings
    model_storage_path: str = "./models"
    enable_model_training: bool = True
    model_update_interval_hours: int = 24
    
    # Monitoring settings
    data_collection_interval_minutes: int = 15
    alert_check_interval_minutes: int = 5
    max_alert_history_days: int = 30
    
    # Security settings
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window_minutes: int = 15
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    @field_validator('debug', mode='before')
    @classmethod
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on')
        return v
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @field_validator('allowed_hosts', mode='before')
    @classmethod
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
        
        # Map environment variables to settings
        fields = {
            'supabase_url': {'env': 'SUPABASE_URL'},
            'supabase_key': {'env': 'SUPABASE_ANON_KEY'},
            'supabase_db_url': {'env': 'SUPABASE_DB_URL'},
            'database_url': {'env': 'DATABASE_URL'},
            'jwt_secret_key': {'env': 'JWT_SECRET_KEY'},
            'openweather_api_key': {'env': 'OPENWEATHER_API_KEY'},
            'noaa_api_key': {'env': 'NOAA_API_KEY'},
            'sentinel_hub_client_id': {'env': 'SENTINEL_HUB_CLIENT_ID'},
            'sentinel_hub_client_secret': {'env': 'SENTINEL_HUB_CLIENT_SECRET'},
            'smtp_username': {'env': 'SMTP_USERNAME'},
            'smtp_password': {'env': 'SMTP_PASSWORD'},
            'twilio_account_sid': {'env': 'TWILIO_ACCOUNT_SID'},
            'twilio_auth_token': {'env': 'TWILIO_AUTH_TOKEN'},
            'twilio_phone_number': {'env': 'TWILIO_PHONE_NUMBER'},
            'firebase_credentials_path': {'env': 'FIREBASE_CREDENTIALS_PATH'},
            'firebase_project_id': {'env': 'FIREBASE_PROJECT_ID'},
            'debug': {'env': 'DEBUG'},
            'log_level': {'env': 'LOG_LEVEL'},
            'log_file': {'env': 'LOG_FILE'},
            'cors_origins': {'env': 'CORS_ORIGINS'},
            'allowed_hosts': {'env': 'ALLOWED_HOSTS'}
        }

# Create global settings instance
settings = Settings()

# Environment-specific configurations
class DevelopmentSettings(Settings):
    debug: bool = True
    log_level: str = "DEBUG"

class ProductionSettings(Settings):
    debug: bool = False
    log_level: str = "INFO"

class TestingSettings(Settings):
    debug: bool = True
    database_url: str = "sqlite:///./test.db"
    log_level: str = "DEBUG"

def get_settings() -> Settings:
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()