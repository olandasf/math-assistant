"""
Lietuvos matematikos bendrosios programos turinys (2023)
=========================================================

Šis failas aprašo matematikos turinį pagal oficialią Lietuvos bendrąją
programą pagrindinio ugdymo koncentrams (5-10 klasės).

TURINIO SRITYS:
1. Skaičiai ir skaičiavimai
2. Algebra
3. Geometrija ir matai
4. Statistika ir tikimybės

PASIEKIMŲ LYGIAI:
- patenkinamas: Minimalūs reikalavimai
- pagrindinis: Vidutinis lygis (dauguma mokinių)
- aukštesnysis: Pažengęs lygis

KONCENTRAI:
- 5-6 klasės: Pirmasis koncentras
- 7-8 klasės: Antrasis koncentras
- 9-10 klasės: Trečiasis koncentras (I-II gimnazijos)

Šaltinis: https://emokykla.lt/metodine-medziaga/medziaga/perziura/131
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class ContentArea(Enum):
    """Turinio sritys pagal BP."""

    NUMBERS = "skaičiai ir skaičiavimai"
    ALGEBRA = "algebra"
    GEOMETRY = "geometrija ir matai"
    STATISTICS = "statistika ir tikimybės"


class AchievementLevel(Enum):
    """Pasiekimų lygiai."""

    SATISFACTORY = "patenkinamas"  # 4-5 balai
    BASIC = "pagrindinis"  # 6-8 balai
    ADVANCED = "aukštesnysis"  # 9-10 balai


class DifficultyLevel(Enum):
    """Sunkumo lygiai uždaviniams."""

    VERY_EASY = 1  # Labai lengvas (patenkinamas lygis, žemesnė klasė)
    EASY = 2  # Lengvas (patenkinamas lygis)
    MEDIUM = 3  # Vidutinis (pagrindinis lygis)
    HARD = 4  # Sunkus (aukštesnysis lygis)
    VERY_HARD = 5  # Labai sunkus (aukštesnysis lygis, olimpiadinis)


class Competency(Enum):
    """Bendrosios kompetencijos pagal BP 2022."""

    COGNITIVE = "pažinimo"  # Kritinis mąstymas, problemų sprendimas
    DIGITAL = "skaitmeninė"  # Technologijų naudojimas
    CREATIVE = "kūrybiškumo"  # Nestandartinių sprendimų paieška
    COMMUNICATION = "komunikavimo"  # Matematinės kalbos vartojimas
    CULTURAL = "kultūrinė"  # Matematikos raida, istorinis kontekstas
    CIVIC = "pilietinė"  # Duomenų interpretavimas socialiniame kontekste


class CognitiveLevel(Enum):
    """Kognityvinės veiklos sritys (pasiekimų sritys)."""

    KNOWLEDGE = "žinios ir supratimas"  # 30-40% testo
    APPLICATION = "taikymas"  # 40-50% testo
    PROBLEM_SOLVING = "problemų sprendimas"  # 10-30% testo


class PassLevel(Enum):
    """Pasiekimų lygiai pagal BP (1-4 skalė)."""

    THRESHOLD = 1  # Slenkstinis - vieno žingsnio veiksmai su pagalba
    SATISFACTORY = 2  # Patenkinamas - standartiniai algoritmai, 1-2 žingsniai
    BASIC = 3  # Pagrindinis - kompleksinis uždavinys, 3-4 žingsniai
    ADVANCED = 4  # Aukštesnysis - olimpiadinio tipo, optimizavimas


@dataclass
class AssessmentWeights:
    """Vertinimo svoriai pagal pasiekimų sritis (PUPP/VBE)."""

    knowledge_understanding: float = 0.35  # Žinios ir supratimas (30-40%)
    application: float = 0.45  # Taikymas (40-50%)
    problem_solving: float = 0.20  # Problemų sprendimas (10-20%)

    def validate(self) -> bool:
        """Patikrina ar svoriai sudaro 100%."""
        total = self.knowledge_understanding + self.application + self.problem_solving
        return abs(total - 1.0) < 0.01


# Standartiniai svoriai pagal koncentrus
PUPP_WEIGHTS = AssessmentWeights(
    knowledge_understanding=0.35, application=0.45, problem_solving=0.20
)

VBE_WEIGHTS = AssessmentWeights(
    knowledge_understanding=0.30, application=0.40, problem_solving=0.30
)

# PUPP turinio sričių pasiskirstymas
PUPP_CONTENT_DISTRIBUTION = {
    ContentArea.NUMBERS: 0.20,  # ~20% (skaičiai + algebra kartu ~40%)
    ContentArea.ALGEBRA: 0.20,  # ~20%
    ContentArea.GEOMETRY: 0.35,  # ~35%
    ContentArea.STATISTICS: 0.25,  # ~25%
}


@dataclass
class Subtopic:
    """Potemė su detaliais reikalavimais."""

    id: str
    name_lt: str
    name_en: str
    description: str  # Trumpas aprašymas

    # Pasiekimų aprašymai pagal lygį
    satisfactory_requirements: List[str]  # Ką turi mokėti patenkinamam
    basic_requirements: List[str]  # Ką turi mokėti pagrindiniui
    advanced_requirements: List[str]  # Ką turi mokėti aukštesniajam

    # Uždavinių pavyzdžiai
    example_easy: str = ""
    example_medium: str = ""
    example_hard: str = ""

    # Susiję įgūdžiai
    skills: List[str] = field(default_factory=list)

    # Distraktorių logika (dažnos klaidos) - iš Matematikos programos
    common_errors: List[str] = field(default_factory=list)  # Dažniausios klaidos
    distractor_logic: str = ""  # Kaip generuoti neteisingus atsakymus

    # Kompetencijos, kurias ugdo ši potemė
    competencies: List[Competency] = field(default_factory=list)


@dataclass
class Topic:
    """Pagrindinė tema."""

    id: str
    name_lt: str
    name_en: str
    content_area: ContentArea

    # Klasės, kuriose mokoma
    grade_introduced: int  # Kada pradedama mokyti
    grade_mastery: int  # Kada turi būti įsisavinta
    grades_available: List[int]  # Visos klasės, kur galima naudoti

    # Potemės
    subtopics: List[Subtopic] = field(default_factory=list)

    # Priklausomybės (kokias temas reikia mokėti prieš)
    prerequisites: List[str] = field(default_factory=list)

    # Papildoma informacija
    description: str = ""
    importance: int = 3  # 1-5, kur 5 = labai svarbi (VBE)

    # Kognityvinė sritis (pagrindinė)
    primary_cognitive_level: CognitiveLevel = CognitiveLevel.APPLICATION

    # Pagrindinės kompetencijos
    competencies: List[Competency] = field(default_factory=list)


@dataclass
class GradeCurriculum:
    """Vienos klasės curriculum."""

    grade: int
    topics: List[Topic]

    # Koncentro info
    concentre_name: str  # "5-6 klasės", "7-8 klasės", "9-10 klasės"

    # Papildomi temos iš žemesnių klasių (kartojimui)
    review_topics: List[str] = field(default_factory=list)


