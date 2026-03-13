"""
Pydantic schemas - Užduotis.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class TaskBase(BaseModel):
    """Bazinė schema užduočiai."""
    number: str = Field(..., min_length=1, max_length=10, description="Užduoties numeris, pvz. '1' arba '1a'")
    text: Optional[str] = Field(None, description="Užduoties tekstas")
    correct_answer: str = Field(..., description="Teisingas atsakymas (LaTeX formatu)")
    correct_answer_numeric: Optional[float] = Field(None, description="Skaitinė atsakymo reikšmė")
    points: float = Field(..., ge=0, description="Taškų skaičius")
    topic: Optional[str] = Field(None, max_length=100, description="Tema")
    difficulty: int = Field(default=1, ge=1, le=5, description="Sudėtingumas (1-5)")


class TaskCreate(TaskBase):
    """Schema naujai užduočiai sukurti."""
    variant_id: int = Field(..., description="Varianto ID")
    order_index: int = Field(default=0, description="Rikiavimo indeksas")
    solution_steps: Optional[str] = Field(None, description="Sprendimo žingsniai (JSON)")


class TaskUpdate(BaseModel):
    """Schema užduočiai atnaujinti."""
    number: Optional[str] = Field(None, min_length=1, max_length=10)
    text: Optional[str] = None
    correct_answer: Optional[str] = None
    correct_answer_numeric: Optional[float] = None
    points: Optional[float] = Field(None, ge=0)
    topic: Optional[str] = Field(None, max_length=100)
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    order_index: Optional[int] = None
    solution_steps: Optional[str] = None


class TaskRead(TaskBase):
    """Schema užduoties skaitymui."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_index: int
    solution_steps: Optional[str] = None
    variant_id: int
    created_at: datetime
    updated_at: datetime


class TaskBulkCreate(BaseModel):
    """Schema daugelio užduočių sukūrimui."""
    variant_id: int = Field(..., description="Varianto ID")
    tasks: List[TaskBase] = Field(..., min_length=1, description="Užduočių sąrašas")
