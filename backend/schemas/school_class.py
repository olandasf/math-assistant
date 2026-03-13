"""
Pydantic schemas - Klasė.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ClassBase(BaseModel):
    """Bazinė schema klasei."""
    name: str = Field(..., min_length=1, max_length=10, description="Klasės pavadinimas, pvz. '5a'")
    grade: int = Field(..., ge=1, le=12, description="Klasės numeris (1-12)")


class ClassCreate(ClassBase):
    """Schema naujai klasei sukurti."""
    school_year_id: int = Field(..., description="Mokslo metų ID")


class ClassUpdate(BaseModel):
    """Schema klasei atnaujinti."""
    name: Optional[str] = Field(None, min_length=1, max_length=10)
    grade: Optional[int] = Field(None, ge=1, le=12)
    school_year_id: Optional[int] = None


class ClassRead(ClassBase):
    """Schema klasės skaitymui."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    school_year_id: int
    created_at: datetime
    updated_at: datetime


class ClassWithStudents(ClassRead):
    """Schema su mokinių sąrašu."""
    students: List["StudentRead"] = []
    students_count: int = 0
    school_year_name: Optional[str] = None


# Forward reference
from schemas.student import StudentRead
ClassWithStudents.model_rebuild()
