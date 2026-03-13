"""
Schemas package - Pydantic schemas.
"""

from schemas.common import PaginatedResponse, MessageResponse, ErrorResponse, HealthCheck, DashboardStats
from schemas.school_year import SchoolYearCreate, SchoolYearUpdate, SchoolYearRead, SchoolYearWithClasses
from schemas.school_class import ClassCreate, ClassUpdate, ClassRead, ClassWithStudents
from schemas.student import StudentCreate, StudentUpdate, StudentRead, StudentWithClass, StudentBulkCreate
from schemas.test import TestCreate, TestUpdate, TestRead, TestWithDetails
from schemas.variant import VariantCreate, VariantUpdate, VariantRead, VariantWithTasks
from schemas.task import TaskCreate, TaskUpdate, TaskRead, TaskBulkCreate
from schemas.submission import SubmissionCreate, SubmissionUpdate, SubmissionRead, SubmissionWithDetails, SubmissionListItem
from schemas.answer import AnswerCreate, AnswerUpdate, AnswerRead, AnswerWithTask
from schemas.error import ErrorCreate, ErrorUpdate, ErrorRead

__all__ = [
    # Common
    "PaginatedResponse",
    "MessageResponse",
    "ErrorResponse",
    "HealthCheck",
    "DashboardStats",
    # School Year
    "SchoolYearCreate",
    "SchoolYearUpdate",
    "SchoolYearRead",
    "SchoolYearWithClasses",
    # Class
    "ClassCreate",
    "ClassUpdate",
    "ClassRead",
    "ClassWithStudents",
    # Student
    "StudentCreate",
    "StudentUpdate",
    "StudentRead",
    "StudentWithClass",
    "StudentBulkCreate",
    # Test
    "TestCreate",
    "TestUpdate",
    "TestRead",
    "TestWithDetails",
    # Variant
    "VariantCreate",
    "VariantUpdate",
    "VariantRead",
    "VariantWithTasks",
    # Task
    "TaskCreate",
    "TaskUpdate",
    "TaskRead",
    "TaskBulkCreate",
    # Submission
    "SubmissionCreate",
    "SubmissionUpdate",
    "SubmissionRead",
    "SubmissionWithDetails",
    "SubmissionListItem",
    # Answer
    "AnswerCreate",
    "AnswerUpdate",
    "AnswerRead",
    "AnswerWithTask",
    # Error
    "ErrorCreate",
    "ErrorUpdate",
    "ErrorRead",
]
