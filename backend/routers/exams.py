"""
Exams Router - kontrolinių API endpointai.

Endpoints:
- POST /exams - sukurti naują kontrolinį (išsaugo DB + generuoja PDF)
- GET /exams - gauti kontrolinių sąrašą
- GET /exams/{id} - gauti kontrolinį su užduotimis
- POST /exams/{id}/check-answer - patikrinti atsakymą
- GET /exams/{id}/pdf - parsisiųsti PDF
"""

from datetime import date
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from services.exam_service import ExamService
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db

router = APIRouter(prefix="/exams", tags=["Kontroliniai"])


# ============================================================
# SCHEMAS
# ============================================================


class TaskCreate(BaseModel):
    """Užduoties kūrimo schema."""

    number: str = Field(..., description="Užduoties numeris: 1, 2, 1a, 1b")
    text: str = Field(..., description="Užduoties tekstas")
    points: int = Field(default=1, ge=1, le=10)
    answer: Optional[str] = Field(None, description="Teisingas atsakymas")
    text_latex: Optional[str] = None
    answer_latex: Optional[str] = None
    solution_hint: Optional[str] = None
    workspace_height_mm: int = Field(default=70, ge=30, le=150)


class VariantCreate(BaseModel):
    """Varianto kūrimo schema."""

    name: str = Field(..., description="Varianto pavadinimas: I, II, A, B")
    tasks: List[TaskCreate]


class ExamCreate(BaseModel):
    """Kontrolinio kūrimo schema."""

    title: str = Field(..., min_length=3, max_length=200)
    class_id: int
    school_year_id: int
    test_date: date
    topic: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: int = Field(default=45, ge=15, le=180)
    grade: int = Field(default=5, ge=5, le=12)
    variants: List[VariantCreate]


class ExamResponse(BaseModel):
    """Kontrolinio atsakymo schema."""

    id: int
    exam_id: str
    title: str
    test_date: str
    total_points: float
    variants_count: int
    tasks_count: int
    student_pdf: str
    teacher_pdf: str
    status: str


class ExamListItem(BaseModel):
    """Kontrolinio sąrašo elementas."""

    id: int
    title: str
    test_date: Optional[str]
    topic: Optional[str]
    max_points: float
    status: str
    class_id: int


class TaskResponse(BaseModel):
    """Užduoties atsakymo schema."""

    id: int
    number: str
    text: Optional[str]
    correct_answer: str
    correct_answer_numeric: Optional[float]
    points: float


class VariantResponse(BaseModel):
    """Varianto atsakymo schema."""

    id: int
    name: str
    max_points: float
    tasks: List[TaskResponse]


class ExamDetailResponse(BaseModel):
    """Detali kontrolinio informacija."""

    id: int
    title: str
    test_date: Optional[str]
    topic: Optional[str]
    max_points: float
    status: str
    variants: List[VariantResponse]


class CheckAnswerRequest(BaseModel):
    """Atsakymo tikrinimo užklausa."""

    task_id: int
    student_answer: str


class CheckAnswerResponse(BaseModel):
    """Atsakymo tikrinimo rezultatas."""

    is_correct: bool
    confidence: float
    needs_ai_review: bool
    correct_answer: str
    points_earned: float = 0
    partial_credit_possible: bool = False


# ============================================================
# ENDPOINTS
# ============================================================


