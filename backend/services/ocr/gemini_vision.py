"""
Gemini Vision OCR servisas.
Naudoja Google Gemini API (Vertex AI arba Generative Language API) matematikos ir teksto atpažinimui.
"""

import base64
import os
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from config import BASE_DIR
from loguru import logger


def _get_gemini_api_key_from_db() -> Optional[str]:
    """Gauti Gemini API raktą iš duomenų bazės."""
    try:
        db_path = BASE_DIR / "database" / "math_teacher.db"
        if not db_path.exists():
            return None
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'gemini_api_key'")
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception as e:
        logger.warning(f"Nepavyko nuskaityti Gemini API rakto iš DB: {e}")
    return None


@dataclass
class GeminiVisionResult:
    """Gemini Vision OCR rezultatas."""

    text: str
    latex: Optional[str] = None
    confidence: float = 0.85
    is_math: bool = False
    processing_time_ms: int = 0


class GeminiVisionClient:
    """Gemini Vision API klientas OCR tikslams - palaiko Vertex AI ir Generative Language API."""

    # Modeliai pagal prioritetą
    # gemini-3-flash-preview - greitas Gemini 3 modelis
    VERTEX_AI_MODEL = "gemini-3-flash-preview"  # Greitas Vertex AI modelis
    FALLBACK_MODEL = "gemini-2.0-flash"  # Fallback API key režimui (stabilus modelis)

    # Google Cloud projekto ID (iš credentials arba env)
    PROJECT_ID = "mtematika-471410"
    # gemini-3-flash-preview pasiekiamas su global endpoint
    LOCATION = "global"

    def __init__(self):
        """Inicializuoja Gemini Vision klientą."""
        self.available = False
        self.api_key = None
        self.use_vertex_ai = False
        self.genai_client = None
        self.model = self.FALLBACK_MODEL

        # Pirma bandome Vertex AI su credentials
        self._try_vertex_ai()

        # Jei Vertex AI neveikia, bandome API key
        if not self.available:
            self._try_api_key()

    def _try_vertex_ai(self):
        """Bandome inicializuoti Vertex AI su Google Cloud credentials."""
        try:
            # Ieškome credentials failo
            credentials_paths = [
                BASE_DIR
                / "backend"
                / "google_credentials.json",  # Įkeltas per Settings
                BASE_DIR / "backend" / "mtematika-471410-e4cb6af744ea.json",
                BASE_DIR / "backend" / "credentials.json",
                BASE_DIR / "credentials.json",
                Path(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")),
            ]

            credentials_path = None
            for path in credentials_paths:
                if path and path.exists():
                    credentials_path = path
                    logger.info(f"🔍 Rastas credentials failas: {path}")
                    break

            if not credentials_path:
                logger.info(
                    "Google Cloud credentials failas nerastas, bandysime API key"
                )
                return

            # Nustatome GOOGLE_APPLICATION_CREDENTIALS
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)

            from google import genai

            # Inicializuojame Vertex AI klientą
            self.genai_client = genai.Client(
                vertexai=True,
                project=self.PROJECT_ID,
                location=self.LOCATION,
            )

            self.use_vertex_ai = True
            self.available = True
            self.model = self.VERTEX_AI_MODEL
            logger.info(
                f"✅ Vertex AI inicializuotas (modelis: {self.model}, projektas: {self.PROJECT_ID})"
            )

        except Exception as e:
            logger.warning(f"Vertex AI inicializacija nepavyko: {e}")
            self.use_vertex_ai = False

    def _try_api_key(self):
        """Bandome inicializuoti su API raktu."""
        try:
            self.api_key = _get_gemini_api_key_from_db()
            if self.api_key:
                self.available = True
                self.model = self.FALLBACK_MODEL
                logger.info(f"✅ Gemini API key inicializuotas (modelis: {self.model})")
            else:
                logger.warning("Gemini API raktas nenustatytas DB")
        except Exception as e:
            logger.warning(f"API key inicializacija nepavyko: {e}")

    async def recognize(self, image_path: str) -> GeminiVisionResult:
        """Atpažįsta tekstą ir matematiką vaizde."""
        if not self.available:
            return GeminiVisionResult(text="", processing_time_ms=0)

        start = time.time()

        try:
            if self.use_vertex_ai:
                result = await self._recognize_vertex_ai(image_path)
            else:
                result = await self._recognize_api_key(image_path)

            processing_time = int((time.time() - start) * 1000)

            # Išparsuojame rezultatą
            text, latex, is_math = self._parse_response(result)

            logger.info(
                f"Gemini OCR rezultatas: {len(text)} simbolių, {processing_time}ms"
            )

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
        """OCR naudojant Vertex AI."""
        import asyncio

        from google.genai import types

        # Nuskaitome vaizdą
        image_bytes = Path(image_path).read_bytes()

        # Nustatome MIME tipą
        mime_type = "image/jpeg"
        if image_path.lower().endswith(".png"):
            mime_type = "image/png"
        elif image_path.lower().endswith(".gif"):
            mime_type = "image/gif"
        elif image_path.lower().endswith(".webp"):
            mime_type = "image/webp"

        prompt = self._get_prompt()

        logger.info(f"🔄 Kviečiamas Vertex AI modelis: {self.model}")

        # Sinchroninis kvietimas - paleidžiame thread pool'e kad neblokuotų event loop
        def _call_vertex_ai():
            return self.genai_client.models.generate_content(
                model=self.model,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=prompt),
                            types.Part.from_bytes(
                                data=image_bytes, mime_type=mime_type
                            ),
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
            # Fallback: bandome be response_mime_type
            logger.info("🔄 Bandome Vertex AI be response_mime_type...")

            def _call_vertex_ai_fallback():
                return self.genai_client.models.generate_content(
                    model=self.model,
                    contents=[
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_text(text=prompt),
                                types.Part.from_bytes(
                                    data=image_bytes, mime_type=mime_type
                                ),
                            ],
                        )
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                        max_output_tokens=8192,
                    ),
                )

            response = await asyncio.to_thread(_call_vertex_ai_fallback)

        # Detalus loginimas
        logger.info(
            f"📡 Vertex AI response object: candidates={len(response.candidates) if response.candidates else 0}"
        )
        if response.candidates:
            for i, candidate in enumerate(response.candidates):
                logger.info(
                    f"  Candidate {i}: finish_reason={candidate.finish_reason}, "
                    f"content_parts={len(candidate.content.parts) if candidate.content and candidate.content.parts else 0}"
                )
                if candidate.content and candidate.content.parts:
                    for j, part in enumerate(candidate.content.parts):
                        part_text = (
                            part.text if hasattr(part, "text") and part.text else ""
                        )
                        logger.info(
                            f"    Part {j}: thought={getattr(part, 'thought', None)}, "
                            f"text_len={len(part_text)}, first_100={part_text[:100] if part_text else 'EMPTY'}"
                        )
        else:
            logger.warning(
                f"📡 Vertex AI: NO candidates! prompt_feedback={getattr(response, 'prompt_feedback', None)}"
            )

        # Iš pradžių bandome response.text
        result = ""
        try:
            result = response.text if response.text else ""
        except Exception as e:
            logger.warning(f"📡 response.text klaida: {e}")

        logger.info(f"📡 Vertex AI atsakymas: {len(result)} simbolių")

        # Jei tuščias - bandome surinkti iš visų parts (ignoruojant thought parts)
        if not result and response.candidates:
            for candidate in response.candidates:
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if (
                            hasattr(part, "text")
                            and part.text
                            and not getattr(part, "thought", False)
                        ):
                            result = part.text
                            logger.info(
                                f"📡 Rastas tekstas iš part: {len(result)} simbolių"
                            )
                            break

        return result

    async def _recognize_api_key(self, image_path: str) -> str:
        """OCR naudojant API key (senas metodas)."""
        import httpx

        image_data = self._load_image_base64(image_path)
        if not image_data:
            return ""

        prompt = self._get_prompt()

        # Nustatome MIME tipą
        mime_type = "image/jpeg"
        if image_data.startswith("iVBOR"):
            mime_type = "image/png"
        elif image_data.startswith("R0lGOD"):
            mime_type = "image/gif"
        elif image_data.startswith("UklGR"):
            mime_type = "image/webp"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

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

        # Retry logika - bandome iki 3 kartų su cold start problema
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
                        logger.error(
                            f"Gemini API klaida: {response.status_code} - {response.text}"
                        )
                        return ""

                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            result = parts[0].get("text", "")
                            if result:
                                return result

                    logger.warning(
                        f"Gemini grąžino tuščią atsakymą (bandymas {attempt + 1}/{max_retries})"
                    )

            except httpx.ConnectError as e:
                last_error = e
                logger.warning(
                    f"Tinklo klaida (bandymas {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    import asyncio

                    await asyncio.sleep(1)  # Palaukiam 1 sekundę prieš kitą bandymą
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
        """Grąžina OCR promptą."""
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

LABAI SVARBU! Mokinys dažnai atlieka TARPINIUS skaičiavimus STULPELIU šalia užduoties:

```
"Stačiakampio ilgis yra 4½ cm..."    45
                                     x11
                                     ---
                                     495
```

⚠️ TIE SKAIČIAI DEŠINĖJE (45, x11, 495) YRA STULPELINIAI SKAIČIAVIMAI!
⚠️ JIE NĖRA UŽDUOTIES TEKSTO DALIS!
⚠️ IGNORUOK JUOS VISIŠKAI!

Teisingas rezultatas: "Stačiakampio ilgis yra 4½ cm..." (BE 45, 11, 495)

=== TRUPMENŲ ATPAŽINIMAS ===

Mišrios trupmenos spausdintame tekste:
- "4½" arba "4 1/2" = keturi su puse (4.5)
- "3¾" arba "3 3/4" = trys ir trys ketvirtos (3.75)
- "1¼" arba "1 1/4" = vienas ir vienas ketvirtis (1.25)

NEMAIŠYK šių trupmenų su šalia esančiais stulpeliniais skaičiavimais!

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
    },
    {
      "number": "4a",
      "question_text": null,
      "student_work": "[Mokinys nepateikė sprendimo]",
      "final_answer": null,
      "confidence": 0.90
    },
    {
      "number": "3b",
      "question_text": null,
      "student_work": "?/? * ?/? = ?",
      "final_answer": "?",
      "confidence": 0.30
    }
  ]
}

