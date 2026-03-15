"""
Together.ai Vision OCR servisas.
Naudoja Together.ai API (OpenAI-suderinama) su Qwen ir Llama modeliais matematikos ir teksto atpažinimui.

Palaikomi modeliai:
- Qwen/Qwen3.5-397B-A17B                                    - Qwen3.5 397B
- meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8          - Llama 4 Maverick

API: https://api.together.xyz/v1/chat/completions
"""

import base64
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from config import BASE_DIR
from loguru import logger

# Together.ai API bazinis URL (OpenAI-suderinama)
TOGETHER_BASE_URL = "https://api.together.xyz/v1"

DEFAULT_MODEL = "Qwen/Qwen3.5-397B-A17B"


def _get_together_api_key_from_db() -> Optional[str]:
    """Gauti Together API raktą iš duomenų bazės."""
    try:
        db_path = BASE_DIR / "database" / "math_teacher.db"
        if not db_path.exists():
            return None
        conn = sqlite3.connect(str(db_path), timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'together_api_key'")
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception as e:
        logger.warning(f"Nepavyko nuskaityti Together API rakto iš DB: {e}")
    return None


def _get_together_model_from_db() -> Optional[str]:
    """Gauti Together modelio pavadinimą iš duomenų bazės."""
    try:
        db_path = BASE_DIR / "database" / "math_teacher.db"
        if not db_path.exists():
            return None
        conn = sqlite3.connect(str(db_path), timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'together_model'")
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception as e:
        logger.warning(f"Nepavyko nuskaityti Together modelio iš DB: {e}")
    return None


@dataclass
class TogetherVisionResult:
    """Together Vision OCR rezultatas."""
    text: str
    latex: Optional[str] = None
    confidence: float = 0.0
    source: str = "together"
    processing_time_ms: int = 0


class TogetherVisionClient:
    """Together.ai Vision API klientas OCR tikslams."""

    def __init__(self):
        """Inicializuoja Together Vision klientą."""
        self.available = False
        self.api_key = None
        self.model = DEFAULT_MODEL

        self._try_api_key()

    def _try_api_key(self):
        """Bandome inicializuoti su API raktu."""
        try:
            self.api_key = _get_together_api_key_from_db()
            if self.api_key:
                self.available = True
                # Nuskaitome modelio pavadinimą iš DB
                db_model = _get_together_model_from_db()
                if db_model:
                    self.model = db_model
                logger.info(f"✅ Together API key inicializuotas (modelis: {self.model})")
            else:
                logger.warning("Together API raktas nenustatytas DB")
        except Exception as e:
            logger.warning(f"Together API key inicializacija nepavyko: {e}")

    async def recognize(self, image_path: str) -> TogetherVisionResult:
        """Atpažįsta tekstą iš vaizdo naudojant Together.ai API."""
        if not self.available:
            return TogetherVisionResult(text="Klaida: Together.ai nėra sukonfigūruotas")

        start_time = time.time()

        try:
            result = await self._recognize_api(image_path)
            elapsed = int((time.time() - start_time) * 1000)

            if not result:
                return TogetherVisionResult(
                    text="Klaida: Together Vision negrąžino teksto",
                    processing_time_ms=elapsed,
                )

            # Parsuojame atsakymą
            text, latex, is_math = self._parse_response(result)

            logger.info(f"Together OCR rezultatas: {len(text)} simbolių, {elapsed}ms")

            return TogetherVisionResult(
                text=text,
                latex=latex,
                confidence=0.9 if text else 0.0,
                processing_time_ms=elapsed,
            )

        except Exception as e:
            elapsed = int((time.time() - start_time) * 1000)
            error_msg = str(e)
            logger.error(f"Together OCR klaida: {error_msg}")
            return TogetherVisionResult(
                text=f"Klaida: {error_msg}",
                processing_time_ms=elapsed,
            )

    async def _recognize_api(self, image_path: str) -> str:
        """Siunčia vaizdą į Together.ai API ir gauna atpažintą tekstą."""
        import httpx

        image_data = self._load_image_base64(image_path)
        if not image_data:
            return ""

        prompt = self._get_prompt()

        # Together.ai naudoja OpenAI-suderinamą formatą
        url = f"{TOGETHER_BASE_URL}/chat/completions"

        request_body = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            "max_tokens": 4096,
            "temperature": 0.0,
        }

        logger.info(f"📷 Together: Vaizdas užkrautas, base64 ilgis: {len(image_data)} simbolių")
        logger.info(f"🔄 Kviečiamas Together modelis: {self.model}")

        # Retry logika
        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=180.0) as client:
                    response = await client.post(
                        url,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {self.api_key}",
                        },
                        json=request_body,
                    )

                    logger.info(f"📡 Together HTTP status: {response.status_code}")
                    if response.status_code != 200:
                        error_text = response.text[:500]
                        logger.error(
                            f"Together API klaida {response.status_code}: {error_text}"
                        )
                        return f"API klaida {response.status_code}: {error_text}"

                    data = response.json()
                    logger.info(
                        f"📡 Together response keys: {list(data.keys())}"
                    )

                    choices = data.get("choices", [])
                    if choices:
                        content = (
                            choices[0]
                            .get("message", {})
                            .get("content", "")
                        )
                        finish_reason = choices[0].get("finish_reason", "unknown")
                        logger.info(
                            f"📡 Together atsakymas: {len(content)} simbolių, "
                            f"finish_reason={finish_reason}, preview: {content[:200]}"
                        )
                        if content:
                            return content
                        else:
                            return f"Klaida: Together API grąžino tuščią content (finish_reason={finish_reason})"
                    else:
                        logger.warning(
                            f"Together grąžino tuščią atsakymą (bandymas {attempt + 1}/{max_retries}). "
                            f"Full response: {str(data)[:500]}"
                        )

            except httpx.ConnectError as e:
                last_error = e
                logger.warning(
                    f"Tinklo klaida (bandymas {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    import asyncio
                    await asyncio.sleep(1)
                    continue
            except httpx.TimeoutException as e:
                last_error = e
                logger.error(
                    f"Timeout klaida (bandymas {attempt + 1}/{max_retries}): "
                    f"Together modelis per lėtai atsakė (timeout=180s)."
                )
                if attempt < max_retries - 1:
                    import asyncio
                    await asyncio.sleep(1)
                    continue
            except Exception as e:
                last_error = e
                logger.error(
                    f"Netikėta klaida {type(e).__name__} (bandymas {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    import asyncio
                    await asyncio.sleep(1)
                    continue

        if last_error:
            raise last_error
        return ""

    def _load_image_base64(self, image_path: str) -> Optional[str]:
        """Nuskaito vaizdą ir konvertuoja į JPEG base64."""
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

    def _get_prompt(self) -> str:
        """Grąžina OCR prompt'ą."""
        return """Nuskaityk šį matematikos darbo vaizdą ir grąžink JSON formatu:

{
  "tasks": [
    {
      "number": "1a",
      "question_text": "Užduoties sąlyga (jei matoma)",
      "student_work": "Mokinio sprendimo žingsniai",
      "final_answer": "Galutinis atsakymas",
      "confidence": 0.95
    }
  ]
}

SVARBIOS TAISYKLĖS:
1. Atpažink VISAS užduotis kurias matai
2. Skaičiai ir formulės turi būti tikslūs
3. Matematiniai simboliai: ×, ÷, √, ², ³, π, ≤, ≥, ≠, ∞
4. Trucpenos rašyk kaip: numerator/denominator
5. Jei matai LaTeX – naudok jį student_work lauke
6. Jei nematai užduoties teksto – palik question_text kaip null
7. confidence rodyk nuo 0.0 iki 1.0

Dabar nuskaityk paveikslėlį ir grąžink JSON su VISOMIS užduotimis."""

    def _parse_response(self, response: str) -> tuple:
        """Išparsuoja Together atsakymą."""
        import json
        import re

        if not response:
            return "", None, False

        text = response
        latex = None
        is_math = False

        # Bandome parsuoti JSON
        try:
            # Pašalinam markdown code block jei yra
            json_str = response
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()

            data = json.loads(json_str)
            tasks = data.get("tasks", [])

            if tasks:
                is_math = True
                text_lines = []
                latex_lines = []

                for task in tasks:
                    number = task.get("number", "?")
                    question = task.get("question_text", "")
                    work = task.get("student_work", "")
                    answer = task.get("final_answer", "")

                    line = f"{number})"
                    if question:
                        line += f" {question}"
                    if work:
                        line += f" → {work}"
                    if answer:
                        line += f" = {answer}"
                    text_lines.append(line)

                    # LaTeX
                    latex_line = f"\\textbf{{{number})}}"
                    if work:
                        latex_line += f" ${work}$"
                    if answer:
                        latex_line += f" $= {answer}$"
                    latex_lines.append(latex_line)

                text = "\n".join(text_lines)

                # LaTeX separator
                latex = "§§§".join(latex_lines)
                logger.info(
                    f"JSON parsuotas: {len(tasks)} užduočių, latex separatorius: §§§"
                )

        except Exception as e:
            logger.debug(f"JSON parsavimas nepavyko, naudojamas raw text: {e}")

        return text, latex, is_math


# Singleton
_together_vision: Optional[TogetherVisionClient] = None


def get_together_vision_client() -> TogetherVisionClient:
    """Gauna Together Vision klientą (singleton)."""
    global _together_vision
    if _together_vision is None:
        _together_vision = TogetherVisionClient()
    return _together_vision


def reset_together_vision_client():
    """Perkrauna Together Vision klientą."""
    global _together_vision
    _together_vision = None

