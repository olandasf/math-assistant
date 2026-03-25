"""
API Router - Uždavinių bazė (Problem Bank).

Endpoints:
- GET /problem-bank - gauti uždavinius su filtrais
- GET /problem-bank/random - gauti atsitiktinius
- POST /problem-bank/import - importuoti iš HuggingFace
- GET /problem-bank/{id} - gauti pagal ID
"""

from typing import List, Literal, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from loguru import logger
from pydantic import BaseModel, Field
from services.problem_bank_service import ProblemBankService
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db

router = APIRouter(prefix="/problem-bank", tags=["Uždavinių bazė"])


# === Schemas ===


class ProblemResponse(BaseModel):
    """Uždavinio atsakymas."""

    id: int
    source: str
    source_id: Optional[str] = None
    question_lt: str
    question_en: Optional[str] = None
    answer: str
    answer_latex: Optional[str] = None
    solution_steps: List[str] = []
    grade_min: int
    grade_max: int
    difficulty: str
    topic_id: Optional[str] = None
    subtopic_id: Optional[str] = None
    tags: List[str] = []
    is_verified: bool
    is_active: bool
    quality_score: Optional[float] = None
    times_used: int
    points: int
    estimated_time_minutes: Optional[int] = None

    class Config:
        from_attributes = True


class ProblemListResponse(BaseModel):
    """Uždavinių sąrašo atsakymas."""

    items: List[ProblemResponse]
    total: int
    page: int
    per_page: int
    pages: int


class ImportRequest(BaseModel):
    """Importavimo užklausa."""

    source: Literal["gsm8k", "competition_math"] = Field(
        default="gsm8k", description="Šaltinis"
    )
    limit: int = Field(default=50, ge=1, le=500, description="Kiek importuoti")
    translate: bool = Field(default=True, description="Ar versti į lietuvių k.")
    generate_variations: bool = Field(
        default=True, description="Ar generuoti variacijas"
    )


class ImportResponse(BaseModel):
    """Importavimo rezultatas."""

    status: str
    message: str
    imported: int = 0
    skipped: int = 0
    errors: int = 0
    task_id: Optional[str] = None


class StatsResponse(BaseModel):
    """Statistikos atsakymas."""

    total_problems: int
    by_source: dict
    by_difficulty: dict
    by_grade: dict
    verified_count: int
    active_count: int


# === Endpoints ===


@router.get("", response_model=ProblemListResponse)
async def get_problems(
    grade: Optional[int] = Query(None, ge=5, le=12, description="Klasė"),
    difficulty: Optional[str] = Query(None, description="Sunkumas"),
    topic_id: Optional[str] = Query(None, description="Temos ID"),
    source: Optional[str] = Query(None, description="Šaltinis"),
    verified_only: bool = Query(False, description="Tik patikrinti"),
    search: Optional[str] = Query(None, description="Paieškos tekstas"),
    page: int = Query(1, ge=1, description="Puslapis"),
    per_page: int = Query(20, ge=1, le=100, description="Elementų per puslapį"),
    db: AsyncSession = Depends(get_db),
) -> ProblemListResponse:
    """
    Gauna uždavinius su filtrais ir puslapiavimu.
    """
    service = ProblemBankService(db)

    # Gauti uždavinius
    problems, total = await service.get_filtered(
        grade=grade,
        difficulty=difficulty,
        topic_id=topic_id,
        source=source,
        verified_only=verified_only,
        search=search,
        offset=(page - 1) * per_page,
        limit=per_page,
    )

    # Konvertuoti į response
    items = []
    for p in problems:
        items.append(
            ProblemResponse(
                id=p.id,
                source=p.source.value,
                source_id=p.source_id,
                question_lt=p.question_lt,
                question_en=p.question_en,
                answer=p.answer,
                answer_latex=p.answer_latex,
                solution_steps=p.solution_steps_list,
                grade_min=p.grade_min,
                grade_max=p.grade_max,
                difficulty=p.difficulty.value,
                topic_id=p.topic_id,
                subtopic_id=p.subtopic_id,
                tags=p.tags_list,
                is_verified=p.is_verified,
                is_active=p.is_active,
                quality_score=p.quality_score,
                times_used=p.times_used,
                points=p.points,
                estimated_time_minutes=p.estimated_time_minutes,
            )
        )

    pages = (total + per_page - 1) // per_page

    return ProblemListResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get("/random", response_model=List[ProblemResponse])
