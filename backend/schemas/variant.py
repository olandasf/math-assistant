"""
Pydantic schemas - Variantas.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class VariantBase(BaseModel):
    """Bazinė schema variantui."""
    name: str = Field(..., min_length=1, max_length=10, description="Varianto pavadinimas, pvz. 'I' arba 'II'")


class VariantCreate(VariantBase):
    """Schema naujam variantui sukurti."""
    test_id: int = Field(..., description="Kontrolinio ID")


class VariantUpdate(BaseModel):
    """Schema variantui atnaujinti."""
    name: Optional[str] = Field(None, min_length=1, max_length=10)


class VariantRead(VariantBase):
    """Schema varianto skaitymui."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    max_points: float
    test_id: int
    created_at: datetime
    updated_at: datetime


class VariantWithTasks(VariantRead):
    """Schema su užduočių sąrašu."""
    tasks: List["TaskRead"] = []
    tasks_count: int = 0


# Forward reference
from schemas.task import TaskRead
VariantWithTasks.model_rebuild()
