"""
Routers package - API endpoints.
"""

from routers.school_years import router as school_years_router
from routers.classes import router as classes_router
from routers.students import router as students_router
from routers.tests import router as tests_router
from routers.dashboard import router as dashboard_router

__all__ = [
    "school_years_router",
    "classes_router",
    "students_router",
    "tests_router",
    "dashboard_router",
]
