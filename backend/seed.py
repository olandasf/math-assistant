"""
Pradinių duomenų sukūrimas (seed).
Paleidžiama: python seed.py
"""

import asyncio
import sys
from datetime import date

from models.school_class import SchoolClass
from models.school_year import SchoolYear
from models.student import Student
from models.task import Task
from models.test import Test
from models.variant import Variant
from sqlalchemy import select

from database import async_session_maker, init_db


async def seed_data():
    """Sukuria pradinius duomenis."""

    try:
        # Inicializuojam DB
        print("🔧 Inicializuojama duomenų bazė...")
        await init_db()

        async with async_session_maker() as db:
            # Patikrinam ar jau yra duomenų
            result = await db.execute(select(SchoolYear).limit(1))
            if result.scalar():
                print("⚠️ Duomenys jau egzistuoja! Seed praleistas.")
                print("   Jei norite iš naujo, ištrinkite database/math_teacher.db")
                return

            # === Mokslo metai ===
            print("📅 Kuriami mokslo metai...")
            school_year = SchoolYear(
                name="2025-2026",
                start_date=date(2025, 9, 1),
                end_date=date(2026, 6, 30),
                is_active=True,
            )
            db.add(school_year)
            await db.flush()

            # === Klasės ===
            print("🏫 Kuriamos klasės...")
            classes_data = [
                {"name": "5a", "grade": 5},
                {"name": "5b", "grade": 5},
                {"name": "6a", "grade": 6},
                {"name": "7a", "grade": 7},
                {"name": "8a", "grade": 8},
            ]

            classes = []
            for cls_data in classes_data:
                cls = SchoolClass(
                    name=cls_data["name"],
                    grade=cls_data["grade"],
                    school_year_id=school_year.id,
                )
                db.add(cls)
                classes.append(cls)
            await db.flush()

            # === Mokiniai ===
            print("👨‍🎓 Kuriami mokiniai...")
            students_5a = [
                ("Jonas", "Jonaitis"),
                ("Petras", "Petraitis"),
                ("Ona", "Onaitė"),
                ("Marija", "Marijaitė"),
                ("Tomas", "Tomaitis"),
                ("Greta", "Gretaitė"),
                ("Lukas", "Lukauskas"),
                ("Gabija", "Gabijaitė"),
                ("Matas", "Mataitis"),
                ("Austėja", "Austėjaitė"),
            ]

            students_5b = [
                ("Andrius", "Andriuškevičius"),
                ("Simona", "Simonaitė"),
                ("Darius", "Dariuškevičius"),
                ("Eglė", "Eglaitė"),
                ("Karolis", "Karolaitis"),
            ]

            students_6a = [
                ("Rokas", "Rokiškis"),
                ("Aistė", "Aistaitė"),
                ("Mantas", "Mantaitis"),
                ("Viktorija", "Viktoraitė"),
                ("Nedas", "Nedaitis"),
                ("Kotryna", "Kotrynaitė"),
            ]

            # 5a mokiniai
            for i, (first, last) in enumerate(students_5a, 1):
                student = Student(
                    first_name=first,
                    last_name=last,
                    unique_code=f"M2026{classes[0].id:02d}{i:03d}",
                    class_id=classes[0].id,
                    is_active=True,
                )
                db.add(student)

            # 5b mokiniai
            for i, (first, last) in enumerate(students_5b, 1):
                student = Student(
                    first_name=first,
                    last_name=last,
                    unique_code=f"M2026{classes[1].id:02d}{i:03d}",
                    class_id=classes[1].id,
                    is_active=True,
                )
                db.add(student)

            # 6a mokiniai
            for i, (first, last) in enumerate(students_6a, 1):
                student = Student(
                    first_name=first,
                    last_name=last,
                    unique_code=f"M2026{classes[2].id:02d}{i:03d}",
                    class_id=classes[2].id,
                    is_active=True,
                )
                db.add(student)

            await db.flush()

            # === Kontroliniai ===
            print("📝 Kuriami kontroliniai...")

            # Kontrolinis 5a klasei
            test1 = Test(
                title="Kontrolinis Nr. 1",
                description="Trupmenų sudėtis ir atimtis",
                class_id=classes[0].id,
                school_year_id=school_year.id,
                topic="Trupmenų sudėtis ir atimtis",
                test_date=date(2025, 10, 15),
                max_points=20,
                status="draft",
            )
            db.add(test1)

            # Kontrolinis 6a klasei
            test2 = Test(
                title="Kontrolinis Nr. 1",
                description="Dešimtainės trupmenos",
                class_id=classes[2].id,
                school_year_id=school_year.id,
                topic="Dešimtainės trupmenos",
                test_date=date(2025, 10, 20),
                max_points=25,
                status="active",
            )
            db.add(test2)

            await db.flush()

            # === Variantai ===
            print("📋 Kuriami variantai...")

            # Test 1 variantai
            variant1_1 = Variant(test_id=test1.id, name="I variantas")
            variant1_2 = Variant(test_id=test1.id, name="II variantas")
            db.add(variant1_1)
            db.add(variant1_2)

            # Test 2 variantai
            variant2_1 = Variant(test_id=test2.id, name="I variantas")
            variant2_2 = Variant(test_id=test2.id, name="II variantas")
            db.add(variant2_1)
            db.add(variant2_2)

            await db.flush()

            # === Užduotys ===
            print("✏️ Kuriamos užduotys...")

            # Variant 1 užduotys (trupmenų sudėtis)
            tasks_v1 = [
                {
                    "number": "1",
                    "order_index": 1,
                    "text": r"Apskaičiuokite: $\frac{1}{2} + \frac{1}{4}$",
                    "correct_answer": r"\frac{3}{4}",
                    "points": 2.0,
                },
                {
                    "number": "2",
                    "order_index": 2,
                    "text": r"Apskaičiuokite: $\frac{2}{3} + \frac{1}{6}$",
                    "correct_answer": r"\frac{5}{6}",
                    "points": 2.0,
                },
                {
                    "number": "3",
                    "order_index": 3,
                    "text": r"Apskaičiuokite: $\frac{3}{4} - \frac{1}{2}$",
                    "correct_answer": r"\frac{1}{4}",
                    "points": 2.0,
                },
                {
                    "number": "4",
                    "order_index": 4,
                    "text": r"Raskite x: $x + \frac{1}{3} = \frac{2}{3}$",
                    "correct_answer": r"\frac{1}{3}",
                    "points": 3.0,
                },
                {
                    "number": "5",
                    "order_index": 5,
                    "text": "Jonas turėjo 12 obuolių. Jis suvalgė 1/4 obuolių. Kiek obuolių liko?",
                    "correct_answer": "9",
                    "correct_answer_numeric": 9.0,
                    "points": 3.0,
                },
            ]

            for task_data in tasks_v1:
                task = Task(variant_id=variant1_1.id, **task_data)
                db.add(task)

            # Variant 2 užduotys (panašios, bet skirtingos)
            tasks_v2 = [
                {
                    "number": "1",
                    "order_index": 1,
                    "text": r"Apskaičiuokite: $\frac{1}{3} + \frac{1}{6}$",
                    "correct_answer": r"\frac{1}{2}",
                    "points": 2.0,
                },
                {
                    "number": "2",
                    "order_index": 2,
                    "text": r"Apskaičiuokite: $\frac{3}{4} + \frac{1}{8}$",
                    "correct_answer": r"\frac{7}{8}",
                    "points": 2.0,
                },
                {
                    "number": "3",
                    "order_index": 3,
                    "text": r"Apskaičiuokite: $\frac{5}{6} - \frac{1}{3}$",
                    "correct_answer": r"\frac{1}{2}",
                    "points": 2.0,
                },
                {
                    "number": "4",
                    "order_index": 4,
                    "text": r"Raskite x: $x + \frac{1}{4} = \frac{3}{4}$",
                    "correct_answer": r"\frac{1}{2}",
                    "points": 3.0,
                },
                {
                    "number": "5",
                    "order_index": 5,
                    "text": "Ona turėjo 15 saldainių. Ji atidavė 1/3 saldainių. Kiek saldainių liko?",
                    "correct_answer": "10",
                    "correct_answer_numeric": 10.0,
                    "points": 3.0,
                },
            ]

            for task_data in tasks_v2:
                task = Task(variant_id=variant1_2.id, **task_data)
                db.add(task)

            # Atnaujinti test max_points
            test1.max_points = sum(t["points"] for t in tasks_v1)

            await db.commit()

            print("✅ Pradiniai duomenys sukurti!")
            print(f"   - Mokslo metai: 1")
            print(f"   - Klasės: {len(classes)}")
            print(
                f"   - Mokiniai: {len(students_5a) + len(students_5b) + len(students_6a)}"
            )
            print(f"   - Kontroliniai: 2")
            print(f"   - Variantai: 4")
            print(f"   - Užduotys: {len(tasks_v1) + len(tasks_v2)}")

    except Exception as e:
        print(f"❌ Klaida: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Windows fix for asyncio
    import platform

    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_data())
