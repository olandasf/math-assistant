"""
Servisas klasėms.
"""

from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.school_class import SchoolClass
from models.student import Student
from schemas.school_class import ClassCreate, ClassUpdate
from services.base import CRUDBase


class ClassService(CRUDBase[SchoolClass, ClassCreate, ClassUpdate]):
    """Servisas klasių CRUD operacijoms."""

    def __init__(self, db: AsyncSession):
        super().__init__(SchoolClass, db)

    async def get_by_school_year(self, school_year_id: int) -> List[SchoolClass]:
        """Gauti visas klases pagal mokslo metus."""
        query = (
            select(SchoolClass)
            .where(SchoolClass.school_year_id == school_year_id)
            .order_by(SchoolClass.grade, SchoolClass.name)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_with_students(self, id: int) -> Optional[SchoolClass]:
        """Gauti klasę su mokiniais."""
        query = (
            select(SchoolClass)
            .where(SchoolClass.id == id)
            .options(selectinload(SchoolClass.students))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_students_count(self, id: int) -> int:
        """Gauti mokinių skaičių klasėje."""
        query = select(func.count(Student.id)).where(Student.class_id == id)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_by_grade(self, grade: int, school_year_id: int) -> List[SchoolClass]:
        """Gauti visas klases pagal klasės numerį."""
        query = (
            select(SchoolClass)
            .where(
                SchoolClass.grade == grade,
                SchoolClass.school_year_id == school_year_id
            )
            .order_by(SchoolClass.name)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
