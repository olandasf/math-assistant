"""
API Router - Dashboard ir statistika.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.student import Student
from models.school_class import SchoolClass
from models.test import Test
from models.submission import Submission
from schemas.common import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db)
) -> DashboardStats:
    """Gauti dashboard statistiką."""

    # Mokinių skaičius
    students_count = await db.execute(select(func.count(Student.id)))
    total_students = students_count.scalar() or 0

    # Klasių skaičius
    classes_count = await db.execute(select(func.count(SchoolClass.id)))
    total_classes = classes_count.scalar() or 0

    # Kontrolinių skaičius
    tests_count = await db.execute(select(func.count(Test.id)))
    total_tests = tests_count.scalar() or 0

    # Laukiančių tikrinimo
    pending_count = await db.execute(
        select(func.count(Submission.id))
        .where(Submission.status.in_(["uploaded", "processing", "ocr_done", "checking"]))
    )
    pending_submissions = pending_count.scalar() or 0

    # Patikrinta šiandien
    from datetime import date
    today = date.today()
    completed_today_count = await db.execute(
        select(func.count(Submission.id))
        .where(
            Submission.status == "completed",
            func.date(Submission.checked_at) == today
        )
    )
    completed_today = completed_today_count.scalar() or 0

    # Vidutinis pažymys
    avg_grade = await db.execute(
        select(func.avg(Submission.grade))
        .where(Submission.grade.isnot(None))
    )
    average_grade = avg_grade.scalar()

    return DashboardStats(
        total_students=total_students,
        total_classes=total_classes,
        total_tests=total_tests,
        pending_submissions=pending_submissions,
        completed_today=completed_today,
        average_grade=round(average_grade, 2) if average_grade else None
    )
