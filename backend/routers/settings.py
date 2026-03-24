"""
API Router - Nustatymai ir API raktų valdymas.

OCR: Gemini Vision arba OpenAI GPT Vision (pasirenkama).
"""

from typing import Optional

from config import settings as app_settings
from utils.crypto_utils import decrypt_value, encrypt_value

import httpx
from fastapi import APIRouter, Depends, HTTPException
from models.setting import Setting
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db

router = APIRouter(prefix="/settings", tags=["Settings"])


class ApiKeysRequest(BaseModel):
    """API raktų užklausa."""

    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = "google/gemini-3.1-pro-preview"
    gemini_credentials_json: Optional[str] = None  # Google Cloud credentials JSON
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = "gpt-5.2"
    novita_api_key: Optional[str] = None
    novita_model: Optional[str] = "qwen3.5"
    together_api_key: Optional[str] = None
    together_model: Optional[str] = "Qwen/Qwen3.5-397B-A17B"
    wolfram_app_id: Optional[str] = None


class OcrProviderRequest(BaseModel):
    """OCR tiekėjo užklausa."""

    provider: str = "gemini"  # "gemini", "openai", "novita" arba "together"


class TestResponse(BaseModel):
    """Testo atsakymas."""

    success: bool
    message: str
    error: Optional[str] = None


# ===== Helper funkcijos DB operacijoms =====


async def get_setting(db: AsyncSession, key: str) -> Optional[str]:
    """Gauti nustatymą iš DB."""
    result = await db.execute(select(Setting).where(Setting.key == key))
    setting = result.scalar_one_or_none()
    return setting.value if setting else None


async def set_setting(
    db: AsyncSession,
    key: str,
    value: str,
    category: str = "general",
    description: str = None,
):
    """Išsaugoti nustatymą į DB."""
    result = await db.execute(select(Setting).where(Setting.key == key))
    setting = result.scalar_one_or_none()

    if setting:
        setting.value = value
        if description:
            setting.description = description
    else:
        setting = Setting(
            key=key, value=value, category=category, description=description
        )
        db.add(setting)

    await db.commit()


async def get_all_api_keys(db: AsyncSession) -> dict:
    """Gauti visus API raktus iš DB."""
    keys = {}
    key_names = [
        "gemini_api_key",
        "gemini_model",
        "openai_api_key",
        "openai_model",
        "novita_api_key",
        "novita_model",
        "wolfram_app_id",
        "ocr_provider",
    ]
    for key_name in key_names:
        value = await get_setting(db, key_name)
        if value:
            keys[key_name] = value
    return keys


@router.post("/api-keys")
async def save_api_keys(keys: ApiKeysRequest, db: AsyncSession = Depends(get_db)):
    """Išsaugo API raktus į duomenų bazę."""
    import json
    from pathlib import Path

    from config import BASE_DIR

    keys_data = keys.model_dump(exclude_none=True)

    for key_name, value in keys_data.items():
        is_api_key = "api_key" in key_name or "app_id" in key_name
        if value:  # Tik jei reikšmė nėra tuščia
            # Specialus atvejis - Google Cloud credentials JSON
            if key_name == "gemini_credentials_json":
                try:
                    # Validuojame JSON
                    creds_data = json.loads(value)

                    # Išsaugome į failą
                    creds_path = BASE_DIR / "backend" / "google_credentials.json"
                    with open(creds_path, "w", encoding="utf-8") as f:
                        json.dump(creds_data, f, indent=2)

                    # Išsaugome kelią į DB
                    await set_setting(
                        db,
                        "google_credentials_path",
                        str(creds_path),
                        category="api_keys",
                        description="Google Cloud credentials failo kelias",
                    )

                    # Perkrauname OCR servisą kad naudotų naujus credentials
                    from services.ocr import reset_ocr_service

                    reset_ocr_service()

                except json.JSONDecodeError:
                    raise HTTPException(
                        status_code=400, detail="Netinkamas JSON formatas"
                    )
            else:
                # Šifruoti API raktus prieš saugojimą
                stored_value = encrypt_value(value, app_settings.SECRET_KEY) if is_api_key else value
                await set_setting(
                    db,
                    key_name,
                    stored_value,
                    category="api_keys",
                    description=f"API raktas: {key_name}",
                )

    # Atnaujinti Gemini klientą jei yra naujas raktas
    if keys.gemini_api_key:
        from ai.gemini_client import configure_gemini

        configure_gemini(keys.gemini_api_key, keys.gemini_model)

    return {"success": True, "message": "API raktai išsaugoti į duomenų bazę"}


