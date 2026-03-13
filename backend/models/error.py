"""
Error modelis - klaida mokinio atsakyme.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from database import Base


class Error(Base):
    """Klaida mokinio atsakyme su paaiškinimu."""

    __tablename__ = "errors"

    id = Column(Integer, primary_key=True, index=True)
    error_type = Column(String(50), nullable=False, index=True)  # "calculation", "concept", "notation"
    error_code = Column(String(20), nullable=True)  # "CALC_001", "SIGN_002"
    description = Column(Text, nullable=False)  # Klaidos aprašymas
    explanation = Column(Text, nullable=True)  # AI paaiškinimas lietuviškai
    suggestion = Column(Text, nullable=True)  # Kaip pataisyti
    severity = Column(Integer, default=1)  # 1-3 (lengva, vidutinė, rimta)

    # Foreign key
    answer_id = Column(Integer, ForeignKey("answers.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    answer = relationship("Answer", back_populates="errors")

    def __repr__(self) -> str:
        return f"<Error(id={self.id}, type='{self.error_type}', answer_id={self.answer_id})>"
