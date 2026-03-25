"""
Exam Sheets Router - API kontrolinių lapų generavimui
=====================================================
Endpoint'ai PDF kontrolinių generavimui su OCR optimizacija.
"""

import io
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from loguru import logger
from pydantic import BaseModel, Field
from services.exam_sheet_generator import (
    ExamSheet,
    ExamSheetGenerator,
    ExamTask,
    ExamVariant,
    create_sample_exam,
)

router = APIRouter(prefix="/exam-sheets", tags=["Exam Sheets"])


# ============================================================
# SCHEMAS
# ============================================================


class TaskCreate(BaseModel):
    """Uždavinio sukūrimo schema."""

    number: str = Field(..., description="Uždavinio numeris (pvz., '1', '1a', '2b')")
    text: str = Field(..., description="Uždavinio tekstas")
    points: int = Field(default=1, ge=1, le=10, description="Taškai už uždavinį")
    answer: Optional[str] = Field(None, description="Teisingas atsakymas")
    workspace_height_mm: int = Field(
        default=50, ge=20, le=150, description="Sprendimo zonos aukštis mm"
    )


class VariantCreate(BaseModel):
    """Varianto sukūrimo schema."""

    name: str = Field(..., description="Varianto pavadinimas (pvz., 'I', 'II', 'A')")
    tasks: List[TaskCreate] = Field(..., min_length=1, description="Uždavinių sąrašas")


class ExamSheetCreate(BaseModel):
    """Kontrolinio lapo sukūrimo schema."""

    title: str = Field(..., description="Kontrolinio pavadinimas")
    subject: str = Field(default="Matematika", description="Dalykas")
    topic: Optional[str] = Field(None, description="Tema")
    grade: int = Field(..., ge=1, le=12, description="Klasė")
    duration_minutes: int = Field(
        default=45, ge=10, le=180, description="Trukmė minutėmis"
    )
    total_points: int = Field(default=20, ge=1, le=100, description="Maksimalūs taškai")
    school_year: str = Field(default="2025-2026", description="Mokslo metai")
    variants: List[VariantCreate] = Field(..., min_length=1, description="Variantai")
    show_grid: bool = Field(
        default=True, description="Rodyti tinklelį sprendimo zonoje"
    )
    teacher_version: bool = Field(
        default=False, description="Mokytojo versija su atsakymais"
    )


class ExamSheetResponse(BaseModel):
    """Kontrolinio lapo atsakymo schema."""

    exam_id: str
    title: str
    grade: int
    variants_count: int
    tasks_count: int
    total_points: int
    pdf_url: str


class QuickExamRequest(BaseModel):
    """Greito kontrolinio generavimo užklausa."""

    grade: int = Field(..., ge=5, le=8, description="Klasė")
    topic_id: Optional[str] = Field(None, description="Temos ID iš curriculum")
    difficulty: str = Field(
        default="medium", description="Sunkumas: easy, medium, hard"
    )
    tasks_count: int = Field(default=5, ge=1, le=10, description="Uždavinių skaičius")
    variants_count: int = Field(default=2, ge=1, le=4, description="Variantų skaičius")
    duration_minutes: int = Field(default=45, description="Trukmė")


# ============================================================
# HELPER FUNKCIJOS
# ============================================================


def _convert_to_exam_sheet(data: ExamSheetCreate) -> ExamSheet:
    """Konvertuoja Pydantic modelį į ExamSheet dataclass."""
    variants = []
    for var_data in data.variants:
        tasks = []
        for task_data in var_data.tasks:
            tasks.append(
                ExamTask(
                    number=task_data.number,
                    text=task_data.text,
                    points=task_data.points,
                    answer=task_data.answer,
                    workspace_height_mm=task_data.workspace_height_mm,
                )
            )
        variants.append(ExamVariant(name=var_data.name, tasks=tasks))

    return ExamSheet(
        title=data.title,
        subject=data.subject,
        topic=data.topic,
        grade=data.grade,
        duration_minutes=data.duration_minutes,
        total_points=data.total_points,
        school_year=data.school_year,
        variants=variants,
        show_grid=data.show_grid,
        teacher_version=data.teacher_version,
    )


# ============================================================
# ENDPOINTS
# ============================================================


@router.post("/generate", response_class=StreamingResponse)
async def generate_exam_pdf(data: ExamSheetCreate):
    """
    Generuoja kontrolinio PDF.

    Grąžina PDF failą su:
    - OCR alignment markeriais
    - QR kodu su exam ID
    - Uždavinių kortelėmis su grid
    - Aiškiomis atsakymų dėžutėmis
    """
    try:
        exam = _convert_to_exam_sheet(data)
        generator = ExamSheetGenerator()

        if not generator.backend:
            raise HTTPException(
                status_code=500,
                detail="PDF generatorius nesukonfigūruotas (ReportLab arba WeasyPrint reikalingas)",
            )

        pdf_bytes = generator.generate_pdf_bytes(exam)

        filename = f"kontrolinis_{exam.exam_id}.pdf"

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "X-Exam-ID": exam.exam_id,
            },
        )

    except Exception as e:
        logger.error(f"Klaida generuojant PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/teacher", response_class=StreamingResponse)