@router.post("", response_model=ExamResponse)
async def create_exam(
    exam_data: ExamCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Sukuria naują kontrolinį darbą.

    1. Išsaugo į duomenų bazę (Test + Variants + Tasks)
    2. Sugeneruoja PDF (mokinio ir mokytojo versijas)
    3. Grąžina kontrolinio informaciją su PDF keliais
    """
    service = ExamService(db)

    variants_data = [
        {
            "name": v.name,
            "tasks": [t.model_dump() for t in v.tasks],
        }
        for v in exam_data.variants
    ]

    result = await service.create_exam(
        title=exam_data.title,
        class_id=exam_data.class_id,
        school_year_id=exam_data.school_year_id,
        test_date=exam_data.test_date,
        variants=variants_data,
        topic=exam_data.topic,
        description=exam_data.description,
        duration_minutes=exam_data.duration_minutes,
        grade=exam_data.grade,
    )

    return ExamResponse(**result)


@router.get("", response_model=List[ExamListItem])
async def list_exams(
    class_id: Optional[int] = Query(None, description="Filtruoti pagal klasę"),
    school_year_id: Optional[int] = Query(
        None, description="Filtruoti pagal mokslo metus"
    ),
    status: Optional[str] = Query(
        None, description="Filtruoti pagal statusą: draft, active, completed"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Grąžina kontrolinių sąrašą.

    Galima filtruoti pagal klasę, mokslo metus ir statusą.
    """
    service = ExamService(db)

    exams = await service.list_exams(
        class_id=class_id,
        school_year_id=school_year_id,
        status=status,
    )

    return [ExamListItem(**e) for e in exams]


@router.get("/{exam_id}", response_model=ExamDetailResponse)
async def get_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Grąžina kontrolinį su visais variantais ir užduotimis.

    Naudojama norint matyti visas užduotis ir teisingus atsakymus.
    """
    service = ExamService(db)

    exam = await service.get_exam_with_tasks(exam_id)

    if not exam:
        raise HTTPException(status_code=404, detail="Kontrolinis nerastas")

    return ExamDetailResponse(**exam)


@router.get("/by-qr/{qr_code}", response_model=ExamDetailResponse)
async def get_exam_by_qr(
    qr_code: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Grąžina kontrolinį pagal QR kodo ID.

    QR kodas yra unikalus 8 simbolių ID (pvz. "7EB58EB2"),
    kuris yra atspausdintas ant kontrolinio lapo.
    """
    service = ExamService(db)

    exam = await service.get_exam_by_qr_code(qr_code)

    if not exam:
        raise HTTPException(
            status_code=404, detail=f"Kontrolinis su QR kodu '{qr_code}' nerastas"
        )

    return ExamDetailResponse(**exam)


# ============================================================
# NAUJI ENDPOINTS - Generuoto kontrolinio išsaugojimas
# ============================================================


class GeneratedTaskInput(BaseModel):
    """Sugeneruotos užduoties schema."""

    variant_index: int
    number: str
    text: str
    correct_answer: str
    points: float = 2.0


class FromGeneratedRequest(BaseModel):
    """Užklausa iš frontend generatoriaus."""

    class_id: int
    title: str
    topic: str
    grade: int = 6
    task_count: int = 5
    difficulty: int = 2
    variants_count: int = 2
    tasks: List[GeneratedTaskInput]


@router.post("/from-generated", response_model=ExamResponse)
async def create_from_generated(
    request: FromGeneratedRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Sukuria kontrolinį iš sugeneruotų užduočių (frontend generatoriaus).

    1. Gauna užduotis iš frontend
    2. Sugrupuoja pagal variantus
    3. Išsaugo DB
    4. Sugeneruoja PDF
    """
    service = ExamService(db)

    # Grupuojame užduotis pagal variant_index
    variants_dict: dict[int, list] = {}
    for task in request.tasks:
        if task.variant_index not in variants_dict:
            variants_dict[task.variant_index] = []
        variants_dict[task.variant_index].append(
            {
                "number": task.number,
                "text": task.text,
                "answer": task.correct_answer,
                "points": int(task.points),
            }
        )

    # Konvertuojam į variantų formatą
    variant_names = ["I", "II", "III", "IV", "V"]
    variants = [
        {
            "name": variant_names[idx] if idx < len(variant_names) else f"V{idx+1}",
            "tasks": tasks,
        }
        for idx, tasks in sorted(variants_dict.items())
    ]

    from datetime import date as dt_date

    result = await service.create_exam(
        title=request.title,
        class_id=request.class_id,
        school_year_id=1,  # Default
        test_date=dt_date.today(),  # Šiandienos data
        variants=variants,
        topic=request.topic,
        description=None,
        duration_minutes=45,
        grade=request.grade if hasattr(request, "grade") and request.grade else 6,
    )

    return ExamResponse(**result)


@router.get("/pdf/{qr_code}")
async def get_exam_pdf(
    qr_code: str,
    teacher: bool = Query(False, description="Ar mokytojo versija su atsakymais"),
    db: AsyncSession = Depends(get_db),
):
    """
    Parsisiunčia kontrolinio PDF pagal QR kodą (exam_id).

    Parametrai:
    - qr_code: Unikalus kontrolinio ID (pvz. "7EB58EB2")
    - teacher: True - mokytojo versija su atsakymais, False - mokinio versija
    """
    service = ExamService(db)

    # Ieškome kontrolinio pagal QR kodą
    exam = await service.get_exam_by_qr_code(qr_code)

    if not exam:
        raise HTTPException(
            status_code=404, detail=f"Kontrolinis su QR kodu '{qr_code}' nerastas"
        )

    # PDF kelias
    pdf_path = exam.get("teacher_pdf_path" if teacher else "student_pdf_path")

    if not pdf_path:
        raise HTTPException(status_code=404, detail="PDF failas nerastas")

    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise HTTPException(
            status_code=404, detail=f"PDF failas neegzistuoja: {pdf_path}"
        )

    return FileResponse(
        path=pdf_file,
        media_type="application/pdf",
        filename=pdf_file.name,
    )


@router.post("/{exam_id}/check-answer", response_model=CheckAnswerResponse)
async def check_answer(
    exam_id: int,
    request: CheckAnswerRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Patikrina mokinio atsakymą pagal DB.

    Greitas tikrinimas:
    1. Tiesioginis palyginimas su teisingu atsakymu
    2. Skaitinis palyginimas (jei tinka)
    3. Panašumo tikrinimas

    Jei neaišku - grąžina needs_ai_review=True
    """
    service = ExamService(db)

    result = await service.check_answer(
        task_id=request.task_id,
        student_answer=request.student_answer,
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return CheckAnswerResponse(**result)


@router.get("/{exam_id}/pdf/{version}")
async def download_exam_pdf(
    exam_id: int,
    version: str = "student",
):
    """
    Parsisiunčia kontrolinio PDF.

    version: "student" arba "teacher"
    """
    Path("exports/exams")

    # Ieškome PDF pagal exam_id
    pattern = (
        f"exam_*_{exam_id}_*.pdf"
        if version == "student"
        else f"exam_*_{exam_id}-T_*.pdf"
    )

    # Paprastesnė paieška - pagal ID
    # TODO: Saugoti PDF kelią DB

    # Kol kas grąžiname klaidą
    raise HTTPException(
        status_code=501,
        detail="PDF atsisiuntimas bus implementuotas vėliau. Naudokite tiesiogiai sugeneruotą kelią.",
    )
