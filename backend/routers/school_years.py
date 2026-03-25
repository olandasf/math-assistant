"""
API Router - Mokslo metai.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.school_year import (
    SchoolYearCreate,
    SchoolYearUpdate,
    SchoolYearRead
)
from schemas.common import MessageResponse
from services.school_year_service import SchoolYearService

router = APIRouter(prefix="/school-years", tags=["Mokslo metai"])


@router.get("/", response_model=List[SchoolYearRead])
async def get_all_school_years(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[SchoolYearRead]:
    """Gauti visus mokslo metus."""
    service = SchoolYearService(db)
    return await service.get_all(skip=skip, limit=limit)


@router.get("/active", response_model=SchoolYearRead)
async def get_active_school_year(
    db: AsyncSession = Depends(get_db)
) -> SchoolYearRead:
    """Gauti aktyvius mokslo metus."""
    service = SchoolYearService(db)
    year = await service.get_active()
    if not year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nėra aktyvių mokslo metų"
        )
    return year


@router.get("/{year_id}", response_model=SchoolYearRead)
async def get_school_year(
    year_id: int,
    db: AsyncSession = Depends(get_db)
) -> SchoolYearRead:
    """Gauti mokslo metus pagal ID."""
    service = SchoolYearService(db)
    year = await service.get_by_id(year_id)
    if not year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mokslo metai nerasti"
        )
    return year


@router.post("/", response_model=SchoolYearRead, status_code=status.HTTP_201_CREATED)
async def create_school_year(
    data: SchoolYearCreate,
    db: AsyncSession = Depends(get_db)
) -> SchoolYearRead:
    """Sukurti naujus mokslo metus."""
    service = SchoolYearService(db)

    # Patikrinti ar neegzistuoja
    existing = await service.get_by_name(data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mokslo metai '{data.name}' jau egzistuoja"
        )

    return await service.create(data)


@router.put("/{year_id}", response_model=SchoolYearRead)
async def update_school_year(
    year_id: int,
    data: SchoolYearUpdate,
    db: AsyncSession = Depends(get_db)
) -> SchoolYearRead:
    """Atnaujinti mokslo metus."""
    service = SchoolYearService(db)
    year = await service.update(year_id, data)
    if not year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mokslo metai nerasti"
        )
    return year


@router.post("/{year_id}/activate", response_model=SchoolYearRead)
async def activate_school_year(
    year_id: int,
    db: AsyncSession = Depends(get_db)
) -> SchoolYearRead:
    """Aktyvuoti mokslo metus."""
    service = SchoolYearService(db)
    year = await service.set_active(year_id)
    if not year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mokslo metai nerasti"
        )
    return year


@router.delete("/{year_id}", response_model=MessageResponse)
async def delete_school_year(
    year_id: int,
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Ištrinti mokslo metus."""
    service = SchoolYearService(db)
    success = await service.delete(year_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mokslo metai nerasti"
        )
    return MessageResponse(message="Mokslo metai ištrinti")