async def generate_teacher_version(data: ExamSheetCreate):
    """
    Generuoja mokytojo versiją su atsakymais.
    """
    data.teacher_version = True
    return await generate_exam_pdf(data)


@router.get("/sample", response_class=StreamingResponse)
async def get_sample_exam(
    teacher_version: bool = Query(
        False, description="Ar mokytojo versija su atsakymais"
    )
):
    """
    Grąžina pavyzdinį kontrolinį PDF.

    Naudinga testavimui ir demonstracijai.
    """
    try:
        exam = create_sample_exam()
        exam.teacher_version = teacher_version

        generator = ExamSheetGenerator()

        if not generator.backend:
            raise HTTPException(
                status_code=500, detail="PDF generatorius nesukonfigūruotas"
            )

        pdf_bytes = generator.generate_pdf_bytes(exam)

        version_suffix = "_mokytojas" if teacher_version else ""
        filename = f"pavyzdinis_kontrolinis{version_suffix}.pdf"

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "X-Exam-ID": exam.exam_id,
            },
        )

    except Exception as e:
        logger.error(f"Klaida generuojant pavyzdinį PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sample/html")
async def get_sample_exam_html(
    teacher_version: bool = Query(False, description="Ar mokytojo versija")
):
    """
    Grąžina pavyzdinį kontrolinį HTML formatu.

    Naudinga peržiūrai naršyklėje.
    """
    from fastapi.responses import HTMLResponse
    from services.exam_sheet_generator import EXAM_CSS

    exam = create_sample_exam()
    exam.teacher_version = teacher_version

    generator = ExamSheetGenerator()
    html = generator.generate_html(exam)

    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{exam.title}</title>
        <style>{EXAM_CSS}</style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """

    return HTMLResponse(content=full_html)


@router.post("/quick-generate", response_class=StreamingResponse)
async def quick_generate_exam(request: QuickExamRequest):
    """
    Greitai sugeneruoja kontrolinį pagal parametrus.

    Naudoja problem_bank arba test_generator uždavinių generavimui.
    """
    try:
        from services.test_generator import TestGenerator

        # Generuoti uždavinius
        test_gen = TestGenerator()

        # Sukurti variantus
        variants = []
        for v_idx in range(request.variants_count):
            variant_name = ["I", "II", "III", "IV"][v_idx]
            tasks = []

            # Generuoti uždavinius šiam variantui
            generated = await test_gen.generate_test(
                grade=request.grade,
                topic=request.topic_id,
                task_count=request.tasks_count,
                difficulty=request.difficulty,
            )

            for i, gen_task in enumerate(
                generated.variants[0].tasks if generated.variants else [], 1
            ):
                tasks.append(
                    ExamTask(
                        number=str(i),
                        text=gen_task.text,
                        points=gen_task.points,
                        answer=gen_task.answer,
                        workspace_height_mm=50 if gen_task.difficulty == "easy" else 70,
                    )
                )

            variants.append(ExamVariant(name=variant_name, tasks=tasks))

        # Sukurti ExamSheet
        topic_name = request.topic_id or "Mišrus"
        exam = ExamSheet(
            title=f"Kontrolinis darbas - {topic_name}",
            topic=topic_name,
            grade=request.grade,
            duration_minutes=request.duration_minutes,
            total_points=sum(t.points for t in variants[0].tasks) if variants else 0,
            variants=variants,
        )

        generator = ExamSheetGenerator()
        pdf_bytes = generator.generate_pdf_bytes(exam)

        filename = f"kontrolinis_{exam.exam_id}.pdf"

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "X-Exam-ID": exam.exam_id,
            },
        )

    except Exception as e:
        logger.error(f"Klaida greitai generuojant: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_generator_info():
    """
    Grąžina informaciją apie generatorių.
    """
    from services.exam_sheet_generator import (
        QR_AVAILABLE,
        REPORTLAB_AVAILABLE,
        WEASYPRINT_AVAILABLE,
    )

    generator = ExamSheetGenerator()

    return {
        "backend": generator.backend,
        "weasyprint_available": WEASYPRINT_AVAILABLE,
        "reportlab_available": REPORTLAB_AVAILABLE,
        "qr_available": QR_AVAILABLE,
        "features": {
            "alignment_markers": True,
            "qr_code": QR_AVAILABLE,
            "grid_workspace": True,
            "answer_boxes": True,
            "teacher_version": True,
            "multi_variant": True,
        },
        "exports_dir": str(generator.EXPORTS_DIR),
    }
