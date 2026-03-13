"""
Exports Router - PDF ataskaitų eksportavimas
============================================
API endpoints PDF generavimui ir atsisiuntimui.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from loguru import logger
from models import Answer, SchoolClass, Student, Submission, Task, Test, Variant
from pydantic import BaseModel
from services.pdf_generator import (
    ClassResult,
    PDFGenerator,
    StudentResult,
    get_pdf_generator,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db

router = APIRouter(prefix="/exports", tags=["exports"])


# Schemas
class StudentReportRequest(BaseModel):
    """Užklausa mokinio ataskaitai."""

    submission_id: int
    include_explanations: bool = True
    teacher_comments: Optional[str] = None


class ClassReportRequest(BaseModel):
    """Užklausa klasės ataskaitai."""

    test_id: int
    class_id: int
    include_individual_results: bool = True


class ExportStatusResponse(BaseModel):
    """Eksporto statusas."""

    available: bool
    backend: Optional[str] = None
    exports_directory: str
    recent_exports: List[str] = []


# Endpoints
@router.get("/status", response_model=ExportStatusResponse)
async def get_export_status():
    """
    Gauti PDF eksporto sistemos statusą.

    Patikrina ar PDF generavimas galimas ir grąžina informaciją.
    """
    generator = get_pdf_generator()

    # Paskutiniai eksportai
    exports_dir = generator.EXPORTS_DIR
    recent_exports = []

    if exports_dir.exists():
        pdf_files = sorted(
            exports_dir.glob("*.pdf"), key=lambda x: x.stat().st_mtime, reverse=True
        )[:10]
        recent_exports = [f.name for f in pdf_files]

    return ExportStatusResponse(
        available=generator.is_available,
        backend=generator.backend,
        exports_directory=str(exports_dir),
        recent_exports=recent_exports,
    )


@router.get("/files")
async def list_exports(
    limit: int = Query(default=20, le=100), offset: int = Query(default=0)
):
    """
    Gauti eksportuotų failų sąrašą.
    """
    generator = get_pdf_generator()
    exports_dir = generator.EXPORTS_DIR

    if not exports_dir.exists():
        return {"files": [], "total": 0}

    all_files = sorted(
        exports_dir.glob("*.pdf"), key=lambda x: x.stat().st_mtime, reverse=True
    )

    total = len(all_files)
    files = all_files[offset : offset + limit]

    file_list = []
    for f in files:
        stat = f.stat()
        file_list.append(
            {
                "name": f.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "download_url": f"/api/v1/exports/download/{f.name}",
            }
        )

    return {"files": file_list, "total": total, "limit": limit, "offset": offset}


@router.get("/download/{filename}")
async def download_export(filename: str):
    """
    Atsisiųsti eksportuotą PDF failą.
    """
    generator = get_pdf_generator()
    filepath = generator.EXPORTS_DIR / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Failas nerastas")

    if not filepath.suffix.lower() == ".pdf":
        raise HTTPException(status_code=400, detail="Tik PDF failai leidžiami")

    return FileResponse(
        path=str(filepath), filename=filename, media_type="application/pdf"
    )


@router.delete("/files/{filename}")
async def delete_export(filename: str):
    """
    Ištrinti eksportuotą failą.
    """
    generator = get_pdf_generator()
    filepath = generator.EXPORTS_DIR / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Failas nerastas")

    try:
        filepath.unlink()
        return {"message": "Failas ištrintas", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nepavyko ištrinti: {str(e)}")


@router.post("/student-report")
async def generate_student_report(
    request: StudentReportRequest, db: AsyncSession = Depends(get_db)
):
    """
    Sugeneruoti mokinio PDF ataskaitą.

    Generuoja PDF su:
    - Mokinio informacija
    - Pažymiu ir taškais
    - Užduočių rezultatais
    - Klaidų paaiškinimais
    - Mokytojo komentarais
    """
    generator = get_pdf_generator()

    if not generator.is_available:
        raise HTTPException(
            status_code=503,
            detail="PDF generavimas negalimas. Įdiekite WeasyPrint: pip install weasyprint",
        )

    # Gauname submission su susijusiais duomenimis
    submission_query = select(Submission).where(Submission.id == request.submission_id)
    result = await db.execute(submission_query)
    submission = result.scalar_one_or_none()

    if not submission:
        raise HTTPException(status_code=404, detail="Pateikimas nerastas")

    # Gauname studentą
    student_query = select(Student).where(Student.id == submission.student_id)
    result = await db.execute(student_query)
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(status_code=404, detail="Mokinys nerastas")

    # Gauname klasę
    class_query = select(SchoolClass).where(SchoolClass.id == student.class_id)
    result = await db.execute(class_query)
    school_class = result.scalar_one_or_none()

    # Gauname variantą ir testą
    variant_query = select(Variant).where(Variant.id == submission.variant_id)
    result = await db.execute(variant_query)
    variant = result.scalar_one_or_none()

    test = None
    if variant:
        test_query = select(Test).where(Test.id == variant.test_id)
        result = await db.execute(test_query)
        test = result.scalar_one_or_none()

    # Gauname atsakymus
    answers_query = select(Answer).where(Answer.submission_id == submission.id)
    result = await db.execute(answers_query)
    answers = result.scalars().all()

    # Ruošiame užduočių rezultatus
    tasks_data = []
    total_points = 0
    max_points = 0

    for answer in answers:
        # Gauname užduotį
        task_query = select(Task).where(Task.id == answer.task_id)
        result = await db.execute(task_query)
        task = result.scalar_one_or_none()

        if task:
            task_points = answer.points if answer.points else 0
            total_points += task_points
            max_points += task.points if task.points else 0

            tasks_data.append(
                {
                    "number": str(task.number),
                    "question": task.question or "",
                    "student_answer": answer.student_answer or "",
                    "correct_answer": task.correct_answer or "",
                    "correct": (
                        answer.is_correct if answer.is_correct is not None else False
                    ),
                    "points": task_points,
                    "max_points": task.points or 0,
                }
            )

    # Skaičiuojame pažymį
    grade = 1
    if max_points > 0:
        percentage = (total_points / max_points) * 100
        if percentage >= 95:
            grade = 10
        elif percentage >= 85:
            grade = 9
        elif percentage >= 75:
            grade = 8
        elif percentage >= 65:
            grade = 7
        elif percentage >= 55:
            grade = 6
        elif percentage >= 45:
            grade = 5
        elif percentage >= 35:
            grade = 4
        elif percentage >= 25:
            grade = 3
        elif percentage >= 15:
            grade = 2
        else:
            grade = 1

    # Kuriame StudentResult objektą
    student_result = StudentResult(
        student_name=f"{student.first_name} {student.last_name}",
        student_code=student.unique_code or f"M{student.id:07d}",
        class_name=school_class.name if school_class else "Nežinoma",
        test_title=test.title if test else "Kontrolinis darbas",
        test_date=(
            test.date.strftime("%Y-%m-%d")
            if test and test.date
            else datetime.now().strftime("%Y-%m-%d")
        ),
        grade=grade,
        max_grade=10,
        points=total_points,
        max_points=max_points,
        tasks=tasks_data,
        errors=[],  # TODO: pridėti klaidų paaiškinimus
        teacher_comments=request.teacher_comments,
    )

    # Generuojame PDF
    pdf_path = generator.generate_student_report(student_result)

    if not pdf_path:
        raise HTTPException(status_code=500, detail="Nepavyko sugeneruoti PDF")

    filename = Path(pdf_path).name

    return {
        "success": True,
        "message": "PDF ataskaita sukurta",
        "filename": filename,
        "download_url": f"/api/v1/exports/download/{filename}",
        "student": student_result.student_name,
        "grade": grade,
    }


@router.get("/student-preview/{submission_id}", response_class=HTMLResponse)
async def preview_student_report(
    submission_id: int, db: AsyncSession = Depends(get_db)
):
    """
    HTML peržiūra mokinio ataskaitai (be PDF generavimo).
    """
    generator = get_pdf_generator()

    # Gauname submission
    submission_query = select(Submission).where(Submission.id == submission_id)
    result = await db.execute(submission_query)
    submission = result.scalar_one_or_none()

    if not submission:
        raise HTTPException(status_code=404, detail="Pateikimas nerastas")

    # Gauname studentą
    student_query = select(Student).where(Student.id == submission.student_id)
    result = await db.execute(student_query)
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(status_code=404, detail="Mokinys nerastas")

    # Gauname klasę
    class_query = select(SchoolClass).where(SchoolClass.id == student.class_id)
    result = await db.execute(class_query)
    school_class = result.scalar_one_or_none()

    # Demo duomenys peržiūrai
    demo_result = StudentResult(
        student_name=f"{student.first_name} {student.last_name}",
        student_code=student.unique_code or f"M{student.id:07d}",
        class_name=school_class.name if school_class else "Nežinoma",
        test_title="Kontrolinis darbas",
        test_date=datetime.now().strftime("%Y-%m-%d"),
        grade=8,
        points=16,
        max_points=20,
        tasks=[
            {
                "number": "1",
                "question": "2/5 + 1/3",
                "student_answer": "11/15",
                "correct_answer": "11/15",
                "correct": True,
                "points": 2,
                "max_points": 2,
            },
            {
                "number": "2",
                "question": "Suprastinkite 6/9",
                "student_answer": "6/9",
                "correct_answer": "2/3",
                "correct": False,
                "points": 1,
                "max_points": 2,
            },
        ],
    )

    html = generator.get_html_preview(demo_result)
    return HTMLResponse(content=html)


@router.post("/class-report")
async def generate_class_report(
    request: ClassReportRequest, db: AsyncSession = Depends(get_db)
):
    """
    Sugeneruoti klasės PDF ataskaitą.

    Generuoja PDF su:
    - Klasės statistika (vidurkis, mediana)
    - Pažymių pasiskirstymu
    - Mokinių rezultatų sąrašu
    """
    generator = get_pdf_generator()

    if not generator.is_available:
        raise HTTPException(
            status_code=503, detail="PDF generavimas negalimas. Įdiekite WeasyPrint."
        )

    # Gauname klasę
    class_query = select(SchoolClass).where(SchoolClass.id == request.class_id)
    result = await db.execute(class_query)
    school_class = result.scalar_one_or_none()

    if not school_class:
        raise HTTPException(status_code=404, detail="Klasė nerasta")

    # Gauname testą
    test_query = select(Test).where(Test.id == request.test_id)
    result = await db.execute(test_query)
    test = result.scalar_one_or_none()

    if not test:
        raise HTTPException(status_code=404, detail="Testas nerastas")

    # Gauname visus mokinius iš klasės
    students_query = select(Student).where(Student.class_id == request.class_id)
    result = await db.execute(students_query)
    students = result.scalars().all()

    # Demo rezultatai (realioje implementacijoje - iš DB)
    student_results = []
    grades = []

    for student in students:
        # Demo pažymys
        import random

        grade = random.randint(4, 10)
        grades.append(grade)

        student_results.append(
            StudentResult(
                student_name=f"{student.first_name} {student.last_name}",
                student_code=student.unique_code or f"M{student.id:07d}",
                class_name=school_class.name,
                test_title=test.title,
                test_date=test.date.strftime("%Y-%m-%d") if test.date else "",
                grade=grade,
                points=grade * 2,
                max_points=20,
            )
        )

    if not grades:
        grades = [0]

    # Statistika
    sorted_grades = sorted(grades)
    grade_distribution = {}
    for g in range(1, 11):
        grade_distribution[str(g)] = grades.count(g)

    class_result = ClassResult(
        class_name=school_class.name,
        test_title=test.title,
        test_date=(
            test.date.strftime("%Y-%m-%d")
            if test.date
            else datetime.now().strftime("%Y-%m-%d")
        ),
        student_results=student_results,
        average_grade=sum(grades) / len(grades),
        median_grade=sorted_grades[len(sorted_grades) // 2],
        highest_grade=max(grades),
        lowest_grade=min(grades),
        grade_distribution=grade_distribution,
    )

    pdf_path = generator.generate_class_report(class_result)

    if not pdf_path:
        raise HTTPException(status_code=500, detail="Nepavyko sugeneruoti PDF")

    filename = Path(pdf_path).name

    return {
        "success": True,
        "message": "Klasės PDF ataskaita sukurta",
        "filename": filename,
        "download_url": f"/api/v1/exports/download/{filename}",
        "class_name": school_class.name,
        "students_count": len(student_results),
        "average_grade": class_result.average_grade,
    }