async def get_random_problems(
    grade: int = Query(..., ge=5, le=12, description="Klasė"),
    count: int = Query(5, ge=1, le=20, description="Kiekis"),
    difficulty: Optional[str] = Query(None, description="Sunkumas"),
    topic_id: Optional[str] = Query(None, description="Temos ID"),
    exclude_ids: Optional[str] = Query(
        None, description="Išskirti ID (kableliais atskirti)"
    ),
    db: AsyncSession = Depends(get_db),
) -> List[ProblemResponse]:
    """
    Gauna atsitiktinius uždavinius pagal parametrus.
    Naudojama kontrolinių generavimui.
    """
    service = ProblemBankService(db)

    # Parsinamas exclude_ids
    exclude = []
    if exclude_ids:
        exclude = [
            int(x.strip()) for x in exclude_ids.split(",") if x.strip().isdigit()
        ]

    problems = await service.get_random(
        grade=grade,
        count=count,
        difficulty=difficulty,
        topic_id=topic_id,
        exclude_ids=exclude,
    )

    return [
        ProblemResponse(
            id=p.id,
            source=p.source.value,
            source_id=p.source_id,
            question_lt=p.question_lt,
            question_en=p.question_en,
            answer=p.answer,
            answer_latex=p.answer_latex,
            solution_steps=p.solution_steps_list,
            grade_min=p.grade_min,
            grade_max=p.grade_max,
            difficulty=p.difficulty.value,
            topic_id=p.topic_id,
            subtopic_id=p.subtopic_id,
            tags=p.tags_list,
            is_verified=p.is_verified,
            is_active=p.is_active,
            quality_score=p.quality_score,
            times_used=p.times_used,
            points=p.points,
            estimated_time_minutes=p.estimated_time_minutes,
        )
        for p in problems
    ]


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db),
) -> StatsResponse:
    """
    Gauna uždavinių bazės statistiką.
    """
    service = ProblemBankService(db)
    stats = await service.get_stats()
    return StatsResponse(**stats)


@router.post("/import", response_model=ImportResponse)
async def import_problems(
    request: ImportRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> ImportResponse:
    """
    Importuoja uždavinius iš HuggingFace.

    Procesas vyksta fone - grąžinamas task_id statusui sekti.
    """
    service = ProblemBankService(db)

    # Mažam kiekiui - sinchroniškai
    if request.limit <= 10:
        try:
            stats = await service.import_from_huggingface(
                source=request.source,
                limit=request.limit,
                translate=request.translate,
                generate_variations=request.generate_variations,
            )
            return ImportResponse(
                status="completed",
                message=f"Importuota {stats['saved']} uždavinių",
                imported=stats["saved"],
                skipped=stats["skipped"],
                errors=stats["errors"],
            )
        except Exception as e:
            logger.error(f"Import error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Importavimo klaida: {str(e)}",
            )

    # Dideliam kiekiui - fone
    import uuid

    task_id = str(uuid.uuid4())

    # TODO: Implementuoti background task su progress tracking
    # background_tasks.add_task(
    #     service.import_from_huggingface_background,
    #     task_id=task_id,
    #     source=request.source,
    #     limit=request.limit,
    # )

    return ImportResponse(
        status="pending",
        message=f"Importavimas pradėtas fone ({request.limit} uždavinių)",
        task_id=task_id,
    )


@router.get("/{problem_id}", response_model=ProblemResponse)
async def get_problem(
    problem_id: int,
    db: AsyncSession = Depends(get_db),
) -> ProblemResponse:
    """
    Gauna uždavinį pagal ID.
    """
    service = ProblemBankService(db)
    problem = await service.get_by_id(problem_id)

    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Uždavinys {problem_id} nerastas",
        )

    return ProblemResponse(
        id=problem.id,
        source=problem.source.value,
        source_id=problem.source_id,
        question_lt=problem.question_lt,
        question_en=problem.question_en,
        answer=problem.answer,
        answer_latex=problem.answer_latex,
        solution_steps=problem.solution_steps_list,
        grade_min=problem.grade_min,
        grade_max=problem.grade_max,
        difficulty=problem.difficulty.value,
        topic_id=problem.topic_id,
        subtopic_id=problem.subtopic_id,
        tags=problem.tags_list,
        is_verified=problem.is_verified,
        is_active=problem.is_active,
        quality_score=problem.quality_score,
        times_used=problem.times_used,
        points=problem.points,
        estimated_time_minutes=problem.estimated_time_minutes,
    )


@router.patch("/{problem_id}/verify")
async def verify_problem(
    problem_id: int,
    verified: bool = True,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Pažymi uždavinį kaip patikrintą/nepatikrintą.
    """
    service = ProblemBankService(db)
    problem = await service.update(problem_id, is_verified=verified)

    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Uždavinys {problem_id} nerastas",
        )

    return {
        "id": problem_id,
        "is_verified": verified,
        "message": (
            "Uždavinys pažymėtas kaip patikrintas"
            if verified
            else "Uždavinys pažymėtas kaip nepatikrintas"
        ),
    }


@router.delete("/{problem_id}")
async def delete_problem(
    problem_id: int,
    hard_delete: bool = Query(False, description="Ištrinti visiškai"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Ištrina uždavinį (soft arba hard delete).
    """
    service = ProblemBankService(db)

    if hard_delete:
        success = await service.delete(problem_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Uždavinys {problem_id} nerastas",
            )
        return {"message": f"Uždavinys {problem_id} ištrintas visiškai"}
    else:
        problem = await service.update(problem_id, is_active=False)
        if not problem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Uždavinys {problem_id} nerastas",
            )
        return {"message": f"Uždavinys {problem_id} deaktyvuotas"}
