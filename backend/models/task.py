"""
Task modelis - užduotis kontroliniame.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text
from sqlalchemy.orm import relationship

from database import Base


class Task(Base):
    """Užduotis kontroliniame (1, 2, 3 arba 1a, 1b, 1c)."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(10), nullable=False)  # "1", "2", "1a", "1b"
    text = Column(Text, nullable=True)  # Užduoties tekstas
    correct_answer = Column(Text, nullable=False)  # LaTeX formatu
    correct_answer_numeric = Column(Float, nullable=True)  # Skaitinė reikšmė jei yra
    points = Column(Float, nullable=False)  # 2.0, 3.0 ir t.t.
    solution_steps = Column(Text, nullable=True)  # JSON - sprendimo žingsniai
    topic = Column(String(100), nullable=True)  # "equations", "fractions"
    difficulty = Column(Integer, default=1)  # 1-5 sudėtingumas
    order_index = Column(Integer, default=0)  # Rikiavimui

    # Foreign key
    variant_id = Column(Integer, ForeignKey("variants.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    variant = relationship("Variant", back_populates="tasks")
    answers = relationship("Answer", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, number='{self.number}', points={self.points})>"
