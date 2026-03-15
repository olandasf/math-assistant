"""
OpenAI GPT Vision OCR servisas.
Naudoja OpenAI GPT-5.2 (arba kitus modelius) su vision galimybėmis matematikos ir teksto atpažinimui.
"""

import base64
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from config import BASE_DIR
from loguru import logger


def _get_openai_api_key_from_db() -> Optional[str]:
    """Gauti OpenAI API raktą iš duomenų bazės."""
    try:
        db_path = BASE_DIR / "database" / "math_teacher.db"
        if not db_path.exists():
            return None
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'openai_api_key'")
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception as e:
        logger.warning(f"Nepavyko nuskaityti OpenAI API rakto iš DB: {e}")
    return None


def _get_openai_model_from_db() -> str:
    """Gauti OpenAI modelio pavadinimą iš duomenų bazės."""
    try:
        db_path = BASE_DIR / "database" / "math_teacher.db"
        if not db_path.exists():
            return "gpt-5.2"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'openai_model'")
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception as e:
        logger.warning(f"Nepavyko nuskaityti OpenAI modelio iš DB: {e}")
    return "gpt-5.2"


@dataclass
class OpenAIVisionResult:
    """OpenAI Vision OCR rezultatas."""

    text: str
    latex: Optional[str] = None
    confidence: float = 0.85
    is_math: bool = False
    processing_time_ms: int = 0


class OpenAIVisionClient:
    """OpenAI GPT Vision API klientas OCR tikslams."""

    DEFAULT_MODEL = "gpt-5.2"  # Pigesnis variantas (ne Pro)

    def __init__(self):
        """Inicializuoja OpenAI Vision klientą."""
        self.available = False
        self.api_key = None
        self.model = self.DEFAULT_MODEL

        self._try_api_key()

    def _try_api_key(self):
        """Bandome inicializuoti su API raktu."""
        try:
            self.api_key = _get_openai_api_key_from_db()
            self.model = _get_openai_model_from_db()
            if self.api_key:
                self.available = True
                logger.info(f"✅ OpenAI API key inicializuotas (modelis: {self.model})")
            else:
                logger.warning("OpenAI API raktas nenustatytas DB")
        except Exception as e:
            logger.warning(f"OpenAI API key inicializacija nepavyko: {e}")

    async def recognize(self, image_path: str) -> OpenAIVisionResult:
        """Atpažįsta tekstą ir matematiką vaizde."""
        if not self.available:
            return OpenAIVisionResult(text="", processing_time_ms=0)

        start = time.time()

        try:
            result = await self._recognize_api(image_path)
            processing_time = int((time.time() - start) * 1000)

            # Išparsuojame rezultatą
            text, latex, is_math = self._parse_response(result)

            logger.info(
                f"OpenAI OCR rezultatas: {len(text)} simbolių, {processing_time}ms"
            )

            return OpenAIVisionResult(
                text=text,
                latex=latex,
                confidence=0.85 if text else 0.0,
                is_math=is_math,
                processing_time_ms=processing_time,
            )

        except Exception as e:
            logger.error(f"OpenAI Vision OCR klaida: {e}")
            return OpenAIVisionResult(
                text=f"Klaida: {e}",
                processing_time_ms=int((time.time() - start) * 1000),
            )

    async def _recognize_api(self, image_path: str) -> str:
        """OCR naudojant OpenAI API."""
        import httpx

        image_data = self._load_image_base64(image_path)
        if not image_data:
            logger.error(f"❌ OpenAI: Nepavyko užkrauti vaizdo: {image_path}")
            return ""
        logger.info(f"📷 OpenAI: Vaizdas užkrautas, base64 ilgis: {len(image_data)} simbolių")

        prompt = self._get_prompt()

        url = "https://api.openai.com/v1/chat/completions"

        # Pagal OpenAI API docs: image_url eina prieš text
        request_body = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}",
                                "detail": "low",
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            "max_completion_tokens": 4096,
            "temperature": 0.0,
        }

        logger.info(f"🔄 Kviečiamas OpenAI modelis: {self.model}")

        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
                json=request_body,
            )

            logger.info(f"📡 OpenAI HTTP status: {response.status_code}")
            if response.status_code != 200:
                error_text = response.text[:500]
                logger.error(
                    f"OpenAI API klaida: {response.status_code} - {error_text}"
                )
                return f"API klaida {response.status_code}: {error_text}"

            data = response.json()
            logger.info(f"📡 OpenAI response keys: {list(data.keys())}")
            choices = data.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                content = message.get("content", "")
                finish_reason = choices[0].get("finish_reason", "unknown")
                logger.info(
                    f"📡 OpenAI atsakymas: {len(content)} simbolių, "
                    f"finish_reason={finish_reason}, "
                    f"preview: {content[:200] if content else 'TUŠČIA'}"
                )
                if content:
                    return content
                else:
                    return f"Klaida: OpenAI grąžino tuščią atsakymą (finish_reason={finish_reason})"
            else:
                logger.error(f"📡 OpenAI: choices tuščias! Full: {str(data)[:500]}")
                return f"Klaida: OpenAI response neturi choices. Response: {str(data)[:300]}"

    def _get_prompt(self) -> str:
        """Grąžina OCR promptą (tas pats kaip Gemini)."""
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

