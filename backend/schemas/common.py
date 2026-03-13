"""
Bendros Pydantic schemas.
"""

from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response schema."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
    error_code: Optional[str] = None


class HealthCheck(BaseModel):
    """Health check response."""
    status: str
    database: str
    api_version: str


class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_students: int = 0
    total_classes: int = 0
    total_tests: int = 0
    pending_submissions: int = 0
    completed_today: int = 0
    average_grade: Optional[float] = None
