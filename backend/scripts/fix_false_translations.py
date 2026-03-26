import sqlite3
import json
from pathlib import Path

db_path = Path(__file__).parent.parent.parent / 'database' / 'math_teacher.db'

def fix_false_translations():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Ieškome visų problemų, kurios NEturi "needs_translation" žymos, bet kurių
    # question_lt lauke vis dar matyti angliškas tekstas
    cur.execute("SELECT id, source_id, question_lt, tags FROM problem_bank WHERE tags NOT LIKE '%needs_translation%'")
    
    count = 0
    for rowid, src, q_lt, tags in cur.fetchall():
        if q_lt and (" the " in q_lt.lower() or " is " in q_lt.lower()):
            count += 1
            if tags:
                tag_list = json.loads(tags)
            else:
                tag_list = []
                
            if "needs_translation" not in tag_list:
                tag_list.append("needs_translation")
                
            new_tags = json.dumps(tag_list, ensure_ascii=False)
            cur.execute("UPDATE problem_bank SET tags = ? WHERE id = ?", (new_tags, rowid))
            
    conn.commit()
    conn.close()
    
    print("--------------------------------------------------")
    print(f"ATSTATYTA Į EILĘ: {count} pseudo-išverstų uždavinių.")
    print("Kadangi nebuvo API rakto, uždaviniai išsisaugojo angliškai be vertimo.")
    print("Dabar jie sėkmingai grąžinti atgal į vertimo sąrašą!")
    print("--------------------------------------------------")

if __name__ == "__main__":
    fix_false_translations()
