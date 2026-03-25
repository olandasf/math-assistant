"""
Konfigūracijos nustatymai iš .env failo.
"""

import secrets
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
    DEBUG: bool = Field(default=False, description="Debug režimas")
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_hex(32),
        description="JWT secret key (auto-generated if not set)",
    )

    # === Duomenų bazė ===
    # Dev: SQLite (default). Produkcija: PostgreSQL per .env:
    # DATABASE_URL=postgresql+asyncpg://mathapp:M4thT3ach3r2026!@192.168.1.50:5432/math_teacher
    DATABASE_URL: str = Field(
        default=f"sqlite+aiosqlite:///{BASE_DIR}/database/math_teacher.db",
        description="DB URL. SQLite (dev) arba PostgreSQL (produkcija)",
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
    """Gauti cached nustatymus. Automatiškai išsaugo SECRET_KEY į .env jei naujas."""
    s = Settings()
    
    # Jei SECRET_KEY nebuvo .env faile, jį reikia išsaugoti
    # kad Fernet šifravimas veiktų tarp paleidimų
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        content = env_path.read_text(encoding="utf-8")
        if "SECRET_KEY" not in content:
            with open(env_path, "a", encoding="utf-8") as f:
                f.write(f"\n# Auto-sugeneruotas JWT ir šifravimo raktas\nSECRET_KEY={s.SECRET_KEY}\n")
    else:
        # Sukurti .env su SECRET_KEY
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"# Auto-sugeneruotas JWT ir šifravimo raktas\nSECRET_KEY={s.SECRET_KEY}\n")
    
    return s


# Global settings instance
settings = get_settings()
