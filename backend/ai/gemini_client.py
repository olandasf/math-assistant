"""
Gemini AI Service - Klaidų paaiškinimas lietuvių kalba
======================================================
Naudoja Google Gemini API matematikos klaidų aiškinimui.
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx
from loguru import logger


@dataclass
class ExplanationResult:
    """AI paaiškinimo rezultatas."""

    success: bool
    explanation: str
    error_type: Optional[str] = None
    suggestions: Optional[List[str]] = None
    similar_examples: Optional[List[str]] = None
    difficulty_level: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


class GeminiClient:
    """Google Gemini API klientas."""

    # Rekomenduojamas modelis lietuvių kalbai
    DEFAULT_MODEL = "gemini-3.1-pro-preview"

    # API endpoint
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Inicializuoja Gemini klientą.

        Args:
            api_key: Gemini API raktas (arba iš env GEMINI_API_KEY)
            model: Modelio pavadinimas
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = model or self.DEFAULT_MODEL

        if not self.api_key:
            logger.warning("Gemini API raktas nenustatytas")

    @property
    def is_configured(self) -> bool:
        """Ar API sukonfigūruotas."""
        return bool(self.api_key)

    async def _call_api(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        max_tokens: int = 8192,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Iškviečia Gemini API.

        Args:
            prompt: Vartotojo užklausa
            system_instruction: Sistemos instrukcijos
            max_tokens: Maksimalus atsakymo ilgis
            temperature: Kūrybiškumo lygis (0-1)

        Returns:
            API atsakymas
        """
        if not self.is_configured:
            raise ValueError("Gemini API raktas nenustatytas")

        url = f"{self.BASE_URL}/models/{self.model}:generateContent"

        headers = {
            "Content-Type": "application/json",
        }

        # Formuojame užklausą
        request_body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            },
        }

        # Pridedame sistemos instrukcijas jei yra
        if system_instruction:
            request_body["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        # Timeout padidintas iki 600s AI generavimui dėl Thinking rėžimo
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(
                f"{url}?key={self.api_key}", headers=headers, json=request_body
            )

            if response.status_code != 200:
                error_msg = response.text
                logger.error(f"Gemini API klaida: {response.status_code} - {error_msg}")
                raise Exception(f"Gemini API klaida: {response.status_code}")

            return response.json()

    def _extract_text(self, response: Dict[str, Any]) -> str:
        """Ištraukia tekstą iš API atsakymo."""
        try:
            candidates = response.get("candidates", [])
            logger.debug(f"Response candidates count: {len(candidates)}")
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                logger.debug(f"Content parts count: {len(parts)}")
                if parts:
                    text = parts[0].get("text", "")
                    logger.debug(f"Extracted text length: {len(text)}")
                    return text
                else:
                    # Kartais atsakymas gali būti blokuotas - patikriname finishReason
                    finish_reason = candidates[0].get("finishReason", "")
                    logger.warning(
                        f"No parts in response. Finish reason: {finish_reason}"
                    )
                    if finish_reason == "SAFETY":
                        logger.warning("Response blocked due to safety filters")
            else:
                logger.warning(f"No candidates in response. Keys: {response.keys()}")
        except (KeyError, IndexError) as e:
            logger.error(f"Error extracting text: {e}")
        return ""

    async def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        max_tokens: int = 8192,
        temperature: float = 0.7,
    ) -> str:
        """
        Generuoja tekstą su Gemini API.

        Paprastas metodas teksto generavimui - naudojamas vertimui,
        uždavinių generavimui ir kt.

        Args:
            prompt: Užklausa
            system_instruction: Sistemos instrukcijos
            max_tokens: Maksimalus atsakymo ilgis
            temperature: Kūrybiškumo lygis (0-1)

        Returns:
            Sugeneruotas tekstas
        """
        if not self.is_configured:
            raise ValueError("Gemini API raktas nenustatytas")

        response = await self._call_api(
            prompt=prompt,
            system_instruction=system_instruction,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return self._extract_text(response)

    async def explain_math_error(
        self,
        student_answer: str,
        correct_answer: str,
        problem: str,
        grade_level: int = 5,
        topic: Optional[str] = None,
    ) -> ExplanationResult:
        """
        Paaiškina matematikos klaidą lietuvių kalba.

        Args:
            student_answer: Mokinio atsakymas
            correct_answer: Teisingas atsakymas
            problem: Užduoties tekstas
            grade_level: Klasė (5-8)
            topic: Tema (pvz., "trupmenos", "lygtys")

        Returns:
            ExplanationResult su paaiškinimu
        """
        if not self.is_configured:
            return ExplanationResult(
                success=False,
                explanation="Gemini API nesukonfigūruotas",
                error_type="not_configured",
            )

        system_instruction = f"""Tu esi matematikos mokytojas, dirbantis su {grade_level} klasės mokiniais Lietuvoje.
Tavo užduotis - paaiškinti matematikos klaidas aiškiai, draugiškai ir suprantamai lietuvių kalba.

Taisyklės:
1. Rašyk TIKTAI lietuvių kalba
2. Naudok paprastus žodžius, tinkamus {grade_level} klasės mokiniui
3. Būk draugiškas ir padrąsinantis
4. Aiškink žingsnis po žingsnio
5. Pateik panašų pavyzdį, kad mokinys galėtų praktikuoti
6. Matematines formules rašyk LaTeX formatu tarp $ simbolių"""

        topic_hint = f" (tema: {topic})" if topic else ""

        prompt = f"""Mokinys sprendė šią užduotį{topic_hint}:
Užduotis: {problem}

Mokinio atsakymas: {student_answer}
Teisingas atsakymas: {correct_answer}

Prašau:
1. Paaiškink, kokią klaidą padarė mokinys
2. Parodyk, kaip reikėjo spręsti teisingai
3. Pateik panašų pratimą praktikai

Atsakyk struktūrizuotai naudodamas šias antraštes:
## Klaida
## Kaip spręsti teisingai
## Praktikos uždavinys"""

        try:
            response = await self._call_api(
                prompt=prompt,
                system_instruction=system_instruction,
                max_tokens=1500,
                temperature=0.7,
            )

            explanation = self._extract_text(response)

            if not explanation:
                return ExplanationResult(
                    success=False,
                    explanation="Nepavyko gauti paaiškinimo",
                    error_type="empty_response",
                )

            return ExplanationResult(
                success=True, explanation=explanation, raw_response=response
            )

        except Exception as e:
            logger.error(f"Gemini klaida: {str(e)}")
            return ExplanationResult(
                success=False, explanation=f"Klaida: {str(e)}", error_type="api_error"
            )

    async def analyze_solution_steps(
        self, problem: str, student_solution: str, grade_level: int = 5
    ) -> ExplanationResult:
        """
        Analizuoja mokinio sprendimo žingsnius.

        Args:
            problem: Užduoties tekstas
            student_solution: Mokinio sprendimas (visi žingsniai)
            grade_level: Klasė

        Returns:
            Analizė su komentarais prie kiekvieno žingsnio
        """
        if not self.is_configured:
            return ExplanationResult(
                success=False,
                explanation="Gemini API nesukonfigūruotas",
                error_type="not_configured",
            )

        system_instruction = f"""Tu esi matematikos mokytojas, analizuojantis {grade_level} klasės mokinio darbą.
Tavo užduotis - peržiūrėti mokinio sprendimo žingsnius ir pakomentuoti kiekvieną.

Rašyk TIKTAI lietuvių kalba.
Būk konstruktyvus - pagirti tai, kas gerai, ir švelniai nurodyti klaidas."""

        prompt = f"""Išanalizuok šio mokinio sprendimą:

Užduotis: {problem}

Mokinio sprendimas:
{student_solution}

Pateik analizę tokiu formatu:
## Žingsnių analizė
(Pakomentuok kiekvieną žingsnį - ar teisingas, ar yra klaidų)

## Bendras įvertinimas
(Trumpas apibendrinimas - kas gerai, ką reikia tobulinti)

## Patarimai
(Konkretūs patarimai mokiniui)"""

        try:
            response = await self._call_api(
                prompt=prompt,
                system_instruction=system_instruction,
                max_tokens=2000,
                temperature=0.6,
            )

            explanation = self._extract_text(response)

            return ExplanationResult(
                success=bool(explanation),
                explanation=explanation or "Nepavyko gauti analizės",
                raw_response=response,
            )

        except Exception as e:
            logger.error(f"Gemini klaida: {str(e)}")
            return ExplanationResult(
                success=False, explanation=f"Klaida: {str(e)}", error_type="api_error"
            )

    async def generate_similar_problem(
        self,
        original_problem: str,
        topic: str,
        grade_level: int = 5,
        difficulty: str = "vidutinis",
    ) -> ExplanationResult:
        """
        Sugeneruoja panašų uždavinį praktikai.

        Args:
            original_problem: Originalus uždavinys
            topic: Tema
            grade_level: Klasė
            difficulty: Sudėtingumo lygis (lengvas/vidutinis/sunkus)

        Returns:
            Naujas uždavinys su sprendimu
        """
        if not self.is_configured:
            return ExplanationResult(
                success=False,
                explanation="Gemini API nesukonfigūruotas",
                error_type="not_configured",
            )

        system_instruction = f"""Tu esi matematikos uždavinių kūrėjas {grade_level} klasei.
Kurk uždavinius lietuvių kalba, tinkamus Lietuvos mokyklos programai."""

        prompt = f"""Sukurk naują {difficulty} sudėtingumo uždavinį, panašų į šį:

Originalus uždavinys: {original_problem}
Tema: {topic}
Klasė: {grade_level}

Pateik:
## Naujas uždavinys
(Užduoties tekstas)

## Sprendimas
(Žingsnis po žingsnio)

## Atsakymas
(Galutinis atsakymas)"""

        try:
            response = await self._call_api(
                prompt=prompt,
                system_instruction=system_instruction,
                max_tokens=1000,
                temperature=0.8,
            )

            explanation = self._extract_text(response)

            return ExplanationResult(
                success=bool(explanation),
                explanation=explanation or "Nepavyko sugeneruoti uždavinio",
                difficulty_level=difficulty,
                raw_response=response,
            )

        except Exception as e:
            logger.error(f"Gemini klaida: {str(e)}")
            return ExplanationResult(
                success=False, explanation=f"Klaida: {str(e)}", error_type="api_error"
            )

    async def generate_alternative_solutions(
        self,
        problem: str,
        correct_answer: str,
        grade_level: int = 6,
        num_solutions: int = 3,
    ) -> ExplanationResult:
        """
        Sugeneruoja alternatyvius uždavinio sprendimo būdus.
        Naudoja Vertex AI Gemini Flash.

        Args:
            problem: Uždavinio tekstas
            correct_answer: Teisingas atsakymas
            grade_level: Klasė (5-10)
            num_solutions: Kiek sprendimo būdų generuoti (1-3)

        Returns:
            ExplanationResult su alternatyviais sprendimais
        """
        try:
            import os

            from config import BASE_DIR
            from google import genai
            from google.genai import types

            # Ieškome credentials failo
            credentials_paths = [
                BASE_DIR / "backend" / "google_credentials.json",
                BASE_DIR / "backend" / "mtematika-471410-e4cb6af744ea.json",
            ]

            credentials_path = None
            for path in credentials_paths:
                if path and path.exists():
                    credentials_path = path
                    break

            if not credentials_path:
                logger.warning("Google Cloud credentials nerastas")
                return ExplanationResult(
                    success=False,
                    explanation="Credentials nerastas",
                    error_type="no_credentials",
                )

            # Nustatome credentials
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)

            # Inicializuojame Vertex AI klientą
            client = genai.Client(
                vertexai=True,
                project="mtematika-471410",
                location="global",
            )

            prompt = f"""Pateik {num_solutions} SKIRTINGUS būdus išspręsti šį matematikos uždavinį.

UŽDAVINYS: {problem}
TEISINGAS ATSAKYMAS: {correct_answer}

Kiekvienam sprendimo būdui pateik:

## 1 būdas: [Būdo pavadinimas]

**Sprendimas:**

1. Pirmas žingsnis su formule $\\frac{{a}}{{b}}$

2. Antras žingsnis

**Atsakymas:** {correct_answer}

---

## 2 būdas: [Būdo pavadinimas]
...

FORMATAVIMO TAISYKLĖS:
- Visas formules rašyk tarp $ ženklų
- VISADA palik tarpą prieš ir po formulės
- Kiekvieną žingsnį rašyk atskiroje eilutėje

Rašyk LIETUVIŲ kalba, taisyklinga gramatika."""

            logger.info(f"🚀 Kviečiamas Gemini alternatyviems sprendimams...")

            # Kviečiame Gemini
            response = client.models.generate_content(
                model="google/gemini-3.1-pro-preview",
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)],
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=0.5,
                    max_output_tokens=2000,
                    thinking_config=types.ThinkingConfig(thinkingBudget=0),
                ),
            )

            # Ištraukiame tekstą
            result_text = ""
            try:
                if response.text:
                    result_text = response.text
            except Exception:
                pass

            if not result_text and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, "content") and candidate.content:
                        parts = getattr(candidate.content, "parts", None)
                        if parts:
                            for part in parts:
                                if hasattr(part, "text") and part.text:
                                    result_text += part.text

            if not result_text:
                logger.warning("Gemini Flash grąžino tuščią atsakymą")
                return ExplanationResult(
                    success=False,
                    explanation="Nepavyko sugeneruoti alternatyvių sprendimų",
                    error_type="empty_response",
                )

            logger.info(
                f"✅ Gemini Flash: gautas {len(result_text)} simbolių atsakymas"
            )

            return ExplanationResult(
                success=True,
                explanation=result_text,
            )

        except Exception as e:
            logger.error(
                f"Gemini klaida generuojant alternatyvius sprendimus: {str(e)}"
            )
            return ExplanationResult(
                success=False,
                explanation=f"Klaida: {str(e)}",
                error_type="api_error",
            )

    async def generate_detailed_solution_with_thinking(
        self,
        problem: str,
        student_answer: str,
        correct_answer: str,
        is_correct: bool,
        grade_level: int = 6,
        no_student_answer: bool = False,
    ) -> ExplanationResult:
        """
        Sugeneruoja išsamų sprendimo paaiškinimą naudojant Gemini Flash.

        Naudoja Vertex AI gemini-3-flash-preview - greitas ir stabilus modelis.

        Args:
            problem: Uždavinio tekstas arba išraiška
            student_answer: Mokinio atsakymas
            correct_answer: Teisingas atsakymas
            is_correct: Ar mokinio atsakymas teisingas
            grade_level: Klasė (5-10)
            no_student_answer: Ar mokinys nepateikė atsakymo

        Returns:
            ExplanationResult su išsamiu paaiškinimu ir sprendimo būdais
        """
        try:
            import os

            from config import BASE_DIR
            from google import genai
            from google.genai import types

            # Ieškome credentials failo
            credentials_paths = [
                BASE_DIR / "backend" / "google_credentials.json",
                BASE_DIR / "backend" / "mtematika-471410-e4cb6af744ea.json",
            ]

            credentials_path = None
            for path in credentials_paths:
                if path and path.exists():
                    credentials_path = path
                    break

            if not credentials_path:
                logger.warning(
                    "Google Cloud credentials nerastas, naudojamas paprastas API"
                )
                return ExplanationResult(
                    success=False,
                    explanation="Credentials nerastas",
                    error_type="no_credentials",
                )

            # Nustatome credentials
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)

            # Inicializuojame Vertex AI klientą
            client = genai.Client(
                vertexai=True,
                project="mtematika-471410",
                location="global",
            )

            # Formuojame prompt pagal situaciją
            if no_student_answer:
                prompt = f"""Mokinys NEPATEIKĖ atsakymo šiam matematikos uždaviniui.

UŽDAVINYS: {problem}
TEISINGAS ATSAKYMAS: {correct_answer if correct_answer else "Apskaičiuok"}

Pateik {grade_level} klasės mokiniui sprendimo paaiškinimą.

FORMATAVIMO TAISYKLĖS (PRIVALOMA):
1. Kiekvieną žingsnį rašyk ATSKIROJE EILUTĖJE
2. Visas formules rašyk tarp $ ženklų: $\\frac{{7}}{{15}}$
3. VISADA palik TARPĄ prieš ir po formulės
4. VISADA palik TARPĄ po taško ir kablelio
5. Naudok numeraciją su nauja eilute:

1. Pirmas žingsnis su formule $\\frac{{a}}{{b}}$ ir paaiškinimas.

2. Antras žingsnis: $23 \\cdot 8 = 184$

3. Atsakymas: $0$

Rašyk LIETUVIŲ kalba, taisyklinga gramatika."""
            elif is_correct:
                prompt = f"""Mokinys TEISINGAI išsprendė: {problem} = {student_answer}

Pateik TRUMPĄ paaiškinimą {grade_level} klasės mokiniui.
Formules rašyk tarp $ ženklų: $\\frac{{a}}{{b}}$
VISADA palik tarpus tarp teksto ir formulių.
Rašyk LIETUVIŲ kalba. Max 80 žodžių."""
            else:
                prompt = f"""Mokinys NETEISINGAI išsprendė matematikos uždavinį.

UŽDAVINYS: {problem}
MOKINIO ATSAKYMAS: {student_answer}
TEISINGAS ATSAKYMAS: {correct_answer}

Pateik {grade_level} klasės mokiniui paaiškinimą.

FORMATAVIMO TAISYKLĖS (PRIVALOMA):
1. Kiekvieną žingsnį rašyk ATSKIROJE EILUTĖJE
2. Visas formules rašyk tarp $ ženklų: $\\frac{{7}}{{15}}$
3. VISADA palik TARPĄ prieš ir po formulės
4. VISADA palik TARPĄ po taško ir kablelio
5. Naudok numeraciją su nauja eilute:

1. Klaida: mokinys parašė $-368$ vietoj $0$.

2. Teisingas sprendimas: $23 \\cdot 8 = 184$

3. Tada: $23 \\cdot (-8) = -184$

4. Sudedame: $184 + (-184) = 0$

5. Atsakymas: $0$

6. Patarimas: visada tikrink ženklus.

Rašyk LIETUVIŲ kalba, taisyklinga gramatika. Max 150 žodžių."""

            logger.info(f"🚀 Kviečiamas Gemini paaiškinimui...")

            # Kviečiame Gemini
            response = client.models.generate_content(
                model="google/gemini-3.1-pro-preview",
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)],
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=0.3,  # Mažesnė temperatūra stabilesniam atsakymui
                    max_output_tokens=1000,  # Trumpesni atsakymai
                    thinking_config=types.ThinkingConfig(
                        thinkingBudget=0
                    ),  # Išjungtas thinking
                ),
            )

            # Ištraukiame tekstą
            result_text = ""
            try:
                if response.text:
                    result_text = response.text
            except Exception:
                pass

            if not result_text and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, "content") and candidate.content:
                        parts = getattr(candidate.content, "parts", None)
                        if parts:
                            for part in parts:
                                if hasattr(part, "text") and part.text:
                                    result_text += part.text

            if not result_text:
                logger.warning("Gemini Flash grąžino tuščią atsakymą")
                return ExplanationResult(
                    success=False,
                    explanation="Nepavyko sugeneruoti paaiškinimo",
                    error_type="empty_response",
                )

            logger.info(
                f"✅ Gemini Flash: gautas {len(result_text)} simbolių atsakymas"
            )
            # DEBUG: Log first 300 chars of the response
            logger.debug(
                f"📝 Gemini Flash atsakymas (pirmi 300 char): {result_text[:300]}"
            )

            return ExplanationResult(
                success=True,
                explanation=result_text,
            )

        except Exception as e:
            logger.error(f"Gemini Flash klaida: {str(e)}")
            return ExplanationResult(
                success=False,
                explanation=f"Klaida: {str(e)}",
                error_type="api_error",
            )

    async def translate_to_student_friendly(
        self, technical_text: str, grade_level: int = 5
    ) -> str:
        """
        Išverčia techninį tekstą į mokiniui suprantamą kalbą.

        Args:
            technical_text: Techninis tekstas
            grade_level: Klasė

        Returns:
            Supaprastintas tekstas
        """
        if not self.is_configured:
            return technical_text

        prompt = f"""Perrašyk šį tekstą taip, kad būtų suprantamas {grade_level} klasės mokiniui.
Naudok paprastus žodžius, trumpus sakinius. Rašyk lietuviškai.

Tekstas: {technical_text}

Supaprastintas tekstas:"""

        try:
            response = await self._call_api(
                prompt=prompt, max_tokens=500, temperature=0.5
            )

            return self._extract_text(response) or technical_text

        except Exception:
            return technical_text


