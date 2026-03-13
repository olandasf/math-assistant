"""
Test for duplicate removal logic.
"""

import json
import re

# Sample AI response with duplicates
SAMPLE_AI_RESPONSE = """
{
  "tasks": [
    {"number": "1a", "student_work": "-52 * (-3/13) = 12", "final_answer": "12"},
    {"number": "1b", "student_work": "23 * (-16) = -368", "final_answer": "-368"},
    {"number": "1b", "student_work": "23 * (-16) = -368", "final_answer": "-368"},
    {"number": "2a", "student_work": "7/15 / (-14/45) = -1.5", "final_answer": "-1.5"},
    {"number": "2a", "student_work": "7/15 / (-14/45) = -1.5", "final_answer": "-1.5"}
  ]
}
"""

EXPECTED_UNIQUE_TASKS = ["1a", "1b", "2a"]


def normalize_task_number(raw_num):
    return re.sub(r"[\s\)\(\.\,]", "", str(raw_num)).lower().strip()


def test_json_duplicate_removal():
    """Test JSON level duplicate removal."""
    data = json.loads(SAMPLE_AI_RESPONSE)
    tasks = data.get("tasks", [])

    print(f"\n=== INITIAL TASKS ({len(tasks)}) ===")
    for i, task in enumerate(tasks):
        print(f"  {i+1}. number='{task['number']}'")

    seen_numbers = set()
    unique_tasks = []

    for task in tasks:
        raw_num = task.get("number", "")
        num = normalize_task_number(raw_num)

        if num and num not in seen_numbers:
            seen_numbers.add(num)
            unique_tasks.append(task)
            print(f"  Added: {num}")
        elif num:
            print(f"  Removed duplicate: {num}")

    print(f"\n=== RESULT ({len(unique_tasks)}) ===")
    result_numbers = [normalize_task_number(t["number"]) for t in unique_tasks]
    print(f"  Numbers: {result_numbers}")

    assert len(unique_tasks) == len(EXPECTED_UNIQUE_TASKS)
    assert result_numbers == EXPECTED_UNIQUE_TASKS


def test_latex_separator_duplicate_removal():
    """Test LaTeX separator duplicate removal."""
    latex = "1a) x=12 Ats.12\xa7\xa7\xa71b) y=-368 Ats.-368\xa7\xa7\xa71b) y=-368 Ats.-368\xa7\xa7\xa72a) z=-1.5"

    print(f"\n=== LATEX WITH SEPARATOR ===")
    lines = latex.split("\xa7\xa7\xa7")
    print(f"  Lines: {len(lines)}")

    seen_ids = set()
    unique_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        id_match = re.match(r"^\s*(\d+[a-z]?)\)", line, re.IGNORECASE)
        if id_match:
            task_id = id_match.group(1).lower()
            if task_id not in seen_ids:
                seen_ids.add(task_id)
                unique_lines.append(line)
                print(f"  Added: {task_id}")
            else:
                print(f"  Removed: {task_id}")
        else:
            unique_lines.append(line)

    print(f"\n=== RESULT ({len(unique_lines)}) ===")
    assert len(unique_lines) == 3


def test_real_output_analysis():
    """Analyze real user output to find duplicates."""
    # Real output from user
    real_output = "1a)x=12Ats.121b)y=-368Ats.-3681b)y=-368Ats.-3682a)z=-1.5Ats.-1.52a)z=-1.5Ats.-1.5"

    print(f"\n=== REAL OUTPUT ANALYSIS ===")
    print(f"  Length: {len(real_output)}")

    # Find all task IDs
    task_pattern = re.compile(r"(\d+[a-z]?)\)", re.IGNORECASE)
    matches = list(task_pattern.finditer(real_output))

    print(f"\n  Found task IDs ({len(matches)}):")
    task_counts = {}
    for match in matches:
        task_id = match.group(1).lower()
        pos = match.start()
        task_counts[task_id] = task_counts.get(task_id, 0) + 1
        print(f"    '{task_id}' at position {pos}")

    print(f"\n  Task ID counts:")
    duplicates_found = []
    for task_id, count in task_counts.items():
        status = "DUPLICATE" if count > 1 else "OK"
        print(f"    {task_id}: {count} times - {status}")
        if count > 1:
            duplicates_found.append(task_id)

    print(f"\n  === CONCLUSION ===")
    if duplicates_found:
        print(f"  DUPLICATES FOUND: {duplicates_found}")
        print(f"  Problem: Duplicate removal is NOT WORKING!")
    else:
        print(f"  No duplicates found")

    # This test should FAIL if there are duplicates
    # assert len(duplicates_found) == 0, f"Found duplicates: {duplicates_found}"


def test_separator_presence():
    """Check if output has separator."""
    # Simulated output without separator
    output_without_sep = "1a)x=121b)y=-3681b)y=-368"
    # Simulated output with separator
    output_with_sep = "1a)x=12\xa7\xa7\xa71b)y=-368"

    print(f"\n=== SEPARATOR CHECK ===")
    print(f"  Without separator has it: {chr(167)*3 in output_without_sep}")
    print(f"  With separator has it: {chr(167)*3 in output_with_sep}")

    if chr(167) * 3 not in output_without_sep:
        print(f"\n  PROBLEM: Output does NOT have separator!")
        print(f"  This means:")
        print(f"    1. Backend is not sending separator, OR")
        print(f"    2. Frontend removes separator before rendering")


if __name__ == "__main__":
    print("=" * 60)
    print("DUPLICATE REMOVAL TESTS")
    print("=" * 60)

    test_json_duplicate_removal()
    print("\n" + "=" * 60)

    test_latex_separator_duplicate_removal()
    print("\n" + "=" * 60)

    test_real_output_analysis()
    print("\n" + "=" * 60)

    test_separator_presence()
    print("\n" + "=" * 60)

    print("\nTests completed!")
