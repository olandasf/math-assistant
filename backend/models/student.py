"""
Student modelis - mokinys.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from database import Base


class Student(Base):
    """Mokinys su unikaliu kodu (GDPR)."""
    
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    unique_code = Column(String(20), unique=True, nullable=False, index=True)  # "M2026001"
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    school_class = relationship("SchoolClass", back_populates="students")
    submissions = relationship("Submission", back_populates="student", cascade="all, delete-orphan")
    statistics = relationship("StudentStatistics", back_populates="student", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        """Pilnas vardas."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def anonymized_name(self) -> str:
        """Anonimizuotas vardas API užklausoms."""
        return f"Mokinys_{self.unique_code}"

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, code='{self.unique_code}', name='{self.full_name}')>"
