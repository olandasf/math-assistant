"""
Answer modelis - mokinio atsakymas į užduotį.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text, Boolean
from sqlalchemy.orm import relationship

from database import Base


class Answer(Base):
    """Mokinio atsakymas į vieną užduotį."""
    
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    
    # OCR rezultatas
    recognized_text = Column(Text, nullable=True)  # Raw OCR tekstas
    recognized_latex = Column(Text, nullable=True)  # LaTeX formatas
    ocr_confidence = Column(Float, default=0.0)  # 0.0 - 1.0
    
    # Tikrinimo rezultatas
    is_correct = Column(Boolean, nullable=True)  # True/False/None (nepatikrinta)
    earned_points = Column(Float, default=0.0)
    max_points = Column(Float, default=0.0)
    
    # AI paaiškinimas
    ai_explanation = Column(Text, nullable=True)  # Klaidos paaiškinimas lietuviškai
    
    # Mokytojo koregavimai
    teacher_override = Column(Boolean, default=False)  # Ar mokytojas pakeitė
    teacher_points = Column(Float, nullable=True)  # Mokytojo skirti taškai
    teacher_comment = Column(Text, nullable=True)  # Mokytojo komentaras
    
    # Nuoroda į paveikslėlį
    image_region = Column(String(100), nullable=True)  # "x1,y1,x2,y2" koordinatės
    
    # Foreign keys
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    submission = relationship("Submission", back_populates="answers")
    task = relationship("Task", back_populates="answers")
    errors = relationship("Error", back_populates="answer", cascade="all, delete-orphan")

    @property
    def final_points(self) -> float:
        """Galutiniai taškai (mokytojo arba automatiniai)."""
        if self.teacher_override and self.teacher_points is not None:
            return self.teacher_points
        return self.earned_points

    def __repr__(self) -> str:
        return f"<Answer(id={self.id}, task_id={self.task_id}, is_correct={self.is_correct})>"
