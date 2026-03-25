"""
Servisas mokslo metams.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.school_year import SchoolYear
from schemas.school_year import SchoolYearCreate, SchoolYearUpdate
from services.base import CRUDBase


class SchoolYearService(CRUDBase[SchoolYear, SchoolYearCreate, SchoolYearUpdate]):
    """Servisas mokslo metų CRUD operacijoms."""

    def __init__(self, db: AsyncSession):
        super().__init__(SchoolYear, db)

    async def get_active(self) -> Optional[SchoolYear]:
        """Gauti aktyvius mokslo metus."""
        query = select(SchoolYear).where(SchoolYear.is_active == True)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def set_active(self, id: int) -> Optional[SchoolYear]:
        """Nustatyti mokslo metus kaip aktyvius (deaktyvuojant kitus)."""
        # Deaktyvuoti visus
        all_years = await self.get_all()
        for year in all_years:
            if year.is_active:
                year.is_active = False

        # Aktyvuoti pasirinktus
        year = await self.get_by_id(id)
        if year:
            year.is_active = True
            await self.db.commit()
            await self.db.refresh(year)

        return year

    async def get_by_name(self, name: str) -> Optional[SchoolYear]:
        """Gauti mokslo metus pagal pavadinimą."""
        query = select(SchoolYear).where(SchoolYear.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
