"""
Services package - Business logic.
"""

from services.base import CRUDBase
from services.school_year_service import SchoolYearService
from services.class_service import ClassService
from services.student_service import StudentService
from services.test_service import TestService
from services.variant_service import VariantService
from services.task_service import TaskService

__all__ = [
    "CRUDBase",
    "SchoolYearService",
    "ClassService",
    "StudentService",
    "TestService",
    "VariantService",
    "TaskService",
]
