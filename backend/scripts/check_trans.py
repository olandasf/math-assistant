import sqlite3
from pathlib import Path

# Naudojame absoliutų kelią į DB
db_path = Path(__file__).parent.parent.parent / "database" / "math_teacher.db"

try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT count(*) FROM problem_bank")
    total = cur.fetchone()[0]

    cur.execute("SELECT count(*) FROM problem_bank WHERE tags LIKE '%needs_translation%'")
    needs_trans = cur.fetchone()[0]

    translated = total - needs_trans

    print("--- STATISTIKA ---")
    print(f"Iš viso uždavinių bazėje: {total}")
    print(f"Sėkmingai išversta į LT (arba nereikalauja vertimo): {translated}")
    print(f"Liko išversti: {needs_trans}")
    print("------------------")

except Exception as e:
    print(f"Klaida nuskaitant duomenų bazę: {e}")
finally:
    if 'conn' in locals():
        conn.close()
