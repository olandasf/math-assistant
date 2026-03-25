import json
import re

with open(r"D:\MATEMATIKA 2026_2\Matematikos programa\Atnaujinta\curriculum_8.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# The data is just one cycle right now.
topics_raw = data[0]["topics"]

cycles = []
current_cycle = None

# Regex to match main chapters like "1. KVADRATINĖ IR KUBINĖ ŠAKNYS"
chapter_re = re.compile(r"^(\d+)\.\s+([A-ZŽČŠĮŲŪĖĄŲ_ ]+)$")
# Regex to match subtopics like "1.1. Kvadratinė šaknis"
subtopic_re = re.compile(r"(\d+\.\d+\.)\s+(.*?)(?=\d+\.\d+\.|$|(?:\d+\.\s+[A-Z]))")

for item in topics_raw:
    text = item["name"]
    duration = item["duration"]
    
    # Let's split the text into parts
    # A chapter title is ALL CAPS usually in this text.
    # Actually, let's just use regex to find all "X. TITLE" and "X.Y. subtitle"
    
    # Find chapter title
    m_chap = re.match(r"(\d+)\.\s+([A-ZŽČŠĮŲŪĖĄ\s]+)(?:(?=\d+\.\d+\.)|$)", text)
    if m_chap:
        c_num = int(m_chap.group(1))
        c_name = m_chap.group(2).strip()
        current_cycle = {
            "cycle": c_num,
            "cycle_name": c_name,
            "duration": f"{duration} pamokos",
            "topics": []
        }
        cycles.append(current_cycle)
        text = text[m_chap.end():]
        
    # Find all subtopics in the remaining text
    subtopics = re.findall(r"(\d+\.\d+\.)\s+(.*?)(?=\d+\.\d+\.|$)", text)
    if subtopics and current_cycle:
        for st_num, st_name in subtopics:
            current_cycle["topics"].append({
                "name": f"{st_num} {st_name.strip()}",
                "duration": "1 pamoka"
            })
            
    # If it was just a continuation (no match for chapter), add to the last cycle
    if not m_chap and current_cycle:
        subtopics_only = re.findall(r"(\d+\.\d+\.)\s+(.*?)(?=\d+\.\d+\.|$)", text)
        for st_num, st_name in subtopics_only:
            current_cycle["topics"].append({
                "name": f"{st_num} {st_name.strip()}",
                "duration": "1 pamoka"
            })

with open(r"D:\MATEMATIKA 2026_2\Matematikos programa\Atnaujinta\curriculum_8_fixed.json", "w", encoding="utf-8") as f:
    json.dump(cycles, f, indent=4, ensure_ascii=False)
