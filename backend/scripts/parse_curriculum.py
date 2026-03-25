import os
import json
import re

EXTRACTED_FILE = r"D:\MATEMATIKA 2026_2\Matematikos programa\Atnaujinta\extracted_text.txt"

def parse_grade_5():
    with open(EXTRACTED_FILE, 'r', encoding='utf-8') as f:
        text = f.read()

    parts = text.split("FILE: ")
    g5_text = ""
    for p in parts:
        if p.startswith("Matematika 5kl_ILGALAIKIS PLANAS_Horizontai_NEW (1).pdf"):
            g5_text = p
            break
            
    lines = g5_text.split("\n")
    cycles = []
    current_cycle = None
    
    for line in lines:
        if line.startswith("    R") and "':" not in line: # R0: [...]
            # parse list
            try:
                row_str = line.split(": ", 1)[1]
                row = eval(row_str, {"__builtins__": None}, {"None": None})
            except:
                continue
                
            if len(row) < 3:
                continue
                
            col0 = row[0]
            col1 = row[1]
            col2 = row[2]
            
            if col0 and "pamok" in col0 and not "Ciklo nr" in col0:
                # new cycle
                # format: "1. Natūralieji\nskaičiai\n19 pamokų"
                match = re.search(r"(\d+)\.\s*(.*?)\n(.*pamok.*)", col0, re.DOTALL)
                if match:
                    cycle_num = int(match.group(1))
                    cycle_name = match.group(2).replace("\n", " ")
                    duration = match.group(3).replace("\n", " ").strip()
                else:
                    cycle_num = len(cycles) + 1
                    cycle_name = col0.split("\n")[0]
                    duration = "?? pamokų"
                
                current_cycle = {
                    "cycle": cycle_num,
                    "cycle_name": cycle_name,
                    "duration": duration,
                    "topics": []
                }
                cycles.append(current_cycle)
                
            if current_cycle and col1 and "Ciklo temos" not in col1:
                topic_name = col1.replace("\n", " ").replace("\xad ", "").strip()
                topic_dur = str(col2).replace("\n", " ").strip() if col2 else ""
                
                # Check for duplicate headers
                if topic_name == "Pakartojame" and not current_cycle["topics"]:
                    pass
                
                if len(topic_name) > 3:
                    current_cycle["topics"].append({
                        "name": topic_name,
                        "duration": f"{topic_dur} pamoka(os)" if str(topic_dur).isdigit() else topic_dur
                    })

    # fix some empty cycles or duplicates
    return [c for c in cycles if c["topics"]]

# Helper for parsing grade 8
def parse_grade_8():
    with open(EXTRACTED_FILE, 'r', encoding='utf-8') as f:
        text = f.read()

    parts = text.split("FILE: ")
    g8_text = ""
    for p in parts:
        if p.startswith("mokymo(si)_ilgalaikis_planas_8kl.pdf"):
            g8_text = p
            break
            
    lines = g8_text.split("\n")
    cycles = []
    current_cycle = None
    
    # Grade 8 does not have Cycle numbers explicitly inside tables in a standard way based on extract.
    # It just lists topics sequentially. We can group them by 1., 2., 3.
    
    topic_regex = re.compile(r"(\d+)\.\s*(.*)")
    
    for line in lines:
        if line.startswith("    R"):
            try:
                row_str = line.split(": ", 1)[1]
                row = eval(row_str, {"__builtins__": None}, {"None": None})
            except:
                continue
            
            if len(row) > 1 and row[0] is not None and len(str(row[0])) > 2:
                col0 = str(row[0]).replace("\n", " ").replace("\xad", "").strip()
                
                # Try to extract topic
                match = topic_regex.match(col0)
                if match:
                    t_num = int(match.group(1))
                    t_name = match.group(2).strip()
                    if t_name:
                        # Find cycle or group it by tens or just let it be one big list.
                        # Wait, Grade 8 is formatted as "I. Realieji skaičiai" or similar?
                        # Let's just create a dummy cycle for now if none exists.
                        if not current_cycle:
                            current_cycle = {
                                "cycle": 1,
                                "cycle_name": "8 Klasės Temos",
                                "duration": "Visos pamokos",
                                "topics": []
                            }
                            cycles.append(current_cycle)
                            
                        current_cycle["topics"].append({
                            "name": col0,
                            "duration": str(row[1]).strip() if len(row) > 1 and row[1] else "1 pamoka"
                        })
    
    return [c for c in cycles if c["topics"]]

if __name__ == "__main__":
    g5 = parse_grade_5()
    with open(r"D:\MATEMATIKA 2026_2\Matematikos programa\Atnaujinta\curriculum_5.json", "w", encoding="utf-8") as f:
        json.dump(g5, f, indent=4, ensure_ascii=False)
    
    g8 = parse_grade_8()
    with open(r"D:\MATEMATIKA 2026_2\Matematikos programa\Atnaujinta\curriculum_8.json", "w", encoding="utf-8") as f:
        json.dump(g8, f, indent=4, ensure_ascii=False)
        
    print(f"Grade 5: {len(g5)} cycles")
    print(f"Grade 8: {len(g8)} cycles")
