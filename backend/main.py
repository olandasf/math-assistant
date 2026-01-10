"""
Matematikos Mokytojo Asistentas - Backend API
=============================================
FastAPI aplikacija mokinių kontrolinių tikrinimui.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from config import settings
from database import init_db

# Loguru konfigūracija
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.DEBUG else "INFO"
)
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="DEBUG"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Aplikacijos lifecycle - startup ir shutdown."""
    # Startup
    logger.info("🚀 Paleidžiamas Matematikos Mokytojo Asistentas...")
    await init_db()
    logger.info("✅ Duomenų bazė paruošta")
    
    yield
    
    # Shutdown
    logger.info("👋 Išjungiamas serveris...")


# FastAPI aplikacija
app = FastAPI(
    title="Matematikos Mokytojo Asistentas",
    description="API mokinių kontrolinių tikrinimui ir vertinimui",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Health check ===
@app.get("/", tags=["Health"])
async def root():
    """Pagrindinis endpoint - health check."""
    return {
        "status": "ok",
        "message": "Matematikos Mokytojo Asistentas veikia!",
        "version": "0.1.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detalus health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "api_version": "0.1.0"
    }


# === Routers ===
# TODO: Pridėti routers kai bus sukurti
# from routers import school_years, classes, students, tests, submissions
# app.include_router(school_years.router, prefix="/api/v1")
# app.include_router(classes.router, prefix="/api/v1")
# app.include_router(students.router, prefix="/api/v1")
# app.include_router(tests.router, prefix="/api/v1")
# app.include_router(submissions.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
