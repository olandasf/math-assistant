"""
Novita.ai Vision OCR servisas.
Naudoja Novita.ai API (OpenAI-suderinama) su Qwen3 VL modeliais matematikos ir teksto atpažinimui.

Palaikomi modeliai:
- qwen/qwen3-vl-235b-a22b-instruct  ($0.30/M in, $1.50/M out) - greitas
- qwen/qwen3-vl-235b-a22b-thinking  ($0.98/M in, $3.95/M out) - su reasoning

API dokumentacija: https://novita.ai/docs/guides/llm-vision
"""

import base64
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from config import BASE_DIR
from loguru import logger

# Novita.ai API bazinis URL (OpenAI-suderinama)
NOVITA_BASE_URL = "https://api.novita.ai/openai"

# Pasiekiami modeliai
NOVITA_MODELS = {
    "qwen3-vl-instruct": "qwen/qwen3-vl-235b-a22b-instruct",
    "qwen3-vl-thinking": "qwen/qwen3-vl-235b-a22b-thinking",
}

DEFAULT_MODEL = "qwen3-vl-instruct"


def _get_novita_api_key_from_db() -> Optional[str]:
    """Gauti Novita API raktą iš duomenų bazės."""
    try:
        db_path = BASE_DIR / "database" / "math_teacher.db"
        if not db_path.exists():
            return None
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'novita_api_key'")
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception as e:
        logger.warning(f"Nepavyko nuskaityti Novita API rakto iš DB: {e}")
    return None


def _get_novita_model_from_db() -> str:
    """Gauti Novita modelio pavadinimą iš duomenų bazės."""
    try:
        db_path = BASE_DIR / "database" / "math_teacher.db"
        if not db_path.exists():
            return DEFAULT_MODEL
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'novita_model'")
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception as e:
        logger.warning(f"Nepavyko nuskaityti Novita modelio iš DB: {e}")
    return DEFAULT_MODEL


@dataclass
class NovitaVisionResult:
    """Novita Vision OCR rezultatas."""

    text: str
    latex: Optional[str] = None
    confidence: float = 0.85
    is_math: bool = False
    processing_time_ms: int = 0


