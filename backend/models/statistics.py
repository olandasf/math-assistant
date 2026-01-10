"""
Statistics modeliai - statistika mokiniams ir klasėms.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text
from sqlalchemy.orm import relationship

from database import Base


class StudentStatistics(Base):
    """Mokinio statistika pagal temą."""
    
    __tablename__ = "student_statistics"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(100), nullable=False, index=True)  # "algebra", "geometry"
    tests_count = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)  # Vidutinis procentas
    average_grade = Column(Float, default=0.0)  # Vidutinis pažymys
    best_score = Column(Float, default=0.0)
    worst_score = Column(Float, default=0.0)
    common_errors = Column(Text, nullable=True)  # JSON - dažniausios klaidos
    improvement_trend = Column(Float, default=0.0)  # Teigiamas = gerėja
    
    # Foreign key
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="statistics")

    def __repr__(self) -> str:
        return f"<StudentStatistics(student_id={self.student_id}, topic='{self.topic}')>"


class ClassStatistics(Base):
    """Klasės statistika pagal temą."""
    
    __tablename__ = "class_statistics"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(100), nullable=False, index=True)
    tests_count = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    average_grade = Column(Float, default=0.0)
    best_score = Column(Float, default=0.0)
    worst_score = Column(Float, default=0.0)
    pass_rate = Column(Float, default=0.0)  # % mokinių >= 4
    common_errors = Column(Text, nullable=True)  # JSON
    
    # Foreign key
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    school_class = relationship("SchoolClass", back_populates="statistics")

    def __repr__(self) -> str:
        return f"<ClassStatistics(class_id={self.class_id}, topic='{self.topic}')>"
