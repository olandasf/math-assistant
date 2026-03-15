"""
Matematikos Mokytojo Asistentas - Backend API
=============================================
FastAPI aplikacija mokinių kontrolinių tikrinimui.
"""

import sys
from contextlib import asynccontextmanager

from config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from database import async_session_maker, init_db

# Loguru konfigūracija
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.DEBUG else "INFO",
)
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="DEBUG",
)


async def load_api_keys_from_db():
    """Užkrauti API raktus iš duomenų bazės į atmintį."""
    from ai.gemini_client import configure_gemini
    from math_checker.wolfram_client import configure_wolfram
    from models.setting import Setting
    from sqlalchemy import select

    async with async_session_maker() as db:
        try: # Added try block
            # Užkrauti Gemini API raktą
            result = await db.execute(
                select(Setting).where(Setting.key == "gemini_api_key")
            )
            gemini_setting = result.scalar_one_or_none()

            # The original request had raw SQL cursor operations, which are not compatible with async_session_maker.
            # Reinterpreting the request to use SQLAlchemy ORM as per existing code pattern.
            # The request also introduced a decrypt_api_key function.

            if gemini_setting and gemini_setting.value:
                api_key = gemini_setting.value

                # Gauti modelį
                result = await db.execute(
                    select(Setting).where(Setting.key == "gemini_model")
                )
                model_setting = result.scalar_one_or_none()
                # Updated default model string as per request
                model = model_setting.value if model_setting else "google/gemini-3.1-pro-preview"
                
                if api_key:
                    configure_gemini(api_key, model)
                    logger.info(f"✅ Gemini sukonfigūruotas su modeliu: {model}")
            else:
                logger.info("ℹ️ Gemini API raktas nerastas. Įveskite jį per Nustatymus.")
        except Exception as e: # The except block from the request
            logger.warning(f"⚠️ Nepavyko užkrauti Gemini konfigūracijos iš DB: {e}")

        # Užkrauti WolframAlpha API raktą
        result = await db.execute(
            select(Setting).where(Setting.key == "wolfram_app_id")
        )
        wolfram_setting = result.scalar_one_or_none()

        if wolfram_setting and wolfram_setting.value:
            configure_wolfram(wolfram_setting.value)
            logger.info("✅ WolframAlpha API raktas užkrautas iš DB")
        else:
            logger.warning("⚠️ WolframAlpha API raktas nenustatytas DB")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Aplikacijos lifecycle - startup ir shutdown."""
    # Startup
    logger.info("🚀 Paleidžiamas Matematikos Mokytojo Asistentas...")
    await init_db()
    logger.info("✅ Duomenų bazė paruošta")

    # Užkrauti API raktus iš DB
    await load_api_keys_from_db()

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
        "version": "0.1.0",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detalus health check."""
    return {"status": "healthy", "database": "connected", "api_version": "0.1.0"}


# === Routers ===
from routers import (
    classes_router,
    dashboard_router,
    school_years_router,
    students_router,
    tests_router,
)
from routers.exam_sheets import router as exam_sheets_router
from routers.exams import router as exams_router
from routers.exports import router as exports_router
from routers.math_checker import router as math_router
from routers.problem_bank import router as problem_bank_router
from routers.settings import router as settings_router
from routers.statistics import router as statistics_router
from routers.submissions import router as submissions_router
from routers.upload import router as upload_router

app.include_router(school_years_router, prefix="/api/v1")
app.include_router(classes_router, prefix="/api/v1")
app.include_router(students_router, prefix="/api/v1")
app.include_router(tests_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")
app.include_router(exports_router, prefix="/api/v1")
app.include_router(math_router, prefix="/api/v1")
app.include_router(statistics_router, prefix="/api/v1")
app.include_router(submissions_router, prefix="/api/v1")
app.include_router(problem_bank_router, prefix="/api/v1")
app.include_router(exam_sheets_router, prefix="/api/v1")
app.include_router(exams_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