class NovitaVisionClient:
    """
    Novita.ai Vision API klientas OCR tikslams.
    Naudoja OpenAI-suderinamą chat/completions endpointą su Qwen3 VL modeliais.
    """

    def __init__(self):
        """Inicializuoja Novita Vision klientą."""
        self.available = False
        self.api_key = None
        self.model_key = DEFAULT_MODEL
        self.model = NOVITA_MODELS[DEFAULT_MODEL]

        self._try_api_key()

    def _try_api_key(self):
        """Bandome inicializuoti su API raktu."""
        try:
            self.api_key = _get_novita_api_key_from_db()
            model_key = _get_novita_model_from_db()
            if model_key in NOVITA_MODELS:
                self.model_key = model_key
                self.model = NOVITA_MODELS[model_key]
            else:
                # Gal vartotojas įvedė pilną modelio pavadinimą
                self.model = model_key
                self.model_key = model_key

            if self.api_key:
                self.available = True
                logger.info(f"✅ Novita API key inicializuotas (modelis: {self.model})")
            else:
                logger.warning("Novita API raktas nenustatytas DB")
        except Exception as e:
            logger.warning(f"Novita API key inicializacija nepavyko: {e}")

    async def recognize(self, image_path: str) -> NovitaVisionResult:
        """Atpažįsta tekstą ir matematiką vaizde."""
        if not self.available:
            return NovitaVisionResult(text="", processing_time_ms=0)

        start = time.time()

        try:
            result = await self._recognize_api(image_path)
            processing_time = int((time.time() - start) * 1000)

            # Išparsuojame rezultatą
            text, latex, is_math = self._parse_response(result)

            logger.info(
                f"Novita OCR rezultatas: {len(text)} simbolių, {processing_time}ms"
            )

            return NovitaVisionResult(
                text=text,
                latex=latex,
                confidence=0.85 if text else 0.0,
                is_math=is_math,
                processing_time_ms=processing_time,
            )

        except Exception as e:
            logger.error(f"Novita Vision OCR klaida: {e}")
            return NovitaVisionResult(
                text=f"Klaida: {e}",
                processing_time_ms=int((time.time() - start) * 1000),
            )

    async def _recognize_api(self, image_path: str) -> str:
        """OCR naudojant Novita.ai API (OpenAI-suderinama)."""
        import httpx

        image_data = self._load_image_base64(image_path)
        if not image_data:
            return ""

        prompt = self._get_prompt()

        # Nustatome MIME tipą
        mime_type = "image/jpeg"
        if image_path.lower().endswith(".png"):
            mime_type = "image/png"
        elif image_path.lower().endswith(".gif"):
            mime_type = "image/gif"
        elif image_path.lower().endswith(".webp"):
            mime_type = "image/webp"

        # OpenAI-suderinama chat/completions užklausa
        url = f"{NOVITA_BASE_URL}/chat/completions"

        request_body = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_data}",
                                "detail": "high",
                            },
                        },
                    ],
                }
            ],
            "max_tokens": 8192,
            "temperature": 0.0,
        }

        # Thinking modeliui pridedame response_format
        if "thinking" not in self.model:
            request_body["response_format"] = {"type": "json_object"}

        logger.info(f"🔄 Kviečiamas Novita modelis: {self.model}")

        # Retry logika
        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(
                        url,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {self.api_key}",
                        },
                        json=request_body,
                    )

                    if response.status_code != 200:
                        error_text = response.text
                        logger.error(
                            f"Novita API klaida: {response.status_code} - {error_text}"
                        )
                        # Jei 429 (rate limit) - pabandome dar kartą
                        if response.status_code == 429 and attempt < max_retries - 1:
                            import asyncio

                            wait_time = 2**attempt  # 1s, 2s, 4s
                            logger.warning(
                                f"Rate limit, laukiame {wait_time}s (bandymas {attempt + 1}/{max_retries})"
                            )
                            await asyncio.sleep(wait_time)
                            continue
                        return ""

                    data = response.json()
                    choices = data.get("choices", [])
                    if choices:
                        message = choices[0].get("message", {})
                        content = message.get("content", "")

                        # Thinking modelis gali turėti reasoning_content
                        reasoning = message.get("reasoning_content", "")
                        if reasoning:
                            logger.debug(
                                f"Novita thinking: {len(reasoning)} simbolių reasoning"
                            )

                        logger.info(f"📡 Novita atsakymas: {len(content)} simbolių")
                        return content

                    logger.warning(
                        f"Novita grąžino tuščią atsakymą (bandymas {attempt + 1}/{max_retries})"
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
            except Exception as e:
                last_error = e
                logger.error(
                    f"Netikėta klaida (bandymas {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    import asyncio

                    await asyncio.sleep(1)
                    continue

        if last_error:
            raise last_error
        return ""

    def _get_prompt(self) -> str:
        """Grąžina OCR promptą (pritaikytas matematikos kontroliniams)."""
        return """Esi matematikos mokytojo asistentas. Tavo užduotis - skaitmenizuoti mokinio kontrolinį darbą iš nuotraukos.

=== KRITINĖ VIZUALINĖ ANALIZĖ ===

PRIEŠ skaitydamas, VIZUALIAI identifikuok TRI ZONAS:

1. **SPAUSDINTAS TEKSTAS** (Printed Zone):
   - Aiškus, vienodas šriftas
   - Užduočių numeriai: 1., 2., 3., a), b), c)
   - Užduočių sąlygos ir instrukcijos

2. **MOKINIO SPRENDIMAS** (Solution Zone):
   - Ranka rašytas tekstas HORIZONTALIOJE eilutėje
   - Lygybės: "= ... = ... = atsakymas"
   - Galutinis atsakymas po "=" arba "Ats."

3. **TRIUKŠMAS - IGNORUOK!** (Noise Zone):
   - VERTIKALŪS skaičiavimai stulpeliu (pvz. daugyba stulpeliu)
   - Skaičiai paraštėse
   - Braukymai, bandymai, juodraščiai
   - BET KOKIE skaičiai išdėstyti VIENAS PO KITO vertikaliai

=== STULPELINIŲ SKAIČIAVIMŲ IGNORAVIMAS ===

LABAI SVARBU! Mokinys dažnai atlieka TARPINIUS skaičiavimus STULPELIU šalia užduoties.
⚠️ TIE SKAIČIAI DEŠINĖJE YRA STULPELINIAI SKAIČIAVIMAI - IGNORUOK JUOS VISIŠKAI!

=== TRUPMENŲ ATPAŽINIMAS ===

Mišrios trupmenos: "4½" = 4.5, "3¾" = 3.75, "1¼" = 1.25
NEMAIŠYK šių trupmenų su stulpeliniais skaičiavimais!

=== JSON FORMATAS ===

Grąžink TIK JSON (be jokio papildomo teksto):

{
  "tasks": [
    {
      "number": "1a",
      "question_text": null,
      "student_work": "-52 * (-3/13) = 52 * 3/13 = 156/13 = 12",
      "final_answer": "12",
      "confidence": 0.95
    }
  ]
}

=== LAUKŲ PAAIŠKINIMAI ===

- **number**: PILNAS užduoties numeris (1a, 1b, 2a, 6, 7)
- **question_text**: TIK SPAUSDINTAS tekstas. Aritmetikai = null. Tekstiniams uždaviniams = pilnas sakinys.
- **student_work**: Mokinio HORIZONTALI lygybė. IGNORUOK stulpelinius skaičiavimus!
- **final_answer**: Galutinis atsakymas (po "=" arba "Ats.")
- **confidence**: PASITIKĖJIMO LYGIS nuo 0.0 iki 1.0

=== NUMERACIJOS TAISYKLĖS ===

- "1. Sudauginkite:" → 1a, 1b, 1c...
- "2. Padalykite:" → 2a, 2b, 2c...
- Tekstiniai uždaviniai: 6, 7, 8... (be raidės)

**SVARBU - TĘSTINĖ NUMERACIJA:**
Jei puslapio viršuje matai "c)", "d)", "e)" BE skaičiaus priekyje - tai yra ANKSTESNĖS užduoties tęsinys!

=== KRITINĖS TAISYKLĖS ===

1. NIEKADA netaisyk mokinio klaidų - jei parašyta "2+2=5", rašyk "2+2=5"
2. Jei neįskaitoma - rašyk "?"
3. Jei atsakymas neaiškus - final_answer = null
4. IGNORUOK VISUS VERTIKALIUS SKAIČIAVIMUS!
5. Nuskaityk ABSOLIUČIAI VISAS užduotis kurias matai!
6. Jei mokinys nepateikė sprendimo - rašyk student_work = "[Mokinys nepateikė sprendimo]"
7. **JOKIŲ DUBLIKATŲ** - kiekvienas užduoties numeris turi būti tik VIENĄ KARTĄ!

Dabar nuskaityk paveikslėlį ir grąžink JSON su VISOMIS UNIKALIOMIS užduotimis."""

    def _load_image_base64(self, image_path: str) -> Optional[str]:
        """Nuskaito vaizdą ir konvertuoja į base64."""
        try:
            path = Path(image_path)
            if not path.exists():
                logger.error(f"Vaizdas nerastas: {image_path}")
                return None
            with open(path, "rb") as f:
                return base64.standard_b64encode(f.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Vaizdo nuskaitymo klaida: {e}")
            return None

    def _parse_response(self, response: str) -> tuple[str, Optional[str], bool]:
        """Išparsuoja Novita atsakymą į tekstą ir LaTeX su post-processing valymu."""
        import json
        import re

        if not response:
            return "", None, False

        text = response
        latex = None
        is_math = False

        try:
            # Thinking modelis gali grąžinti <think>...</think> bloką prieš JSON
            clean_response = response
            think_match = re.search(r"<think>.*?</think>\s*", clean_response, re.DOTALL)
            if think_match:
                clean_response = clean_response[think_match.end() :]
                logger.debug(
                    f"Pašalintas thinking blokas ({think_match.end()} simbolių)"
                )

            # Ištraukiame JSON iš atsakymo
            json_match = re.search(r"```json\s*(.*?)\s*```", clean_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            elif clean_response.strip().startswith("{"):
                json_str = clean_response.strip()
            elif "tasks" in clean_response and "{" in clean_response:
                start_idx = clean_response.find("{")
                json_str = (
                    clean_response[start_idx:].strip() if start_idx != -1 else None
                )
            else:
                json_str = None

            if json_str:
                data = json.loads(json_str)
                tasks = data.get("tasks", [])

                if tasks:
                    # Pašaliname dublikatus
                    seen_numbers = set()
                    unique_tasks = []
                    for task in tasks:
                        raw_num = task.get("number", "")
                        num = re.sub(r"[\s\)\(\.\,]", "", str(raw_num)).lower().strip()

                        if num and num not in seen_numbers:
                            seen_numbers.add(num)
                            unique_tasks.append(task)
                        elif num:
                            logger.info(f"🗑️ Pašalintas dublikatas iš JSON: '{raw_num}'")
                        else:
                            unique_tasks.append(task)

                    original_count = len(tasks)
                    tasks = unique_tasks
                    if original_count != len(tasks):
                        logger.info(
                            f"✅ Dublikatai pašalinti: {original_count} -> {len(tasks)} užduočių"
                        )

                    text_lines = []
                    latex_lines = []

                    for task in tasks:
                        num = task.get("number", "").strip()
                        solution = task.get("student_work") or task.get("solution", "")
                        answer = task.get("final_answer") or task.get("answer")
                        question_text = task.get("question_text")
                        confidence = task.get("confidence", 0.5)

                        if solution == "?" or solution == "":
                            solution = "[Mokinys nepateikė sprendimo]"
                        else:
                            solution = self._clean_solution(solution)

                        # Formatuojame tekstą
                        if question_text:
                            if answer:
                                task_text = (
                                    f"{num}) {question_text} | {solution} Ats. {answer}"
                                )
                            else:
                                task_text = f"{num}) {question_text} | {solution}"
                        else:
                            if answer:
                                task_text = f"{num}) {solution} Ats. {answer}"
                            else:
                                task_text = f"{num}) {solution}"
                        text_lines.append(task_text)

                        # Formatuojame LaTeX
                        latex_solution = self._to_latex(solution)
                        conf_prefix = f"[conf:{confidence:.2f}]"
                        if answer and "Ats" not in solution:
                            latex_line = (
                                f"{conf_prefix}{num}) {latex_solution} Ats. {answer}"
                            )
                        else:
                            latex_line = f"{conf_prefix}{num}) {latex_solution}"
                        latex_lines.append(latex_line)

                    text = "\n".join(text_lines)
                    latex = "§§§".join(latex_lines)
                    is_math = True

                    # Pašaliname dublikatus iš LaTeX
                    latex = self._remove_duplicate_tasks(latex)

                    logger.info(
                        f"JSON parsuotas: {len(tasks)} užduočių, latex separatorius: §§§"
                    )
                    return text, latex, is_math

        except Exception as e:
            logger.debug(f"JSON parsavimas nepavyko: {e}")

        # Fallback
        math_indicators = ["=", "+", "-", "×", "÷", "*", "/"]
        is_math = any(ind in response for ind in math_indicators)
        return text, None, is_math

    def _clean_solution(self, text: str) -> str:
        """Valo mokinio sprendimo tekstą."""
        import re

        if not text or len(text) < 3:
            return text

        # Pašaliname inline dublikatus
        def normalize(s: str) -> str:
            s = s.replace("·", "*").replace("×", "*").replace("⋅", "*")
            s = s.replace("÷", "/").replace(":", "/")
            s = s.replace("−", "-").replace("–", "-")
            s = re.sub(r"\s+", "", s)
            return s.lower()

        normalized = normalize(text)
        text_len = len(normalized)

        for split_point in range(text_len // 2 - 5, text_len // 2 + 10):
            if split_point <= 0 or split_point >= text_len:
                continue
            first_half = normalized[:split_point]
            second_half = normalized[split_point:]
            min_len = min(len(first_half), len(second_half))
            if min_len < 5:
                continue
            common_start = 0
            for i in range(min(20, min_len)):
                if first_half[i] == second_half[i]:
                    common_start = i + 1
                else:
                    break
            if common_start >= 10:
                for i in range(len(text) // 2 - 10, len(text) // 2 + 20):
                    if i <= 0 or i >= len(text):
                        continue
                    first_part = text[:i]
                    second_part = text[i:]
                    first_norm = normalize(first_part)
                    second_norm = normalize(second_part)
                    if len(second_norm) >= 10 and len(first_norm) >= 10:
                        if first_norm[:10] == second_norm[:10]:
                            return first_part.strip()

        return text

    def _to_latex(self, text: str) -> str:
        """Konvertuoja tekstą į LaTeX formatą."""
        import re

        if not text:
            return ""

        text = text.replace("*", " \\cdot ")
        text = text.replace("×", " \\cdot ")
        text = text.replace("·", " \\cdot ")
        text = text.replace(":", " \\div ")
        text = text.replace("÷", " \\div ")
        text = re.sub(r"(\d+)/(\d+)", r"\\frac{\1}{\2}", text)

        return text

    def _remove_duplicate_tasks(self, latex: str) -> str:
        """Pašalina dublikuotus uždavinius iš LaTeX string."""
        import re

        if not latex or "§§§" not in latex:
            return latex

        lines = latex.split("§§§")
        seen_ids = set()
        unique_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Pašaliname confidence prefix prieš tikrinti ID
            clean_line = re.sub(r"^\[conf:\d+\.\d+\]", "", line).strip()
            id_match = re.match(r"^\s*(\d+[a-z]?)\)", clean_line, re.IGNORECASE)
            if id_match:
                task_id = id_match.group(1).lower()
                if task_id not in seen_ids:
                    seen_ids.add(task_id)
                    unique_lines.append(line)
                else:
                    logger.debug(f"Pašalintas dublikatas: {task_id}")
            else:
                unique_lines.append(line)

        return "§§§".join(unique_lines)


# Singleton instance
_novita_vision: Optional[NovitaVisionClient] = None


def get_novita_vision_client() -> NovitaVisionClient:
    """Grąžina NovitaVisionClient singleton instanciją."""
    global _novita_vision
    if _novita_vision is None:
        _novita_vision = NovitaVisionClient()
    return _novita_vision


def reset_novita_vision_client():
    """Perkrauna Novita Vision klientą."""
    global _novita_vision
    _novita_vision = None
    logger.info("🔄 Novita Vision klientas perkrautas")
