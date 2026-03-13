"""
ProblemBank modelis - uždavinių bazė iš HuggingFace ir kitų šaltinių.

Saugo išverstus ir adaptuotus matematinius uždavinius.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class ProblemSource(str, Enum):
    """Uždavinio šaltinis."""

    GSM8K = "gsm8k"  # HuggingFace gsm8k (6-8 kl.)
    COMPETITION_MATH = "competition"  # Olimpiadiniai (10-12 kl.)
    GEOMETRY = "geometry"  # Geometrijos (9-12 kl.)
    NUMINA_MATH = "numina"  # NuminaMath olimpiadiniai (8-12 kl.)
    MATH_INSTRUCT = "instruct"  # MathInstruct įvairūs (6-12 kl.)
    TEMPLATE = "template"  # Šabloninis generatorius
    GEMINI = "gemini"  # AI sugeneruotas
    MANUAL = "manual"  # Rankiniu būdu įvestas
    KHAN_ACADEMY = "khan"  # Khan Academy


class ProblemDifficulty(str, Enum):
    """Uždavinio sunkumas."""

    EASY = "easy"  # Lengvas (1-2 žingsniai)
    MEDIUM = "medium"  # Vidutinis (3-4 žingsniai)
    HARD = "hard"  # Sudėtingas (5+ žingsniai)
    OLYMPIAD = "olympiad"  # Olimpiadinis
    VBE = "vbe"  # VBE lygio


class ProblemBank(Base):
    """
    Uždavinių bazė.

    Saugo matematinius uždavinius iš įvairių šaltinių:
    - HuggingFace (gsm8k, competition_math)
    - Šabloninis generatorius
    - Gemini AI
    - Rankiniu būdu įvesti
    """

    __tablename__ = "problem_bank"

    # === Pirminiai laukai ===
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Šaltinio informacija
    source: Mapped[ProblemSource] = mapped_column(
        SQLEnum(ProblemSource), nullable=False, index=True
    )
    source_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Originalus ID šaltinyje (pvz., gsm8k index)",
    )

    # === Uždavinio turinys ===
    question_lt: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Uždavinio tekstas lietuvių kalba"
    )
    question_en: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Originalus tekstas anglų kalba"
    )

    # Atsakymas ir sprendimas
    answer: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Teisingas atsakymas"
    )
    answer_latex: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Atsakymas LaTeX formatu"
    )
    solution_steps: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Sprendimo žingsniai (JSON array)"
    )
    solution_latex: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Pilnas sprendimas LaTeX formatu"
    )

    # === Klasifikacija ===
    grade_min: Mapped[int] = mapped_column(
        Integer, nullable=False, default=5, comment="Minimali klasė"
    )
    grade_max: Mapped[int] = mapped_column(
        Integer, nullable=False, default=8, comment="Maksimali klasė"
    )

    difficulty: Mapped[ProblemDifficulty] = mapped_column(
        SQLEnum(ProblemDifficulty),
        nullable=False,
        default=ProblemDifficulty.MEDIUM,
        index=True,
    )

    # Tema ir potemė (iš curriculum.py)
    topic_id: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True, comment="Temos ID iš curriculum.py"
    )
    subtopic_id: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True, comment="Potemės ID iš curriculum.py"
    )

    # Papildomos žymos (JSON array)
    tags: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Papildomos žymos (JSON array)"
    )

    # === Kokybės kontrolė ===
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Ar patikrintas mokytojo"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, index=True, comment="Ar aktyvus (naudojamas)"
    )

    quality_score: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Kokybės įvertinimas (0-1)"
    )

    times_used: Mapped[int] = mapped_column(
        Integer, default=0, comment="Kiek kartų panaudotas kontroliniuose"
    )

    # === Variacijos ===
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("problem_bank.id"),
        nullable=True,
        comment="Tėvinio uždavinio ID (jei tai variacija)",
    )
    variation_number: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Variacijos numeris (1, 2, 3...)"
    )

    # === Metaduomenys ===
    points: Mapped[int] = mapped_column(
        Integer, default=1, comment="Rekomenduojami taškai"
    )
    estimated_time_minutes: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Numatomas sprendimo laikas minutėmis"
    )

    # === Laiko žymos ===
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # === Ryšiai ===
    parent = relationship(
        "ProblemBank", remote_side=[id], backref="variations", foreign_keys=[parent_id]
    )

    def __repr__(self) -> str:
        return f"<ProblemBank(id={self.id}, source={self.source.value}, grade={self.grade_min}-{self.grade_max})>"

    @property
    def solution_steps_list(self) -> list[str]:
        """Grąžina sprendimo žingsnius kaip sąrašą."""
        if not self.solution_steps:
            return []
        import json

        try:
            return json.loads(self.solution_steps)
        except json.JSONDecodeError:
            return [self.solution_steps]

    @property
    def tags_list(self) -> list[str]:
        """Grąžina žymas kaip sąrašą."""
        if not self.tags:
            return []
        import json

        try:
            return json.loads(self.tags)
        except json.JSONDecodeError:
            return []
