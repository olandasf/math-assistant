"""
API Router - Mokiniai.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentRead,
    StudentBulkCreate
)
from schemas.common import MessageResponse
from services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["Mokiniai"])


@router.get("/", response_model=List[StudentRead])
async def get_all_students(
    class_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[StudentRead]:
    """Gauti visus mokinius (galima filtruoti pagal klasę)."""
    service = StudentService(db)

    if class_id:
        return await service.get_by_class(class_id)
    else:
        return await service.get_all(skip=skip, limit=limit)


@router.get("/search", response_model=List[StudentRead])
async def search_students(
    q: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
) -> List[StudentRead]:
    """Ieškoti mokinių pagal vardą, pavardę arba kodą."""
    if len(q) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Paieškos tekstas turi būti bent 2 simboliai"
        )

    service = StudentService(db)
    return await service.search(q, limit=limit)


@router.get("/{student_id}", response_model=StudentRead)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_db)
) -> StudentRead:
    """Gauti mokinį pagal ID."""
    service = StudentService(db)
    student = await service.get_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mokinys nerastas"
        )
    return student


@router.get("/code/{unique_code}", response_model=StudentRead)
async def get_student_by_code(
    unique_code: str,
    db: AsyncSession = Depends(get_db)
) -> StudentRead:
    """Gauti mokinį pagal unikalų kodą."""
    service = StudentService(db)
    student = await service.get_by_unique_code(unique_code)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mokinys nerastas"
        )
    return student


@router.post("/", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
async def create_student(
    data: StudentCreate,
    db: AsyncSession = Depends(get_db)
) -> StudentRead:
    """Sukurti naują mokinį."""
    service = StudentService(db)
    return await service.create(data)


@router.post("/bulk", response_model=List[StudentRead], status_code=status.HTTP_201_CREATED)
async def bulk_create_students(
    data: StudentBulkCreate,
    db: AsyncSession = Depends(get_db)
) -> List[StudentRead]:
    """Sukurti daug mokinių vienu metu."""
    service = StudentService(db)
    return await service.bulk_create(data)


@router.put("/{student_id}", response_model=StudentRead)
async def update_student(
    student_id: int,
    data: StudentUpdate,
    db: AsyncSession = Depends(get_db)
) -> StudentRead:
    """Atnaujinti mokinį."""
    service = StudentService(db)
    student = await service.update(student_id, data)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mokinys nerastas"
        )
    return student


@router.delete("/{student_id}", response_model=MessageResponse)
async def delete_student(
    student_id: int,
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Ištrinti mokinį."""
    service = StudentService(db)
    success = await service.delete(student_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mokinys nerastas"
        )
    return MessageResponse(message="Mokinys ištrintas")
