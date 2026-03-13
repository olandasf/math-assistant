"""
Task Translator - verčia ir LOKALIZUOJA uždavinius į lietuvių kalbą.

Naudoja Gemini AI:
1. LOKALIZUOTI (ne tik versti) uždavinius
2. Adaptuoti kontekstą (vardai, valiuta, vienetai, kultūra)
3. Generuoti variacijas su kitais skaičiais
4. Validuoti lokalizacijos kokybę

Palaikomi šaltiniai:
- GSM8K (8500 žodinių uždavinių)
- Competition Math (olimpiadiniai)
"""

import json
import random
import re
from dataclasses import dataclass, field
from typing import Optional

from ai.gemini_client import GeminiClient, get_gemini_client
from loguru import logger
from services.huggingface_loader import RawProblem

# Bandyti importuoti Faker (nebūtina)
try:
    from faker import Faker

    FAKER_LT = Faker("lt_LT")
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_LT = None
    FAKER_AVAILABLE = False


@dataclass
class TranslatedProblem:
    """Išverstas ir adaptuotas uždavinys."""

    question_lt: str  # Tekstas lietuviškai
    question_en: str  # Originalas angliškai
    answer: str  # Atsakymas
    answer_latex: Optional[str]  # Atsakymas LaTeX
    solution_steps: list[str]  # Sprendimo žingsniai LT
    difficulty: str  # Sunkumas
    grade_min: int  # Min klasė
    grade_max: int  # Max klasė
    source: str  # Šaltinis
    source_id: str  # Šaltinio ID
    topic_id: Optional[str] = None  # Tema (jei nustatyta)
    tags: list[str] = field(default_factory=list)  # Žymos
    localization_score: float = 1.0  # Lokalizacijos kokybės balas (0-1)


# Lietuviški vardai pagal lytį (išplėstas sąrašas su retesniais vardais)
LITHUANIAN_NAMES = {
    "male": [
        # Klasikiniai
        "Jonas",
        "Petras",
        "Tomas",
        "Lukas",
        "Matas",
        "Mantas",
        "Domas",
        "Rokas",
        "Paulius",
        "Karolis",
        "Andrius",
        "Mindaugas",
        "Vytautas",
        "Gediminas",
        # Šiuolaikiški
        "Dominykas",
        "Aurimas",
        "Darius",
        "Edvinas",
        "Arnoldas",
        "Ignas",
        "Dovydas",
        "Nojus",
        "Jokūbas",
        "Kajus",
        "Benas",
        "Emilijus",
        "Adomas",
        "Gabrielius",
        # Lietuviški gamtos vardai
        "Ąžuolas",
        "Uosis",
        "Joris",
        "Rytis",
        "Saulius",
        "Gintaras",
        "Algirdas",
        "Kęstutis",
        "Tautvydas",
        "Rimvydas",
        "Arvydas",
        "Dainius",
    ],
    "female": [
        # Klasikiniai
        "Ona",
        "Marija",
        "Ieva",
        "Greta",
        "Austėja",
        "Gabija",
        "Emilija",
        "Julija",
        "Karolina",
        "Agnė",
        "Ugnė",
        "Miglė",
        "Justė",
        "Indrė",
        "Rūta",
        "Simona",
        # Šiuolaikiški
        "Laura",
        "Viktorija",
        "Eglė",
        "Monika",
        "Kristina",
        "Justina",
        "Aistė",
        "Kotryna",
        "Ema",
        "Lėja",
        "Urtė",
        "Kamilė",
        "Rugilė",
        "Patricija",
        # Lietuviški gamtos vardai
        "Liepa",
        "Eglė",
        "Rūta",
        "Živilė",
        "Giedrė",
        "Saulė",
        "Aušra",
        "Žemyna",
        "Danutė",
        "Laima",
        "Ramunė",
        "Milda",
        "Dalia",
        "Vitalija",
    ],
}


def get_random_lithuanian_name(gender: Optional[str] = None) -> str:
    """
    Grąžina atsitiktinį lietuvišką vardą.

    Args:
        gender: "male", "female" arba None (atsitiktinis)
    """
    if (
        FAKER_AVAILABLE and FAKER_LT and random.random() < 0.3
    ):  # 30% tikimybė naudoti Faker
        try:
            if gender == "male":
                return FAKER_LT.first_name_male()
            elif gender == "female":
                return FAKER_LT.first_name_female()
            else:
                return FAKER_LT.first_name()
        except Exception:
            pass

    # Fallback į statinį sąrašą
    if gender is None:
        gender = random.choice(["male", "female"])
    return random.choice(LITHUANIAN_NAMES.get(gender, LITHUANIAN_NAMES["male"]))


