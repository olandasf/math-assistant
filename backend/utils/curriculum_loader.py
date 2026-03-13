"""
Matematikos programos temų įkroviklis iš JSON failų.

Skaito temas iš `Matematikos programa/grade_*.json` failų.
Kiekviena klasė kumuliatyviai gauna žemesnių klasių temas:
  - 5 kl. → tik 5 kl. temos
  - 6 kl. → 5 kl. + 6 kl. temos
  - 7 kl. → 5 + 6 + 7 kl. temos
  - ...
  - 12 kl. → 5 + 6 + 7 + 8 + 9 + 10 + 11 + 12 kl. temos

Kiekviena potemė turi difficulty_rules:
  EASY / MEDIUM / HARD - sunkumo lygių aprašymai lietuvių kalba.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import BASE_DIR

logger = logging.getLogger(__name__)

# Kelias iki programos failų
PROGRAM_DIR = BASE_DIR / "Matematikos programa"

# Kešas - pakraunama tik kartą
_grade_cache: Dict[int, List[Dict[str, Any]]] = {}
_loaded = False


def _load_grade_file(grade: int) -> List[Dict[str, Any]]:
    """Nuskaito vienos klasės JSON failą ir grąžina temų sąrašą."""
    filepath = PROGRAM_DIR / f"grade_{grade}.json"
    if not filepath.exists():
        logger.warning(f"Programos failas nerastas: {filepath}")
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        topics = data.get("topics", [])
        # Pridedame grade info prie kiekvienos temos
        for topic in topics:
            topic["source_grade"] = grade
            for subtopic in topic.get("subtopics", []):
                subtopic["source_grade"] = grade
        return topics

    except json.JSONDecodeError as e:
        logger.error(f"JSON klaida faile {filepath}: {e}")
        return []
    except Exception as e:
        logger.error(f"Klaida skaitant {filepath}: {e}")
        return []


def _ensure_loaded():
    """Užtikrina, kad visi failai pakrauti į kešą."""
    global _loaded, _grade_cache
    if _loaded:
        return

    for grade in range(5, 13):
        topics = _load_grade_file(grade)
        _grade_cache[grade] = topics
        if topics:
            subtopic_count = sum(len(t.get("subtopics", [])) for t in topics)
            logger.info(
                f"📚 Pakrauta {grade} kl. programa: "
                f"{len(topics)} temos, {subtopic_count} potemės"
            )

    _loaded = True
    total = sum(len(t) for t in _grade_cache.values())
    logger.info(f"✅ Matematikos programa pakrauta: {total} temų iš viso")


def reload_curriculum():
    """Perkrauna programos duomenis (jei failai pasikeitė)."""
    global _loaded, _grade_cache
    _loaded = False
    _grade_cache = {}
    _ensure_loaded()


def get_grade_topics(grade: int) -> List[Dict[str, Any]]:
    """
    Grąžina TIK nurodytos klasės temas (be kumuliacijos).

    Args:
        grade: Klasė (5-12)

    Returns:
        Temų sąrašas su potemėmis ir difficulty_rules
    """
    _ensure_loaded()
    return _grade_cache.get(grade, [])


def get_cumulative_topics(grade: int) -> Dict[int, List[Dict[str, Any]]]:
    """
    Grąžina kumuliatyvias temas - nuo 5 klasės iki nurodytos klasės.

    Rezultatas sugrupuotas pagal klasę:
    {
        5: [tema1, tema2, ...],
        6: [tema1, tema2, ...],
        ...
        grade: [tema1, tema2, ...]
    }

    Args:
        grade: Klasė (5-12)

    Returns:
        Dict su klasės numeriu kaip raktu ir temų sąrašais kaip reikšmėmis
    """
    _ensure_loaded()
    result = {}
    for g in range(5, grade + 1):
        topics = _grade_cache.get(g, [])
        if topics:
            result[g] = topics
    return result


def get_flat_cumulative_topics(grade: int) -> List[Dict[str, Any]]:
    """
    Grąžina visas temas (kumuliacines) plokščiu sąrašu.

    Args:
        grade: Klasė (5-12)

    Returns:
        Visų temų sąrašas nuo 5 iki grade klasės
    """
    _ensure_loaded()
    all_topics = []
    for g in range(5, grade + 1):
        all_topics.extend(_grade_cache.get(g, []))
    return all_topics


def get_subtopic_by_id(subtopic_id: str) -> Optional[Dict[str, Any]]:
    """Randa potemę pagal ID per visas klases."""
    _ensure_loaded()
    for grade_topics in _grade_cache.values():
        for topic in grade_topics:
            for subtopic in topic.get("subtopics", []):
                if subtopic.get("id") == subtopic_id:
                    return {
                        **subtopic,
                        "topic_id": topic.get("id"),
                        "topic_title": topic.get("title"),
                    }
    return None


def get_difficulty_rules_for_subtopics(
    subtopic_ids: List[str],
    difficulty: Optional[str] = None,
) -> Dict[str, Dict[str, str]]:
    """
    Grąžina sunkumo taisykles pasirinktoms potemėms.

    Args:
        subtopic_ids: Potemių ID sąrašas
        difficulty: Jei nurodyta ("EASY", "MEDIUM", "HARD") - grąžina tik tą lygį

    Returns:
        Dict[subtopic_id -> difficulty_rules arba vienos taisyklės tekstas]
    """
    _ensure_loaded()
    result = {}
    for grade_topics in _grade_cache.values():
        for topic in grade_topics:
            for subtopic in topic.get("subtopics", []):
                if subtopic.get("id") in subtopic_ids:
                    rules = subtopic.get("difficulty_rules", {})
                    if difficulty:
                        key = difficulty.upper()
                        result[subtopic["id"]] = {
                            "name": subtopic.get("name", ""),
                            "topic": topic.get("title", ""),
                            "rule": rules.get(key, ""),
                        }
                    else:
                        result[subtopic["id"]] = {
                            "name": subtopic.get("name", ""),
                            "topic": topic.get("title", ""),
                            "rules": rules,
                        }
    return result


def build_prompt_context(
    subtopic_ids: List[str],
    difficulty: str = "MEDIUM",
    grade: int = 5,
) -> str:
    """
    Parengia kontekstinį tekstą AI generatoriui.

    Sukuria struktūrizuotą aprašymą su pasirinktomis potemėmis
    ir jų sunkumo taisyklėmis.

    Args:
        subtopic_ids: Pasirinktos potemės
        difficulty: Sunkumo lygis (EASY, MEDIUM, HARD)
        grade: Klasė

    Returns:
        Tekstas AI promptui
    """
    _ensure_loaded()
    lines = [
        f"MATEMATIKOS KONTROLINIS DARBAS - {grade} KLASĖ",
        f"Sunkumo lygis: {difficulty}",
        "",
        "PASIRINKTOS TEMOS IR REIKALAVIMAI:",
        "",
    ]

    difficulty_key = difficulty.upper()
    if difficulty_key not in ("EASY", "MEDIUM", "HARD"):
        difficulty_key = "MEDIUM"

    for grade_topics in _grade_cache.values():
        for topic in grade_topics:
            topic_subtopics = [
                st for st in topic.get("subtopics", []) if st.get("id") in subtopic_ids
            ]
            if topic_subtopics:
                lines.append(f"### {topic.get('title', '')}")
                for st in topic_subtopics:
                    rules = st.get("difficulty_rules", {})
                    rule_text = rules.get(difficulty_key, "")
                    lines.append(f"  - {st.get('name', '')}")
                    if rule_text:
                        lines.append(f"    Reikalavimas: {rule_text}")
                lines.append("")

    return "\n".join(lines)


def get_available_grades() -> List[int]:
    """Grąžina klases, kurioms yra programos failai."""
    _ensure_loaded()
    return sorted(g for g in _grade_cache if _grade_cache[g])
