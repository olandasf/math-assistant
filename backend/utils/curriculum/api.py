"""
Funkcijos darbui su ugdymo programos duomenimis.
"""
from typing import Dict, List, Optional
from utils.curriculum.models import (
    Topic, Subtopic, ContentArea, AchievementLevel, DifficultyLevel
)
from utils.curriculum.grade_data import CURRICULUM_BY_GRADE


def get_all_topics_for_grade(grade: int, include_review: bool = True) -> List[Topic]:
    """
    Gauna visas temas nurodytai klasei.

    Args:
        grade: Klasė (5-10)
        include_review: Ar įtraukti kartojimo temas iš žemesnių klasių

    Returns:
        Temų sąrašas
    """
    if grade not in CURRICULUM_BY_GRADE:
        return []

    curriculum = CURRICULUM_BY_GRADE[grade]
    topics = list(curriculum.topics)

    if include_review:
        # Pridedame kartojimo temas iš žemesnių klasių
        for review_topic_id in curriculum.review_topics:
            for lower_grade in range(5, grade):
                if lower_grade in CURRICULUM_BY_GRADE:
                    for topic in CURRICULUM_BY_GRADE[lower_grade].topics:
                        if topic.id == review_topic_id:
                            topics.append(topic)
                            break

    return topics


def get_topic_by_id(topic_id: str) -> Optional[Topic]:
    """Randa temą pagal ID."""
    for grade in range(5, 11):
        if grade in CURRICULUM_BY_GRADE:
            for topic in CURRICULUM_BY_GRADE[grade].topics:
                if topic.id == topic_id:
                    return topic
    return None


def get_subtopic_by_id(subtopic_id: str) -> Optional[Subtopic]:
    """Randa potemę pagal ID."""
    for grade in range(5, 11):
        if grade in CURRICULUM_BY_GRADE:
            for topic in CURRICULUM_BY_GRADE[grade].topics:
                for subtopic in topic.subtopics:
                    if subtopic.id == subtopic_id:
                        return subtopic
    return None


def get_topics_by_content_area(
    area: ContentArea, grade: Optional[int] = None
) -> List[Topic]:
    """Gauna temas pagal turinio sritį."""
    topics = []
    grades_to_check = [grade] if grade else range(5, 11)

    for g in grades_to_check:
        if g in CURRICULUM_BY_GRADE:
            for topic in CURRICULUM_BY_GRADE[g].topics:
                if topic.content_area == area:
                    topics.append(topic)

    return topics


def get_difficulty_for_grade_and_level(
    grade: int, achievement_level: AchievementLevel
) -> DifficultyLevel:
    """
    Nustato sunkumo lygį pagal klasę ir pasiekimų lygį.

    Args:
        grade: Klasė
        achievement_level: Pasiekimų lygis (patenkinamas, pagrindinis, aukštesnysis)

    Returns:
        Rekomenduojamas sunkumo lygis
    """
    # Bazinis sunkumas pagal klasę
    base_difficulty = {5: 1, 6: 1, 7: 2, 8: 2, 9: 3, 10: 3}.get(grade, 2)

    # Koregavimas pagal pasiekimų lygį
    level_adjustment = {
        AchievementLevel.SATISFACTORY: -1,
        AchievementLevel.BASIC: 0,
        AchievementLevel.ADVANCED: 1,
    }.get(achievement_level, 0)

    final_difficulty = max(1, min(5, base_difficulty + level_adjustment))

    return DifficultyLevel(final_difficulty)


def get_topics_summary() -> Dict[int, Dict]:
    """Grąžina apibendrintą informaciją apie visas klases ir temas."""
    summary = {}

    for grade, curriculum in CURRICULUM_BY_GRADE.items():
        topics_by_area = {}
        for topic in curriculum.topics:
            area_name = topic.content_area.value
            if area_name not in topics_by_area:
                topics_by_area[area_name] = []
            topics_by_area[area_name].append(
                {
                    "id": topic.id,
                    "name": topic.name_lt,
                    "subtopic_count": len(topic.subtopics),
                    "importance": topic.importance,
                }
            )

        summary[grade] = {
            "concentre": curriculum.concentre_name,
            "topic_count": len(curriculum.topics),
            "review_count": len(curriculum.review_topics),
            "topics_by_area": topics_by_area,
        }

    return summary


def search_topics(query: str, grade: Optional[int] = None) -> List[Topic]:
    """
    Ieško temų pagal paieškos užklausą.

    Args:
        query: Paieškos tekstas
        grade: Jei nurodyta, ieško tik toje klasėje

    Returns:
        Atitinkančių temų sąrašas
    """
    query_lower = query.lower()
    results = []

    grades_to_check = [grade] if grade else range(5, 11)

    for g in grades_to_check:
        if g in CURRICULUM_BY_GRADE:
            for topic in CURRICULUM_BY_GRADE[g].topics:
                # Ieškome temos pavadinime
                if (
                    query_lower in topic.name_lt.lower()
                    or query_lower in topic.name_en.lower()
                ):
                    results.append(topic)
                    continue

                # Ieškome potemėse
                for subtopic in topic.subtopics:
                    if (
                        query_lower in subtopic.name_lt.lower()
                        or query_lower in subtopic.name_en.lower()
                        or query_lower in subtopic.description.lower()
                    ):
                        results.append(topic)
                        break

    return results


# =============================================================================
# API FUNKCIJOS (naudojamos frontend)
# =============================================================================


def get_topics_for_api(grade: int) -> List[Dict]:
    """Grąžina temas formatu tinkamu API atsakymui."""
    topics = get_all_topics_for_grade(grade, include_review=True)

    return [
        {
            "id": topic.id,
            "name": topic.name_lt,
            "name_en": topic.name_en,
            "content_area": topic.content_area.value,
            "grade_introduced": topic.grade_introduced,
            "importance": topic.importance,
            "subtopics": [
                {
                    "id": st.id,
                    "name": st.name_lt,
                    "description": st.description,
                    "skills": st.skills,
                }
                for st in topic.subtopics
            ],
        }
        for topic in topics
    ]


def get_topic_details_for_api(topic_id: str) -> Optional[Dict]:
    """Grąžina detalią temos informaciją."""
    topic = get_topic_by_id(topic_id)
    if not topic:
        return None

    return {
        "id": topic.id,
        "name": topic.name_lt,
        "name_en": topic.name_en,
        "content_area": topic.content_area.value,
        "description": topic.description,
        "grade_introduced": topic.grade_introduced,
        "grade_mastery": topic.grade_mastery,
        "grades_available": topic.grades_available,
        "importance": topic.importance,
        "prerequisites": topic.prerequisites,
        "subtopics": [
            {
                "id": st.id,
                "name": st.name_lt,
                "description": st.description,
                "satisfactory_requirements": st.satisfactory_requirements,
                "basic_requirements": st.basic_requirements,
                "advanced_requirements": st.advanced_requirements,
                "example_easy": st.example_easy,
                "example_medium": st.example_medium,
                "example_hard": st.example_hard,
                "skills": st.skills,
            }
            for st in topic.subtopics
        ],
    }