@router.get("/api-keys")
async def get_api_keys(db: AsyncSession = Depends(get_db)):
    """Gauna API raktų statusą (be pačių raktų)."""
    keys = await get_all_api_keys(db)
    return {
        "gemini": bool(keys.get("gemini_api_key")),
        "openai": bool(keys.get("openai_api_key")),
        "novita": bool(keys.get("novita_api_key")),
        "together": bool(keys.get("together_api_key")),
        "wolfram": bool(keys.get("wolfram_app_id")),
        "ocr_provider": keys.get("ocr_provider", "gemini"),
    }


# ===== OCR Provider =====


@router.get("/ocr-provider")
async def get_ocr_provider(db: AsyncSession = Depends(get_db)):
    """Gauti dabartinį OCR tiekėją."""
    provider = await get_setting(db, "ocr_provider")
    return {"provider": provider or "gemini"}


@router.post("/ocr-provider")
async def set_ocr_provider(
    request: OcrProviderRequest, db: AsyncSession = Depends(get_db)
):
    """Nustatyti OCR tiekėją."""
    if request.provider not in ["gemini", "openai", "novita", "together"]:
        raise HTTPException(status_code=400, detail="Netinkamas tiekėjas")

    await set_setting(
        db,
        "ocr_provider",
        request.provider,
        category="ocr",
        description="OCR tiekėjas (gemini, openai arba novita)",
    )

    # Perkrauname OCR servisą
    from services.ocr import reset_ocr_service

    reset_ocr_service()

    return {"success": True, "provider": request.provider}


@router.post("/test/gemini", response_model=TestResponse)
async def test_gemini(keys: ApiKeysRequest):
    """Testuoja Google Gemini API ryšį (naudojamas OCR ir AI)."""
    api_key = keys.gemini_api_key
    model = keys.gemini_model or "gemini-3.1-pro-preview"
    # AI Studio API naudoja modelį be "google/" prefikso
    if model.startswith("google/"):
        model = model[len("google/"):]

    if not api_key:
        return TestResponse(
            success=False, message="Neprisijungta", error="Trūksta API Key"
        )

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Gemini API test
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": "Atsakyk vienu žodžiu: 2+2=?"}]}],
                    "generationConfig": {"maxOutputTokens": 10},
                },
            )

            if response.status_code == 200:
                data = response.json()
                if "candidates" in data:
                    return TestResponse(
                        success=True,
                        message=f"Gemini API ({model}) prisijungta sėkmingai! Naudojama OCR ir AI.",
                    )
                else:
                    return TestResponse(
                        success=True, message=f"Gemini API ({model}) prisijungta."
                    )
            elif response.status_code == 429:
                return TestResponse(
                    success=True,
                    message=f"Gemini API ({model}) prisijungta! (Rate limit - palaukite ir bandykite vėliau)",
                )
            elif response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get(
                    "message", "Nežinoma klaida"
                )
                if "not found" in error_msg.lower():
                    return TestResponse(
                        success=False,
                        message="Neprisijungta",
                        error=f"Modelis '{model}' nerastas. Pabandykite 'gemini-3.1-pro-preview'",
                    )
                return TestResponse(
                    success=False, message="Neprisijungta", error=error_msg
                )
            elif response.status_code == 401 or response.status_code == 403:
                return TestResponse(
                    success=False,
                    message="Neprisijungta",
                    error="Neteisingas API raktas arba API neįjungta",
                )
            else:
                return TestResponse(
                    success=False,
                    message="Neprisijungta",
                    error=f"API klaida: {response.status_code}",
                )

    except httpx.TimeoutException:
        return TestResponse(
            success=False, message="Neprisijungta", error="Ryšio timeout"
        )
    except Exception as e:
        return TestResponse(success=False, message="Neprisijungta", error=str(e))


