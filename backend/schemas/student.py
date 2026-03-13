"""
Pydantic schemas - Mokinys.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class StudentBase(BaseModel):
    """Bazinė schema mokiniui."""
    first_name: str = Field(..., min_length=1, max_length=50, description="Vardas")
    last_name: str = Field(..., min_length=1, max_length=50, description="Pavardė")


class StudentCreate(StudentBase):
    """Schema naujam mokiniui sukurti."""
    class_id: int = Field(..., description="Klasės ID")
    unique_code: Optional[str] = Field(None, max_length=20, description="Unikalus kodas (generuojamas automatiškai)")


class StudentUpdate(BaseModel):
    """Schema mokiniui atnaujinti."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    class_id: Optional[int] = None


class StudentRead(StudentBase):
    """Schema mokinio skaitymui."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    unique_code: str
    class_id: int
    created_at: datetime
    updated_at: datetime


class StudentWithClass(StudentRead):
    """Schema su klasės informacija."""
    class_name: Optional[str] = None
    grade: Optional[int] = None


class StudentBulkCreate(BaseModel):
    """Schema daugelio mokinių sukūrimui vienu metu."""
    class_id: int = Field(..., description="Klasės ID")
    students: list[StudentBase] = Field(..., min_length=1, description="Mokinių sąrašas")
