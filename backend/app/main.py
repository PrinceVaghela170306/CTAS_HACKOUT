from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

# Import routers
from app.routers import auth, dashboard, alerts, forecasting, notifications, environmental
from app.routers import monitoring as monitoring_router

# Import models to ensure they are registered with SQLAlchemy
from app.models import monitoring, environmental_data, alert

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up Coastal Guard API...")
    
    # Initialize services here if needed
    # await initialize_ml_models()
    # await setup_database_connections()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Coastal Guard API...")
    # Cleanup resources here if needed

# Create FastAPI application
app = FastAPI(
    title="Coastal Guard API",
    description="AI-powered coastal monitoring and flood prediction system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js frontend
        "http://localhost:3001",  # Next.js frontend (alternate port)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "https://your-frontend-domain.com",  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.your-domain.com"]
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Coastal Guard API",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Coastal Guard API",
        "description": "AI-powered coastal monitoring and flood prediction system",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(forecasting.router, prefix="/api/v1/forecasting", tags=["Forecasting"])
app.include_router(monitoring_router.router, prefix="/api/v1/monitoring", tags=["Monitoring"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(environmental.router, prefix="/api/v1/environmental", tags=["Environmental"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )