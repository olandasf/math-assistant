"""
Bazinis CRUD servisas.
"""

from typing import TypeVar, Generic, Type, Optional, List, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Bazinis CRUD servisas su standartinėmis operacijomis.

    Pavyzdys:
        class StudentService(CRUDBase[Student, StudentCreate, StudentUpdate]):
            pass

        service = StudentService(Student, db)
        students = await service.get_all()
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Gauti įrašą pagal ID."""
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[Any] = None
    ) -> List[ModelType]:
        """Gauti visus įrašus su paginacija."""
        query = select(self.model)

        if order_by is not None:
            query = query.order_by(order_by)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(self) -> int:
        """Suskaičiuoti visus įrašus."""
        query = select(func.count(self.model.id))
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def create(self, data: CreateSchemaType) -> ModelType:
        """Sukurti naują įrašą."""
        db_obj = self.model(**data.model_dump())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, id: int, data: UpdateSchemaType) -> Optional[ModelType]:
        """Atnaujinti esamą įrašą."""
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> bool:
        """Ištrinti įrašą."""
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return False

        await self.db.delete(db_obj)
        await self.db.commit()
        return True

    async def exists(self, id: int) -> bool:
        """Patikrinti ar įrašas egzistuoja."""
        query = select(func.count(self.model.id)).where(self.model.id == id)
        result = await self.db.execute(query)
        return (result.scalar() or 0) > 0