# Anglų -> lietuvių vardų mapingas
NAMES_MAPPING = {
    # Vyrški
    "John": "Jonas",
    "Peter": "Petras",
    "Tom": "Tomas",
    "Thomas": "Tomas",
    "Luke": "Lukas",
    "Matthew": "Matas",
    "Matt": "Matas",
    "Mark": "Markas",
    "James": "Jokūbas",
    "David": "Dovydas",
    "Michael": "Mykolas",
    "William": "Vilius",
    "Robert": "Robertas",
    "Andrew": "Andrius",
    "Paul": "Paulius",
    "Daniel": "Danielius",
    "George": "Jurgis",
    "Alex": "Aleksas",
    "Sam": "Simas",
    "Ben": "Benjaminas",
    "Jack": "Jokūbas",
    "Charlie": "Karolis",
    "Max": "Maksas",
    "Nick": "Nikolas",
    # Moteriški
    "Mary": "Marija",
    "Anna": "Ona",
    "Eva": "Ieva",
    "Lisa": "Elzbieta",
    "Sarah": "Sara",
    "Emma": "Ema",
    "Julia": "Julija",
    "Sophia": "Sofija",
    "Emily": "Emilija",
    "Amy": "Amelija",
    "Kate": "Kotryna",
    "Catherine": "Kotryna",
    "Jennifer": "Jurgita",
    "Jessica": "Justė",
    "Ashley": "Austėja",
    "Natalia": "Natalija",
    "Olivia": "Olivija",
    "Grace": "Gražina",
    "Rachel": "Rūta",
    "Megan": "Miglė",
    "Lauren": "Laura",
}

# Valiutų konversija
CURRENCY_PATTERNS = [
    (r"\$(\d+(?:\.\d{2})?)", r"\1 €"),  # $5.00 -> 5.00 €
    (r"(\d+(?:\.\d{2})?) dollars?", r"\1 eurų"),
    (r"(\d+(?:\.\d{2})?) cents?", r"\1 centų"),
    (r"(\d+) pennies", r"\1 centų"),
    (r"(\d+) dimes?", r"\1 eurų"),  # apytiksliai
    (r"(\d+) quarters?", r"\1 eurų"),
    (r"(\d+) nickels?", r"\1 centų"),
]

# =============================================================================
# VIENETŲ KONVERSIJOS TAISYKLĖS (Imperial -> Metrinė)
# =============================================================================

# Tikslios konversijos su apvalinimo taisyklėmis
UNIT_CONVERSIONS = {
    # Svoris
    "pounds": {"to": "kg", "factor": 0.453592, "round_to_nice": True},
    "pound": {"to": "kg", "factor": 0.453592, "round_to_nice": True},
    "lbs": {"to": "kg", "factor": 0.453592, "round_to_nice": True},
    "lb": {"to": "kg", "factor": 0.453592, "round_to_nice": True},
    "ounces": {"to": "g", "factor": 28.3495, "round_to_nice": True},
    "ounce": {"to": "g", "factor": 28.3495, "round_to_nice": True},
    "oz": {"to": "g", "factor": 28.3495, "round_to_nice": True},
    # Ilgis
    "miles": {"to": "km", "factor": 1.60934, "round_to_nice": True},
    "mile": {"to": "km", "factor": 1.60934, "round_to_nice": True},
    "feet": {"to": "m", "factor": 0.3048, "round_to_nice": True},
    "foot": {"to": "m", "factor": 0.3048, "round_to_nice": True},
    "ft": {"to": "m", "factor": 0.3048, "round_to_nice": True},
    "inches": {"to": "cm", "factor": 2.54, "round_to_nice": True},
    "inch": {"to": "cm", "factor": 2.54, "round_to_nice": True},
    "yards": {"to": "m", "factor": 0.9144, "round_to_nice": True},
    "yard": {"to": "m", "factor": 0.9144, "round_to_nice": True},
    # Tūris
    "gallons": {"to": "l", "factor": 3.78541, "round_to_nice": True},
    "gallon": {"to": "l", "factor": 3.78541, "round_to_nice": True},
    "quarts": {"to": "l", "factor": 0.946353, "round_to_nice": True},
    "quart": {"to": "l", "factor": 0.946353, "round_to_nice": True},
    "pints": {"to": "ml", "factor": 473.176, "round_to_nice": True},
    "pint": {"to": "ml", "factor": 473.176, "round_to_nice": True},
    "cups": {"to": "ml", "factor": 236.588, "round_to_nice": True},
    "cup": {"to": "ml", "factor": 236.588, "round_to_nice": True},
    # Temperatūra (speciali logika)
    "fahrenheit": {"to": "celsius", "formula": "(x-32)*5/9"},
}

