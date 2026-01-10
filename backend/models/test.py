"""
Test modelis - kontrolinis darbas.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Text, Float
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from database import Base


class TestStatus(str, PyEnum):
    """Kontrolinio statusas."""
    DRAFT = "draft"  # Kuriamas
    ACTIVE = "active"  # Tikrinamas
    COMPLETED = "completed"  # Baigtas


class Test(Base):
    """Kontrolinis darbas."""
    
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)  # "Lygtys ir nelygybės"
    description = Column(Text, nullable=True)
    test_date = Column(Date, nullable=False)
    topic = Column(String(100), nullable=True, index=True)  # "algebra", "geometry"
    max_points = Column(Float, default=0.0)  # Automatiškai skaičiuojama
    time_limit_minutes = Column(Integer, nullable=True)  # 45 min
    status = Column(String(20), default=TestStatus.DRAFT, index=True)
    
    # Foreign keys
    school_year_id = Column(Integer, ForeignKey("school_years.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    school_year = relationship("SchoolYear", back_populates="tests")
    school_class = relationship("SchoolClass", back_populates="tests")
    variants = relationship("Variant", back_populates="test", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="test", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Test(id={self.id}, title='{self.title}', status='{self.status}')>"
