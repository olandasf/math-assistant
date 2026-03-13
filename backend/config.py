"""
Konfigūracijos nustatymai iš .env failo.
"""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings

# Projekto šakninis katalogas
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Aplikacijos nustatymai."""

    # === Aplinka ===
    DEBUG: bool = Field(default=True, description="Debug režimas")
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production", description="JWT secret key"
    )

    # === Duomenų bazė ===
    DATABASE_URL: str = Field(
        default=f"sqlite+aiosqlite:///{BASE_DIR}/database/math_teacher.db",
        description="SQLite duomenų bazės URL",
    )

    # === CORS ===
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Leidžiami CORS origins",
    )

    # === API Keys ===
    # Google Cloud (Gemini Vision OCR)
    GOOGLE_APPLICATION_CREDENTIALS: str = Field(
        default="", description="Google Cloud credentials path"
    )
    GOOGLE_CREDENTIALS_PATH: str = Field(
        default="", description="Google Cloud credentials path (alias)"
    )
    GOOGLE_GEMINI_API_KEY: str = Field(default="", description="Google Gemini API key")

    # WolframAlpha (backup skaičiavimams)
    WOLFRAM_ALPHA_APP_ID: str = Field(default="", description="WolframAlpha App ID")

    # Legacy - nebereikalingi (palikti dėl suderinamumo)
    MATHPIX_APP_ID: str = Field(default="", description="[DEPRECATED] MathPix App ID")
    MATHPIX_APP_KEY: str = Field(default="", description="[DEPRECATED] MathPix App Key")
    GOOGLE_VISION_API_KEY: str = Field(
        default="", description="[DEPRECATED] Google Cloud Vision API key"
    )

    # === Failų nustatymai ===
    UPLOAD_DIR: str = Field(default="uploads", description="Įkeltų failų katalogas")
    EXPORT_DIR: str = Field(default="exports", description="Eksportuotų PDF katalogas")
    MAX_UPLOAD_SIZE_MB: int = Field(default=50, description="Maksimalus failo dydis MB")
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=["pdf", "png", "jpg", "jpeg", "tiff", "bmp"],
        description="Leidžiami failų plėtiniai",
    )

    # === OCR nustatymai ===
    OCR_CONFIDENCE_THRESHOLD: float = Field(
        default=0.7, description="Minimali OCR tikimybė"
    )
    # Legacy - nebereikalingi (sistema naudoja tik Gemini Vision)
    USE_MATHPIX: bool = Field(
        default=False, description="[DEPRECATED] Naudoti MathPix OCR"
    )
    USE_GOOGLE_VISION: bool = Field(
        default=False, description="[DEPRECATED] Naudoti Google Vision"
    )
    USE_LOCAL_OCR: bool = Field(
        default=False, description="[DEPRECATED] Naudoti lokalų Tesseract/EasyOCR"
    )

    # === Vertinimo nustatymai ===
    GRADING_SCALE: dict = Field(
        default={
            10: (91, 100),
            9: (81, 90),
            8: (71, 80),
            7: (61, 70),
            6: (51, 60),
            5: (41, 50),
            4: (31, 40),
            3: (21, 30),
            2: (11, 20),
            1: (0, 10),
        },
        description="Vertinimo skalė",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Gauti cached nustatymus."""
    return Settings()


# Global settings instance
settings = get_settings()
