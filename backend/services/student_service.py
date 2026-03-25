"""
Servisas mokiniams.
"""

from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.student import Student
from schemas.student import StudentCreate, StudentUpdate, StudentBulkCreate
from services.base import CRUDBase


class StudentService(CRUDBase[Student, StudentCreate, StudentUpdate]):
    """Servisas mokinių CRUD operacijoms."""

    def __init__(self, db: AsyncSession):
        super().__init__(Student, db)

    async def get_by_class(self, class_id: int) -> List[Student]:
        """Gauti visus mokinius pagal klasę."""
        query = (
            select(Student)
            .where(Student.class_id == class_id)
            .order_by(Student.last_name, Student.first_name)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_unique_code(self, code: str) -> Optional[Student]:
        """Gauti mokinį pagal unikalų kodą."""
        query = select(Student).where(Student.unique_code == code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def search(self, query_str: str, limit: int = 20) -> List[Student]:
        """Ieškoti mokinių pagal vardą arba pavardę."""
        search = f"%{query_str}%"
        query = (
            select(Student)
            .where(
                (Student.first_name.ilike(search)) |
                (Student.last_name.ilike(search)) |
                (Student.unique_code.ilike(search))
            )
            .order_by(Student.last_name, Student.first_name)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def generate_unique_code(self) -> str:
        """Generuoti unikalų mokinio kodą."""
        # Formatas: M2026XXX
        query = select(func.count(Student.id))
        result = await self.db.execute(query)
        count = (result.scalar() or 0) + 1
        return f"M2026{count:03d}"

    async def create(self, data: StudentCreate) -> Student:
        """Sukurti naują mokinį (su automatišku kodu)."""
        data_dict = data.model_dump()
        if not data_dict.get("unique_code"):
            data_dict["unique_code"] = await self.generate_unique_code()

        db_obj = Student(**data_dict)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def bulk_create(self, data: StudentBulkCreate) -> List[Student]:
        """Sukurti daug mokinių vienu metu."""
        students = []
        for student_data in data.students:
            code = await self.generate_unique_code()
            student = Student(
                first_name=student_data.first_name,
                last_name=student_data.last_name,
                class_id=data.class_id,
                unique_code=code
            )
            self.db.add(student)
            students.append(student)

        await self.db.commit()
        for student in students:
            await self.db.refresh(student)

        return students

    async def get_with_class(self, id: int) -> Optional[Student]:
        """Gauti mokinį su klasės informacija."""
        query = (
            select(Student)
            .where(Student.id == id)
            .options(selectinload(Student.school_class))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