=== LAUKŲ PAAIŠKINIMAI ===

- **number**: PILNAS užduoties numeris (1a, 1b, 2a, 6, 7)
- **question_text**: TIK SPAUSDINTAS tekstas. Aritmetikai = null. Tekstiniams uždaviniams = pilnas sakinys.
- **student_work**: Mokinio HORIZONTALI lygybė. IGNORUOK stulpelinius skaičiavimus!
- **final_answer**: Galutinis atsakymas (po "=" arba "Ats.")
- **confidence**: PASITIKĖJIMO LYGIS nuo 0.0 iki 1.0:
  - **0.9-1.0**: Labai aiškiai įskaitoma, tikrai teisingai atpažinta
  - **0.7-0.9**: Gerai įskaitoma, greičiausiai teisinga
  - **0.5-0.7**: Vidutiniškai įskaitoma, gali būti klaidų
  - **0.3-0.5**: Sunkiai įskaitoma, daug neaiškumų
  - **0.0-0.3**: Beveik neįskaitoma, spėjimas

=== NUMERACIJOS TAISYKLĖS ===

- "1. Sudauginkite:" → 1a, 1b, 1c...
- "2. Padalykite:" → 2a, 2b, 2c...
- "5. Apskaičiuokite:" → 5a, 5b, 5c, 5d, 5e...
- Tekstiniai uždaviniai: 6, 7, 8... (be raidės)

