#!/usr/bin/env python3
"""
Startup script for Coastal Guard API

This script initializes the database and starts the FastAPI server.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_db, check_db_connection
from app.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def setup_database():
    """Initialize database tables and check connection"""
    logger.info("Setting up database...")
    
    # Check database connection
    if not check_db_connection():
        logger.error("Failed to connect to database. Please check your configuration.")
        sys.exit(1)
    
    # Initialize database tables
    try:
        init_db()
        logger.info("Database setup completed successfully")
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        sys.exit(1)

def main():
    """Main startup function"""
    logger.info("Starting Coastal Guard API...")
    
    # Load settings
    settings = get_settings()
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Setup database
    setup_database()
    
    # Start the server
    import uvicorn
    
    logger.info("Starting FastAPI server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server startup failed: {str(e)}")
        sys.exit(1)