@router.post("/test/wolfram", response_model=TestResponse)
async def test_wolfram(keys: ApiKeysRequest):
    """Testuoja WolframAlpha API ryšį."""
    app_id = keys.wolfram_app_id

    if not app_id:
        return TestResponse(
            success=False, message="Neprisijungta", error="Trūksta App ID"
        )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # WolframAlpha Simple API test
            response = await client.get(
                "https://api.wolframalpha.com/v2/query",
                params={
                    "input": "2+2",
                    "appid": app_id,
                    "format": "plaintext",
                    "output": "json",
                },
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("queryresult", {}).get("success"):
                    return TestResponse(
                        success=True, message="WolframAlpha API prisijungta sėkmingai!"
                    )
                elif "Invalid appid" in str(data):
                    return TestResponse(
                        success=False,
                        message="Neprisijungta",
                        error="Neteisingas App ID",
                    )
                else:
                    return TestResponse(
                        success=False,
                        message="Neprisijungta",
                        error="API atsakė, bet rezultatas netikėtas",
                    )
            else:
                return TestResponse(
                    success=False,
                    message="Neprisijungta",
                    error=f"API klaida: {response.status_code}",
                )

    except httpx.TimeoutException:
        return TestResponse(
            success=False, message="Neprisijungta", error="Ryšio timeout"
        )
    except Exception as e:
        return TestResponse(success=False, message="Neprisijungta", error=str(e))


@router.post("/test/openai", response_model=TestResponse)
async def test_openai(keys: ApiKeysRequest):
    """Testuoja OpenAI API ryšį (GPT Vision)."""
    import logging

    logger = logging.getLogger(__name__)

    api_key = keys.openai_api_key
    model = keys.openai_model or "gpt-5.2"

    if not api_key:
        return TestResponse(
            success=False, message="Neprisijungta", error="Trūksta API Key"
        )

    logger.info(f"🔄 Testuojamas OpenAI API su modeliu: {model}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            logger.info("📡 Siunčiama užklausa į OpenAI...")
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "user", "content": "Atsakyk vienu žodžiu: 2+2=?"}
                    ],
                    "max_completion_tokens": 10,
                },
            )

            logger.info(f"📥 OpenAI atsakymas: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ OpenAI sėkmingai atsakė")
                if "choices" in data:
                    return TestResponse(
                        success=True,
                        message=f"OpenAI API ({model}) prisijungta sėkmingai! Galima naudoti OCR.",
                    )
                else:
                    return TestResponse(
                        success=True, message=f"OpenAI API ({model}) prisijungta."
                    )
            elif response.status_code == 401:
                return TestResponse(
                    success=False,
                    message="Neprisijungta",
                    error="Neteisingas API raktas",
                )
            elif response.status_code == 404:
                return TestResponse(
                    success=False,
                    message="Neprisijungta",
                    error=f"Modelis '{model}' nerastas. Pabandykite 'gpt-4o' arba 'gpt-4-turbo'",
                )
            else:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get(
                    "message", f"API klaida: {response.status_code}"
                )
                logger.error(f"❌ OpenAI klaida: {error_msg}")
                return TestResponse(
                    success=False, message="Neprisijungta", error=error_msg
                )

    except httpx.TimeoutException:
        logger.error("❌ OpenAI timeout (60s)")
        return TestResponse(
            success=False,
            message="Neprisijungta",
            error="Ryšio timeout (60s) - bandykite dar kartą",
        )
    except Exception as e:
        logger.error(f"❌ OpenAI klaida: {e}")
        return TestResponse(success=False, message="Neprisijungta", error=str(e))