=== JSON FORMATAS ===

Grąžink TIK JSON (be jokio papildomo teksto):

{
  "tasks": [
    {
      "number": "1a",
      "question_text": null,
      "student_work": "-52 * (-3/13) = 52 * 3/13 = 156/13 = 12",
      "final_answer": "12"
    },
    {
      "number": "7",
      "question_text": "Stačiakampio ilgis yra 4½ cm, o plotis lygus ¼ stačiakampio ilgio. Apskaičiuokite stačiakampio perimetrą ir plotą.",
      "student_work": "plotis = 4.5 / 4 = 1.125; P = (4.5 + 1.125) * 2 = 11.25",
      "final_answer": "P = 11.25 cm, S = 5.0625 cm²"
    }
  ]
}

=== LAUKŲ PAAIŠKINIMAI ===

- **number**: PILNAS užduoties numeris (1a, 1b, 2a, 6, 7)
- **question_text**: TIK SPAUSDINTAS tekstas. Aritmetikai = null. Tekstiniams uždaviniams = pilnas sakinys.
- **student_work**: Mokinio HORIZONTALI lygybė. IGNORUOK stulpelinius skaičiavimus!
- **final_answer**: Galutinis atsakymas (po "=" arba "Ats.")

=== NUMERACIJOS TAISYKLĖS ===

- "1. Sudauginkite:" → 1a, 1b, 1c...
- "2. Padalykite:" → 2a, 2b, 2c...
- "5. Apskaičiuokite:" → 5a, 5b, 5c, 5d, 5e...
- Tekstiniai uždaviniai: 6, 7, 8... (be raidės)

**SVARBU - TĘSTINĖ NUMERACIJA:**
Jei puslapio viršuje matai "c)", "d)", "e)" BE skaičiaus priekyje - tai yra ANKSTESNĖS užduoties tęsinys!

=== KRITINĖS TAISYKLĖS ===

1. NIEKADA netaisyk mokinio klaidų - jei parašyta "2+2=5", rašyk "2+2=5"
2. Jei neįskaitoma - rašyk "?"
3. Jei atsakymas neaiškus - final_answer = null
4. IGNORUOK VISUS VERTIKALIUS SKAIČIAVIMUS!
5. **SVARBU**: Nuskaityk ABSOLIUČIAI VISAS užduotis kurias matai!
6. Jei mokinys nepateikė sprendimo - rašyk student_work = "[Mokinys nepateikė sprendimo]"

=== ⚠️ KRITIŠKAI SVARBU - JOKIŲ DUBLIKATŲ! ===

**KIEKVIENAS UŽDUOTIES NUMERIS TURI BŪTI TIK VIENĄ KARTĄ!**

❌ NEGERAI (dublikatas):
```json
{"tasks": [
  {"number": "1b", "student_work": "23*(-16)=-368", "final_answer": "-368"},
  {"number": "1b", "student_work": "23·(-16)=-368", "final_answer": "-368"}
]}
```

✅ GERAI (be dublikatų):
```json
{"tasks": [
  {"number": "1b", "student_work": "23*(-16)=-368", "final_answer": "-368"}
]}
```

Jei matai tą pačią užduotį parašytą dviem būdais - PASIRINK TIK VIENĄ!

