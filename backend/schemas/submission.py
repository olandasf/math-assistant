"""
Pydantic schemas - Pateiktas darbas (Submission).
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class SubmissionBase(BaseModel):
    """Bazinė schema pateiktam darbui."""
    file_name: str = Field(..., max_length=200, description="Failo pavadinimas")
    file_type: str = Field(..., max_length=10, description="Failo tipas")


class SubmissionCreate(BaseModel):
    """Schema naujam pateikimui sukurti."""
    student_id: int = Field(..., description="Mokinio ID")
    test_id: int = Field(..., description="Kontrolinio ID")
    variant_id: Optional[int] = Field(None, description="Varianto ID")


class SubmissionUpdate(BaseModel):
    """Schema pateikimui atnaujinti."""
    status: Optional[str] = Field(None, pattern="^(uploaded|processing|ocr_done|checking|reviewed|completed)$")
    variant_id: Optional[int] = None
    total_points: Optional[float] = Field(None, ge=0)
    grade: Optional[int] = Field(None, ge=1, le=10)
    teacher_notes: Optional[str] = None


class SubmissionRead(BaseModel):
    """Schema pateikimo skaitymui."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_path: str
    file_name: str
    file_type: str
    status: str
    total_points: float
    max_points: float
    percentage: float
    grade: Optional[int]
    teacher_notes: Optional[str]
    student_id: int
    test_id: int
    variant_id: Optional[int]
    submitted_at: datetime
    checked_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class SubmissionWithDetails(SubmissionRead):
    """Schema su papildoma informacija."""
    student_name: Optional[str] = None
    student_code: Optional[str] = None
    test_title: Optional[str] = None
    variant_name: Optional[str] = None
    answers_count: int = 0


class SubmissionListItem(BaseModel):
    """Schema sąrašo elementui (lengvesnė)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_name: str
    status: str
    total_points: float
    max_points: float
    percentage: float
    grade: Optional[int]
    student_id: int
    student_name: Optional[str] = None
    submitted_at: datetime
