"""
Pydantic schemas - Klaida.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ErrorBase(BaseModel):
    """Bazinė schema klaidai."""
    error_type: str = Field(..., max_length=50, description="Klaidos tipas")
    error_code: Optional[str] = Field(None, max_length=20, description="Klaidos kodas")
    description: str = Field(..., description="Klaidos aprašymas")


class ErrorCreate(ErrorBase):
    """Schema naujai klaidai sukurti."""
    answer_id: int = Field(..., description="Atsakymo ID")
    explanation: Optional[str] = Field(None, description="Paaiškinimas")
    suggestion: Optional[str] = Field(None, description="Patarimas")
    severity: int = Field(default=1, ge=1, le=3, description="Sunkumas (1-3)")


class ErrorUpdate(BaseModel):
    """Schema klaidai atnaujinti."""
    error_type: Optional[str] = Field(None, max_length=50)
    error_code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    explanation: Optional[str] = None
    suggestion: Optional[str] = None
    severity: Optional[int] = Field(None, ge=1, le=3)


class ErrorRead(BaseModel):
    """Schema klaidos skaitymui."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    error_type: str
    error_code: Optional[str]
    description: str
    explanation: Optional[str]
    suggestion: Optional[str]
    severity: int
    answer_id: int
    created_at: datetime
