"""
Pydantic schemas - Atsakymas.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class AnswerBase(BaseModel):
    """Bazinė schema atsakymui."""
    recognized_text: Optional[str] = Field(None, description="Atpažintas tekstas")
    recognized_latex: Optional[str] = Field(None, description="Atpažintas LaTeX")


class AnswerCreate(BaseModel):
    """Schema naujam atsakymui sukurti."""
    submission_id: int = Field(..., description="Pateikimo ID")
    task_id: int = Field(..., description="Užduoties ID")
    recognized_text: Optional[str] = None
    recognized_latex: Optional[str] = None
    ocr_confidence: float = Field(default=0.0, ge=0, le=1)
    image_region: Optional[str] = None


class AnswerUpdate(BaseModel):
    """Schema atsakymui atnaujinti."""
    recognized_text: Optional[str] = None
    recognized_latex: Optional[str] = None
    is_correct: Optional[bool] = None
    earned_points: Optional[float] = Field(None, ge=0)
    ai_explanation: Optional[str] = None
    teacher_override: Optional[bool] = None
    teacher_points: Optional[float] = Field(None, ge=0)
    teacher_comment: Optional[str] = None


class AnswerRead(BaseModel):
    """Schema atsakymo skaitymui."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    recognized_text: Optional[str]
    recognized_latex: Optional[str]
    ocr_confidence: float
    is_correct: Optional[bool]
    earned_points: float
    max_points: float
    ai_explanation: Optional[str]
    teacher_override: bool
    teacher_points: Optional[float]
    teacher_comment: Optional[str]
    image_region: Optional[str]
    submission_id: int
    task_id: int
    created_at: datetime
    updated_at: datetime


class AnswerWithTask(AnswerRead):
    """Schema su užduoties informacija."""
    task_number: Optional[str] = None
    correct_answer: Optional[str] = None


class AnswerCheck(BaseModel):
    """Schema atsakymo tikrinimo rezultatui."""
    answer_id: int
    is_correct: bool
    earned_points: float
    explanation: Optional[str] = None
    errors: List["ErrorRead"] = []


# Forward reference
from schemas.error import ErrorRead
AnswerCheck.model_rebuild()
