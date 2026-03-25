"""
Servisas variantams.
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.variant import Variant
from models.task import Task
from schemas.variant import VariantCreate, VariantUpdate
from services.base import CRUDBase


class VariantService(CRUDBase[Variant, VariantCreate, VariantUpdate]):
    """Servisas variantų CRUD operacijoms."""

    def __init__(self, db: AsyncSession):
        super().__init__(Variant, db)

    async def get_by_test(self, test_id: int) -> List[Variant]:
        """Gauti visus variantus pagal kontrolinį."""
        query = (
            select(Variant)
            .where(Variant.test_id == test_id)
            .order_by(Variant.name)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_with_tasks(self, id: int) -> Optional[Variant]:
        """Gauti variantą su užduotimis."""
        query = (
            select(Variant)
            .where(Variant.id == id)
            .options(selectinload(Variant.tasks))
        )
        result = await self.db.execute(query)
        variant = result.scalar_one_or_none()

        if variant and variant.tasks:
            # Rikiuoti užduotis pagal order_index
            variant.tasks = sorted(variant.tasks, key=lambda t: t.order_index)

        return variant

    async def update_max_points(self, id: int) -> Optional[Variant]:
        """Atnaujinti maksimalius taškus pagal užduotis."""
        variant = await self.get_with_tasks(id)
        if not variant:
            return None

        variant.max_points = sum(task.points for task in variant.tasks)
        await self.db.commit()
        await self.db.refresh(variant)
        return variant

    async def create_with_default_tasks(
        self,
        data: VariantCreate,
        task_count: int = 8
    ) -> Variant:
        """Sukurti variantą su tuščiomis užduotimis."""
        # Sukurti variantą
        variant = Variant(**data.model_dump())
        self.db.add(variant)
        await self.db.commit()
        await self.db.refresh(variant)

        # Sukurti tuščias užduotis
        for i in range(1, task_count + 1):
            task = Task(
                number=str(i),
                correct_answer="",
                points=1.0,
                order_index=i,
                variant_id=variant.id
            )
            self.db.add(task)

        await self.db.commit()
        return variant
