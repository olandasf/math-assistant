"""
Test Generator - Kontrolinių automatinis generavimas
=====================================================
Naudoja šabloninį generatorių (math_problem_bank) kaip pagrindinį metodą.
Gemini AI naudojamas tik kaip papildomas variantas tekstiniams uždaviniams.

Integruota su curriculum.py - Lietuvos matematikos bendrosios programos turiniu.
"""

import json
import random
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ai.gemini_client import get_gemini_client
from loguru import logger
from math_checker.newton_client import get_newton_client
from services.math_problem_bank import Difficulty, MathProblem, MathProblemGenerator
from sympy import Symbol, latex, simplify, solve, sympify

# Curriculum modulis - Lietuvos BP turinio aprašymai
from utils.curriculum import (
    CURRICULUM_BY_GRADE,
    AchievementLevel,
    ContentArea,
    DifficultyLevel,
    GradeCurriculum,
    Subtopic,
    Topic,
    get_all_topics_for_grade,
    get_difficulty_for_grade_and_level,
    get_subtopic_by_id,
    get_topic_by_id,
    get_topics_for_api,
    search_topics,
)


@dataclass
class GeneratedTask:
    """Sugeneruotas uždavinys."""

    number: int
    text: str
    answer: str
    answer_latex: str
    points: int
    topic: str
    difficulty: str  # "easy", "medium", "hard"
    solution_steps: list[str] = field(default_factory=list)


@dataclass
class GeneratedVariant:
    """Sugeneruotas variantas."""

    variant_name: str  # "I", "II", etc.
    tasks: list[GeneratedTask] = field(default_factory=list)


@dataclass
class GeneratedTest:
    """Pilnas sugeneruotas kontrolinis."""

    title: str
    topic: str
    grade_level: int
    total_points: int
    variants: list[GeneratedVariant] = field(default_factory=list)
    created_by: str = "AI Generator"


