"""
Ugdymo programos modulis. Paskirstytas į smulkesnius failus:
- models.py: Duomenų struktūros (Topic, Subtopic, etc.)
- grade_data.py: Hardkoduoti ugdymo programos turinio duomenys 5-10 klasėms
- api.py: Pagalbinės funkcijos duomenų gavimui

Ateityje grade_data.py bus pakeistas JSON failų skaitytuvu.
"""

from utils.curriculum.models import (
    ContentArea, AchievementLevel, DifficultyLevel, Competency,
    CognitiveLevel, PassLevel, AssessmentWeights, Subtopic, Topic, GradeCurriculum,
    PUPP_WEIGHTS, VBE_WEIGHTS, PUPP_CONTENT_DISTRIBUTION
)
from utils.curriculum.grade_data import (
    GRADE_5_TOPICS, GRADE_6_TOPICS, GRADE_7_TOPICS,
    GRADE_8_TOPICS, GRADE_9_TOPICS, GRADE_10_TOPICS,
    CURRICULUM_BY_GRADE
)
from utils.curriculum.api import (
    get_all_topics_for_grade, get_topic_by_id, get_subtopic_by_id,
    get_topics_by_content_area, get_difficulty_for_grade_and_level,
    get_topics_summary, search_topics, get_topics_for_api,
    get_topic_details_for_api
)
