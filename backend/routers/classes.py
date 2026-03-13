"""
API Router - Klasės.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.school_class import (
    ClassCreate,
    ClassUpdate,
    ClassRead,
    ClassWithStudents
)
from schemas.common import MessageResponse
from services.class_service import ClassService

router = APIRouter(prefix="/classes", tags=["Klasės"])


@router.get("/", response_model=List[ClassRead])
async def get_all_classes(
    school_year_id: int = None,
    grade: int = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[ClassRead]:
    """Gauti visas klases (galima filtruoti pagal mokslo metus arba klasę)."""
    service = ClassService(db)

    if school_year_id and grade:
        return await service.get_by_grade(grade, school_year_id)
    elif school_year_id:
        return await service.get_by_school_year(school_year_id)
    else:
        return await service.get_all(skip=skip, limit=limit)


@router.get("/{class_id}", response_model=ClassRead)
async def get_class(
    class_id: int,
    db: AsyncSession = Depends(get_db)
) -> ClassRead:
    """Gauti klasę pagal ID."""
    service = ClassService(db)
    school_class = await service.get_by_id(class_id)
    if not school_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Klasė nerasta"
        )
    return school_class


@router.get("/{class_id}/with-students", response_model=ClassWithStudents)
async def get_class_with_students(
    class_id: int,
    db: AsyncSession = Depends(get_db)
) -> ClassWithStudents:
    """Gauti klasę su mokinių sąrašu."""
    service = ClassService(db)
    school_class = await service.get_with_students(class_id)
    if not school_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Klasė nerasta"
        )

    # Pridėti students_count
    result = ClassWithStudents.model_validate(school_class)
    result.students_count = len(school_class.students)
    return result


@router.post("/", response_model=ClassRead, status_code=status.HTTP_201_CREATED)
async def create_class(
    data: ClassCreate,
    db: AsyncSession = Depends(get_db)
) -> ClassRead:
    """Sukurti naują klasę."""
    service = ClassService(db)
    return await service.create(data)


@router.put("/{class_id}", response_model=ClassRead)
async def update_class(
    class_id: int,
    data: ClassUpdate,
    db: AsyncSession = Depends(get_db)
) -> ClassRead:
    """Atnaujinti klasę."""
    service = ClassService(db)
    school_class = await service.update(class_id, data)
    if not school_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Klasė nerasta"
        )
    return school_class


@router.delete("/{class_id}", response_model=MessageResponse)
async def delete_class(
    class_id: int,
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Ištrinti klasę."""
    service = ClassService(db)
    success = await service.delete(class_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Klasė nerasta"
        )
    return MessageResponse(message="Klasė ištrinta")
