"""
Lietuvos matematikos bendrosios programos turinys (2023)
=========================================================

PASTABA: Šis failas yra plonas wrapper atgaliniam suderinamumui.
Paskirstytas į smulkesnius failus:
- utils/curriculum/models.py: Duomenų struktūros
- utils/curriculum/grade_data.py: Ugdymo programos turinio duomenys
- utils/curriculum/api.py: Pagalbinės funkcijos
"""

from utils.curriculum import (  # noqa: F401
    ContentArea,
    AchievementLevel,
    DifficultyLevel,
    Competency,
    CognitiveLevel,
    PassLevel,
    AssessmentWeights,
    Subtopic,
    Topic,
    GradeCurriculum,
    PUPP_WEIGHTS,
    VBE_WEIGHTS,
    PUPP_CONTENT_DISTRIBUTION,
    GRADE_5_TOPICS,
    GRADE_6_TOPICS,
    GRADE_7_TOPICS,
    GRADE_8_TOPICS,
    GRADE_9_TOPICS,
    GRADE_10_TOPICS,
    CURRICULUM_BY_GRADE,
    get_all_topics_for_grade,
    get_topic_by_id,
    get_subtopic_by_id,
    get_topics_by_content_area,
    get_difficulty_for_grade_and_level,
    get_topics_summary,
    search_topics,
    get_topics_for_api,
    get_topic_details_for_api,
)
