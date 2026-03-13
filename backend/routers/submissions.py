"""
Submissions Router - Pateiktų darbų API
=======================================
CRUD operacijos su mokinių pateiktais kontroliniais darbais.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from models.answer import Answer
from models.student import Student
from models.submission import Submission, SubmissionStatus
from models.task import Task
from models.test import Test
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db

router = APIRouter(prefix="/submissions", tags=["submissions"])


# === Schemas ===


class AnswerResult(BaseModel):
    """Vieno atsakymo rezultatas."""

    task_id: int
    task_number: str
    student_answer: Optional[str] = None
    is_correct: bool
    earned_points: float
    max_points: float
    ai_explanation: Optional[str] = None


class SubmissionCreate(BaseModel):
    """Naujo pateikimo sukūrimas."""

    student_id: int
    test_id: int
    variant_id: Optional[int] = None
    file_path: str
    file_name: str
    file_type: str = "png"


class SubmissionUpdate(BaseModel):
    """Pateikimo atnaujinimas."""

    status: Optional[str] = None
    total_points: Optional[float] = None
    max_points: Optional[float] = None
    percentage: Optional[float] = None
    grade: Optional[int] = Field(None, ge=1, le=10)
    teacher_notes: Optional[str] = None


class AnswerCreate(BaseModel):
    """Atsakymo išsaugojimas."""

    task_id: int
    recognized_text: Optional[str] = None
    recognized_latex: Optional[str] = None
    is_correct: bool
    earned_points: float
    max_points: float
    ai_explanation: Optional[str] = None


class SubmissionWithAnswers(BaseModel):
    """Pilnas pateikimas su atsakymais."""

    id: int
    student_id: int
    student_name: Optional[str] = None
    test_id: int
    test_title: Optional[str] = None
    variant_id: Optional[int] = None
    file_name: str
    status: str
    total_points: float
    max_points: float
    percentage: float
    grade: Optional[int] = None
    teacher_notes: Optional[str] = None
    submitted_at: datetime
    checked_at: Optional[datetime] = None
    answers: List[AnswerResult] = []

    class Config:
        from_attributes = True


class SubmissionSummary(BaseModel):
    """Trumpa pateikimo informacija sąrašui."""

    id: int
    student_id: int
    student_name: str
    test_id: int
    test_title: str
    status: str
    total_points: float
    max_points: float
    percentage: float
    grade: Optional[int] = None
    submitted_at: datetime

    class Config:
        from_attributes = True


class SaveCheckResultsRequest(BaseModel):
    """Tikrinimo rezultatų išsaugojimas."""

    student_id: int
    test_id: int
    variant_id: Optional[int] = None
    file_path: str
    file_name: str
    latex_content: str
    answers: List[AnswerCreate]
    total_points: float
    max_points: float
    ai_explanation: Optional[str] = None


class GradeUpdateRequest(BaseModel):
    """Balo atnaujinimas."""

    grade: int = Field(..., ge=1, le=10)
    teacher_notes: Optional[str] = None


# === Endpoints ===


@router.get("/", response_model=List[SubmissionSummary])
async def list_submissions(
    test_id: Optional[int] = None,
    student_id: Optional[int] = None,
    class_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    Gauti pateikimų sąrašą su filtrais.
    """
    query = select(Submission).options(
        selectinload(Submission.student),
        selectinload(Submission.test),
    )

    if test_id:
        query = query.where(Submission.test_id == test_id)
    if student_id:
        query = query.where(Submission.student_id == student_id)
    if status:
        query = query.where(Submission.status == status)
    if class_id:
        query = query.join(Student).where(Student.class_id == class_id)

    query = query.order_by(Submission.submitted_at.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    submissions = result.scalars().all()

    return [
        SubmissionSummary(
            id=s.id,
            student_id=s.student_id,
            student_name=(
                f"{s.student.first_name} {s.student.last_name}" if s.student else "?"
            ),
            test_id=s.test_id,
            test_title=s.test.title if s.test else "?",
            status=s.status,
            total_points=s.total_points or 0,
            max_points=s.max_points or 0,
            percentage=s.percentage or 0,
            grade=s.grade,
            submitted_at=s.submitted_at,
        )
        for s in submissions
    ]


@router.get("/{submission_id}", response_model=SubmissionWithAnswers)
async def get_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Gauti vieną pateikimą su visais atsakymais.
    """
    query = (
        select(Submission)
        .options(
            selectinload(Submission.student),
            selectinload(Submission.test),
            selectinload(Submission.answers).selectinload(Answer.task),
        )
        .where(Submission.id == submission_id)
    )

    result = await db.execute(query)
    submission = result.scalar_one_or_none()

    if not submission:
        raise HTTPException(status_code=404, detail="Pateikimas nerastas")

    answers = [
        AnswerResult(
            task_id=a.task_id,
            task_number=a.task.number if a.task else "?",
            student_answer=a.recognized_text,
            is_correct=a.is_correct or False,
            earned_points=a.earned_points or 0,
            max_points=a.max_points or 0,
            ai_explanation=a.ai_explanation,
        )
        for a in submission.answers
    ]

    return SubmissionWithAnswers(
        id=submission.id,
        student_id=submission.student_id,
        student_name=(
            f"{submission.student.first_name} {submission.student.last_name}"
            if submission.student
            else None
        ),
        test_id=submission.test_id,
        test_title=submission.test.title if submission.test else None,
        variant_id=submission.variant_id,
        file_name=submission.file_name,
        status=submission.status,
        total_points=submission.total_points or 0,
        max_points=submission.max_points or 0,
        percentage=submission.percentage or 0,
        grade=submission.grade,
        teacher_notes=submission.teacher_notes,
        submitted_at=submission.submitted_at,
        checked_at=submission.checked_at,
        answers=answers,
    )


@router.post("/save-results", response_model=SubmissionWithAnswers)
async def save_check_results(
    request: SaveCheckResultsRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Išsaugoti tikrinimo rezultatus.
    Sukuria naują Submission ir Answer įrašus.
    """
    logger.info(
        f"Saugomi rezultatai: student={request.student_id}, test={request.test_id}"
    )

    # Apskaičiuojame procentus
    percentage = (
        (request.total_points / request.max_points * 100)
        if request.max_points > 0
        else 0
    )

    # Apskaičiuojame balą (1-10)
    grade = calculate_grade(percentage)

    # Sukuriame Submission
    submission = Submission(
        student_id=request.student_id,
        test_id=request.test_id,
        variant_id=request.variant_id,
        file_path=request.file_path,
        file_name=request.file_name,
        file_type=(
            request.file_name.split(".")[-1] if "." in request.file_name else "png"
        ),
        status=SubmissionStatus.COMPLETED,
        total_points=request.total_points,
        max_points=request.max_points,
        percentage=percentage,
        grade=grade,
        checked_at=datetime.utcnow(),
    )

    db.add(submission)
    await db.flush()  # Gauname submission.id

    # Sukuriame Answers
    for ans in request.answers:
        answer = Answer(
            submission_id=submission.id,
            task_id=ans.task_id,
            recognized_text=ans.recognized_text,
            recognized_latex=ans.recognized_latex,
            is_correct=ans.is_correct,
            earned_points=ans.earned_points,
            max_points=ans.max_points,
            ai_explanation=ans.ai_explanation,
        )
        db.add(answer)

    await db.commit()
    await db.refresh(submission)

    logger.info(f"Išsaugota: submission_id={submission.id}, grade={grade}")

    # Grąžiname pilną objektą
    return await get_submission(submission.id, db)


@router.patch("/{submission_id}/grade", response_model=SubmissionWithAnswers)
async def update_grade(
    submission_id: int,
    request: GradeUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Atnaujinti balą rankiniu būdu.
    """
    query = select(Submission).where(Submission.id == submission_id)
    result = await db.execute(query)
    submission = result.scalar_one_or_none()

    if not submission:
        raise HTTPException(status_code=404, detail="Pateikimas nerastas")

    submission.grade = request.grade
    if request.teacher_notes:
        submission.teacher_notes = request.teacher_notes
    submission.status = SubmissionStatus.REVIEWED

    await db.commit()
    await db.refresh(submission)

    logger.info(f"Atnaujintas balas: submission={submission_id}, grade={request.grade}")

    return await get_submission(submission_id, db)


@router.delete("/{submission_id}")
async def delete_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Ištrinti pateikimą.
    """
    query = select(Submission).where(Submission.id == submission_id)
    result = await db.execute(query)
    submission = result.scalar_one_or_none()

    if not submission:
        raise HTTPException(status_code=404, detail="Pateikimas nerastas")

    await db.delete(submission)
    await db.commit()

    return {"message": "Pateikimas ištrintas"}


def calculate_grade(percentage: float) -> int:
    """
    Apskaičiuoti balą pagal procentus (Lietuvos sistema).
    """
    if percentage >= 95:
        return 10
    elif percentage >= 85:
        return 9
    elif percentage >= 75:
        return 8
    elif percentage >= 65:
        return 7
    elif percentage >= 55:
        return 6
    elif percentage >= 45:
        return 5
    elif percentage >= 35:
        return 4
    elif percentage >= 25:
        return 3
    elif percentage >= 15:
        return 2
    else:
        return 1