# Amerikiečių monetos -> EUR centai (supaprastinta)
US_COINS_TO_CENTS = {
    "quarter": 25,  # 25 centai
    "quarters": 25,
    "dime": 10,  # 10 centų
    "dimes": 10,
    "nickel": 5,  # 5 centai
    "nickels": 5,
    "penny": 1,  # 1 centas
    "pennies": 1,
}

# Kultūrinio konteksto pakeitimai
CULTURAL_REPLACEMENTS = {
    # Sportas
    "baseball": "krepšinis",
    "football": "futbolas",  # Amerikietis -> Europos
    "soccer": "futbolas",
    "basketball": "krepšinis",
    "hockey": "ledo ritulys",
    "softball": "krepšinis",
    # Šventės
    "Thanksgiving": "Kalėdos",
    "Halloween": "Užgavėnės",
    "Fourth of July": "Vasario 16-oji",
    "Independence Day": "Vasario 16-oji",
    "Labor Day": "Gegužės 1-oji",
    "Memorial Day": "Gegužės 1-oji",
    # Maistas
    "candy store": "saldainių parduotuvė",
    "candy": "saldainiai",
    "cookies": "sausainiai",
    "cookie": "sausainis",
    "brownie": "pyragėlis",
    "brownies": "pyragėliai",
    "cupcake": "keksas",
    "cupcakes": "keksai",
    "donut": "spurga",
    "donuts": "spurgos",
    "hotdog": "dešrainis",
    "hotdogs": "dešrainiai",
    "hamburger": "mėsainis",
    "hamburgers": "mėsainiai",
    "french fries": "bulvytės",
    "fries": "bulvytės",
    # Vietos
    "grocery store": "maisto parduotuvė",
    "mall": "prekybos centras",
    "drugstore": "vaistinė",
    "convenience store": "parduotuvė",
    # Mokykla
    "high school": "gimnazija",
    "middle school": "pagrindinė mokykla",
    "elementary school": "pradinė mokykla",
    "college": "universitetas",
    "freshman": "pirmo kurso studentas",
    "sophomore": "antro kurso studentas",
    "junior": "trečio kurso studentas",
    "senior": "ketvirto kurso studentas",
}

# Raktažodžiai kurie NETURI likti išverstame tekste (indikuoja nepavykusią lokalizaciją)
FORBIDDEN_TERMS_IN_LT = [
    # Vienetai
    "pounds",
    "pound",
    "lbs",
    "lb",
    "ounces",
    "ounce",
    "oz",
    "miles",
    "mile",
    "feet",
    "foot",
    "ft",
    "inches",
    "inch",
    "gallons",
    "gallon",
    "quarts",
    "quart",
    "pints",
    "pint",
    # Valiuta
    "dollars",
    "dollar",
    "quarters",
    "quarter",
    "dimes",
    "dime",
    "nickels",
    "nickel",
    "pennies",
    "penny",
    # Kultūra
    "baseball",
    "softball",
    "Thanksgiving",
    "Halloween",
    "Fourth of July",
]


def validate_localization(translated_text: str, original_text: str) -> dict:
    """
    Tikrina ar lokalizacija pavyko.

    Returns:
        dict su: {"valid": bool, "issues": list[str], "score": float}
    """
    issues = []
    text_lower = translated_text.lower()

    # Tikrinti draudžiamus terminus
    for term in FORBIDDEN_TERMS_IN_LT:
        if term.lower() in text_lower:
            issues.append(f"Neišverstas terminas: '{term}'")

    # Tikrinti ar yra $ simbolis (turėtų būti €)
    if "$" in translated_text:
        issues.append("Likęs dolerio simbolis ($)")

    # Tikrinti angliškus vardus
    common_english_names = [
        "John",
        "Mary",
        "Tom",
        "James",
        "Sarah",
        "Emily",
        "Mike",
        "Lisa",
    ]
    for name in common_english_names:
        if name in translated_text:
            issues.append(f"Neišverstas vardas: '{name}'")

    # Apskaičiuoti kokybės balą
    score = 1.0 - (len(issues) * 0.1)
    score = max(0.0, score)

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "score": score,
        "needs_review": len(issues) > 0,
    }