@router.post("/test/novita", response_model=TestResponse)
async def test_novita(keys: ApiKeysRequest):
    """Testuoja Novita.ai API ryšį (Qwen3 VL Vision)."""
    import logging

    logger = logging.getLogger(__name__)

    api_key = keys.novita_api_key
    model_key = keys.novita_model or "qwen3.5"

    if not api_key:
        return TestResponse(
            success=False, message="Neprisijungta", error="Trūksta API Key"
        )

    # Išverčiame trumpą pavadinimą į pilną
    from services.ocr.novita_vision import NOVITA_MODELS

    model = NOVITA_MODELS.get(model_key, model_key)

    logger.info(f"🔄 Testuojamas Novita API su modeliu: {model}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.novita.ai/openai/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "user", "content": "Atsakyk vienu žodžiu: 2+2=?"}
                    ],
                    "max_tokens": 10,
                },
            )

            logger.info(f"📥 Novita atsakymas: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if "choices" in data:
                    return TestResponse(
                        success=True,
                        message=f"Novita API ({model}) prisijungta sėkmingai! Galima naudoti OCR.",
                    )
                else:
                    return TestResponse(
                        success=True, message=f"Novita API ({model}) prisijungta."
                    )
            elif response.status_code == 401:
                return TestResponse(
                    success=False,
                    message="Neprisijungta",
                    error="Neteisingas API raktas",
                )
            elif response.status_code == 404:
                return TestResponse(
                    success=False,
                    message="Neprisijungta",
                    error=f"Modelis '{model}' nerastas",
                )
            else:
                error_data = (
                    response.json()
                    if response.headers.get("content-type", "").startswith(
                        "application/json"
                    )
                    else {}
                )
                error_msg = (
                    error_data.get("error", {}).get(
                        "message", f"API klaida: {response.status_code}"
                    )
                    if isinstance(error_data, dict)
                    else f"API klaida: {response.status_code}"
                )
                return TestResponse(
                    success=False, message="Neprisijungta", error=error_msg
                )

    except httpx.TimeoutException:
        return TestResponse(
            success=False,
            message="Neprisijungta",
            error="Ryšio timeout (60s) - bandykite dar kartą",
        )
    except Exception as e:
        logger.error(f"❌ Novita klaida: {e}")
        return TestResponse(success=False, message="Neprisijungta", error=str(e))


@router.post("/test/together", response_model=TestResponse)
async def test_together(keys: ApiKeysRequest):
    """Testuoja Together.ai API ryšį."""
    api_key = keys.together_api_key
    model = keys.together_model or "Qwen/Qwen3.5-397B-A17B"

    if not api_key:
        return TestResponse(
            success=False, message="Neprisijungta", error="Trūksta API Key"
        )

    logger.info(f"🔄 Testuojamas Together API su modeliu: {model}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.together.xyz/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": "Atsakyk vienu žodžiu: 2+2=?",
                        }
                    ],
                    "max_tokens": 10,
                    "temperature": 0.0,
                },
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("choices"):
                    return TestResponse(
                        success=True,
                        message=f"Together API ({model}) prisijungta sėkmingai!",
                    )
                return TestResponse(
                    success=True, message=f"Together API ({model}) prisijungta."
                )
            elif response.status_code == 429:
                return TestResponse(
                    success=True,
                    message=f"Together API ({model}) prisijungta! (Rate limit)",
                )
            elif response.status_code == 401:
                return TestResponse(
                    success=False,
                    message="Neprisijungta",
                    error="Neteisingas API raktas",
                )
            else:
                return TestResponse(
                    success=False,
                    message="Neprisijungta",
                    error=f"API klaida: {response.status_code} - {response.text[:200]}",
                )

    except httpx.TimeoutException:
        return TestResponse(
            success=False,
            message="Neprisijungta",
            error="Ryšio timeout (60s) - bandykite dar kartą",
        )
    except Exception as e:
        logger.error(f"❌ Together klaida: {e}")
        return TestResponse(success=False, message="Neprisijungta", error=str(e))


# ===== TEMŲ VALDYMAS =====

from utils.topics import (
    TOPIC_CATEGORIES,
    get_all_topics_list,
    get_topic_name,
    get_topics_by_grade,
    get_topics_grouped,
)


@router.get("/topics")
async def get_topics(grade: Optional[int] = None):
    """
    Gauti visų temų sąrašą.

    Args:
        grade: Filtruoti pagal klasę (5-10)
    """
    if grade:
        topics = get_topics_by_grade(grade)
        return {
            "topics": [
                {
                    "id": t.id,
                    "name": t.name_lt,
                    "category": t.category,
                    "grade_levels": t.grade_levels,
                }
                for t in topics
            ],
            "grade_filter": grade,
        }
    return {"topics": get_all_topics_list()}


@router.get("/topics/grouped")
async def get_topics_by_category():
    """Gauti temas sugrupuotas pagal kategorijas."""
    return get_topics_grouped()


@router.get("/topics/categories")
async def get_topic_categories():
    """Gauti temų kategorijų sąrašą."""
    return {
        "categories": [
            {"id": cat_id, "name": cat_name}
            for cat_id, cat_name in TOPIC_CATEGORIES.items()
        ]
    }
