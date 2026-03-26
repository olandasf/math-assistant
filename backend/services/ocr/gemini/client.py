"""Gemini Vision OCR client."""
import base64
import os
import time
from pathlib import Path
from typing import Optional

from config import BASE_DIR
from loguru import logger
from .models import GeminiVisionResult
from .prompts import get_ocr_prompt
from .parsers import parse_response


def _get_gemini_api_key_from_db() -> Optional[str]:
    """Gauti Gemini API raktą iš aplinkos kintamojo arba duomenų bazės."""
    # 1. Prioritetas: aplinkos kintamasis (nustatytas main.py startupe)
    env_key = os.environ.get("GEMINI_API_KEY")
    if env_key:
        return env_key

    # 2. Fallback: tiesioginė DB prieiga (sinchroninė, naudoti tik jei env nėra)
    try:
        db_path = BASE_DIR / "database" / "math_teacher.db"
        if not db_path.exists():
            return None
        import sqlite3
        conn = sqlite3.connect(str(db_path), timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'gemini_api_key'")
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            value = row[0]
            # Dešifruoti jei šifruotas (enc: prefiksas)
            if value.startswith("enc:"):
                logger.debug("Gemini API raktas šifruotas, bandoma dešifruoti...")
                try:
                    from utils.crypto_utils import decrypt_value
                    secret = os.environ.get("SECRET_KEY", "")
                    if secret:
                        value = decrypt_value(value, secret)
                except Exception:
                    logger.warning("Nepavyko dešifruoti Gemini API rakto")
                    return None
            return value
    except Exception as e:
        logger.warning(f"Nepavyko nuskaityti Gemini API rakto iš DB: {e}")
    return None


class GeminiVisionClient:
    """Gemini Vision API klientas OCR tikslams - palaiko Google AI Studio (API key) ir Vertex AI."""

    AI_STUDIO_MODEL = "gemini-3-flash-preview"
    VERTEX_AI_MODEL = "google/gemini-3-flash-preview"
    PROJECT_ID = "mtematika-471410"
    LOCATION = "global"

    def __init__(self):
        """Inicializuoja Gemini Vision klientą."""
        self.available = False
        self.api_key = None
        self.use_vertex_ai = False
        self.genai_client = None
        self.model = self.AI_STUDIO_MODEL

        self._try_api_key()

        if not self.available:
            self._try_vertex_ai()

    def _try_vertex_ai(self):
        try:
            credentials_paths = [
                BASE_DIR / "backend" / "google_credentials.json",
                BASE_DIR / "backend" / "mtematika-471410-e4cb6af744ea.json",
                BASE_DIR / "backend" / "credentials.json",
                BASE_DIR / "credentials.json",
                Path(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")),
            ]

            credentials_path = None
            for path in credentials_paths:
                if str(path) and Path(path).exists():
                    credentials_path = Path(path)
                    logger.info(f"🔍 Rastas credentials failas: {path}")
                    break

            if not credentials_path:
                logger.info("Google Cloud credentials failas nerastas, bandysime API key")
                return

            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)

            from google import genai
            self.genai_client = genai.Client(
                vertexai=True,
                project=self.PROJECT_ID,
                location=self.LOCATION,
            )

            self.use_vertex_ai = True
            self.available = True
            self.model = self.VERTEX_AI_MODEL
            logger.info(f"✅ Vertex AI inicializuotas (modelis: {self.model}, projektas: {self.PROJECT_ID})")

        except Exception as e:
            logger.warning(f"Vertex AI inicializacija nepavyko: {e}")
            self.use_vertex_ai = False

    def _try_api_key(self):
        try:
            self.api_key = _get_gemini_api_key_from_db()
            if self.api_key:
                self.available = True
                self.use_vertex_ai = False
                self.model = self.AI_STUDIO_MODEL
                logger.info(f"✅ Gemini AI Studio API key inicializuotas (modelis: {self.model})")
            else:
                logger.warning("Gemini API raktas nenustatytas DB")
        except Exception as e:
            logger.warning(f"API key inicializacija nepavyko: {e}")

    async def recognize(self, image_path: str) -> GeminiVisionResult:
        if not self.available:
            return GeminiVisionResult(text="", processing_time_ms=0)

        start = time.time()

        try:
            if self.use_vertex_ai:
                result = await self._recognize_vertex_ai(image_path)
            else:
                result = await self._recognize_api_key(image_path)

            processing_time = int((time.time() - start) * 1000)

            text, latex, is_math = parse_response(result)

            logger.info(f"Gemini OCR rezultatas: {len(text)} simbolių, {processing_time}ms")

            return GeminiVisionResult(
                text=text,
                latex=latex,
                confidence=0.85 if text else 0.0,
                is_math=is_math,
                processing_time_ms=processing_time,
            )

        except Exception as e:
            logger.error(f"Gemini Vision OCR klaida: {e}")
            return GeminiVisionResult(
                text=f"Klaida: {e}",
                processing_time_ms=int((time.time() - start) * 1000),
            )

    async def _recognize_vertex_ai(self, image_path: str) -> str:
        import asyncio
        from google.genai import types

        image_bytes = Path(image_path).read_bytes()

        mime_type = "image/jpeg"
        if image_path.lower().endswith(".png"):
            mime_type = "image/png"
        elif image_path.lower().endswith(".gif"):
            mime_type = "image/gif"
        elif image_path.lower().endswith(".webp"):
            mime_type = "image/webp"

        prompt = get_ocr_prompt()

        logger.info(f"🔄 Kviečiamas Vertex AI modelis: {self.model}")

        def _call_vertex_ai():
            return self.genai_client.models.generate_content(
                model=self.model,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=prompt),
                            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                        ],
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=8192,
                    response_mime_type="application/json",
                ),
            )

        try:
            response = await asyncio.to_thread(_call_vertex_ai)
        except Exception as e:
            logger.error(f"❌ Vertex AI kvietimo klaida: {e}")
            logger.info("🔄 Bandome Vertex AI be response_mime_type...")

            def _call_vertex_ai_fallback():
                return self.genai_client.models.generate_content(
                    model=self.model,
                    contents=[
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_text(text=prompt),
                                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                            ],
                        )
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                        max_output_tokens=8192,
                    ),
                )

            response = await asyncio.to_thread(_call_vertex_ai_fallback)

        result = ""
        try:
            result = response.text if response.text else ""
        except Exception as e:
            logger.warning(f"📡 response.text klaida: {e}")

        if not result and response.candidates:
            for candidate in response.candidates:
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, "text") and part.text and not getattr(part, "thought", False):
                            result = part.text
                            break

        return result

    async def _recognize_api_key(self, image_path: str) -> str:
        import httpx

        image_data = self._load_image_base64(image_path)
        if not image_data:
            return ""

        prompt = get_ocr_prompt()
        mime_type = "image/jpeg"

        api_model = self.model
        if api_model.startswith("google/"):
            api_model = api_model[len("google/"):]

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{api_model}:generateContent"

        request_body = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": mime_type, "data": image_data}},
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 4096,
                "temperature": 0.0,
                "responseMimeType": "application/json",
            },
        }

        logger.info(f"🔄 Kviečiamas API key modelis: {self.model}")

        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
                    response = await client.post(
                        f"{url}?key={self.api_key}",
                        headers={"Content-Type": "application/json"},
                        json=request_body,
                    )

                    if response.status_code != 200:
                        logger.error(f"Gemini API klaida: {response.status_code} - {response.text}")
                        return ""

                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            result = parts[0].get("text", "")
                            if result:
                                return result

            except httpx.ConnectError as e:
                last_error = e
                if attempt < max_retries - 1:
                    import asyncio
                    await asyncio.sleep(1)
                    continue
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    import asyncio
                    await asyncio.sleep(1)
                    continue

        if last_error:
            raise last_error
        return ""

    def _load_image_base64(self, image_path: str) -> Optional[str]:
        try:
            path = Path(image_path)
            if not path.exists():
                logger.error(f"Vaizdas nerastas: {image_path}")
                return None
            from PIL import Image
            import io
            with Image.open(path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG", quality=90)
                return base64.b64encode(buffered.getvalue()).decode('utf-8')
        except Exception as e:
            logger.error(f"Vaizdo nuskaitymo klaida: {e}")
            return None
