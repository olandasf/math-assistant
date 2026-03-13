"""
SchoolClass modelis - klasė.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from database import Base


class SchoolClass(Base):
    """Klasė (pvz., 5a, 7b)."""

    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(10), nullable=False, index=True)  # "5a", "7b"
    grade = Column(Integer, nullable=False, index=True)  # 5, 6, 7, 8
    school_year_id = Column(Integer, ForeignKey("school_years.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    school_year = relationship("SchoolYear", back_populates="classes")
    students = relationship("Student", back_populates="school_class", cascade="all, delete-orphan")
    tests = relationship("Test", back_populates="school_class")
    statistics = relationship("ClassStatistics", back_populates="school_class", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<SchoolClass(id={self.id}, name='{self.name}', grade={self.grade})>"
