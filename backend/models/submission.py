"""
Submission modelis - mokinio pateiktas darbas.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from database import Base


class SubmissionStatus(str, PyEnum):
    """Pateikto darbo statusas."""
    UPLOADED = "uploaded"  # Įkeltas
    PROCESSING = "processing"  # Apdorojamas OCR
    OCR_DONE = "ocr_done"  # OCR baigtas
    CHECKING = "checking"  # Tikrinamas
    REVIEWED = "reviewed"  # Peržiūrėtas mokytojo
    COMPLETED = "completed"  # Baigtas


class Submission(Base):
    """Mokinio pateiktas kontrolinio darbas."""

    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(500), nullable=False)  # Kelias iki failo
    file_name = Column(String(200), nullable=False)  # Originalus pavadinimas
    file_type = Column(String(10), nullable=False)  # "pdf", "png", "jpg"
    status = Column(String(20), default=SubmissionStatus.UPLOADED, index=True)

    # Rezultatai
    total_points = Column(Float, default=0.0)
    max_points = Column(Float, default=0.0)
    percentage = Column(Float, default=0.0)  # 0-100
    grade = Column(Integer, nullable=True)  # 1-10

    # Mokytojo pastabos
    teacher_notes = Column(Text, nullable=True)

    # Foreign keys
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("variants.id"), nullable=True)

    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow)
    checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="submissions")
    test = relationship("Test", back_populates="submissions")
    variant = relationship("Variant", back_populates="submissions")
    answers = relationship("Answer", back_populates="submission", cascade="all, delete-orphan")
    ocr_results = relationship("OCRResult", back_populates="submission", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Submission(id={self.id}, student_id={self.student_id}, status='{self.status}')>"
