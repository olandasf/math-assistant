"""
Pydantic schemas - Kontrolinis darbas.
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class TestBase(BaseModel):
    """Bazinė schema kontroliniam."""
    title: str = Field(..., min_length=1, max_length=200, description="Pavadinimas")
    description: Optional[str] = Field(None, max_length=1000, description="Aprašymas")
    test_date: date = Field(..., description="Kontrolinio data")
    topic: Optional[str] = Field(None, max_length=100, description="Tema")
    time_limit_minutes: Optional[int] = Field(None, ge=1, le=180, description="Laiko limitas minutėmis")


class TestCreate(TestBase):
    """Schema naujam kontroliniui sukurti."""
    school_year_id: int = Field(..., description="Mokslo metų ID")
    class_id: int = Field(..., description="Klasės ID")


class TestUpdate(BaseModel):
    """Schema kontroliniui atnaujinti."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    test_date: Optional[date] = None
    topic: Optional[str] = Field(None, max_length=100)
    time_limit_minutes: Optional[int] = Field(None, ge=1, le=180)
    status: Optional[str] = Field(None, pattern="^(draft|active|completed)$")


class TestRead(TestBase):
    """Schema kontrolinio skaitymui."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    max_points: float
    status: str
    school_year_id: int
    class_id: int
    created_at: datetime
    updated_at: datetime


class TestWithDetails(TestRead):
    """Schema su papildoma informacija."""
    class_name: Optional[str] = None
    variants_count: int = 0
    submissions_count: int = 0
    checked_count: int = 0
