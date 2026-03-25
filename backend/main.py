"""
Matematikos Mokytojo Asistentas - Backend API
=============================================
FastAPI aplikacija mokinių kontrolinių tikrinimui.
"""

from routers.upload import router as upload_router
from routers.submissions import router as submissions_router
from routers.statistics import router as statistics_router
from routers.settings import router as settings_router
from routers.problem_bank import router as problem_bank_router
from routers.math_checker import router as math_router
from routers.exports import router as exports_router
from routers.exams import router as exams_router
from routers.exam_sheets import router as exam_sheets_router
from routers.auth import router as auth_router
from routers import (
    classes_router,
    dashboard_router,
    school_years_router,
    students_router,
    tests_router,
)
import sys
from contextlib import asynccontextmanager

from config import settings
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from database import async_session_maker, init_db
from utils.auth_deps import verify_token

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

# Endpointai kurie NEREIKALAUJA autentifikacijos
PUBLIC_PATHS = {
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/auth/login",
    "/api/v1/auth/status",
    "/api/v1/auth/setup",
}


async def load_api_keys_from_db():
    """Užkrauti API raktus iš duomenų bazės į atmintį."""
    from ai.gemini_client import configure_gemini
    from math_checker.wolfram_client import configure_wolfram
    from models.setting import Setting
    from sqlalchemy import select
    from utils.crypto_utils import decrypt_value

    async with async_session_maker() as db:
        try:
            # Užkrauti Gemini API raktą
            result = await db.execute(
                select(Setting).where(Setting.key == "gemini_api_key")
            )
            gemini_setting = result.scalar_one_or_none()

            if gemini_setting and gemini_setting.value:
                api_key = decrypt_value(gemini_setting.value, settings.SECRET_KEY)

                # Gauti modelį
                result = await db.execute(
                    select(Setting).where(Setting.key == "gemini_model")
                )
                model_setting = result.scalar_one_or_none()
                model = model_setting.value if model_setting else "google/gemini-3.1-pro-preview"

                if api_key:
                    configure_gemini(api_key, model)
                    logger.info(f"✅ Gemini sukonfigūruotas su modeliu: {model}")
            else:
                logger.info("ℹ️ Gemini API raktas nerastas. Įveskite jį per Nustatymus.")
        except Exception as e:
            logger.warning(f"⚠️ Nepavyko užkrauti Gemini konfigūracijos iš DB: {e}")

        # Užkrauti WolframAlpha API raktą
        try:
            result = await db.execute(
                select(Setting).where(Setting.key == "wolfram_app_id")
            )
            wolfram_setting = result.scalar_one_or_none()

            if wolfram_setting and wolfram_setting.value:
                wolfram_key = decrypt_value(wolfram_setting.value, settings.SECRET_KEY)
                configure_wolfram(wolfram_key)
                logger.info("✅ WolframAlpha API raktas užkrautas iš DB")
            else:
                logger.warning("⚠️ WolframAlpha API raktas nenustatytas DB")
        except Exception as e:
            logger.warning(f"⚠️ Nepavyko užkrauti WolframAlpha konfigūracijos: {e}")


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
    version="0.2.0",
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


# === Auth Middleware ===
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """
    Globalus autentifikacijos middleware.
    Tikrina JWT Bearer tokeną visiems endpointams, 
    išskyrus viešus (login, status, setup, health).
    """
    path = request.url.path

    # Leisti viešus endpointus
    if path in PUBLIC_PATHS or path.startswith("/api/v1/auth/"):
        return await call_next(request)

    # Tikrinti Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Reikalingas prisijungimas"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ", 1)[1]
    payload = verify_token(token)
    if not payload:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Netinkamas arba pasibaigęs tokenas"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Tokenas validus - leisti tęsti
    return await call_next(request)


# === Health check ===
@app.get("/", tags=["Health"])
async def root():
    """Pagrindinis endpoint - health check."""
    return {
        "status": "ok",
        "message": "Matematikos Mokytojo Asistentas veikia!",
        "version": "0.2.0",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detalus health check."""
    return {"status": "healthy", "database": "connected", "api_version": "0.2.0"}


# === Routers ===

# Auth (viešas + apsaugotas)
app.include_router(auth_router, prefix="/api/v1")

# Apsaugoti routers
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
