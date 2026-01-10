"""
SchoolYear modelis - mokslo metai.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from database import Base


class SchoolYear(Base):
    """Mokslo metai (pvz., 2025-2026)."""
    
    __tablename__ = "school_years"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, nullable=False, index=True)  # "2025-2026"
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    classes = relationship("SchoolClass", back_populates="school_year", cascade="all, delete-orphan")
    tests = relationship("Test", back_populates="school_year", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<SchoolYear(id={self.id}, name='{self.name}', is_active={self.is_active})>"