# Singleton instancija
_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Gauna Gemini klientą."""
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client


def configure_gemini(api_key: str, model: Optional[str] = None):
    """Konfigūruoja Gemini klientą."""
    global _client
    _client = GeminiClient(api_key=api_key, model=model)


# === Convenience funkcijos ===


async def explain_error(
    student_answer: str, correct_answer: str, problem: str, grade_level: int = 5
) -> ExplanationResult:
    """Paaiškina klaidą."""
    return await get_gemini_client().explain_math_error(
        student_answer=student_answer,
        correct_answer=correct_answer,
        problem=problem,
        grade_level=grade_level,
    )


async def analyze_steps(
    problem: str, student_solution: str, grade_level: int = 5
) -> ExplanationResult:
    """Analizuoja sprendimo žingsnius."""
    return await get_gemini_client().analyze_solution_steps(
        problem=problem, student_solution=student_solution, grade_level=grade_level
    )


if __name__ == "__main__":
    import asyncio

    async def test():
        print("=== Gemini Client Test ===\n")

        client = GeminiClient()

        if not client.is_configured:
            print("⚠️ Gemini API raktas nenustatytas!")
            print("   Nustatykite GEMINI_API_KEY aplinkos kintamąjį")
            return

        # Test 1: Klaidos paaiškinimas
        print("1. Testuojamas klaidos paaiškinimas...")
        result = await client.explain_math_error(
            student_answer="6/8",
            correct_answer="3/4",
            problem="Suprastinkite trupmeną 6/8",
            grade_level=5,
            topic="trupmenos",
        )

        if result.success:
            print(f"   ✅ Paaiškinimas gautas:\n{result.explanation[:200]}...")
        else:
            print(f"   ❌ Klaida: {result.explanation}")

        print("\n✅ Testavimas baigtas!")

    asyncio.run(test())