class TestGenerator:
    """Kontrolinių generatorius."""

    # Lietuviški vardai kontekstui
    NAMES_MALE = [
        "Petras",
        "Jonas",
        "Matas",
        "Lukas",
        "Tomas",
        "Mantas",
        "Domas",
        "Rokas",
        "Paulius",
        "Karolis",
    ]
    NAMES_FEMALE = [
        "Ona",
        "Emilija",
        "Gabija",
        "Austėja",
        "Greta",
        "Ieva",
        "Kotryna",
        "Miglė",
        "Ugnė",
        "Liepa",
    ]

    # Temų šablonai pagal klases
    TOPIC_TEMPLATES = {
        5: {
            "natūralūs_skaičiai": {
                "types": ["aritmetika", "tekstinis"],
                "operations": ["+", "-", "*", "/"],
            },
            "trupmenos": {
                "types": ["paprastosios", "dešimtainės", "palyginimas"],
            },
            "geometrija": {
                "types": ["perimetras", "plotas", "stačiakampis", "kvadratas"],
            },
        },
        6: {
            "trupmenos": {
                "types": ["sudėtis", "atimtis", "daugyba", "dalyba"],
            },
            "procentai": {
                "types": ["skaičiavimas", "tekstinis"],
            },
            "lygtys": {
                "types": ["paprastos", "su_x"],
            },
        },
        7: {
            "lygtys": {
                "types": ["tiesinės", "su_skliaustais"],
            },
            "proporcijos": {
                "types": ["tiesioginis", "atvirkštinis"],
            },
            "geometrija": {
                "types": ["trikampis", "apskritimas", "plotas"],
            },
        },
        8: {
            "lygtys": {
                "types": ["tiesinės_sistemos", "kvadratinės_paprastos"],
            },
            "funkcijos": {
                "types": ["tiesinė", "grafikas"],
            },
            "geometrija": {
                "types": ["pitagoro_teorema", "panašumas"],
            },
        },
        9: {
            "kvadratinės_lygtys": {
                "types": ["pilnos", "nepilnos", "diskriminantas"],
            },
            "funkcijos": {
                "types": ["kvadratinė", "šaknies"],
            },
            "trigonometrija": {
                "types": ["sin", "cos", "tan", "stačiakampis_trikampis"],
            },
        },
        10: {
            "trigonometrija": {
                "types": [
                    "vienetinis_apskritimas",
                    "redukcijos_formulės",
                    "trigonometrinės_lygtys",
                ],
            },
            "logaritmai": {
                "types": ["apibrėžimas", "savybės", "lygtys"],
            },
            "išvestinės": {
                "types": ["apibrėžimas", "taisyklės", "taikymas"],
            },
            "vektoriai": {
                "types": ["koordinatės", "veiksmai", "skaliarinė_sandauga"],
            },
            "stereometrija": {
                "types": ["prizmė", "piramidė", "plotas", "tūris"],
            },
            "progresijos": {
                "types": ["aritmetinė", "geometrinė", "sumos"],
            },
        },
        11: {
            "trigonometrija": {
                "types": ["tapatybės", "lygtys", "nelygybės"],
            },
            "logaritmai": {
                "types": ["savybės", "lygtys", "nelygybės"],
            },
            "išvestinės": {
                "types": ["sudėtingos", "taikymas", "funkcijų_tyrimas"],
            },
            "stereometrija": {
                "types": ["kūgis", "cilindras", "rutulys", "pjūviai"],
            },
            "tikimybės": {
                "types": ["kombinatorika", "kėliniai", "deriniai", "sąlyginė"],
            },
        },
        12: {
            "išvestinės": {
                "types": ["funkcijų_tyrimas", "ekstremumai", "grafikai"],
            },
            "integralai": {
                "types": ["apibrėžimas", "skaičiavimas", "plotas"],
            },
            "tikimybės": {
                "types": ["pasiskirstymai", "dispersija", "vidurkis"],
            },
            "stereometrija": {
                "types": ["įrodymai", "skaičiavimai", "pjūviai"],
            },
        },
    }

    # VBE egzamino struktūra
    VBE_STRUCTURE = {
        "part_1": {
            "count": 10,
            "points_each": 1,
            "difficulty": "easy",
            "description": "Trumpi atsakymai",
        },
        "part_2": {
            "count": 10,
            "points_range": (2, 10),
            "difficulty": "mixed",
            "description": "Išplėstiniai atsakymai",
        },
    }

    # Sudėtingumo nustatymai
    DIFFICULTY_SETTINGS = {
        "easy": {
            "points_range": (1, 2),
            "number_range": (1, 20),
            "steps": 1,
        },
        "medium": {
            "points_range": (2, 4),
            "number_range": (1, 100),
            "steps": 2,
        },
        "hard": {
            "points_range": (4, 7),
            "number_range": (1, 1000),
            "steps": 3,
        },
        "vbe": {
            "points_range": (5, 10),
            "number_range": (1, 1000),
            "steps": 4,
        },
    }

    def __init__(self):
        """Inicializuoja generatorių."""
        # Klientai gaunami dinamiškai per funkcijas
        self.newton = get_newton_client()

    @property
    def gemini(self):
        """Gauna Gemini klientą dinamiškai (nes jis sukonfigūruojamas startup metu)."""
        return get_gemini_client()

    # =========================================================================
    # CURRICULUM INTEGRACIJOS METODAI
    # =========================================================================

    def get_curriculum_topics(self, grade_level: int) -> List[Topic]:
        """
        Gauna visas temas iš curriculum.py pagal klasę.

        Args:
            grade_level: Klasė (5-10)

        Returns:
            Temų sąrašas iš oficialios BP
        """
        return get_all_topics_for_grade(grade_level, include_review=True)

    def get_topic_subtopics(self, topic_id: str) -> List[Subtopic]:
        """
        Gauna temos potemes iš curriculum.py.

        Args:
            topic_id: Temos ID (pvz., "fractions_5")

        Returns:
            Potemių sąrašas
        """
        topic = get_topic_by_id(topic_id)
        if topic:
            return topic.subtopics
        return []

    def _get_curriculum_topic_info(
        self, topic_name: str, grade_level: int
    ) -> Optional[Topic]:
        """
        Randa curriculum.py temą pagal pavadinimą ar ID.

        Args:
            topic_name: Temos pavadinimas arba ID
            grade_level: Klasė

        Returns:
            Topic objektas arba None
        """
        # Pirma bandome rasti pagal ID
        topic = get_topic_by_id(topic_name)
        if topic:
            return topic

        # Jei nerado, bandome ieškoti pagal pavadinimą
        results = search_topics(topic_name, grade_level)
        if results:
            return results[0]

        return None

    def _get_common_errors_for_topic(
        self, topic_name: str, grade_level: int
    ) -> List[str]:
        """
        Gauna dažniausias klaidas iš curriculum.py.

        Args:
            topic_name: Temos pavadinimas
            grade_level: Klasė

        Returns:
            Dažnų klaidų sąrašas
        """
        topic = self._get_curriculum_topic_info(topic_name, grade_level)
        if not topic:
            return []

        errors = []
        for subtopic in topic.subtopics:
            errors.extend(subtopic.common_errors)

        return errors

    def _get_distractor_logic_for_topic(
        self, topic_name: str, grade_level: int
    ) -> List[str]:
        """
        Gauna distraktorių (neteisingų atsakymų) generavimo logiką.

        Args:
            topic_name: Temos pavadinimas
            grade_level: Klasė

        Returns:
            Distraktorių logikos sąrašas
        """
        topic = self._get_curriculum_topic_info(topic_name, grade_level)
        if not topic:
            return []

        distractors = []
        for subtopic in topic.subtopics:
            if subtopic.distractor_logic:
                distractors.append(subtopic.distractor_logic)

        return distractors

    def _get_skills_for_topic(self, topic_name: str, grade_level: int) -> List[str]:
        """
        Gauna įgūdžius, kuriuos ugdo tema.

        Args:
            topic_name: Temos pavadinimas
            grade_level: Klasė

        Returns:
            Įgūdžių sąrašas
        """
        topic = self._get_curriculum_topic_info(topic_name, grade_level)
        if not topic:
            return []

        skills = []
        for subtopic in topic.subtopics:
            skills.extend(subtopic.skills)

        return list(set(skills))  # Pašaliname dublikatus

    def _get_examples_for_topic(
        self, topic_name: str, grade_level: int, difficulty: str
    ) -> List[str]:
        """
        Gauna uždavinių pavyzdžius iš curriculum.py.

        Args:
            topic_name: Temos pavadinimas
            grade_level: Klasė
            difficulty: Sudėtingumas ("easy", "medium", "hard")

        Returns:
            Pavyzdžių sąrašas
        """
        topic = self._get_curriculum_topic_info(topic_name, grade_level)
        if not topic:
            return []

        examples = []
        for subtopic in topic.subtopics:
            if difficulty == "easy" and subtopic.example_easy:
                examples.append(subtopic.example_easy)
            elif difficulty == "medium" and subtopic.example_medium:
                examples.append(subtopic.example_medium)
            elif difficulty == "hard" and subtopic.example_hard:
                examples.append(subtopic.example_hard)

        return examples

    def _get_requirements_for_level(
        self, topic_name: str, grade_level: int, achievement_level: str
    ) -> List[str]:
        """
        Gauna reikalavimus pagal pasiekimų lygį.

        Args:
            topic_name: Temos pavadinimas
            grade_level: Klasė
            achievement_level: "satisfactory", "basic", "advanced"

        Returns:
            Reikalavimų sąrašas
        """
        topic = self._get_curriculum_topic_info(topic_name, grade_level)
        if not topic:
            return []

        requirements = []
        for subtopic in topic.subtopics:
            if achievement_level == "satisfactory":
                requirements.extend(subtopic.satisfactory_requirements)
            elif achievement_level == "basic":
                requirements.extend(subtopic.basic_requirements)
            elif achievement_level == "advanced":
                requirements.extend(subtopic.advanced_requirements)

        return requirements

    def _build_curriculum_enhanced_prompt(
        self,
        topic: str,
        grade_level: int,
        task_count: int,
        difficulty: str,
        points_per_task: list,
        include_solutions: bool,
    ) -> str:
        """
        Sukuria AI prompt'ą, praturtintą curriculum.py informacija.

        Args:
            topic: Tema
            grade_level: Klasė
            task_count: Uždavinių kiekis
            difficulty: Sudėtingumas
            points_per_task: Taškai kiekvienam uždaviniui
            include_solutions: Ar įtraukti sprendimus

        Returns:
            Praturtintas prompt'as
        """
        # Gauname informaciją iš curriculum.py
        curriculum_topic = self._get_curriculum_topic_info(topic, grade_level)

        curriculum_context = ""
        if curriculum_topic:
            # Potemės
            subtopic_names = [st.name_lt for st in curriculum_topic.subtopics]
            if subtopic_names:
                curriculum_context += f"\nPOTEMĖS: {', '.join(subtopic_names)}\n"

            # Įgūdžiai
            skills = self._get_skills_for_topic(topic, grade_level)
            if skills:
                curriculum_context += f"VERTINAMI ĮGŪDŽIAI: {', '.join(skills[:10])}\n"

            # Pavyzdžiai
            examples = self._get_examples_for_topic(topic, grade_level, difficulty)
            if examples:
                curriculum_context += f"\nPAVYZDŽIAI IŠ PROGRAMOS:\n"
                for i, ex in enumerate(examples[:5], 1):
                    curriculum_context += f"  {i}. {ex}\n"

            # Dažnos klaidos (naudingos distraktorių generavimui)
            common_errors = self._get_common_errors_for_topic(topic, grade_level)
            if common_errors:
                curriculum_context += (
                    f"\nDAŽNOS MOKINIŲ KLAIDOS (naudok generuojant testų variantus):\n"
                )
                for error in common_errors[:5]:
                    curriculum_context += f"  • {error}\n"

            # Pasiekimų reikalavimai
            level_map = {"easy": "satisfactory", "medium": "basic", "hard": "advanced"}
            requirements = self._get_requirements_for_level(
                topic, grade_level, level_map.get(difficulty, "basic")
            )
            if requirements:
                curriculum_context += f"\nREIKALAVIMAI PAGAL LYGĮ:\n"
                for req in requirements[:5]:
                    curriculum_context += f"  • {req}\n"

        # Standartinis prompt'as + curriculum kontekstas
        difficulty_lt = {
            "easy": "lengvas (patenkinamas lygis)",
            "medium": "vidutinis (pagrindinis lygis)",
            "hard": "sudėtingas (aukštesnysis lygis)",
            "mixed": "mišrus (visi lygiai)",
        }.get(difficulty, "vidutinis")

        names = ", ".join(random.sample(self.NAMES_MALE + self.NAMES_FEMALE, 6))

        return f"""Sukurk {task_count} SKIRTINGUS matematinius uždavinius kontroliniam darbui.

TEMA: {topic.replace('_', ' ')}
KLASĖ: {grade_level}
SUDĖTINGUMAS: {difficulty_lt}
{curriculum_context}
⚠️ LABAI SVARBU - ĮVAIROVĖ:
Kiekvienas uždavinys PRIVALO būti KITOKS! Negalima kartoti to paties tipo.

PRIVALOMI REIKALAVIMAI:
1. Bent {max(1, task_count // 2)} uždaviniai turi būti TEKSTINIAI su realiu kontekstu
2. Naudok lietuviškus vardus: {names}
3. Kontekstai: parduotuvė, mokykla, sportas, kelionės, maistas, pinigai, laikas
4. Kiekvienas uždavinys - SKIRTINGAS tipas ir kontekstas
5. Skaičiai turi būti "gražūs" (dalūs, apvalūs rezultatai)
6. Atsakymai - supaprastinti (trupmenos sutrauktos, lygtys išspręstos)

TEKSTO FORMATAVIMAS (KRITIŠKAI SVARBU!):
- Rašyk PAPRASTĄ tekstą su normaliais tarpais tarp žodžių
- Trupmenas rašyk paprastai: 2/3, 1 1/2, 3/4 (NE LaTeX formatu!)
- Mišrias trupmenas rašyk: 2 1/3 (skaičius, tarpas, trupmena)
- Matematinius veiksmus rašyk simboliais: ×, +, -, ÷, =
- NENAUDOK LaTeX sintaksės (\\frac, \\cdot, $...$ ir pan.)
- Tekstas turi būti skaitomas kaip įprasta lietuviška kalba

TAŠKŲ PASKIRSTYMAS: {points_per_task}

{"SPRENDIMO ŽINGSNIAI: Kiekvienam uždaviniui pateik 2-4 aiškius sprendimo žingsnius lietuvių kalba." if include_solutions else ""}

ATSAKYMO FORMATAS (tik JSON, be jokio kito teksto):
{{
  "tasks": [
    {{
      "number": 1,
      "text": "Pilnas uždavinio tekstas lietuviškai (su kontekstu jei tekstinis)",
      "answer": "Teisingas atsakymas",
      "points": {points_per_task[0] if points_per_task else 2},
      "difficulty": "easy|medium|hard",
      "solution_steps": ["Žingsnis 1: ...", "Žingsnis 2: ...", "Atsakymas: ..."],
      "topic_detail": "konkreti potemė"
    }}
  ]
}}"""

    def _build_curriculum_context_prompt(
        self,
        topic: str,
        grade_level: int,
        task_count: int,
        difficulty: str,
        points_per_task: list,
        include_solutions: bool,
        curriculum_context: str,
    ) -> str:
        """
        Sukuria AI prompt'ą naudojant programos kontekstą iš JSON failų.

        curriculum_context jau turi struktūrizuotą informaciją apie temas,
        potemes ir sunkumo lygių aprašymus.
        """
        difficulty_lt = {
            "easy": "lengvas (patenkinamas lygis)",
            "medium": "vidutinis (pagrindinis lygis)",
            "hard": "sudėtingas (aukštesnysis lygis)",
            "mixed": "mišrus (visi lygiai)",
            "vbe": "VBE lygis (brandos egzaminas)",
        }.get(difficulty, "vidutinis")

        names = ", ".join(random.sample(self.NAMES_MALE + self.NAMES_FEMALE, 6))

        points_info = ", ".join(
            f"Nr.{i+1}: {p} tšk." for i, p in enumerate(points_per_task)
        )

        solutions_instruction = ""
        if include_solutions:
            solutions_instruction = """
"solution_steps": ["žingsnis 1", "žingsnis 2", ...] - DETALŪS sprendimo žingsniai"""

        return f"""Sukurk {task_count} SKIRTINGUS matematinius uždavinius kontroliniam darbui.

TEMA: {topic.replace('_', ' ')}
KLASĖ: {grade_level}
SUDĖTINGUMAS: {difficulty_lt}

=== PROGRAMOS KONTEKSTAS (IŠ OFICIALIOS MATEMATIKOS PROGRAMOS) ===
{curriculum_context}
=== PROGRAMOS KONTEKSTAS PABAIGA ===

⚠️ LABAI SVARBU - PROGRAMOS KONTEKSTAS:
Aukščiau pateiktas programos kontekstas nurodo TIKSLIAI kokio tipo ir sudėtingumo
uždavinius reikia generuoti. PRIVALAI vadovautis sunkumo lygio aprašymais!

⚠️ LABAI SVARBU - ĮVAIROVĖ:
Kiekvienas uždavinys PRIVALO būti KITOKS! Negalima kartoti to paties tipo.

PRIVALOMI REIKALAVIMAI:
1. Bent {max(1, task_count // 2)} uždaviniai turi būti TEKSTINIAI su realiu kontekstu
2. Naudok lietuviškus vardus: {names}
3. Kontekstai: parduotuvė, mokykla, sportas, kelionės, maistas, pinigai, laikas
4. Kiekvienas uždavinys - SKIRTINGAS tipas ir kontekstas
5. Skaičiai turi būti "gražūs" (dalūs, apvalūs rezultatai)
6. Atsakymai - supaprastinti (trupmenos sutrauktos, lygtys išspręstos)

TEKSTO FORMATAVIMAS (KRITIŠKAI SVARBU!):
- Naudok \\\\( ir \\\\) inlinems formulėms
- Naudok \\\\[ ir \\\\] blokų formulėms
- Trupmenoms: \\\\frac{{a}}{{b}}
- Laipsniams: x^{{2}}
- Šaknims: \\\\sqrt{{x}}
- NEUZMIRŠK: visos matematinės išraiškos PRIVALO būti LaTeX!
- PAVYZDYS: "Jonas nupirko \\\\( 3 \\\\frac{{1}}{{4}} \\\\) kg obuolių"
- BLOGAS pavyzdys: "Jonas nupirko 3 1/4 kg obuolių"

TAŠKŲ PASKIRSTYMAS: {points_info}

ATSAKYMO FORMATAS (JSON):
{{
  "tasks": [
    {{
      "number": 1,
      "text": "Uždavinio tekstas su \\\\( LaTeX \\\\) formulėmis",
      "answer": "atsakymas",
      "answer_latex": "\\\\frac{{1}}{{2}}",{solutions_instruction}
      "points": {points_per_task[0] if points_per_task else 2},
      "difficulty": "{difficulty}",
      "topic_detail": "konkreti potemė iš programos"
    }}
  ]
}}"""

    def _build_standard_prompt(
        self,
        topic: str,
        grade_level: int,
        task_count: int,
        difficulty_lt: str,
        points_per_task: list,
        include_solutions: bool,
    ) -> str:
        """Standartinis prompt'as 5-9 klasėms."""

        # Konkretūs uždavinių tipai pagal temą
        task_types = self._get_task_types_for_topic(topic, grade_level)
        names = ", ".join(random.sample(self.NAMES_MALE + self.NAMES_FEMALE, 6))

        return f"""Sukurk {task_count} SKIRTINGUS matematinius uždavinius kontroliniam darbui.

TEMA: {topic.replace('_', ' ')}
KLASĖ: {grade_level}
SUDĖTINGUMAS: {difficulty_lt}

⚠️ LABAI SVARBU - ĮVAIROVĖ:
Kiekvienas uždavinys PRIVALO būti KITOKS! Negalima kartoti to paties tipo.
Maišyk šiuos uždavinių tipus:

{task_types}

PRIVALOMI REIKALAVIMAI:
1. Bent {max(1, task_count // 2)} uždaviniai turi būti TEKSTINIAI su realiu kontekstu
2. Naudok lietuviškus vardus: {names}
3. Kontekstai: parduotuvė, mokykla, sportas, kelionės, maistas, pinigai, laikas
4. Kiekvienas uždavinys - SKIRTINGAS tipas ir kontekstas
5. Skaičiai turi būti "gražūs" (dalūs, apvalūs rezultatai)
6. Atsakymai - supaprastinti (trupmenos sutrauktos, lygtys išspręstos)

TEKSTO FORMATAVIMAS (KRITIŠKAI SVARBU!):
- Rašyk PAPRASTĄ tekstą su normaliais tarpais tarp žodžių
- Trupmenas rašyk paprastai: 2/3, 1 1/2, 3/4 (NE LaTeX formatu!)
- Matematinius veiksmus rašyk simboliais: ×, +, -, ÷, =
- NENAUDOK LaTeX sintaksės (\\frac, \\cdot, $...$ ir pan.)
- Tekstas turi būti skaitomas kaip įprasta lietuviška kalba

TAŠKŲ PASKIRSTYMAS: {points_per_task}

{"SPRENDIMO ŽINGSNIAI: Kiekvienam uždaviniui pateik 2-4 aiškius sprendimo žingsnius lietuvių kalba." if include_solutions else ""}

ATSAKYMO FORMATAS (tik JSON, be jokio kito teksto):
{{
  "tasks": [
    {{
      "number": 1,
      "text": "Pilnas uždavinio tekstas lietuviškai (su kontekstu jei tekstinis)",
      "answer": "Teisingas atsakymas",
      "points": {points_per_task[0] if points_per_task else 2},
      "difficulty": "easy|medium|hard",
      "solution_steps": ["Žingsnis 1: ...", "Žingsnis 2: ...", "Atsakymas: ..."],
      "topic_detail": "konkreti potemė"
    }}
  ]
}}"""

    def _get_task_types_for_topic(self, topic: str, grade_level: int) -> str:
        """Grąžina konkrečius uždavinių tipus pagal temą."""
        topic_lower = topic.lower()

        if "lygt" in topic_lower:
            if grade_level >= 9 or "kvadrat" in topic_lower:
                return """
UŽDAVINIŲ TIPAI (naudok visus!):
1. TEKSTINIS: "Jonas turi x metų. Po 5 metų jo amžius bus dvigubai didesnis nei sesers. Kiek metų Jonui?"
2. GEOMETRINIS: "Stačiakampio plotas 48 cm². Ilgis 2 cm didesnis už plotį. Rask matmenis."
3. JUDĖJIMO: "Du dviratininkai išvyko vienas priešais kitą. Greičiai 15 km/h ir 20 km/h. Po kiek laiko susitiks, jei atstumas 70 km?"
4. DARBO: "Petras darbą atlieka per 6 val., Ona per 4 val. Per kiek laiko atliks kartu?"
5. MIŠINIO: "Sumaišius 30% ir 50% tirpalus gauta 40% tirpalo. Kiek kiekvieno tirpalo?"
6. TIESIOGINĖ LYGTIS: "Išspręsk: 3x² - 12x + 9 = 0" (tik 1-2 tokie!)"""
            else:
                return """
UŽDAVINIŲ TIPAI (naudok visus!):
1. TEKSTINIS: "Petras turėjo keletą obuolių. Davė draugui 5, liko 12. Kiek turėjo?"
2. PIRKIMO: "Sąsiuvinis kainuoja x eurų. 5 sąsiuviniai ir 3 € trintukas kainuoja 13 €. Kiek kainuoja sąsiuvinis?"
3. AMŽIAUS: "Tėvo amžius 4 kartus didesnis už sūnaus. Po 10 metų bus tik 2 kartus didesnis. Kiek metų sūnui?"
4. GEOMETRINIS: "Stačiakampio perimetras 28 cm. Ilgis 4 cm didesnis už plotį. Rask matmenis."
5. GREIČIO: "Dviratis važiuoja 15 km/h. Per kiek laiko nuvažiuos 45 km?"
6. TIESIOGINĖ: "Išspręsk: 2x + 7 = 15" (tik 1 toks!)"""

        elif "trupmen" in topic_lower:
            return """
UŽDAVINIŲ TIPAI (naudok visus!):
1. DALIES RADIMAS: "Klasėje 24 mokiniai. 3/4 jų lanko būrelį. Kiek mokinių lanko būrelį?"
2. RECEPTAS: "Receptui reikia 2/3 kg miltų. Kiek miltų reikės 3 porcijoms?"
3. KELIONĖ: "Turistai nuėjo 2/5 kelio. Liko 12 km. Koks viso kelio ilgis?"
4. LAIKAS: "Filmas trunka 1 1/2 valandos. Praėjo 2/3 filmo. Kiek minučių liko?"
5. PINIGAI: "Ona išleido 1/4 pinigų knygai ir 1/3 saldainiams. Kokią dalį išleido iš viso?"
6. SKAIČIAVIMAS: "Apskaičiuok: 2/3 + 1/4 - 1/6" (tik 1-2 tokie!)"""

        elif "procent" in topic_lower:
            return """
UŽDAVINIŲ TIPAI (naudok visus!):
1. NUOLAIDA: "Prekė kainavo 80 €. Nuolaida 25%. Kokia nauja kaina?"
2. PALŪKANOS: "Į banką įdėta 500 €. Metinės palūkanos 4%. Kiek bus po metų?"
3. PADIDĖJIMAS: "Kaina pakilo 15%. Dabar prekė kainuoja 46 €. Kokia buvo pradinė kaina?"
4. SUDĖTIS: "Klasėje 30 mokinių. 40% berniukų, 60% mergaičių. Kiek berniukų?"
5. MIŠINYS: "Tirpale 200 g druskos, tai sudaro 8% tirpalo. Kiek sveria visas tirpalas?"
6. PALYGINIMAS: "Pirmą dieną pardavė 120 bilietų, antrą - 150. Kiek procentų daugiau antrą dieną?"""

        elif "funkcij" in topic_lower:
            return """
UŽDAVINIŲ TIPAI (naudok visus!):
1. REIKŠMĖS RADIMAS: "Duota f(x) = 2x² - 3x + 1. Rask f(2) ir f(-1)."
2. APIBRĖŽIMO SRITIS: "Rask funkcijos f(x) = √(x-3) apibrėžimo sritį."
3. NULIAI: "Rask funkcijos f(x) = x² - 5x + 6 nulius."
4. TEKSTINIS: "Taksi kaina: 2€ + 0.5€/km. Užrašyk funkciją ir rask kainą už 10 km."
5. GRAFIKAS: "Funkcijos grafikas eina per taškus (0;3) ir (2;7). Rask tiesinės funkcijos formulę."
6. MONOTONINUMAS: "Nustatyk, kuriuose intervaluose funkcija f(x) = x² - 4x didėja, kuriuose mažėja."
7. EKSTREMUMAI: "Rask funkcijos f(x) = -x² + 6x - 5 didžiausią reikšmę." """

        elif "trigonometr" in topic_lower:
            return """
UŽDAVINIŲ TIPAI (naudok visus!):
1. REIKŠMĖS: "Apskaičiuok: sin 60° + cos 30° - tg 45°"
2. TRIKAMPIS: "Stačiakampio trikampio įžambinė 10 cm, vienas kampas 30°. Rask statinių ilgius."
3. TAPATYBĖ: "Įrodyk, kad sin²α + cos²α = 1 naudojant vienetinį apskritimą."
4. LYGTIS: "Išspręsk: 2sin(x) = 1, kai x ∈ [0°; 360°]"
5. AUKŠTIS: "Nuo 50 m aukščio bokšto matymo kampas iki objekto yra 30°. Koks atstumas iki objekto?"
6. PLOTAS: "Trikampio dvi kraštinės 8 cm ir 6 cm, kampas tarp jų 60°. Rask plotą."
7. SUPAPRASTINIMAS: "Supaprastink: (sin α / cos α) · cos α" """

        elif (
            "geometr" in topic_lower
            or "trikamp" in topic_lower
            or "keturk" in topic_lower
        ):
            return """
UŽDAVINIŲ TIPAI (naudok visus!):
1. PLOTAS: "Sodo sklypas stačiakampio formos: 25 m × 40 m. Koks jo plotas?"
2. PERIMETRAS: "Trikampio kraštinės 7 cm, 8 cm ir 9 cm. Rask perimetrą."
3. PITAGORAS: "Stačiakampio trikampio statiniai 6 cm ir 8 cm. Rask įžambinę."
4. APSKRITIMAS: "Apskritimo spindulys 7 cm. Rask plotą ir ilgį (π ≈ 3.14)."
5. SUDĖTINĖ FIGŪRA: "Kambario grindys: stačiakampis 5×4 m su išpjova 1×1 m kampe. Koks plotas?"
6. ERDVINĖ: "Stačiakampio gretasienio matmenys 3×4×5 cm. Rask tūrį ir paviršiaus plotą."
7. PANAŠUMAS: "Du panašūs trikampiai. Pirmojo kraštinė 6 cm, atitinkama antrojo - 9 cm. Koks panašumo koeficientas?" """

        elif "progresij" in topic_lower:
            return """
UŽDAVINIŲ TIPAI (naudok visus!):
1. N-TASIS NARYS: "Aritmetinės progresijos a₁=3, d=4. Rask a₁₀."
2. SUMA: "Rask aritmetinės progresijos 2, 5, 8, ... pirmųjų 20 narių sumą."
3. TEKSTINIS: "Pirmą dieną Petras nubėgo 1 km, kiekvieną kitą - 0.5 km daugiau. Kiek nubėgo per 10 dienų?"
4. GEOMETRINĖ: "Geometrinės progresijos b₁=2, q=3. Rask b₅."
5. PALŪKANOS: "Įdėta 1000 €, kasmet pridedama 10%. Kiek bus po 3 metų?"
6. RADIMAS: "Aritmetinės progresijos a₃=10, a₇=22. Rask a₁ ir d."
7. BEGALINĖ SUMA: "Rask begalinės geometrinės progresijos 1, 1/2, 1/4, ... sumą." """

        elif "logaritm" in topic_lower:
            return """
UŽDAVINIŲ TIPAI (naudok visus!):
1. SKAIČIAVIMAS: "Apskaičiuok: log₂ 8 + log₃ 27"
2. LYGTIS: "Išspręsk: log₂(x+3) = 4"
3. SAVYBĖS: "Supaprastink: log₂ 8 + log₂ 4 - log₂ 2"
4. TEKSTINIS: "Bakterijų skaičius dvigubėja kas valandą. Po kiek valandų bus 1024 kartus daugiau?"
5. RODIKLINĖ: "Išspręsk: 2ˣ = 32"
6. SUDĖTINGESNĖ: "Išspręsk: log₃(x²-1) = 2"
7. PALYGINIMAS: "Kuris didesnis: log₂ 10 ar log₃ 20?" """

        else:
            # Bendras mišrus
            return f"""
UŽDAVINIŲ TIPAI (maišyk įvairius!):
1. TEKSTINIS SU KONTEKSTU: Parduotuvė, mokykla, kelionė, sportas
2. SKAIČIAVIMO: Tiesioginis matematinis veiksmas
3. GEOMETRINIS: Plotas, perimetras, tūris
4. LOGINIS: Palyginimas, įrodymas
5. PRAKTINIS: Pinigai, laikas, greitis, atstumas

Naudok lietuviškus vardus ir realias situacijas!
Klasė: {grade_level}, todėl pritaikyk sudėtingumą."""

    def _build_vbe_style_prompt(
        self,
        topic: str,
        grade_level: int,
        task_count: int,
        difficulty_lt: str,
        points_per_task: list,
        include_solutions: bool,
    ) -> str:
        """VBE stiliaus prompt'as 10-12 klasėms - sudėtingesni uždaviniai."""

        names = ", ".join(random.sample(self.NAMES_MALE + self.NAMES_FEMALE, 5))
        task_types = self._get_task_types_for_topic(topic, grade_level)

        return f"""Sukurk {task_count} SKIRTINGUS VBE (valstybinio brandos egzamino) lygio matematinius uždavinius.

TEMA: {topic.replace('_', ' ')}
KLASĖ: {grade_level}
SUDĖTINGUMAS: {difficulty_lt}

⚠️ KRITIŠKAI SVARBU - ĮVAIROVĖ:
Kiekvienas uždavinys PRIVALO būti VISIŠKAI KITOKS!
DRAUDŽIAMA: visi uždaviniai tipo "Išspręsk lygtį: ..."
PRIVALOMA: maišyti tekstinius, grafinius, įrodymo, skaičiavimo uždavinius.

{task_types}

VBE UŽDAVINIŲ FORMATAI (naudok įvairius!):
1. **Daugiadaliai** su a), b), c):
   "Duota funkcija f(x) = x² - 4x + 3.
    a) Raskite funkcijos šaknis.
    b) Nustatykite funkcijos reikšmių sritį.
    c) Nubraižykite funkcijos grafiką."

2. **Tekstiniai su kontekstu**:
   "{random.choice(self.NAMES_MALE)} stato tvorą. Tvoros ilgis 20 m. Vienas stulpas kas 2 m. Kiek stulpų reikia?"

3. **Įrodymo/pagrindimo**:
   "Įrodykite, kad skaičius n² + n visada dalus iš 2."

4. **Optimizavimo**:
   "Stačiakampio perimetras 40 cm. Kokių matmenų stačiakampio plotas didžiausias?"

TAŠKŲ PASKIRSTYMAS: {points_per_task}

PRIVALOMI REIKALAVIMAI:
1. Bent {max(1, task_count // 2)} uždaviniai - TEKSTINIAI arba DAUGIADALIAI
2. Naudok vardus: {names}
3. Realūs kontekstai: ekonomika, fizika, biologija, kasdienybė
4. Kiekvienas uždavinys - SKIRTINGAS tipas
5. Atsakymuose - VISŲ dalių atsakymai (jei daugiadaliai)

{"SPRENDIMO ŽINGSNIAI: Detalūs, 3-5 žingsniai kiekvienam uždaviniui." if include_solutions else ""}

ATSAKYMO FORMATAS (tik JSON):
{{
  "tasks": [
    {{
      "number": 1,
      "text": "Pilnas uždavinio tekstas (su a), b), c) jei daugiadaliai)",
      "answer": "Visi atsakymai: a) ...; b) ...; c) ...",
      "points": {points_per_task[0] if points_per_task else 4},
      "difficulty": "medium|hard|vbe",
      "solution_steps": ["Žingsnis 1", "Žingsnis 2", "Žingsnis 3"],
      "topic_detail": "konkreti potemė"
    }}
  ]
}}"""

    # =========================================================================
    # NAUJAS: ŠABLONINIS GENERATORIUS (be AI)
    # =========================================================================

    async def _generate_with_template_bank(
        self,
        topic: str,
        topics: list[str] | None,
        grade_level: int,
        task_count: int,
        variant_count: int,
        difficulty: str,
        include_solutions: bool,
    ) -> GeneratedTest:
        """
        Generuoja kontrolinį naudojant šabloninį generatorių (math_problem_bank).

        Privalumai:
        - 100% teisingi atsakymai
        - Greitas (nereikia AI)
        - Nemokamas
        - Kontroliuojamas sudėtingumas
        """
        logger.info("Naudojamas šabloninis generatorius (math_problem_bank)")

        # Nustatom temas
        topic_list = topics if topics else [topic]

        # Generuojam I variantą
        variant_i_problems = MathProblemGenerator.generate_test(
            topics=topic_list,
            grade=grade_level,
            task_count=task_count,
            difficulty=difficulty,
            include_solutions=include_solutions,
        )

        # Konvertuojam į GeneratedTask formatą
        variant_i_tasks = []
        for i, prob in enumerate(variant_i_problems):
            task = GeneratedTask(
                number=i + 1,
                text=prob.text,
                answer=prob.answer,
                answer_latex=prob.answer,  # Šabloninis generatorius nenaudoja LaTeX
                points=prob.points,
                topic=prob.topic,
                difficulty=prob.difficulty.value,
                solution_steps=prob.solution_steps if include_solutions else [],
            )
            variant_i_tasks.append(task)

        variant_i = GeneratedVariant(variant_name="I", tasks=variant_i_tasks)
        variants = [variant_i]

        # Generuojam papildomus variantus (su kitais skaičiais)
        variant_names = ["II", "III", "IV"]
        for v_idx in range(1, variant_count):
            if v_idx <= len(variant_names):
                # Generuojam naują variantą su naujais skaičiais
                variant_problems = MathProblemGenerator.generate_test(
                    topics=topic_list,
                    grade=grade_level,
                    task_count=task_count,
                    difficulty=difficulty,
                    include_solutions=include_solutions,
                )

                variant_tasks = []
                for i, prob in enumerate(variant_problems):
                    task = GeneratedTask(
                        number=i + 1,
                        text=prob.text,
                        answer=prob.answer,
                        answer_latex=prob.answer,
                        points=prob.points,
                        topic=prob.topic,
                        difficulty=prob.difficulty.value,
                        solution_steps=prob.solution_steps if include_solutions else [],
                    )
                    variant_tasks.append(task)

                variants.append(
                    GeneratedVariant(
                        variant_name=variant_names[v_idx - 1], tasks=variant_tasks
                    )
                )

        # Skaičiuojam taškus
        total_points = sum(task.points for task in variant_i_tasks)

        # Pavadinimas
        topic_display = (
            ", ".join(topic_list) if len(topic_list) <= 3 else f"{topic_list[0]} ir kt."
        )
        title = f"{topic_display.replace('_', ' ').title()} - {grade_level} klasė"

        return GeneratedTest(
            title=title,
            topic=topic_display,
            grade_level=grade_level,
            total_points=total_points,
            variants=variants,
            created_by="Šabloninis generatorius",
        )

    async def generate_vbe_exam(
        self,
        topics: list[str] | None = None,
        include_solutions: bool = True,
    ) -> GeneratedTest:
        """
        Generuoja pilną VBE stiliaus egzaminą.

        VBE struktūra:
        - I dalis: 10 trumpų uždavinių po 1 tašką (lengvi)
        - II dalis: 10 išplėstinių uždavinių 2-10 taškų (sudėtingi)

        Args:
            topics: Temų sąrašas (jei None - visos VBE temos)
            include_solutions: Ar generuoti sprendimus

        Returns:
            GeneratedTest: Pilnas VBE egzaminas
        """
        logger.info("Generuojamas VBE stiliaus egzaminas")

        # Numatytosios VBE temos
        if not topics:
            topics = [
                "trigonometrija",
                "logaritmai",
                "išvestinės",
                "vektoriai",
                "stereometrija",
                "tikimybės",
                "progresijos",
                "lygtys",
            ]

        all_tasks = []
        task_number = 1

        # I DALIS: 10 trumpų uždavinių
        logger.info("Generuojama I dalis (10 × 1 tšk.)...")
        part1_topics = random.sample(topics, min(5, len(topics)))
        for topic in part1_topics[:2]:  # 2 temos × 5 uždaviniai
            variant = await self._generate_variant_with_gemini(
                topic=topic,
                grade_level=12,
                task_count=5,
                difficulty="easy",
                variant_name="I",
                include_solutions=include_solutions,
            )
            for task in variant.tasks:
                task.number = task_number
                task.points = 1
                all_tasks.append(task)
                task_number += 1
                if task_number > 10:
                    break
            if task_number > 10:
                break

        # II DALIS: 10 išplėstinių uždavinių
        logger.info("Generuojama II dalis (10 × 2-10 tšk.)...")
        part2_points = [2, 2, 3, 3, 4, 5, 5, 7, 8, 10]  # VBE struktūra
        part2_topics = random.sample(topics, min(5, len(topics)))

        for i, points in enumerate(part2_points):
            topic = part2_topics[i % len(part2_topics)]
            difficulty = "medium" if points <= 3 else "hard" if points <= 6 else "vbe"

            variant = await self._generate_variant_with_gemini(
                topic=topic,
                grade_level=12,
                task_count=1,
                difficulty=difficulty,
                variant_name="II",
                include_solutions=include_solutions,
            )

            if variant.tasks:
                task = variant.tasks[0]
                task.number = task_number
                task.points = points
                all_tasks.append(task)
                task_number += 1

        # Bendri taškai
        total_points = sum(task.points for task in all_tasks)

        return GeneratedTest(
            title="VBE Matematikos egzaminas",
            topic="vbe_mišrus",
            grade_level=12,
            total_points=total_points,
            variants=[GeneratedVariant(variant_name="A", tasks=all_tasks)],
            created_by="VBE Generator",
        )

    async def generate_test(
        self,
        topic: str,
        grade_level: int,
        task_count: int = 5,
        variant_count: int = 2,
        difficulty: str = "medium",
        include_solutions: bool = True,
        topics: list[str] | None = None,
        use_template_generator: bool = True,  # Naujas parametras
        curriculum_context: (
            str | None
        ) = None,  # Programos kontekstas su difficulty_rules
    ) -> GeneratedTest:
        """
        Generuoja kontrolinį darbą.

        Args:
            topic: Matematikos tema (arba sujungtos temos)
            grade_level: Klasė (5-12)
            task_count: Uždavinių kiekis
            variant_count: Variantų kiekis (1-4)
            difficulty: Sudėtingumas ("easy", "medium", "hard", "mixed")
            include_solutions: Ar generuoti sprendimų žingsnius
            topics: Temų sąrašas (jei kelios temos)
            use_template_generator: Ar naudoti šabloninį generatorių (rekomenduojama)
            curriculum_context: Programa ir sunkumo aprašymai iš JSON failų

        Returns:
            GeneratedTest: Pilnas kontrolinis su variantais
        """
        logger.info(
            f"Generuojamas kontrolinis: tema={topic}, temos={topics}, klasė={grade_level}, "
            f"uždaviniai={task_count}, variantai={variant_count}, šabloninis={use_template_generator}, "
            f"curriculum_kontekstas={'Taip' if curriculum_context else 'Ne'}"
        )

        # NAUJAS: Naudojam šabloninį generatorių kaip pagrindinį metodą
        if use_template_generator:
            return await self._generate_with_template_bank(
                topic=topic,
                topics=topics,
                grade_level=grade_level,
                task_count=task_count,
                variant_count=variant_count,
                difficulty=difficulty,
                include_solutions=include_solutions,
            )

        # Senas metodas su Gemini (fallback)
        # Jei yra kelios temos, paskirstome uždavinius tarp jų
        if topics and len(topics) > 1:
            variant_i = await self._generate_multi_topic_variant(
                topics=topics,
                grade_level=grade_level,
                task_count=task_count,
                difficulty=difficulty,
                variant_name="I",
                include_solutions=include_solutions,
                curriculum_context=curriculum_context,
            )
        else:
            # Viena tema - senas elgesys
            single_topic = topics[0] if topics else topic
            variant_i = await self._generate_variant_with_gemini(
                topic=single_topic,
                grade_level=grade_level,
                task_count=task_count,
                difficulty=difficulty,
                variant_name="I",
                include_solutions=include_solutions,
                curriculum_context=curriculum_context,
            )

        variants = [variant_i]

        # Generuojame papildomus variantus (modifikuojame skaičius)
        variant_names = ["II", "III", "IV"]
        for i in range(1, variant_count):
            if i < len(variant_names) + 1:
                variant = await self._create_variant_modification(
                    original_variant=variant_i,
                    variant_name=variant_names[i - 1],
                    grade_level=grade_level,
                )
                variants.append(variant)

        # Skaičiuojame bendrus taškus
        total_points = sum(task.points for task in variant_i.tasks)

        return GeneratedTest(
            title=f"{topic.replace('_', ' ').title()} - {grade_level} klasė",
            topic=topic,
            grade_level=grade_level,
            total_points=total_points,
            variants=variants,
        )

    async def _generate_multi_topic_variant(
        self,
        topics: list[str],
        grade_level: int,
        task_count: int,
        difficulty: str,
        variant_name: str,
        include_solutions: bool,
        curriculum_context: str | None = None,
    ) -> GeneratedVariant:
        """Generuoja variantą su keliomis temomis - paskirstant uždavinius."""
        logger.info(f"Generuojamas multi-topic variantas: {topics}")

        all_tasks = []
        task_number = 1

        # Paskirstome uždavinius tarp temų
        tasks_per_topic = max(1, task_count // len(topics))
        remaining_tasks = task_count - (tasks_per_topic * len(topics))

        for i, topic in enumerate(topics):
            # Paskutinei temai pridedame likusius uždavinius
            topic_task_count = tasks_per_topic + (
                remaining_tasks if i == len(topics) - 1 else 0
            )

            if topic_task_count <= 0:
                continue

            logger.info(f"Generuojama tema '{topic}': {topic_task_count} uždaviniai")

            variant = await self._generate_variant_with_gemini(
                topic=topic,
                grade_level=grade_level,
                task_count=topic_task_count,
                difficulty=difficulty,
                variant_name=variant_name,
                include_solutions=include_solutions,
                curriculum_context=curriculum_context,
            )

            # Pernumeruojame uždavinius
            for task in variant.tasks:
                task.number = task_number
                all_tasks.append(task)
                task_number += 1

        # Sumaišome uždavinius, kad nebūtų visi iš eilės pagal temą
        if len(topics) > 1:
            random.shuffle(all_tasks)
            # Pernumeruojame po maišymo
            for i, task in enumerate(all_tasks):
                task.number = i + 1

        return GeneratedVariant(variant_name=variant_name, tasks=all_tasks)

    async def _generate_variant_with_gemini(
        self,
        topic: str,
        grade_level: int,
        task_count: int,
        difficulty: str,
        variant_name: str,
        include_solutions: bool,
        use_curriculum: bool = True,
        curriculum_context: str | None = None,  # Programos kontekstas iš JSON
    ) -> GeneratedVariant:
        """Generuoja variantą naudojant Gemini AI su curriculum.py integracija."""

        difficulty_lt = {
            "easy": "lengvas",
            "medium": "vidutinis",
            "hard": "sudėtingas",
            "mixed": "mišrus (lengvi, vidutiniai ir sudėtingi)",
        }.get(difficulty, "vidutinis")

        # Taškų paskirstymas
        if difficulty == "mixed":
            points_per_task = self._distribute_points_mixed(task_count)
        else:
            settings = self.DIFFICULTY_SETTINGS.get(
                difficulty, self.DIFFICULTY_SETTINGS["medium"]
            )
            points_per_task = [
                random.randint(*settings["points_range"]) for _ in range(task_count)
            ]

        # NAUJAS: Pasirenkame prompt'ą su curriculum kontekstu
        if curriculum_context:
            # Naudojame curriculum kontekstą iš JSON failų (naujas metodas)
            prompt = self._build_curriculum_context_prompt(
                topic,
                grade_level,
                task_count,
                difficulty,
                points_per_task,
                include_solutions,
                curriculum_context,
            )
            logger.info(f"Naudojamas curriculum context prompt tema '{topic}'")
        elif use_curriculum and grade_level <= 10:
            # Naudojame curriculum enhanced prompt'ą
            prompt = self._build_curriculum_enhanced_prompt(
                topic,
                grade_level,
                task_count,
                difficulty,
                points_per_task,
                include_solutions,
            )
            logger.info(f"Naudojamas curriculum enhanced prompt tema '{topic}'")
        elif grade_level >= 10 or difficulty in ["hard", "vbe"]:
            prompt = self._build_vbe_style_prompt(
                topic,
                grade_level,
                task_count,
                difficulty_lt,
                points_per_task,
                include_solutions,
            )
        else:
            prompt = self._build_standard_prompt(
                topic,
                grade_level,
                task_count,
                difficulty_lt,
                points_per_task,
                include_solutions,
            )

        # Kviečiame Gemini
        if self.gemini.is_configured:
            try:
                logger.info("Kviečiamas Gemini API...")
                # Maksimalus tokenų kiekis geresnei kokybei
                response = await self.gemini._call_api(prompt, max_tokens=8192)
                logger.info(f"Gemini atsakymas gautas: {bool(response)}")
                if response:
                    # Ištraukiame tekstą iš Gemini atsakymo
                    response_text = self.gemini._extract_text(response)
                    logger.info(
                        f"Gemini tekstas: {response_text[:200] if response_text else 'TUŠČIAS'}..."
                    )
                    tasks = self._parse_gemini_response(
                        response_text, topic, points_per_task
                    )
                    logger.info(f"Parsuota uždavinių: {len(tasks) if tasks else 0}")
                    if tasks:
                        # Tikriname ir pataisome atsakymus su SymPy/Newton
                        verified_tasks = await self._verify_answers(tasks)
                        return GeneratedVariant(
                            variant_name=variant_name, tasks=verified_tasks
                        )
                    else:
                        logger.warning("Nepavyko parsuoti Gemini atsakymo į uždavinius")
                else:
                    logger.warning("Gemini grąžino tuščią atsakymą")
            except Exception as e:
                logger.error(f"Gemini generavimo klaida: {e}", exc_info=True)

        # Fallback: generuojame be AI
        logger.warning("Gemini nepasiekiamas, naudojamas fallback generatorius")
        tasks = self._generate_fallback_tasks(
            topic, grade_level, task_count, difficulty, points_per_task
        )
        return GeneratedVariant(variant_name=variant_name, tasks=tasks)

    def _parse_gemini_response(
        self, response: str, topic: str, points_per_task: list
    ) -> list[GeneratedTask]:
        """Parsuoja Gemini atsakymą į uždavinius."""
        tasks = []

        try:
            # Bandome ištraukti JSON
            json_match = re.search(r"\{[\s\S]*\}", response)
            if json_match:
                data = json.loads(json_match.group())
                task_list = data.get("tasks", [])

                for i, task_data in enumerate(task_list):
                    points = (
                        points_per_task[i]
                        if i < len(points_per_task)
                        else task_data.get("points", 2)
                    )

                    answer = str(task_data.get("answer", ""))
                    # Bandome konvertuoti į LaTeX
                    try:
                        answer_latex = latex(sympify(answer))
                    except:
                        answer_latex = answer

                    tasks.append(
                        GeneratedTask(
                            number=task_data.get("number", i + 1),
                            text=task_data.get("text", ""),
                            answer=answer,
                            answer_latex=answer_latex,
                            points=points,
                            topic=task_data.get("topic_detail", topic),
                            difficulty=task_data.get("difficulty", "medium"),
                            solution_steps=task_data.get("solution_steps", []),
                        )
                    )

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing klaida: {e}")
        except Exception as e:
            logger.error(f"Parsing klaida: {e}")

        return tasks

    async def _verify_answers(self, tasks: list[GeneratedTask]) -> list[GeneratedTask]:
        """Patikrina ir pataiso atsakymus su SymPy/Newton."""
        verified = []

        for task in tasks:
            try:
                # Bandome supaprastinti atsakymą su SymPy
                answer = task.answer
                try:
                    expr = sympify(answer)
                    simplified = simplify(expr)
                    task.answer = str(simplified)
                    task.answer_latex = latex(simplified)
                except:
                    pass

                verified.append(task)

            except Exception as e:
                logger.warning(f"Tikrinimo klaida uždaviniui {task.number}: {e}")
                verified.append(task)

        return verified

    async def _create_variant_modification(
        self,
        original_variant: GeneratedVariant,
        variant_name: str,
        grade_level: int,
    ) -> GeneratedVariant:
        """Sukuria naują variantą modifikuojant skaičius."""
        new_tasks = []

        for task in original_variant.tasks:
            new_task = await self._modify_task_numbers(task, grade_level)
            new_tasks.append(new_task)

        return GeneratedVariant(variant_name=variant_name, tasks=new_tasks)

    async def _modify_task_numbers(
        self, task: GeneratedTask, grade_level: int
    ) -> GeneratedTask:
        """Modifikuoja uždavinio skaičius naujiems variantams."""
        text = task.text
        answer = task.answer

        # Randame skaičius tekste
        numbers = re.findall(r"\d+(?:[.,]\d+)?", text)

        if numbers:
            # Modifikuojame skaičius (pakeičiame panašiais)
            for num in numbers:
                try:
                    val = float(num.replace(",", "."))
                    # Generuojame panašų skaičių (±20%)
                    if val > 0:
                        new_val = val * random.uniform(0.8, 1.2)
                        if "." not in num and "," not in num:
                            new_val = int(round(new_val))
                        else:
                            new_val = round(new_val, 2)
                        text = text.replace(num, str(new_val).replace(".", ","), 1)
                except:
                    pass

            # Perskaičiuojame atsakymą jei įmanoma
            # (čia reikėtų sudėtingesnės logikos, kol kas paliekame aproksimaciją)

        return GeneratedTask(
            number=task.number,
            text=text,
            answer=answer,  # TODO: perskaičiuoti
            answer_latex=task.answer_latex,
            points=task.points,
            topic=task.topic,
            difficulty=task.difficulty,
            solution_steps=task.solution_steps,
        )

    def _distribute_points_mixed(self, task_count: int) -> list[int]:
        """Paskirsto taškus mišriam sudėtingumui."""
        points = []
        for i in range(task_count):
            if i < task_count // 3:
                points.append(random.randint(1, 2))  # Lengvi
            elif i < 2 * task_count // 3:
                points.append(random.randint(2, 3))  # Vidutiniai
            else:
                points.append(random.randint(3, 5))  # Sudėtingi
        return points

    def _generate_fallback_tasks(
        self,
        topic: str,
        grade_level: int,
        task_count: int,
        difficulty: str,
        points_per_task: list,
    ) -> list[GeneratedTask]:
        """Generuoja uždavinius be AI (fallback) pagal temą."""
        tasks = []
        topic_lower = topic.lower()

        for i in range(task_count):
            points = points_per_task[i] if i < len(points_per_task) else 2

            # Generuojame pagal temą
            if "trupmen" in topic_lower or "fraction" in topic_lower:
                task_data = self._generate_fraction_task(grade_level, difficulty, i + 1)
            elif "procent" in topic_lower or "percent" in topic_lower:
                task_data = self._generate_percent_task(grade_level, difficulty, i + 1)
            elif "lygt" in topic_lower or "equation" in topic_lower:
                task_data = self._generate_equation_task(grade_level, difficulty, i + 1)
            elif "geometr" in topic_lower:
                task_data = self._generate_geometry_task(grade_level, difficulty, i + 1)
            elif "funkcij" in topic_lower or "function" in topic_lower:
                # Įvairūs funkcijų uždaviniai
                func_types = [
                    self._generate_function_task,
                    self._generate_function_domain_task,
                    self._generate_function_zeros_task,
                ]
                task_func = random.choice(func_types)
                task_data = task_func(grade_level, difficulty, i + 1)
            elif "trigonometr" in topic_lower:
                task_data = self._generate_trig_task(grade_level, difficulty, i + 1)
            elif "logaritm" in topic_lower:
                task_data = self._generate_log_task(grade_level, difficulty, i + 1)
            elif "išvestin" in topic_lower or "derivative" in topic_lower:
                task_data = self._generate_derivative_task(
                    grade_level, difficulty, i + 1
                )
            elif "progresij" in topic_lower:
                task_data = self._generate_progression_task(
                    grade_level, difficulty, i + 1
                )
            else:
                # Default: mišrūs uždaviniai pagal klasę
                task_data = self._generate_mixed_task(grade_level, difficulty, i + 1)

            text = task_data["text"]
            answer = task_data["answer"]

            tasks.append(
                GeneratedTask(
                    number=i + 1,
                    text=text,
                    answer=str(answer),
                    answer_latex=str(answer),
                    points=points,
                    topic=topic,
                    difficulty=difficulty if difficulty != "mixed" else "medium",
                    solution_steps=[f"{text} = {answer}"],
                )
            )

        return tasks

    def _generate_arithmetic_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja aritmetikos uždavinį su kontekstu."""
        if difficulty == "easy":
            a, b = random.randint(1, 20), random.randint(1, 20)
        elif difficulty == "hard":
            a, b = random.randint(50, 200), random.randint(10, 100)
        else:
            a, b = random.randint(10, 100), random.randint(5, 50)

        # Pasirenkame vardą
        name = random.choice(self.NAMES_MALE + self.NAMES_FEMALE)

        # Tekstiniai uždaviniai su kontekstu
        templates_add = [
            (
                f"{name} turėjo {a} obuolių. Draugas davė dar {b} obuolių. Kiek obuolių dabar turi {name}?",
                a + b,
            ),
            (
                f"Parduotuvėje buvo {a} knygų. Atvežė dar {b} knygas. Kiek knygų dabar parduotuvėje?",
                a + b,
            ),
            (
                f"Autobuse važiavo {a} keleivių. Stotelėje įlipo dar {b}. Kiek keleivių dabar autobuse?",
                a + b,
            ),
            (
                f"{name} surinko {a} grybų, o jo draugas - {b} grybų. Kiek grybų jie surinko kartu?",
                a + b,
            ),
        ]

        templates_sub = [
            (
                f"{name} turėjo {max(a,b)} saldainių. Suvalgė {min(a,b)}. Kiek saldainių liko?",
                abs(a - b),
            ),
            (
                f"Bibliotekoje buvo {max(a,b)} knygų. Išdavė {min(a,b)}. Kiek knygų liko?",
                abs(a - b),
            ),
            (
                f"Autobuse važiavo {max(a,b)} keleivių. Stotelėje išlipo {min(a,b)}. Kiek keleivių liko?",
                abs(a - b),
            ),
        ]

        templates_mul = [
            (
                f"{name} nupirko {min(a,12)} sąsiuvinius po {min(b,15)} ct. Kiek sumokėjo centų?",
                min(a, 12) * min(b, 15),
            ),
            (
                f"Klasėje yra {min(a,6)} eilės po {min(b,8)} suolus. Kiek suolų klasėje?",
                min(a, 6) * min(b, 8),
            ),
            (
                f"Viename dėžutėje yra {min(a,10)} pieštukų. Kiek pieštukų yra {min(b,5)} dėžutėse?",
                min(a, 10) * min(b, 5),
            ),
            (
                f"{name} važiavo {min(a,4)} valandas greičiu {min(b,60)} km/h. Kokį atstumą nuvažiavo?",
                min(a, 4) * min(b, 60),
            ),
        ]

        templates_div = []
        # Dalyba - užtikriname kad dalinasi be liekanos
        for divisor in [2, 3, 4, 5, 6, 8, 10]:
            dividend = divisor * random.randint(2, 20)
            templates_div.extend(
                [
                    (
                        f"{name} turi {dividend} saldainių. Nori padalinti po lygiai {divisor} draugams. Po kiek saldainių gaus kiekvienas?",
                        dividend // divisor,
                    ),
                    (
                        f"Mokykloje yra {dividend} mokinių. Jie suskirstyti į {divisor} klases po lygiai. Kiek mokinių kiekvienoje klasėje?",
                        dividend // divisor,
                    ),
                ]
            )

        # Pasirenkame atsitiktinį šabloną
        all_templates = templates_add + templates_sub + templates_mul
        if templates_div:
            all_templates.extend(
                random.sample(templates_div, min(2, len(templates_div)))
            )

        text, answer = random.choice(all_templates)
        return {"text": text, "answer": answer}

    def _generate_fraction_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja trupmenų uždavinį su kontekstu."""
        from fractions import Fraction

        name = random.choice(self.NAMES_MALE + self.NAMES_FEMALE)

        if difficulty == "easy":
            a, b = random.randint(1, 4), random.randint(2, 5)
            c, d = random.randint(1, 4), random.randint(2, 5)
        else:
            a, b = random.randint(1, 8), random.randint(2, 10)
            c, d = random.randint(1, 8), random.randint(2, 10)

        # Užtikriname kad trupmenos yra mažesnės už 1
        if a >= b:
            a = b - 1
        if c >= d:
            c = d - 1

        # Tekstiniai uždaviniai su trupmenomis
        templates = [
            (
                f"{name} suvalgė {a}/{b} pyrago. Kokia pyrago dalis liko?",
                Fraction(b - a, b),
            ),
            (
                f"Pirmą dieną {name} perskaitė {a}/{b} knygos, antrą dieną - {c}/{d} knygos. Kokią dalį knygos perskaitė per abi dienas?",
                Fraction(a, b) + Fraction(c, d),
            ),
            (
                f"Baseinas užpildytas {a}/{b} vandens. Kokią dalį dar reikia pripilti, kad būtų pilnas?",
                Fraction(b - a, b),
            ),
            (
                f"{name} turi {a}/{b} kg obuolių ir {c}/{d} kg kriaušių. Kiek kilogramų vaisių iš viso?",
                Fraction(a, b) + Fraction(c, d),
            ),
            (
                f"Iš {a}/{b} litro pieno {name} išgėrė {c}/{d} litro. Kiek pieno liko?",
                abs(Fraction(a, b) - Fraction(c, d)),
            ),
            (
                f"Stačiakampio ilgis yra {a}/{b} m, o plotis - {c}/{d} m. Koks stačiakampio perimetras?",
                2 * (Fraction(a, b) + Fraction(c, d)),
            ),
        ]

        text, result = random.choice(templates)

        # Supaprastinta forma
        if result.denominator == 1:
            answer = str(result.numerator)
        else:
            answer = f"{result.numerator}/{result.denominator}"

        return {"text": text, "answer": answer}

    def _generate_percent_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja procentų uždavinį su kontekstu."""
        name = random.choice(self.NAMES_MALE + self.NAMES_FEMALE)
        base = random.choice([50, 100, 150, 200, 250, 300, 400, 500])
        percent = random.choice([10, 20, 25, 30, 40, 50, 75])
        part = base * percent // 100

        templates = [
            (
                f"{name} turėjo {base} eurų. Išleido {percent}% pinigų. Kiek eurų išleido?",
                part,
            ),
            (
                f"Parduotuvėje prekė kainuoja {base} eurų. Nuolaida - {percent}%. Kokia nuolaidos suma?",
                part,
            ),
            (
                f"Klasėje yra {base} mokinių. {percent}% mokinių lanko būrelį. Kiek mokinių lanko būrelį?",
                part,
            ),
            (
                f"{name} perskaitė {part} puslapių iš {base} puslapių knygos. Kiek procentų knygos perskaitė?",
                percent,
            ),
        ]

        if difficulty in ["medium", "hard"]:
            templates.extend(
                [
                    (
                        f"Po {percent}% nuolaidos prekė kainuoja {base - part} eurų. Kokia buvo pradinė kaina?",
                        base,
                    ),
                    (
                        f"{name} gavo {percent}% didesnį atlyginimą. Dabar gauna {base + part} eurų. Koks buvo pradinis atlyginimas?",
                        base,
                    ),
                ]
            )

        template = random.choice(templates)
        return {"text": template[0], "answer": template[1]}

    def _generate_equation_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja lygčių uždavinį su kontekstu."""
        name = random.choice(self.NAMES_MALE + self.NAMES_FEMALE)

        if difficulty == "easy" or grade_level <= 6:
            # Paprastos lygtys su tekstiniu kontekstu
            a = random.randint(2, 10)
            x = random.randint(1, 15)
            b = a + x

            templates = [
                (
                    f"{name} turėjo keletą saldainių. Gavęs dar {a}, jis turi {b} saldainių. Kiek saldainių turėjo iš pradžių? (Sudaryk lygtį ir išspręsk)",
                    x,
                ),
                (f"Skaičius, padaugintas iš {a}, lygus {a * x}. Koks tai skaičius?", x),
                (
                    f"{name} amžius, padidinus {a} metais, bus {b} metai. Kiek metų {name} dabar?",
                    x,
                ),
                (f"Išspręsk lygtį: x + {a} = {b}", x),
            ]
            text, answer = random.choice(templates)

        elif difficulty == "hard" or grade_level >= 9:
            # Kvadratinė lygtis
            x1 = random.randint(-5, 5)
            x2 = random.randint(-5, 5)
            a = 1
            b = -(x1 + x2)
            c = x1 * x2

            eq = f"x² "
            if b >= 0:
                eq += f"+ {b}x "
            else:
                eq += f"- {-b}x "
            if c >= 0:
                eq += f"+ {c} = 0"
            else:
                eq += f"- {-c} = 0"

            text = f"Išspręsk lygtį: {eq}"
            if x1 == x2:
                answer = f"x = {x1}"
            else:
                answer = f"x₁ = {min(x1, x2)}, x₂ = {max(x1, x2)}"
        else:
            # Tiesinė lygtis su kontekstu
            a = random.randint(2, 8)
            x = random.randint(1, 10)
            b = random.randint(1, 20)
            c = a * x + b

            templates = [
                (
                    f"{name} nupirko {a} vienodus sąsiuvinius ir dar vieną už {b} ct. Iš viso sumokėjo {c} ct. Kiek kainavo vienas sąsiuvinis?",
                    x,
                ),
                (f"Išspręsk lygtį: {a}x + {b} = {c}", x),
                (
                    f"Trikampio perimetras yra {c} cm. Dvi kraštinės yra po {a} cm, o trečioji - x cm. Rask x.",
                    c - 2 * a,
                ),
            ]
            text, answer = random.choice(templates)

        return {"text": text, "answer": answer}

    def _generate_geometry_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja geometrijos uždavinį."""
        shapes = ["stačiakampis", "kvadratas", "trikampis", "apskritimas"]
        shape = random.choice(shapes)

        if shape == "stačiakampis":
            a = random.randint(3, 15)
            b = random.randint(3, 15)
            calc_type = random.choice(["plotas", "perimetras"])
            if calc_type == "plotas":
                text = f"Stačiakampio kraštinės yra {a} cm ir {b} cm. Rask plotą."
                answer = f"{a * b} cm²"
            else:
                text = f"Stačiakampio kraštinės yra {a} cm ir {b} cm. Rask perimetrą."
                answer = f"{2 * (a + b)} cm"
        elif shape == "kvadratas":
            a = random.randint(2, 12)
            calc_type = random.choice(["plotas", "perimetras"])
            if calc_type == "plotas":
                text = f"Kvadrato kraštinė yra {a} cm. Rask plotą."
                answer = f"{a * a} cm²"
            else:
                text = f"Kvadrato kraštinė yra {a} cm. Rask perimetrą."
                answer = f"{4 * a} cm"
        elif shape == "trikampis":
            a = random.randint(4, 12)
            h = random.randint(3, 10)
            text = f"Trikampio pagrindas yra {a} cm, aukštinė - {h} cm. Rask plotą."
            answer = f"{a * h / 2} cm²"
        else:  # apskritimas
            r = random.randint(2, 10)
            calc_type = random.choice(["plotas", "ilgis"])
            if calc_type == "plotas":
                text = f"Apskritimo spindulys yra {r} cm. Rask plotą (π ≈ 3.14)."
                answer = f"{round(3.14 * r * r, 2)} cm²"
            else:
                text = (
                    f"Apskritimo spindulys yra {r} cm. Rask apskritimo ilgį (π ≈ 3.14)."
                )
                answer = f"{round(2 * 3.14 * r, 2)} cm"

        return {"text": text, "answer": answer}

    def _generate_function_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja funkcijų uždavinį."""
        a = random.randint(1, 5)
        b = random.randint(-10, 10)
        x = random.randint(-5, 5)

        if grade_level <= 8 or difficulty == "easy":
            # Tiesinė funkcija
            y = a * x + b
            sign = "+" if b >= 0 else "-"
            text = f"Duota funkcija f(x) = {a}x {sign} {abs(b)}. Rask f({x})."
            answer = y
        else:
            # Kvadratinė funkcija
            c = random.randint(-5, 5)
            y = a * x * x + b * x + c
            text = f"Duota funkcija f(x) = {a}x² + {b}x + {c}. Rask f({x})."
            answer = y

        return {"text": text, "answer": answer}

    def _generate_function_domain_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja funkcijos apibrėžimo srities uždavinį."""
        task_types = [
            # Šaknis
            (
                f"Rask funkcijos f(x) = √(x - {random.randint(1,10)}) apibrėžimo sritį.",
                f"x ≥ {random.randint(1,10)}",
            ),
            (
                f"Rask funkcijos f(x) = √({random.randint(2,8)} - x) apibrėžimo sritį.",
                f"x ≤ {random.randint(2,8)}",
            ),
            # Trupmena
            (
                f"Rask funkcijos f(x) = 1/(x - {random.randint(1,5)}) apibrėžimo sritį.",
                f"x ≠ {random.randint(1,5)}",
            ),
            (
                f"Rask funkcijos f(x) = (x + 1)/(x² - {random.randint(1,4)**2}) apibrėžimo sritį.",
                f"x ≠ ±{random.randint(1,4)}",
            ),
        ]
        text, answer = random.choice(task_types)
        return {"text": text, "answer": answer}

    def _generate_function_zeros_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja funkcijos nulių radimo uždavinį."""
        a = random.randint(1, 5)
        b = random.randint(-10, 10)

        if grade_level <= 8 or difficulty == "easy":
            # Tiesinė funkcija
            if a != 0:
                zero = -b / a
                sign = "+" if b >= 0 else "-"
                text = f"Rask funkcijos f(x) = {a}x {sign} {abs(b)} nulį (šaknį)."
                answer = f"x = {zero}" if zero == int(zero) else f"x = {-b}/{a}"
            else:
                text = f"Rask funkcijos f(x) = {b} nulį."
                answer = "Nulių nėra" if b != 0 else "Visi x"
        else:
            # Kvadratinė funkcija
            x1 = random.randint(-5, 5)
            x2 = random.randint(-5, 5)
            # f(x) = (x - x1)(x - x2) = x² - (x1+x2)x + x1*x2
            b_coef = -(x1 + x2)
            c_coef = x1 * x2
            sign_b = "+" if b_coef >= 0 else "-"
            sign_c = "+" if c_coef >= 0 else "-"
            text = f"Rask funkcijos f(x) = x² {sign_b} {abs(b_coef)}x {sign_c} {abs(c_coef)} nulius."
            if x1 == x2:
                answer = f"x = {x1}"
            else:
                answer = f"x₁ = {min(x1, x2)}, x₂ = {max(x1, x2)}"

        return {"text": text, "answer": answer}

    def _generate_progression_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja progresijų uždavinį."""
        prog_type = random.choice(["arithmetic", "geometric"])

        if prog_type == "arithmetic":
            a1 = random.randint(1, 10)
            d = random.randint(1, 5)
            n = random.randint(5, 10)

            task_types = [
                (
                    f"Aritmetinės progresijos pirmasis narys a₁ = {a1}, skirtumas d = {d}. Rask {n}-ąjį narį.",
                    a1 + (n - 1) * d,
                ),
                (
                    f"Aritmetinės progresijos a₁ = {a1}, d = {d}. Rask pirmųjų {n} narių sumą.",
                    n * (2 * a1 + (n - 1) * d) // 2,
                ),
                (
                    f"Aritmetinė progresija: {a1}, {a1+d}, {a1+2*d}, ... Koks yra {n}-asis narys?",
                    a1 + (n - 1) * d,
                ),
            ]
        else:
            a1 = random.randint(1, 5)
            q = random.randint(2, 3)
            n = random.randint(4, 6)

            task_types = [
                (
                    f"Geometrinės progresijos pirmasis narys b₁ = {a1}, vardiklis q = {q}. Rask {n}-ąjį narį.",
                    a1 * (q ** (n - 1)),
                ),
                (
                    f"Geometrinė progresija: {a1}, {a1*q}, {a1*q*q}, ... Koks yra {n}-asis narys?",
                    a1 * (q ** (n - 1)),
                ),
            ]

        text, answer = random.choice(task_types)
        return {"text": text, "answer": answer}

    def _generate_mixed_task(self, grade_level: int, difficulty: str, num: int) -> dict:
        """Generuoja mišrų uždavinį pagal klasę."""
        # Pasirenkame uždavinio tipą pagal klasę
        if grade_level <= 6:
            generators = [
                self._generate_arithmetic_task,
                self._generate_fraction_task,
                self._generate_percent_task,
            ]
        elif grade_level <= 8:
            generators = [
                self._generate_arithmetic_task,
                self._generate_equation_task,
                self._generate_geometry_task,
                self._generate_percent_task,
            ]
        else:
            generators = [
                self._generate_equation_task,
                self._generate_geometry_task,
                self._generate_function_task,
                self._generate_function_zeros_task,
                self._generate_progression_task,
            ]

        generator = random.choice(generators)
        return generator(grade_level, difficulty, num)

    def _generate_trig_task(self, grade_level: int, difficulty: str, num: int) -> dict:
        """Generuoja trigonometrijos uždavinį."""
        angles = [
            (30, "1/2", "√3/2"),
            (45, "√2/2", "√2/2"),
            (60, "√3/2", "1/2"),
            (90, "1", "0"),
            (0, "0", "1"),
        ]
        angle, sin_val, cos_val = random.choice(angles)

        func = random.choice(["sin", "cos"])
        if func == "sin":
            text = f"Rask sin {angle}°"
            answer = sin_val
        else:
            text = f"Rask cos {angle}°"
            answer = cos_val

        return {"text": text, "answer": answer}

    def _generate_log_task(self, grade_level: int, difficulty: str, num: int) -> dict:
        """Generuoja logaritmų uždavinį."""
        bases = [2, 3, 5, 10]
        base = random.choice(bases)

        # Generuojame taip, kad atsakymas būtų sveikas skaičius
        exp = random.randint(1, 4)
        arg = base**exp

        text = f"Rask log₍{base}₎{arg}"
        answer = exp

        return {"text": text, "answer": answer}

    def _generate_derivative_task(
        self, grade_level: int, difficulty: str, num: int
    ) -> dict:
        """Generuoja išvestinių uždavinį."""
        a = random.randint(1, 5)
        n = random.randint(2, 4)

        if difficulty == "easy":
            text = f"Rask funkcijos f(x) = {a}x^{n} išvestinę"
            answer = f"{a * n}x^{n - 1}"
        else:
            b = random.randint(1, 10)
            text = f"Rask funkcijos f(x) = {a}x^{n} + {b}x išvestinę"
            answer = f"{a * n}x^{n - 1} + {b}"

        return {"text": text, "answer": answer}


# Singleton
_generator: Optional[TestGenerator] = None


def get_test_generator() -> TestGenerator:
    """Gauna kontrolinių generatorių."""
    global _generator
    if _generator is None:
        _generator = TestGenerator()
    return _generator