class TaskTranslator:
    """
    Verčia ir adaptuoja matematinius uždavinius.

    Naudojimas:
        translator = TaskTranslator()
        translated = await translator.translate(raw_problem)
        variations = await translator.generate_variations(translated, count=2)
    """

    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        """
        Inicializuoja vertėją.

        Args:
            gemini_client: Gemini klientas (default: global singleton)
        """
        self._gemini_client = gemini_client

    @property
    def gemini(self) -> GeminiClient:
        """Grąžina Gemini klientą."""
        if self._gemini_client is None:
            self._gemini_client = get_gemini_client()
        return self._gemini_client

    async def translate(
        self, problem: RawProblem, detect_topic: bool = True, validate: bool = True
    ) -> TranslatedProblem:
        """
        Išverčia ir LOKALIZUOJA uždavinį į lietuvių kalbą.

        Args:
            problem: Originalus uždavinys (EN)
            detect_topic: Ar bandyti nustatyti temą pagal curriculum
            validate: Ar tikrinti lokalizacijos kokybę

        Returns:
            TranslatedProblem su lietuvišku tekstu
        """
        prompt = self._build_translation_prompt(problem)

        try:
            response = await self.gemini.generate_content(prompt)
            result = self._parse_translation_response(response, problem)

            # Validuoti lokalizaciją
            if validate:
                validation = validate_localization(result.question_lt, problem.question)
                if not validation["valid"]:
                    logger.warning(
                        f"Lokalizacijos problemos ({problem.source_id}): {validation['issues']}"
                    )
                    # Pridėti žymą apie reikalingą peržiūrą
                    if result.tags is None:
                        result.tags = []
                    result.tags.append("needs_review")
                    for issue in validation["issues"][:3]:  # Max 3 problemos
                        result.tags.append(f"issue:{issue[:30]}")

            # Nustatyti temą
            if detect_topic:
                result.topic_id = await self._detect_topic(result.question_lt)

            return result

        except Exception as e:
            logger.error(f"Klaida verčiant uždavinį: {e}")
            # Fallback: grąžinti su baziniu vertimu
            return self._fallback_translation(problem)

    async def generate_variations(
        self, problem: TranslatedProblem, count: int = 2
    ) -> list[TranslatedProblem]:
        """
        Generuoja uždavinio variacijas su kitais skaičiais.

        Args:
            problem: Bazinis uždavinys (jau išverstas)
            count: Kiek variacijų generuoti

        Returns:
            Sąrašas naujų uždavinių
        """
        prompt = self._build_variation_prompt(problem, count)

        try:
            response = await self.gemini.generate_content(prompt)
            variations = self._parse_variations_response(response, problem)
            return variations[:count]

        except Exception as e:
            logger.error(f"Klaida generuojant variacijas: {e}")
            return []

    async def translate_batch(
        self, problems: list[RawProblem], max_concurrent: int = 5
    ) -> list[TranslatedProblem]:
        """
        Verčia kelis uždavinius vienu metu.

        Args:
            problems: Uždavinių sąrašas
            max_concurrent: Maksimalus lygiagrečių užklausų skaičius

        Returns:
            Išverstų uždavinių sąrašas
        """
        import asyncio

        results = []

        # Padalinti į batch'us
        for i in range(0, len(problems), max_concurrent):
            batch = problems[i : i + max_concurrent]
            tasks = [self.translate(p) for p in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, TranslatedProblem):
                    results.append(result)
                else:
                    logger.warning(f"Nepavyko išversti uždavinio: {result}")

        return results

    def _build_translation_prompt(self, problem: RawProblem) -> str:
        """Sukuria Gemini prompt'ą LOKALIZACIJAI (ne tik vertimui)."""
        return (
            f"""Tu esi profesionalus Lietuvos matematikos mokytojas ir redaktorius.
Tavo užduotis - ADAPTUOTI (ne tiesiogiai išversti) šį matematinį uždavinį Lietuvos rinkai.

ORIGINALUS UŽDAVINYS (angliškai):
{problem.question}

ORIGINALUS ATSAKYMAS:
{problem.answer}

ORIGINALUS SPRENDIMAS:
{problem.solution or "Nėra"}

=== LOKALIZACIJOS TAISYKLĖS ===

1. VALIUTA:
   - Visus $ keičk į € (EUR)
   - Amerikiečių monetas PERVERTINK:
     * quarters (25¢) -> "25 centų moneta" arba tiesiog adaptuok sumą
     * dimes (10¢) -> "10 centų"
     * nickels (5¢) -> "5 centų"
     * pennies (1¢) -> "centai"
   - Jei monetos skaičius svarbus, išlaikyk matematinę logiką:
     "3 quarters" = 75¢ -> "75 centai" arba "trys 25 centų monetos"

2. VIENETAI (Imperial -> Metrinė):
   - pounds (lbs) -> kg (1 lb ≈ 0.45 kg, SUAPVALINTI iki gražaus skaičiaus)
   - miles -> km (1 mile ≈ 1.6 km)
   - feet -> m (1 ft ≈ 0.3 m)
   - gallons -> l (1 gal ≈ 3.8 l)
   - ounces -> g (1 oz ≈ 28 g)
   - SVARBU: Jei konversija sukuria negražius skaičius (pvz., 2.27 kg),
     PAKEISK originalų skaičių, kad gautas skaičius būtų sveikasis!
     Pvz.: "5 lbs of apples" -> "2 kg obuolių" (ne 2.27 kg)

3. VARDAI:
   - John -> Jonas, Mary -> Marija, Tom -> Tomas
   - Mr. Smith -> Ponas Petraitis, Mrs. Johnson -> Ponia Jonaitienė
   - Naudok įvairius lietuviškus vardus (ne tik Jonas ir Marija)

4. KULTŪRINIS KONTEKSTAS:
   - Baseball -> Krepšinis
   - Football (amerikietis) -> Futbolas
   - Thanksgiving -> Kalėdos arba Velykos
   - Halloween -> Užgavėnės
   - Candy store -> Saldainių parduotuvė
   - Mall -> Prekybos centras
   - High school -> Gimnazija

5. SINTAKSĖ:
   - Neversk pažodžiui! Perrašyk sakinius natūralia lietuvių kalba.
   - "How many times as many..." -> "Kiek kartų daugiau..."
   - "Mary has 3 times as many apples as John" -> "Marija turi 3 kartus daugiau obuolių nei Jonas"

6. SPRENDIMO ŽINGSNIAI:
   - Išversk ir adaptuok visus sprendimo žingsnius
   - Naudok lietuviškus matematinius terminus
   - Užtikrink, kad skaičiai atitinka adaptuotą sąlygą

7. ATSAKYMAS:
   - Grąžink TIK skaičių arba matematinę išraišką
   - Nerašyk "Atsakymas: " priešakyje
   - Jei keitei vienetų, perskaičiuok atsakymą!

=== ATSAKYMO FORMATAS ===

ATSAKYK TIK JSON FORMATU:
{{
    "question_lt": "Pilnas uždavinio tekstas lietuviškai",
    "answer": "Galutinis atsakymas (TIK skaičius ar išraiška)",
    "answer_latex": "Atsakymas LaTeX formatu (jei tinka, kitaip null)",
    "solution_steps": ["1 žingsnis lietuviškai", "2 žingsnis...", ...],
    "tags": ["tema1", "tema2"],
    "units_changed": true,
    "answer_recalculated": true
}}

ATSAKYK TIK JSON, be jokio papildomo teksto."""
            ""
        )

    def _build_variation_prompt(self, problem: TranslatedProblem, count: int) -> str:
        """Sukuria prompt'ą variacijoms generuoti."""
        return f"""Esi matematikos mokytojo asistentas. Sukurk {count} šio uždavinio variacijas su KITAIS SKAIČIAIS.

ORIGINALUS UŽDAVINYS:
{problem.question_lt}

ATSAKYMAS: {problem.answer}

INSTRUKCIJOS:
1. Pakeisk skaičius uždavinyje (bet išlaikyk tą pačią logiką)
2. Gali pakeisti vardus į kitus lietuviškus
3. Apskaičiuok TEISINGUS atsakymus naujiems skaičiams
4. Kiekviena variacija turi būti UNIKALI

ATSAKYK JSON FORMATU:
{{
    "variations": [
        {{
            "question_lt": "Nauja uždavinio versija",
            "answer": "Teisingas atsakymas",
            "solution_steps": ["žingsnis1", "žingsnis2"]
        }},
        ...
    ]
}}

Atsakyk TIK JSON formatu."""

    def _parse_translation_response(
        self, response: str, original: RawProblem
    ) -> TranslatedProblem:
        """Išparsuoja Gemini atsakymą."""
        try:
            # Išvalyti JSON
            json_str = self._extract_json(response)
            data = json.loads(json_str)

            return TranslatedProblem(
                question_lt=data.get("question_lt", ""),
                question_en=original.question,
                answer=data.get("answer", original.answer),
                answer_latex=data.get("answer_latex"),
                solution_steps=data.get("solution_steps", []),
                difficulty=original.difficulty,
                grade_min=original.estimated_grade_min,
                grade_max=original.estimated_grade_max,
                source=original.source,
                source_id=original.source_id,
                tags=data.get("tags", []),
            )

        except json.JSONDecodeError as e:
            logger.warning(f"Nepavyko išparsuoti JSON: {e}")
            return self._fallback_translation(original)

    def _parse_variations_response(
        self, response: str, original: TranslatedProblem
    ) -> list[TranslatedProblem]:
        """Išparsuoja variacijų atsakymą."""
        try:
            json_str = self._extract_json(response)
            data = json.loads(json_str)
            variations = data.get("variations", [])

            result = []
            for i, var in enumerate(variations, 1):
                result.append(
                    TranslatedProblem(
                        question_lt=var.get("question_lt", ""),
                        question_en=original.question_en,
                        answer=var.get("answer", ""),
                        answer_latex=var.get("answer_latex"),
                        solution_steps=var.get("solution_steps", []),
                        difficulty=original.difficulty,
                        grade_min=original.grade_min,
                        grade_max=original.grade_max,
                        source=original.source,
                        source_id=f"{original.source_id}_var{i}",
                        topic_id=original.topic_id,
                        tags=original.tags,
                    )
                )

            return result

        except json.JSONDecodeError:
            logger.warning("Nepavyko išparsuoti variacijų JSON")
            return []

    def _extract_json(self, text: str) -> str:
        """Ištraukia JSON iš teksto."""
        # Bandyti rasti JSON tarp ```
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if match:
            return match.group(1).strip()

        # Bandyti rasti {} arba []
        match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
        if match:
            return match.group(1)

        return text.strip()

    def _fallback_translation(self, problem: RawProblem) -> TranslatedProblem:
        """Bazinis vertimas jei Gemini nepavyksta."""
        # Pakeisti vardus ir valiutą paprastai
        question = problem.question

        for en_name, lt_name in NAMES_MAPPING.items():
            question = re.sub(rf"\b{en_name}\b", lt_name, question, flags=re.IGNORECASE)

        for pattern, replacement in CURRENCY_PATTERNS:
            question = re.sub(pattern, replacement, question, flags=re.IGNORECASE)

        return TranslatedProblem(
            question_lt=question,  # Dar angliškai, bet su pakeistais vardais
            question_en=problem.question,
            answer=problem.answer,
            answer_latex=None,
            solution_steps=problem.solution.split("\n") if problem.solution else [],
            difficulty=problem.difficulty,
            grade_min=problem.estimated_grade_min,
            grade_max=problem.estimated_grade_max,
            source=problem.source,
            source_id=problem.source_id,
            tags=["needs_review"],  # Pažymėti peržiūrai
        )

    async def _detect_topic(self, question: str) -> Optional[str]:
        """Bando nustatyti temą pagal uždavinio turinį."""
        # Paprastas keyword matching
        keywords_to_topic = {
            ("trupmena", "trupmenos", "skaitiklis", "vardiklis"): "fractions",
            ("procentas", "procentai", "procentų"): "percentages",
            ("lygtis", "x =", "raskite x"): "equations",
            ("plotas", "perimetras", "ilgis", "plotis"): "geometry_area",
            ("trikampis", "stačiakampis", "apskritimas"): "geometry_shapes",
            ("greitis", "atstumas", "laikas"): "word_problems_motion",
            ("kaina", "eurų", "€", "nusipirko"): "word_problems_money",
        }

        question_lower = question.lower()

        for keywords, topic_id in keywords_to_topic.items():
            if any(kw in question_lower for kw in keywords):
                return topic_id

        return None


# Singleton instance
_translator_instance: Optional[TaskTranslator] = None


def get_task_translator() -> TaskTranslator:
    """Grąžina TaskTranslator singleton."""
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = TaskTranslator()
    return _translator_instance
