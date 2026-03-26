"""
Exam Service - kontrolinių valdymas ir išsaugojimas į DB.

Šis servisas:
1. Išsaugo sugeneruotą kontrolinį į DB (Test + Variants + Tasks)
2. Susieja PDF su DB per exam_id (QR kodas)
3. Leidžia greitai tikrinti atsakymus pagal DB
"""

from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger
from models.task import Task
from models.test import Test, TestStatus
from models.variant import Variant
from services.exam_sheet_generator import (
    ExamSheet,
    ExamSheetGenerator,
    ExamTask,
    ExamVariant,
)
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession


class ExamService:
    """Servisas kontrolinių valdymui."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.generator = ExamSheetGenerator()

    async def create_exam(
        self,
        title: str,
        class_id: int,
        school_year_id: int,
        test_date: date,
        variants: List[Dict[str, Any]],
        topic: Optional[str] = None,
        description: Optional[str] = None,
        duration_minutes: int = 45,
        grade: int = 5,
    ) -> Dict[str, Any]:
        """
        Sukuria kontrolinį: išsaugo į DB ir sugeneruoja PDF.

        Args:
            title: Kontrolinio pavadinimas
            class_id: Klasės ID
            school_year_id: Mokslo metų ID
            test_date: Kontrolinio data
            variants: Variantų sąrašas su užduotimis
            topic: Tema (pvz., "Lygtys")
            description: Aprašymas
            duration_minutes: Trukmė minutėmis
            grade: Klasė (5-10)

        Returns:
            Dict su kontrolinio info ir PDF keliais
        """
        # 1. Sukuriame ExamSheet objektą
        exam_variants = []
        total_points = 0

        for var_data in variants:
            tasks = []
            for task_data in var_data.get("tasks", []):
                task = ExamTask(
                    number=task_data["number"],
                    text=task_data["text"],
                    points=task_data.get("points", 1),
                    answer=task_data.get("answer"),
                    text_latex=task_data.get("text_latex"),
                    answer_latex=task_data.get("answer_latex"),
                    solution_hint=task_data.get("solution_hint"),
                    workspace_height_mm=task_data.get("workspace_height_mm", 70),
                )
                tasks.append(task)
                if var_data["name"] == "I":  # Skaičiuojam tik iš pirmo varianto
                    total_points += task.points

            exam_variants.append(ExamVariant(name=var_data["name"], tasks=tasks))

        exam_sheet = ExamSheet(
            title=title,
            topic=topic,
            grade=grade,
            date=test_date.strftime("%Y-%m-%d"),
            duration_minutes=duration_minutes,
            total_points=total_points,
            variants=exam_variants,
        )

        # 2. Generuojame PDF (pirma, kad gautume kelius)
        student_pdf, teacher_pdf = await self._generate_pdfs(exam_sheet)

        # 3. Išsaugome į DB su PDF keliais
        db_test = await self._save_to_db(
            exam_sheet=exam_sheet,
            class_id=class_id,
            school_year_id=school_year_id,
            test_date=test_date,
            description=description,
            student_pdf_path=str(student_pdf),
            teacher_pdf_path=str(teacher_pdf),
        )

        logger.info(
            f"Kontrolinis sukurtas: {title} (ID: {db_test.id}, exam_id: {exam_sheet.exam_id})"
        )

        return {
            "id": db_test.id,
            "exam_id": exam_sheet.exam_id,
            "title": title,
            "test_date": test_date.isoformat(),
            "total_points": total_points,
            "variants_count": len(exam_variants),
            "tasks_count": sum(len(v.tasks) for v in exam_variants),
            "student_pdf": str(student_pdf),
            "teacher_pdf": str(teacher_pdf),
            "status": db_test.status,
        }

    async def _save_to_db(
        self,
        exam_sheet: ExamSheet,
        class_id: int,
        school_year_id: int,
        test_date: date,
        description: Optional[str] = None,
        student_pdf_path: Optional[str] = None,
        teacher_pdf_path: Optional[str] = None,
    ) -> Test:
        """Išsaugo kontrolinį į duomenų bazę."""

        # Sukuriame Test
        db_test = Test(
            exam_id=exam_sheet.exam_id,  # QR kodui
            title=exam_sheet.title,
            description=description,
            test_date=test_date,
            topic=exam_sheet.topic,
            max_points=exam_sheet.total_points,
            time_limit_minutes=exam_sheet.duration_minutes,
            status=TestStatus.DRAFT,
            school_year_id=school_year_id,
            class_id=class_id,
            student_pdf_path=student_pdf_path,
            teacher_pdf_path=teacher_pdf_path,
        )
        self.db.add(db_test)
        await self.db.flush()  # Gauname ID

        # Sukuriame Variants ir Tasks
        for exam_variant in exam_sheet.variants:
            variant_points = sum(t.points for t in exam_variant.tasks)

            db_variant = Variant(
                name=exam_variant.name,
                max_points=variant_points,
                test_id=db_test.id,
            )
            self.db.add(db_variant)
            await self.db.flush()

            for idx, exam_task in enumerate(exam_variant.tasks):
                # Bandome išgauti skaitinę reikšmę
                numeric_answer = self._parse_numeric_answer(exam_task.answer)

                db_task = Task(
                    number=exam_task.number,
                    text=exam_task.text,
                    correct_answer=exam_task.answer or "",
                    correct_answer_numeric=numeric_answer,
                    points=exam_task.points,
                    solution_steps=exam_task.solution_hint,
                    topic=exam_sheet.topic,
                    order_index=idx,
                    variant_id=db_variant.id,
                )
                self.db.add(db_task)

        await self.db.commit()
        await self.db.refresh(db_test)

        logger.info(f"Kontrolinis išsaugotas DB: Test ID={db_test.id}")
        return db_test

    def _parse_numeric_answer(self, answer: Optional[str]) -> Optional[float]:
        """Bando išgauti skaitinę reikšmę iš atsakymo."""
        if not answer:
            return None

        import re
        # Pašaliname vienetų žymėjimus (tik kaip atskirus žodžius/prie skaičių)
        clean = re.sub(r'\s*(cm²|cm|mm|km|kg|m²|m|€|Lt|vnt|l)\b', '', answer)
        clean = clean.strip()

        # Jei yra "x = 27" tipo, imame skaičių
        if "=" in clean:
            parts = clean.split("=")
            if len(parts) == 2:
                clean = parts[1].strip()

        try:
            return float(clean)
        except ValueError:
            return None

    async def _generate_pdfs(self, exam_sheet: ExamSheet) -> tuple[Path, Path]:
        """Generuoja mokinio ir mokytojo PDF versijas."""

        # Naudojame absoliutų kelią
        base_dir = Path(__file__).parent.parent.parent  # MATEMATIKA 2026_2
        exports_dir = base_dir / "exports" / "exams"
        exports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Mokinio versija (be atsakymų)
        exam_sheet.teacher_version = False
        student_path = exports_dir / f"exam_{exam_sheet.exam_id}_{timestamp}.pdf"
        self.generator.generate_pdf(exam_sheet, student_path)

        # Mokytojo versija (su atsakymais)
        exam_sheet.teacher_version = True
        teacher_path = exports_dir / f"exam_{exam_sheet.exam_id}-T_{timestamp}.pdf"
        self.generator.generate_pdf(exam_sheet, teacher_path)

        return student_path, teacher_path

    async def get_exam_by_id(self, exam_id: int) -> Optional[Test]:
        """Gauna kontrolinį pagal DB ID."""
        result = await self.db.execute(select(Test).where(Test.id == exam_id))
        return result.scalar_one_or_none()

    async def get_exam_by_qr_code(self, qr_code: str) -> Optional[Dict[str, Any]]:
        """Gauna kontrolinį pagal QR kodo ID (exam_id)."""
        result = await self.db.execute(select(Test).where(Test.exam_id == qr_code))
        test = result.scalar_one_or_none()

        if not test:
            return None

        return await self.get_exam_with_tasks(test.id)

    async def get_exam_with_tasks(self, exam_id: int) -> Optional[Dict[str, Any]]:
        """Gauna kontrolinį su visais variantais ir užduotimis."""
        test = await self.get_exam_by_id(exam_id)
        if not test:
            return None

        # Gauname variantus
        variants_result = await self.db.execute(
            select(Variant).where(Variant.test_id == exam_id)
        )
        variants = variants_result.scalars().all()

        variants_data = []
        for variant in variants:
            # Gauname užduotis
            tasks_result = await self.db.execute(
                select(Task)
                .where(Task.variant_id == variant.id)
                .order_by(Task.order_index)
            )
            tasks = tasks_result.scalars().all()

            variants_data.append(
                {
                    "id": variant.id,
                    "name": variant.name,
                    "max_points": variant.max_points,
                    "tasks": [
                        {
                            "id": t.id,
                            "number": t.number,
                            "text": t.text,
                            "correct_answer": t.correct_answer,
                            "correct_answer_numeric": t.correct_answer_numeric,
                            "points": t.points,
                        }
                        for t in tasks
                    ],
                }
            )

        return {
            "id": test.id,
            "exam_id": test.exam_id,  # QR kodas
            "title": test.title,
            "test_date": test.test_date.isoformat() if test.test_date else None,
            "topic": test.topic,
            "max_points": test.max_points,
            "status": test.status,
            "student_pdf_path": test.student_pdf_path,  # PDF kelias
            "teacher_pdf_path": test.teacher_pdf_path,  # PDF kelias
            "variants": variants_data,
        }

    async def list_exams(
        self,
        class_id: Optional[int] = None,
        school_year_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Grąžina kontrolinių sąrašą filtravimui."""
        query = select(Test)

        conditions = []
        if class_id:
            conditions.append(Test.class_id == class_id)
        if school_year_id:
            conditions.append(Test.school_year_id == school_year_id)
        if status:
            conditions.append(Test.status == status)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(Test.test_date.desc())

        result = await self.db.execute(query)
        tests = result.scalars().all()

        return [
            {
                "id": t.id,
                "title": t.title,
                "test_date": t.test_date.isoformat() if t.test_date else None,
                "topic": t.topic,
                "max_points": t.max_points,
                "status": t.status,
                "class_id": t.class_id,
            }
            for t in tests
        ]

    async def check_answer(
        self,
        task_id: int,
        student_answer: str,
    ) -> Dict[str, Any]:
        """
        Greitas atsakymo tikrinimas pagal DB.

        Returns:
            Dict su tikrinimo rezultatu:
            - is_correct: bool
            - confidence: float (0-1)
            - needs_ai_review: bool - ar reikia AI patikrinimo
            - correct_answer: str
        """
        # Gauname užduotį
        result = await self.db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()

        if not task:
            return {"error": "Užduotis nerasta", "task_id": task_id}

        correct = task.correct_answer
        correct_numeric = task.correct_answer_numeric

        # Normalizuojame atsakymus
        student_clean = self._normalize_answer(student_answer)
        correct_clean = self._normalize_answer(correct)

        # 1. Tiesioginis palyginimas
        if student_clean == correct_clean:
            return {
                "is_correct": True,
                "confidence": 1.0,
                "needs_ai_review": False,
                "correct_answer": correct,
                "points_earned": task.points,
            }

        # 2. Skaitinis palyginimas (jei yra)
        if correct_numeric is not None:
            student_numeric = self._parse_numeric_answer(student_answer)
            if student_numeric is not None:
                # Leidžiame mažą paklaidą (0.01%)
                if abs(student_numeric - correct_numeric) < 0.0001 * abs(
                    correct_numeric
                ):
                    return {
                        "is_correct": True,
                        "confidence": 0.99,
                        "needs_ai_review": False,
                        "correct_answer": correct,
                        "points_earned": task.points,
                    }

        # 3. Panašumo tikrinimas
        similarity = self._calculate_similarity(student_clean, correct_clean)

        if similarity > 0.9:
            # Labai panašu - tikriausiai teisinga (formatavimo skirtumas)
            return {
                "is_correct": True,
                "confidence": similarity,
                "needs_ai_review": True,  # Bet geriau patikrinti
                "correct_answer": correct,
                "points_earned": task.points,
            }
        elif similarity > 0.5:
            # Dalinai panašu - reikia AI
            return {
                "is_correct": False,
                "confidence": similarity,
                "needs_ai_review": True,
                "correct_answer": correct,
                "points_earned": 0,
                "partial_credit_possible": True,
            }
        else:
            # Visiškai skiriasi
            return {
                "is_correct": False,
                "confidence": 1.0 - similarity,
                "needs_ai_review": False,
                "correct_answer": correct,
                "points_earned": 0,
            }

    def _normalize_answer(self, answer: str) -> str:
        """Normalizuoja atsakymą palyginimui."""
        if not answer:
            return ""

        result = answer.lower().strip()
        # Pašaliname tarpus
        result = result.replace(" ", "")
        # Keičiame lietuviškas raides
        result = result.replace("ą", "a").replace("č", "c").replace("ę", "e")
        result = result.replace("ė", "e").replace("į", "i").replace("š", "s")
        result = result.replace("ų", "u").replace("ū", "u").replace("ž", "z")
        # Normalizuojame skaičius
        result = result.replace(",", ".")

        return result

    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """Apskaičiuoja panašumą tarp dviejų stringų (0-1)."""
        if not s1 or not s2:
            return 0.0

        if s1 == s2:
            return 1.0

        # Levenshtein atstumas (supaprastinta versija)
        len1, len2 = len(s1), len(s2)
        if len1 > len2:
            s1, s2 = s2, s1
            len1, len2 = len2, len1

        distances = range(len1 + 1)
        for i2, c2 in enumerate(s2):
            new_distances = [i2 + 1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    new_distances.append(distances[i1])
                else:
                    new_distances.append(
                        1 + min(distances[i1], distances[i1 + 1], new_distances[-1])
                    )
            distances = new_distances

        max_len = max(len1, len2)
        if max_len == 0:
            return 1.0

        return 1.0 - (distances[-1] / max_len)

    async def create_exam_with_tasks(
        self,
        class_id: int,
        title: str,
        topic: str = "general",
        task_count: int = 5,
        difficulty: int = 2,
        variants_count: int = 2,
        school_year_id: int = 1,
        test_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Sukuria kontrolinį su automatiškai sugeneruotomis užduotimis.

        Args:
            class_id: Klasės ID
            title: Kontrolinio pavadinimas
            topic: Tema (equations, fractions, geometry, etc.)
            task_count: Užduočių skaičius per variantą
            difficulty: Sudėtingumas 1-5
            variants_count: Variantų skaičius (1 arba 2)
            school_year_id: Mokslo metų ID
            test_date: Kontrolinio data

        Returns:
            Dict su kontrolinio info
        """
        from datetime import date as date_type

        if test_date is None:
            test_date = date_type.today()

        # Generuojame pavyzdines užduotis pagal temą
        variants = []
        for var_idx in range(variants_count):
            var_name = ["I", "II", "III"][var_idx] if var_idx < 3 else f"V{var_idx+1}"
            tasks = self._generate_sample_tasks(topic, task_count, difficulty, var_idx)
            variants.append({"name": var_name, "tasks": tasks})

        # Naudojame pagrindinį create_exam metodą
        return await self.create_exam(
            title=title,
            class_id=class_id,
            school_year_id=school_year_id,
            test_date=test_date,
            variants=variants,
            topic=topic,
            duration_minutes=45,
            grade=5,
        )

    def _generate_sample_tasks(
        self, topic: str, count: int, difficulty: int, variant_idx: int
    ) -> List[Dict[str, Any]]:
        """Generuoja pavyzdines užduotis pagal temą."""

        # Baziniai skaičiai pagal variantą (kad būtų skirtingi)
        base = (variant_idx + 1) * 10

        tasks = []

        if topic == "equations":
            # Lygtys
            templates = [
                {
                    "text": f"Išspręskite lygtį: x + {base + 5} = {base + 20}",
                    "answer": f"x = {15}",
                    "points": 2,
                },
                {
                    "text": f"Išspręskite lygtį: x - {base + 3} = {base + 12}",
                    "answer": f"x = {base + 15}",
                    "points": 2,
                },
                {
                    "text": f"Išspręskite lygtį: {2 + variant_idx}x = {(2 + variant_idx) * (base + 4)}",
                    "answer": f"x = {base + 4}",
                    "points": 3,
                },
                {
                    "text": f"Išspręskite lygtį: x / {3 + variant_idx} = {base + 2}",
                    "answer": f"x = {(3 + variant_idx) * (base + 2)}",
                    "points": 3,
                },
                {
                    "text": f"Jonas turi x obuolių. Jis atidavė {base} obuolių ir liko {base + 5}. Kiek obuolių turėjo Jonas?",
                    "answer": f"x = {base * 2 + 5}",
                    "points": 4,
                },
            ]
        elif topic == "fractions":
            # Trupmenos
            templates = [
                {
                    "text": f"Apskaičiuokite: 1/{2 + variant_idx} + 1/{4 + variant_idx}",
                    "answer": f"{6 + 2*variant_idx}/{(2 + variant_idx) * (4 + variant_idx)}",
                    "points": 2,
                },
                {
                    "text": f"Apskaičiuokite: {base}/ 5 + {base + 5}/5",
                    "answer": f"{(base * 2 + 5) // 5}",
                    "points": 2,
                },
                {
                    "text": f"Suprastinkite trupmeną: {base + 10}/{base + 20}",
                    "answer": f"1/2",
                    "points": 3,
                },
                {
                    "text": f"Apskaičiuokite: {2 + variant_idx}/3 × {base + 6}",
                    "answer": f"{(2 + variant_idx) * (base + 6) // 3}",
                    "points": 3,
                },
                {
                    "text": f"Kiek yra {base + 5}% nuo {100 + base * 2}?",
                    "answer": f"{(base + 5) * (100 + base * 2) // 100}",
                    "points": 4,
                },
            ]
        elif topic == "geometry":
            # Geometrija
            a, b = base + 2, base + 5
            templates = [
                {
                    "text": f"Stačiakampio ilgis {a} cm, plotis {b} cm. Apskaičiuokite plotą.",
                    "answer": f"S = {a * b} cm²",
                    "points": 2,
                },
                {
                    "text": f"Stačiakampio ilgis {a} cm, plotis {b} cm. Apskaičiuokite perimetrą.",
                    "answer": f"P = {2 * (a + b)} cm",
                    "points": 2,
                },
                {
                    "text": f"Kvadrato kraštinė {a} cm. Apskaičiuokite plotą ir perimetrą.",
                    "answer": f"S = {a * a} cm², P = {4 * a} cm",
                    "points": 3,
                },
                {
                    "text": f"Trikampio pagrindas {a * 2} cm, aukštinė {b} cm. Apskaičiuokite plotą.",
                    "answer": f"S = {a * b} cm²",
                    "points": 3,
                },
                {
                    "text": f"Stačiakampio plotas {a * b} cm², ilgis {a} cm. Koks plotis?",
                    "answer": f"plotis = {b} cm",
                    "points": 4,
                },
            ]
        else:
            # Bendros (aritmetika)
            templates = [
                {
                    "text": f"Apskaičiuokite: {base + 25} + {base + 47} - {base + 9}",
                    "answer": f"{base + 25 + base + 47 - base - 9}",
                    "points": 2,
                },
                {
                    "text": f"Apskaičiuokite: {base + 15} × {3 + variant_idx}",
                    "answer": f"{(base + 15) * (3 + variant_idx)}",
                    "points": 2,
                },
                {
                    "text": f"Apskaičiuokite: {(base + 20) * 4} ÷ 4",
                    "answer": f"{base + 20}",
                    "points": 2,
                },
                {
                    "text": f"Jonas nupirko {base} obuolių ir {base + 5} kriaušių. Kiek viso vaisių?",
                    "answer": f"{base * 2 + 5}",
                    "points": 3,
                },
                {
                    "text": f"Mokykloje {base * 10} mokinių. {base * 3} išvyko į ekskursiją. Kiek liko?",
                    "answer": f"{base * 7}",
                    "points": 3,
                },
            ]

        # Imame tiek užduočių, kiek reikia
        for i in range(min(count, len(templates))):
            task = templates[i].copy()
            task["number"] = str(i + 1)
            task["workspace_height_mm"] = 70 if difficulty >= 3 else 50
            tasks.append(task)

        return tasks
