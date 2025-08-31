from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
from loguru import logger

# Import routers
from app.routers import auth, dashboard, alerts, forecasting, monitoring
from app.core.config import settings
from app.core.database import init_db
from app.services.scheduler import start_scheduler

security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Coastal Threat Alert System API")
    await init_db()
    start_scheduler()
    yield
    # Shutdown
    logger.info("Shutting down CTAS API")

app = FastAPI(
    title="Coastal Threat Alert System",
    description="AI-powered coastal monitoring and threat prediction system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(forecasting.router, prefix="/api/forecasting", tags=["forecasting"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])

@app.get("/")
async def root():
    return {
        "message": "Coastal Threat Alert System API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )