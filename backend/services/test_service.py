"""
Servisas kontroliniams darbams.
"""

from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.test import Test, TestStatus
from models.variant import Variant
from models.submission import Submission
from schemas.test import TestCreate, TestUpdate
from services.base import CRUDBase


class TestService(CRUDBase[Test, TestCreate, TestUpdate]):
    """Servisas kontrolinių darbų CRUD operacijoms."""

    def __init__(self, db: AsyncSession):
        super().__init__(Test, db)

    async def get_by_class(self, class_id: int) -> List[Test]:
        """Gauti visus kontrolinius pagal klasę."""
        query = (
            select(Test)
            .where(Test.class_id == class_id)
            .order_by(Test.test_date.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_school_year(self, school_year_id: int) -> List[Test]:
        """Gauti visus kontrolinius pagal mokslo metus."""
        query = (
            select(Test)
            .where(Test.school_year_id == school_year_id)
            .order_by(Test.test_date.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_status(self, status: str) -> List[Test]:
        """Gauti kontrolinius pagal statusą."""
        query = (
            select(Test)
            .where(Test.status == status)
            .order_by(Test.test_date.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_with_variants(self, id: int) -> Optional[Test]:
        """Gauti kontrolinį su variantais."""
        query = (
            select(Test)
            .where(Test.id == id)
            .options(selectinload(Test.variants).selectinload(Variant.tasks))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_submissions_count(self, id: int) -> int:
        """Gauti pateikimų skaičių."""
        query = select(func.count(Submission.id)).where(Submission.test_id == id)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def update_max_points(self, id: int) -> Optional[Test]:
        """Atnaujinti maksimalius taškus pagal užduotis."""
        test = await self.get_with_variants(id)
        if not test:
            return None

        max_points = 0.0
        for variant in test.variants:
            variant_points = sum(task.points for task in variant.tasks)
            variant.max_points = variant_points
            if variant_points > max_points:
                max_points = variant_points

        test.max_points = max_points
        await self.db.commit()
        await self.db.refresh(test)
        return test

    async def set_status(self, id: int, status: str) -> Optional[Test]:
        """Pakeisti kontrolinio statusą."""
        test = await self.get_by_id(id)
        if not test:
            return None

        test.status = status
        await self.db.commit()
        await self.db.refresh(test)
        return test
