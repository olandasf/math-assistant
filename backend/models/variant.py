"""
Variant modelis - kontrolinio variantas (I, II).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship

from database import Base


class Variant(Base):
    """Kontrolinio variantas (I arba II)."""
    
    __tablename__ = "variants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(10), nullable=False)  # "I", "II"
    max_points = Column(Float, default=0.0)  # Suma visų užduočių taškų
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test = relationship("Test", back_populates="variants")
    tasks = relationship("Task", back_populates="variant", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="variant")

    def __repr__(self) -> str:
        return f"<Variant(id={self.id}, name='{self.name}', test_id={self.test_id})>"