Dabar nuskaityk paveikslėlį ir grąžink JSON su VISOMIS UNIKALIOMIS užduotimis (be dublikatų)."""

    def _load_image_base64(self, image_path: str) -> Optional[str]:
        """Nuskaito vaizdą ir konvertuoja į JPEG base64."""
        try:
            path = Path(image_path)
            if not path.exists():
                logger.error(f"Vaizdas nerastas: {image_path}")
                return None
            # Konvertuojame per PIL į JPEG (užtikrina teisingą formatą visoms API)
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

    def _parse_response(self, response: str) -> tuple[str, Optional[str], bool]:
        """Išparsuoja OpenAI atsakymą į tekstą ir LaTeX."""
        import json
        import re

        if not response:
            return "", None, False

        text = response
        latex = None
        is_math = False

        try:
            # Ištraukiame JSON iš atsakymo
            json_match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            elif response.strip().startswith("{"):
                json_str = response.strip()
            else:
                json_str = None

            if json_str:
                data = json.loads(json_str)
                tasks = data.get("tasks", [])

                if tasks:
                    # PIRMA: Pašaliname dublikatus iš tasks pagal numerį
                    # Normalizuojame numerį - pašaliname tarpus, skliaustus ir konvertuojame į lowercase
                    seen_numbers = set()
                    unique_tasks = []
                    for task in tasks:
                        raw_num = task.get("number", "")
                        # Normalizuojame: pašaliname tarpus, skliaustus, konvertuojame į lowercase
                        num = re.sub(r"[\s\)\(]", "", str(raw_num)).lower()
                        if num and num not in seen_numbers:
                            seen_numbers.add(num)
                            unique_tasks.append(task)
                        elif num:
                            logger.info(
                                f"🗑️ Pašalintas dublikatas iš JSON: '{raw_num}' (normalizuotas: '{num}')"
                            )
                        else:
                            # Jei nėra numerio, pridedame
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

                        if solution == "?" or solution == "":
                            solution = "[Mokinys nepateikė sprendimo]"
                        else:
                            # Pašaliname inline dublikatus iš solution
                            solution = self._remove_inline_content_duplicates(solution)

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
                        if answer and "Ats" not in solution:
                            latex_line = f"{num}) {latex_solution} Ats. {answer}"
                        else:
                            latex_line = f"{num}) {latex_solution}"
                        latex_lines.append(latex_line)

                    text = "\n".join(text_lines)
                    latex = "§§§".join(latex_lines)
                    is_math = True

                    # Pašaliname dublikatus iš LaTeX
                    latex = self._remove_duplicate_tasks(latex)

                    logger.info(f"JSON parsuotas: {len(tasks)} užduočių")
                    return text, latex, is_math

        except Exception as e:
            logger.debug(f"JSON parsavimas nepavyko: {e}")

        # Fallback
        math_indicators = ["=", "+", "-", "×", "÷", "*", "/"]
        is_math = any(ind in response for ind in math_indicators)
        return text, None, is_math

    def _remove_inline_content_duplicates(self, text: str) -> str:
        """
        Pašalina inline turinio dublikatus iš student_work.
        Pvz: "23*(-16)=-368 23·(-16)=-368" -> "23*(-16)=-368"
        """
        import re

        if not text or len(text) < 10:
            return text

        def normalize_for_comparison(s: str) -> str:
            s = s.replace("·", "*").replace("×", "*").replace("⋅", "*")
            s = s.replace("÷", "/").replace(":", "/")
            s = s.replace("−", "-").replace("–", "-")
            s = re.sub(r"\s+", "", s)
            return s.lower()

        normalized = normalize_for_comparison(text)
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

                    first_norm = normalize_for_comparison(first_part)
                    second_norm = normalize_for_comparison(second_part)

                    if len(second_norm) >= 10 and len(first_norm) >= 10:
                        if first_norm[:10] == second_norm[:10]:
                            logger.info(
                                f"🗑️ Pašalintas turinio dublikatas: '{text[i:i+30]}...'"
                            )
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

        if not latex:
            return latex

        # Pirma skaidome pagal §§§ separatorių
        if "§§§" in latex:
            lines = latex.split("§§§")
            seen_ids = set()
            unique_lines = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Ištraukiame užduoties ID (pvz. "1a)", "1b)", "2a)")
                id_match = re.match(r"^\s*(\d+[a-z]?)\)", line, re.IGNORECASE)
                if id_match:
                    task_id = id_match.group(1).lower()
                    if task_id not in seen_ids:
                        seen_ids.add(task_id)
                        unique_lines.append(line)
                    else:
                        logger.debug(f"Pašalintas dublikatas: {task_id}")
                else:
                    # Jei nėra ID, tiesiog pridedame
                    unique_lines.append(line)

            result = "§§§".join(unique_lines)
            logger.info(
                f"Dublikatų šalinimas: {len(lines)} -> {len(unique_lines)} eilučių"
            )
            return result

        # Jei nėra separatoriaus, bandome pašalinti inline dublikatus
        task_pattern = re.compile(r"(\d+[a-z]?)\)", re.IGNORECASE)
        matches = list(task_pattern.finditer(latex))

        if len(matches) <= 1:
            return latex

        # Grupuojame pagal task ID
        task_occurrences = {}
        for match in matches:
            task_id = match.group(1).lower()
            if task_id not in task_occurrences:
                task_occurrences[task_id] = []
            task_occurrences[task_id].append(match.start())

        # Jei yra dublikatų, pašaliname juos
        parts_to_remove = []
        for task_id, positions in task_occurrences.items():
            if len(positions) > 1:
                logger.info(
                    f"Rastas inline dublikatas: {task_id} ({len(positions)} kartai)"
                )
                for i in range(1, len(positions)):
                    start_pos = positions[i]
                    next_match = None
                    for m in matches:
                        if m.start() > start_pos:
                            next_match = m
                            break
                    end_pos = next_match.start() if next_match else len(latex)
                    parts_to_remove.append((start_pos, end_pos))

        if parts_to_remove:
            parts_to_remove.sort(key=lambda x: x[0], reverse=True)
            result = latex
            for start, end in parts_to_remove:
                result = result[:start] + result[end:]
            logger.info(f"Pašalinta {len(parts_to_remove)} inline dublikatų")
            return result

        return latex


# Singleton instance
_openai_vision: Optional[OpenAIVisionClient] = None


def get_openai_vision_client() -> OpenAIVisionClient:
    """Grąžina OpenAIVisionClient singleton instanciją."""
    global _openai_vision
    if _openai_vision is None:
        _openai_vision = OpenAIVisionClient()
    return _openai_vision
