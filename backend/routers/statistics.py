"""
Statistics Router - Statistikos API
===================================
Endpointai statistikos gavimui.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from pydantic import BaseModel
from services.statistics_service import (
    ClassStats,
    ErrorPattern,
    StatisticsService,
    StudentStats,
    TopicStats,
)
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db

router = APIRouter(prefix="/statistics", tags=["statistics"])


# === Schemas ===


class StudentStatsResponse(BaseModel):
    """Mokinio statistikos atsakymas."""

    student_id: int
    student_name: str
    student_code: str
    class_name: str
    total_tests: int
    completed_tests: int
    average_grade: float
    highest_grade: float
    lowest_grade: float
    total_points: float
    max_points: float
    percentage: float
    correct_answers: int
    incorrect_answers: int
    accuracy: float
    grade_trend: List[float]


class ClassStatsResponse(BaseModel):
    """Klasės statistikos atsakymas."""

    class_id: int
    class_name: str
    student_count: int
    average_grade: float
    median_grade: float
    highest_grade: float
    lowest_grade: float
    std_deviation: float
    grade_distribution: Dict[str, int]
    top_students: List[Dict[str, Any]]
    struggling_students: List[Dict[str, Any]]


class TopicStatsResponse(BaseModel):
    """Temos statistikos atsakymas."""

    topic: str
    total_tasks: int
    correct_count: int
    incorrect_count: int
    accuracy: float
    average_points: float


class ErrorPatternResponse(BaseModel):
    """Klaidų šablono atsakymas."""

    error_type: str
    description: str
    frequency: int
    affected_students: int
    suggestions: List[str]


class OverviewResponse(BaseModel):
    """Bendros statistikos atsakymas."""

    students_count: int
    classes_count: int
    tests_count: int
    submissions_count: int
    pending_count: int
    average_grade: float
    this_week_tests: int


# === Endpoints ===


@router.get("/overview", response_model=OverviewResponse)
async def get_overview_stats(db: AsyncSession = Depends(get_db)):
    """
    Gauti bendrą statistikos apžvalgą (Dashboard).
    """
    service = StatisticsService(db)
    stats = await service.get_dashboard_stats()

    return OverviewResponse(**stats)


@router.get("/student/{student_id}", response_model=StudentStatsResponse)
async def get_student_stats(
    student_id: int,
    school_year_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Gauti mokinio statistiką.

    Grąžina:
    - Vidutinį pažymį
    - Aukščiausią/žemiausią pažymį
    - Taškų procentą
    - Teisingų atsakymų skaičių
    - Pažymių tendenciją
    """
    try:
        service = StatisticsService(db)
        stats = await service.get_student_statistics(student_id, school_year_id)

        return StudentStatsResponse(
            student_id=stats.student_id,
            student_name=stats.student_name,
            student_code=stats.student_code,
            class_name=stats.class_name,
            total_tests=stats.total_tests,
            completed_tests=stats.completed_tests,
            average_grade=stats.average_grade,
            highest_grade=stats.highest_grade,
            lowest_grade=stats.lowest_grade,
            total_points=stats.total_points,
            max_points=stats.max_points,
            percentage=stats.percentage,
            correct_answers=stats.correct_answers,
            incorrect_answers=stats.incorrect_answers,
            accuracy=stats.accuracy,
            grade_trend=stats.grade_trend,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/class/{class_id}", response_model=ClassStatsResponse)
async def get_class_stats(
    class_id: int, test_id: Optional[int] = None, db: AsyncSession = Depends(get_db)
):
    """
    Gauti klasės statistiką.

    Grąžina:
    - Vidutinį pažymį
    - Medianą
    - Standartinį nuokrypį
    - Pažymių pasiskirstymą
    - Top ir silpniausius mokinius
    """
    try:
        service = StatisticsService(db)
        stats = await service.get_class_statistics(class_id, test_id)

        # Convert grade_distribution keys to strings for JSON
        grade_dist = {str(k): v for k, v in stats.grade_distribution.items()}

        return ClassStatsResponse(
            class_id=stats.class_id,
            class_name=stats.class_name,
            student_count=stats.student_count,
            average_grade=stats.average_grade,
            median_grade=stats.median_grade,
            highest_grade=stats.highest_grade,
            lowest_grade=stats.lowest_grade,
            std_deviation=stats.std_deviation,
            grade_distribution=grade_dist,
            top_students=stats.top_students,
            struggling_students=stats.struggling_students,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/topics", response_model=List[TopicStatsResponse])
async def get_topics_stats(
    class_id: Optional[int] = None,
    test_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Gauti temų statistiką.

    Grąžina kiekvienai temai:
    - Užduočių skaičių
    - Teisingų/neteisingų atsakymų skaičių
    - Tikslumą procentais
    """
    service = StatisticsService(db)
    topics = await service.get_topic_statistics(class_id, test_id)

    return [
        TopicStatsResponse(
            topic=t.topic,
            total_tasks=t.total_tasks,
            correct_count=t.correct_count,
            incorrect_count=t.incorrect_count,
            accuracy=t.accuracy,
            average_points=t.average_points,
        )
        for t in topics
    ]


@router.get("/errors", response_model=List[ErrorPatternResponse])
async def get_error_patterns(
    class_id: Optional[int] = None,
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Gauti dažniausių klaidų šablonus.

    Naudinga identifikuoti:
    - Dažniausiai klystamas užduotis
    - Bendrus sunkumus
    """
    service = StatisticsService(db)
    patterns = await service.get_error_patterns(class_id, limit)

    return [
        ErrorPatternResponse(
            error_type=p.error_type,
            description=p.description[:100] if p.description else "",
            frequency=p.frequency,
            affected_students=p.affected_students,
            suggestions=p.suggestions,
        )
        for p in patterns
    ]


@router.get("/comparison")
async def compare_classes(
    class_ids: str = Query(
        ..., description="Klasių ID atskirti kableliais, pvz: 1,2,3"
    ),
    test_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Palyginti kelių klasių statistiką.
    """
    try:
        ids = [int(x.strip()) for x in class_ids.split(",")]
    except ValueError:
        raise HTTPException(status_code=400, detail="Neteisingas class_ids formatas")

    service = StatisticsService(db)
    results = []

    for class_id in ids:
        try:
            stats = await service.get_class_statistics(class_id, test_id)
            results.append(
                {
                    "class_id": stats.class_id,
                    "class_name": stats.class_name,
                    "student_count": stats.student_count,
                    "average_grade": stats.average_grade,
                    "median_grade": stats.median_grade,
                }
            )
        except ValueError:
            continue

    return {
        "classes": results,
        "comparison": {
            "best_class": (
                max(results, key=lambda x: x["average_grade"])["class_name"]
                if results
                else None
            ),
            "average_all": (
                sum(r["average_grade"] for r in results) / len(results)
                if results
                else 0
            ),
        },
    }


@router.get("/trends/{class_id}")
async def get_grade_trends(
    class_id: int,
    months: int = Query(default=6, le=12),
    db: AsyncSession = Depends(get_db),
):
    """
    Gauti pažymių tendencijas per laikotarpį.
    """
    # TODO: Implementuoti realų skaičiavimą pagal datas
    # Dabar grąžiname demo duomenis

    return {
        "class_id": class_id,
        "period_months": months,
        "data": [
            {"month": "2025-09", "average": 6.8},
            {"month": "2025-10", "average": 7.1},
            {"month": "2025-11", "average": 7.0},
            {"month": "2025-12", "average": 7.3},
            {"month": "2026-01", "average": 7.5},
        ],
    }
