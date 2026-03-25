"""
Test Generator Models - Kontrolinių duomenų modeliai
=====================================================
Naudoja ProblemBank DB kaip pirminį šaltinį.
Šabloninis generatorius kaip fallback.

Integruota su curriculum.py - Lietuvos matematikos bendrosios programos turiniu.
"""

from dataclasses import dataclass, field
from typing import Optional


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
    problem_bank_id: Optional[int] = None  # Nuoroda į ProblemBank DB (jei iš DB)


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
    created_by: str = "Uždavinių bazė"
