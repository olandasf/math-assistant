"""
Pydantic schemas - Mokslo metai.
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class SchoolYearBase(BaseModel):
    """Bazinė schema mokslo metams."""
    name: str = Field(..., min_length=7, max_length=20, description="Pavadinimas, pvz. '2025-2026'")
    start_date: date = Field(..., description="Pradžios data")
    end_date: date = Field(..., description="Pabaigos data")


class SchoolYearCreate(SchoolYearBase):
    """Schema naujiems mokslo metams sukurti."""
    is_active: bool = Field(default=False, description="Ar šie metai aktyvūs")


class SchoolYearUpdate(BaseModel):
    """Schema mokslo metams atnaujinti."""
    name: Optional[str] = Field(None, min_length=7, max_length=20)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None


class SchoolYearRead(SchoolYearBase):
    """Schema mokslo metų skaitymui."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SchoolYearWithClasses(SchoolYearRead):
    """Schema su klasių sąrašu."""
    classes: List["ClassRead"] = []
    classes_count: int = 0


# Forward reference
from schemas.school_class import ClassRead
SchoolYearWithClasses.model_rebuild()