**SVARBU - TĘSTINĖ NUMERACIJA:**
Jei puslapio viršuje matai "c)", "d)", "e)" BE skaičiaus priekyje - tai yra ANKSTESNĖS užduoties tęsinys!
Pavyzdžiui:
- Jei ankstesnis puslapis baigėsi "5b)", tai "c)" = "5c", "d)" = "5d", "e)" = "5e"
- Jei matai tik raides be skaičių, naudok paskutinį žinomą užduoties numerį

=== KRITINĖS TAISYKLĖS ===

1. NIEKADA netaisyk mokinio klaidų - jei parašyta "2+2=5", rašyk "2+2=5"
2. Jei neįskaitoma - rašyk "?"
3. Jei atsakymas neaiškus - final_answer = null
4. IGNORUOK VISUS VERTIKALIUS SKAIČIAVIMUS!
5. **SVARBU**: Nuskaityk ABSOLIUČIAI VISAS užduotis kurias matai! Gali būti 5, 10, 15, 20 ar daugiau užduočių. NIEKADA nepraleisk užduočių!
6. Tekstiniuose uždaviniuose ATKURK pilną spausdintą sakinį, NEMAIŠYK su stulpeliniais skaičiais!
7. Jei mokinys nepateikė sprendimo - rašyk student_work = "[Mokinys nepateikė sprendimo]"
8. Jei matai "c)", "d)", "e)" puslapio viršuje be skaičiaus - tai yra 5c, 5d, 5e (arba ankstesnės užduoties tęsinys)

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

