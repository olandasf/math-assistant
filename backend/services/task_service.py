"""
Servisas užduotims.
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.task import Task
from schemas.task import TaskCreate, TaskUpdate, TaskBulkCreate
from services.base import CRUDBase


class TaskService(CRUDBase[Task, TaskCreate, TaskUpdate]):
    """Servisas užduočių CRUD operacijoms."""

    def __init__(self, db: AsyncSession):
        super().__init__(Task, db)

    async def get_by_variant(self, variant_id: int) -> List[Task]:
        """Gauti visas užduotis pagal variantą."""
        query = (
            select(Task)
            .where(Task.variant_id == variant_id)
            .order_by(Task.order_index)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def bulk_create(self, data: TaskBulkCreate) -> List[Task]:
        """Sukurti daug užduočių vienu metu."""
        tasks = []
        for i, task_data in enumerate(data.tasks):
            task = Task(
                number=task_data.number,
                text=task_data.text,
                correct_answer=task_data.correct_answer,
                correct_answer_numeric=task_data.correct_answer_numeric,
                points=task_data.points,
                topic=task_data.topic,
                difficulty=task_data.difficulty,
                order_index=i + 1,
                variant_id=data.variant_id
            )
            self.db.add(task)
            tasks.append(task)

        await self.db.commit()
        for task in tasks:
            await self.db.refresh(task)

        return tasks

    async def reorder(self, variant_id: int, task_ids: List[int]) -> List[Task]:
        """Pakeisti užduočių eiliškumą."""
        tasks = await self.get_by_variant(variant_id)
        task_map = {t.id: t for t in tasks}

        for i, task_id in enumerate(task_ids):
            if task_id in task_map:
                task_map[task_id].order_index = i + 1

        await self.db.commit()
        return await self.get_by_variant(variant_id)

    async def get_by_topic(self, topic: str, limit: int = 50) -> List[Task]:
        """Gauti užduotis pagal temą."""
        query = (
            select(Task)
            .where(Task.topic == topic)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
