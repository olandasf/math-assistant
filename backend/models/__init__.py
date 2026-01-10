"""
Models package - SQLAlchemy modeliai.
"""

from models.school_year import SchoolYear
from models.school_class import SchoolClass
from models.student import Student
from models.test import Test
from models.variant import Variant
from models.task import Task
from models.submission import Submission
from models.answer import Answer
from models.error import Error
from models.statistics import StudentStatistics, ClassStatistics
from models.ocr_result import OCRResult
from models.setting import Setting
from models.backup import Backup

__all__ = [
    "SchoolYear",
    "SchoolClass", 
    "Student",
    "Test",
    "Variant",
    "Task",
    "Submission",
    "Answer",
    "Error",
    "StudentStatistics",
    "ClassStatistics",
    "OCRResult",
    "Setting",
    "Backup"
]