Jei matai tą pačią užduotį parašytą dviem būdais (pvz. su Unicode ir LaTeX simboliais) -
PASIRINK TIK VIENĄ ir NEGRĄŽINK DUBLIKATO!

Dabar nuskaityk paveikslėlį ir grąžink JSON su VISOMIS UNIKALIOMIS užduotimis (be dublikatų)."""

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
        """Išparsuoja Gemini atsakymą į tekstą ir LaTeX su post-processing valymu."""
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
            elif "tasks" in response and "{" in response:
                start_idx = response.find("{")
                json_str = response[start_idx:].strip() if start_idx != -1 else None
            else:
                json_str = None

            if json_str:
                data = json.loads(json_str)
                tasks = data.get("tasks", [])

                if tasks:
                    # PIRMA: Pašaliname dublikatus iš tasks pagal numerį
                    # Normalizuojame numerį - pašaliname tarpus ir konvertuojame į lowercase
                    seen_numbers = set()
                    unique_tasks = []
                    for task in tasks:
                        raw_num = task.get("number", "")
                        # Normalizuojame: pašaliname tarpus, skliaustus, taškus, konvertuojame į lowercase
                        num = re.sub(r"[\s\)\(\.\,]", "", str(raw_num)).lower().strip()

                        # DEBUG: Loginti kiekvieną numerį
                        logger.debug(
                            f"Task number: raw='{raw_num}', normalized='{num}', seen={num in seen_numbers}"
                        )

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
                    else:
                        logger.info(
                            f"ℹ️ Dublikatų nerasta JSON lygmenyje ({len(tasks)} užduočių)"
                        )

                    text_lines = []
                    latex_lines = []

                    for task in tasks:
                        num = task.get("number", "").strip()
                        solution = task.get("student_work") or task.get("solution", "")
                        answer = task.get("final_answer") or task.get("answer")
                        question_text = task.get("question_text")
                        confidence = task.get("confidence", 0.5)  # Default 0.5 jei nėra

                        # POST-PROCESSING: Valome lietuvišką tekstą
                        if solution == "?" or solution == "":
                            solution = "[Mokinys nepateikė sprendimo]"
                        else:
                            solution = self._clean_lithuanian_text(solution)
                            # Pašaliname inline dublikatus iš solution
                            solution = self._remove_inline_content_duplicates(solution)

                        if question_text:
                            question_text = self._clean_lithuanian_text(question_text)

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

                        # Formatuojame LaTeX - naudojame KaTeX suderinamą formatą
                        # Pridedame užduoties numerį kad parse_latex_tasks galėtų išparsuoti
                        latex_solution = self._to_latex(solution)
                        # Pridedame confidence kaip komentarą LaTeX eilutės pradžioje: [conf:0.85]
                        conf_prefix = f"[conf:{confidence:.2f}]"
                        # Jei solution jau turi "Ats." - nepridedame dar kartą
                        if answer and "Ats" not in solution:
                            latex_line = (
                                f"{conf_prefix}{num}) {latex_solution} Ats. {answer}"
                            )
                        else:
                            latex_line = f"{conf_prefix}{num}) {latex_solution}"
                        latex_lines.append(latex_line)

                    text = "\n".join(text_lines)
                    # Naudojame UNIKALU separatorių "§§§" kurį tikrai niekas nenaudoja
                    latex = "§§§".join(latex_lines)
                    is_math = True

                    # Pašaliname dublikatus iš LaTeX (kai Gemini grąžina tą patį uždavinį kelis kartus)
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

    def _remove_inline_content_duplicates(self, text: str) -> str:
        """
        Pašalina inline turinio dublikatus iš student_work.
        Pvz: "23*(-16)=-368 23·(-16)=-368" -> "23*(-16)=-368"

        AI kartais grąžina tą patį sprendimą du kartus su skirtingais simboliais.
        """
        import re

        if not text or len(text) < 10:
            return text

        # Normalizuojame tekstą palyginimui (pakeičiame visus math simbolius į vienodus)
        def normalize_for_comparison(s: str) -> str:
            s = s.replace("·", "*").replace("×", "*").replace("⋅", "*")
            s = s.replace("÷", "/").replace(":", "/")
            s = s.replace("−", "-").replace("–", "-")
            s = re.sub(r"\s+", "", s)  # Pašaliname tarpus
            return s.lower()

        normalized = normalize_for_comparison(text)
        text_len = len(normalized)

        # Tikriname ar tekstas yra dubliuotas (pirma pusė = antra pusė)
        # Leidžiame nedidelį skirtumą dėl "Ats." ir pan.
        for split_point in range(text_len // 2 - 5, text_len // 2 + 10):
            if split_point <= 0 or split_point >= text_len:
                continue

            first_half = normalized[:split_point]
            second_half = normalized[split_point:]

            # Tikriname ar antra pusė prasideda panašiai kaip pirma
            # (nes gali būti "Ats.-368" pabaigoje)
            min_len = min(len(first_half), len(second_half))
            if min_len < 5:
                continue

            # Ieškome bendro pradžios fragmento
            common_start = 0
            for i in range(min(20, min_len)):
                if first_half[i] == second_half[i]:
                    common_start = i + 1
                else:
                    break

            # Jei bent 10 simbolių sutampa pradžioje - tai dublikatas
            if common_start >= 10:
                # Randame tikrą padalinimo tašką originaliame tekste
                # Ieškome kur prasideda dublikatas
                original_normalized = normalize_for_comparison(text)

                # Bandome rasti dublikato pradžią originaliame tekste
                # Ieškome pattern'o kuris kartojasi
                for i in range(len(text) // 2 - 10, len(text) // 2 + 20):
                    if i <= 0 or i >= len(text):
                        continue

                    first_part = text[:i]
                    second_part = text[i:]

                    first_norm = normalize_for_comparison(first_part)
                    second_norm = normalize_for_comparison(second_part)

                    # Tikriname ar second_part prasideda kaip first_part
                    if len(second_norm) >= 10 and len(first_norm) >= 10:
                        # Patikriname ar pirmi 10 simbolių sutampa
                        if first_norm[:10] == second_norm[:10]:
                            logger.info(
                                f"🗑️ Pašalintas turinio dublikatas: '{text[i:i+30]}...'"
                            )
                            return first_part.strip()

        return text

    def _clean_lithuanian_text(self, text: str) -> str:
        """Sutvarko sulūžusias lietuviškas raides ir šiukšles."""
        import re

        if not text:
            return ""

        # 1. Sutvarkom varneles ir nosines
        text = re.sub(r"c\s*[ˇv̌]", "č", text, flags=re.IGNORECASE)
        text = re.sub(r"s\s*[ˇv̌]", "š", text, flags=re.IGNORECASE)
        text = re.sub(r"z\s*[ˇv̌]", "ž", text, flags=re.IGNORECASE)
        text = re.sub(r"a\s*[˛̨]", "ą", text, flags=re.IGNORECASE)
        text = re.sub(r"e\s*[˛̨]", "ę", text, flags=re.IGNORECASE)
        text = re.sub(r"i\s*[˛̨]", "į", text, flags=re.IGNORECASE)
        text = re.sub(r"u\s*[˛̨]", "ų", text, flags=re.IGNORECASE)

        # 2. Specifinės teksto šiukšlės
        text = text.replace("Skaic ių", "Skaičių")
        text = text.replace("Skaic̆ių", "Skaičių")
        text = text.replace("skaič ių", "skaičių")
        text = text.replace("prieš ingą", "priešingą")
        text = text.replace("atvirkš tinį", "atvirkštinį")
        text = text.replace("Stač iakampio", "Stačiakampio")
        text = text.replace("Apskaič iuokite", "Apskaičiuokite")

        # 3. Svarbus pataisymas: [Mokinysnepateike˙sprendimo] ir panašūs variantai
        # Pašaliname taškelį viršuje
        text = text.replace("˙", "")
        # Įvairūs variantai be tarpų
        text = text.replace("[Mokinysnepateiksprendimo]", "[Nėra sprendimo]")
        text = text.replace("[Mokinysnepateikesprendimo]", "[Nėra sprendimo]")
        text = re.sub(
            r"\[Mokinys\s*nepateik[eė]?\s*sprendimo\]",
            "[Nėra sprendimo]",
            text,
            flags=re.IGNORECASE,
        )
        # Dar vienas variantas - su tarpais
        text = re.sub(
            r"\[\s*Mokinys\s*nepateik[eė]?\s*sprendimo\s*\]",
            "[Nėra sprendimo]",
            text,
            flags=re.IGNORECASE,
        )

        # 4. Atsakymo atskyrimas "12Ats" -> "12 Ats." ir "490Ats" -> "490 Ats."
        text = re.sub(r"(\d)Ats\.?", r"\1 Ats.", text)
        # Taip pat "Ats.490" -> "Ats. 490"
        text = re.sub(r"Ats\.(\d)", r"Ats. \1", text)

        # 5. KRITINIS: "121b)" atskyrimas
        # Jei randame skaičių (pvz 12), po kurio iškart eina naujas uždavinys (1b, 2a)
        text = re.sub(r"(\d+)([1-9][a-e]\))", r"\1 \2", text)

        return text.strip()

    def _to_latex(self, text: str) -> str:
        """Konvertuoja tekstą į LaTeX formatą (KaTeX suderinamas)."""
        import re

        if not text:
            return ""

        # Pakeičiam matematinius simbolius
        text = text.replace("*", " \\cdot ")
        text = text.replace("×", " \\cdot ")
        text = text.replace("·", " \\cdot ")
        text = text.replace(":", " \\div ")
        text = text.replace("÷", " \\div ")

        # Pakeičiam paprastas trupmenas į LaTeX frac
        # Bet tik jei tai tikrai trupmena (ne data ar pan.)
        text = re.sub(r"(\d+)/(\d+)", r"\\frac{\1}{\2}", text)

        # Pakeičiam neigiamus skaičius su skliaustais
        text = re.sub(r"\((-\d+)\)", r"(\1)", text)

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
        # Pattern: randame visus task ID ir jų pozicijas
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
                # Paliekame tik pirmą, pašaliname likusius
                for i in range(1, len(positions)):
                    start_pos = positions[i]
                    # Randame kur baigiasi šis dublikatas (iki kito task arba pabaigos)
                    remaining = latex[start_pos:]
                    # Ieškome kito task ID po šio
                    next_match = None
                    for m in matches:
                        if m.start() > start_pos:
                            next_match = m
                            break
                    end_pos = next_match.start() if next_match else len(latex)
                    parts_to_remove.append((start_pos, end_pos))

        # Pašaliname dublikatus (nuo galo, kad nepakeistume pozicijų)
        if parts_to_remove:
            parts_to_remove.sort(key=lambda x: x[0], reverse=True)
            result = latex
            for start, end in parts_to_remove:
                result = result[:start] + result[end:]
            logger.info(f"Pašalinta {len(parts_to_remove)} inline dublikatų")
            return result

        return latex


# Singleton instance
_gemini_vision: Optional[GeminiVisionClient] = None


def get_gemini_vision_client() -> GeminiVisionClient:
    """Grąžina GeminiVisionClient singleton instanciją."""
    global _gemini_vision
    if _gemini_vision is None:
        _gemini_vision = GeminiVisionClient()
    return _gemini_vision
