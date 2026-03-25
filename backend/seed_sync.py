"""
Sinchroninis pradinių duomenų sukūrimas (seed).
Paleidžiama: python seed_sync.py
"""

import os
import sqlite3

# Duomenų bazės kelias
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "math_teacher.db")


def generate_unique_code(index: int) -> str:
    """Generuoja unikalų mokinio kodą."""
    return f"M2026{index:03d}"


def seed_data():
    """Sukuria pradinius duomenis sinchroniškai."""

    print(f"📂 DB kelias: {os.path.abspath(DB_PATH)}")

    if not os.path.exists(DB_PATH):
        print("❌ Duomenų bazė neegzistuoja! Pirma paleiskite backend serverį.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Patikrinam ar jau yra duomenų (klasių)
        cursor.execute("SELECT COUNT(*) FROM classes")
        count = cursor.fetchone()[0]
        if count > 0:
            print("⚠️ Duomenys jau egzistuoja! Seed praleistas.")
            print(
                "   Jei norite iš naujo, ištrinkite database/math_teacher.db ir paleiskite serverį"
            )
            return

        # === Mokslo metai ===
        print("📅 Kuriami mokslo metai...")
        cursor.execute(
            """
            INSERT INTO school_years (name, start_date, end_date, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
        """,
            ("2025-2026", "2025-09-01", "2026-06-30", 1),
        )
        school_year_id = cursor.lastrowid

        # === Klasės ===
        print("🏫 Kuriamos klasės...")
        classes_data = [
            ("5a", 5),
            ("5b", 5),
            ("6a", 6),
            ("7a", 7),
            ("8a", 8),
        ]

        class_ids = {}
        for name, grade in classes_data:
            cursor.execute(
                """
                INSERT INTO classes (name, grade, school_year_id, created_at, updated_at)
                VALUES (?, ?, ?, datetime('now'), datetime('now'))
            """,
                (name, grade, school_year_id),
            )
            class_ids[name] = cursor.lastrowid

        # === Mokiniai ===
        print("👨‍🎓 Kuriami mokiniai...")

        students_data = {
            "5a": [
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
            ],
            "5b": [
                ("Andrius", "Andriuškevičius"),
                ("Simona", "Simonaitė"),
                ("Darius", "Dariuškevičius"),
                ("Eglė", "Eglaitė"),
                ("Karolis", "Karolaitis"),
            ],
            "6a": [
                ("Rokas", "Rokiškis"),
                ("Aistė", "Aistaitė"),
                ("Mantas", "Mantaitis"),
                ("Viktorija", "Viktoraitė"),
                ("Nedas", "Nedaitis"),
                ("Kotryna", "Kotrynaitė"),
            ],
            "7a": [
                ("Paulius", "Paulaitis"),
                ("Ieva", "Ievaitė"),
                ("Dovydas", "Dovydaitis"),
                ("Emilija", "Emilijaitė"),
                ("Justas", "Justaitis"),
                ("Ugnė", "Ugnaitė"),
                ("Danielius", "Danielaitis"),
            ],
            "8a": [
                ("Arnas", "Arnaitis"),
                ("Kamilė", "Kamilaitė"),
                ("Eimantas", "Eimantaitis"),
                ("Laura", "Lauraitė"),
                ("Dominykas", "Dominykaitė"),
                ("Akvilė", "Akvilaitė"),
                ("Benas", "Benaitis"),
                ("Rugilė", "Rugilaitė"),
            ],
        }

        student_index = 1
        student_ids = {}
        for class_name, students in students_data.items():
            class_id = class_ids[class_name]
            for first_name, last_name in students:
                unique_code = generate_unique_code(student_index)
                cursor.execute(
                    """
                    INSERT INTO students (first_name, last_name, unique_code, class_id, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                """,
                    (first_name, last_name, unique_code, class_id, 1),
                )
                student_ids[f"{first_name} {last_name}"] = cursor.lastrowid
                student_index += 1

        # === Kontroliniai darbai ===
        print("📝 Kuriami kontroliniai darbai...")

        tests_data = [
            (
                "Trupmenų sudėtis ir atimtis",
                "5a",
                "2025-10-15",
                "graded",
                "Paprastosios trupmenos",
            ),
            (
                "Dešimtainės trupmenos",
                "5a",
                "2025-11-20",
                "graded",
                "Dešimtainės trupmenos",
            ),
            (
                "Natūralieji skaičiai",
                "5b",
                "2025-10-10",
                "graded",
                "Natūralieji skaičiai",
            ),
            ("Procentai", "6a", "2025-11-05", "graded", "Procentai"),
            (
                "Teigiami ir neigiami skaičiai",
                "6a",
                "2025-12-01",
                "pending",
                "Teigiami ir neigiami skaičiai",
            ),
            ("Lygtys", "7a", "2025-10-25", "graded", "Tiesinės lygtys"),
            ("Funkcijos", "7a", "2025-11-28", "pending", "Tiesinė funkcija"),
            ("Kvadratinės lygtys", "8a", "2025-11-15", "graded", "Kvadratinės lygtys"),
            ("Pitagoro teorema", "8a", "2025-12-10", "pending", "Geometrija"),
        ]

        test_ids = {}
        for title, class_name, test_date, status, topic in tests_data:
            class_id = class_ids[class_name]
            cursor.execute(
                """
                INSERT INTO tests (title, class_id, test_date, status, max_points, topic, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """,
                (title, class_id, test_date, status, 20.0, topic),
            )
            test_ids[title] = cursor.lastrowid

        # === Variantai ir užduotys ===
        print("📋 Kuriami variantai ir užduotys...")

        # Trupmenų kontroliniam sukuriame variantus su užduotimis
        trupmenu_test_id = test_ids["Trupmenų sudėtis ir atimtis"]

        for variant_name in ["I variantas", "II variantas"]:
            cursor.execute(
                """
                INSERT INTO variants (name, test_id, created_at, updated_at)
                VALUES (?, ?, datetime('now'), datetime('now'))
            """,
                (variant_name, trupmenu_test_id),
            )
            variant_id = cursor.lastrowid

            # Užduotys
            tasks = [
                (
                    "1",
                    r"Apskaičiuokite: $\frac{2}{5} + \frac{1}{3}$",
                    r"\frac{11}{15}",
                    2.0,
                    "paprastoji",
                ),
                (
                    "2",
                    r"Apskaičiuokite: $\frac{5}{6} - \frac{1}{4}$",
                    r"\frac{7}{12}",
                    2.0,
                    "paprastoji",
                ),
                (
                    "3",
                    r"Suprastinkite: $\frac{12}{18}$",
                    r"\frac{2}{3}",
                    2.0,
                    "paprastoji",
                ),
                (
                    "4",
                    r"Raskite: $2\frac{1}{4} + 1\frac{2}{3}$",
                    r"3\frac{11}{12}",
                    3.0,
                    "mišrioji",
                ),
                (
                    "5",
                    r"Uždavinys: Jonas suvalgė $\frac{1}{4}$ pyrago, Petras $\frac{1}{3}$. Kiek liko?",
                    r"\frac{5}{12}",
                    4.0,
                    "tekstinis",
                ),
            ]

            for task_num, question, answer, points, task_type in tasks:
                cursor.execute(
                    """
                    INSERT INTO tasks (task_number, question_text, correct_answer, max_points, task_type, variant_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                """,
                    (task_num, question, answer, points, task_type, variant_id),
                )

        # Commit visus pakeitimus
        conn.commit()

        # Statistika
        cursor.execute("SELECT COUNT(*) FROM school_years")
        years = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM classes")
        classes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM students")
        students = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tests")
        tests = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM variants")
        variants = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tasks")
        tasks = cursor.fetchone()[0]

        print("\n✅ Seed baigtas sėkmingai!")
        print(f"   📅 Mokslo metai: {years}")
        print(f"   🏫 Klasės: {classes}")
        print(f"   👨‍🎓 Mokiniai: {students}")
        print(f"   📝 Kontroliniai: {tests}")
        print(f"   📋 Variantai: {variants}")
        print(f"   ✏️ Užduotys: {tasks}")

    except Exception as e:
        print(f"❌ Klaida: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    seed_data()
