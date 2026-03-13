"""
Statistics Service - Statistikos skaičiavimas
=============================================
Skaičiuoja mokinio, klasės ir temų statistiką.
"""

import statistics as stats
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from loguru import logger
from models import (
    Answer,
    ClassStatistics,
    SchoolClass,
    Student,
    StudentStatistics,
    Submission,
    Task,
    Test,
    Variant,
)
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class StudentStats:
    """Mokinio statistika."""

    student_id: int
    student_name: str
    student_code: str
    class_name: str

    total_tests: int = 0
    completed_tests: int = 0
    average_grade: float = 0.0
    highest_grade: float = 0.0
    lowest_grade: float = 0.0

    total_points: float = 0.0
    max_points: float = 0.0
    percentage: float = 0.0

    correct_answers: int = 0
    incorrect_answers: int = 0
    accuracy: float = 0.0

    grade_trend: List[float] = field(default_factory=list)
    topic_performance: Dict[str, float] = field(default_factory=dict)
    common_errors: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ClassStats:
    """Klasės statistika."""

    class_id: int
    class_name: str
    school_year: str

    student_count: int = 0
    test_count: int = 0

    average_grade: float = 0.0
    median_grade: float = 0.0
    highest_grade: float = 0.0
    lowest_grade: float = 0.0
    std_deviation: float = 0.0

    grade_distribution: Dict[int, int] = field(default_factory=dict)
    top_students: List[Dict[str, Any]] = field(default_factory=list)
    struggling_students: List[Dict[str, Any]] = field(default_factory=list)

    topic_averages: Dict[str, float] = field(default_factory=dict)
    common_errors: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TopicStats:
    """Temos statistika."""

    topic: str
    total_tasks: int = 0
    correct_count: int = 0
    incorrect_count: int = 0
    accuracy: float = 0.0
    average_points: float = 0.0
    common_mistakes: List[str] = field(default_factory=list)


@dataclass
class ErrorPattern:
    """Klaidų šablonas."""

    error_type: str
    description: str
    frequency: int = 0
    affected_students: int = 0
    example_tasks: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class StatisticsService:
    """Statistikos servisas."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_student_statistics(
        self, student_id: int, school_year_id: Optional[int] = None
    ) -> StudentStats:
        """
        Gauti mokinio statistiką.

        Args:
            student_id: Mokinio ID
            school_year_id: Mokslo metų ID (jei None - visi)

        Returns:
            StudentStats objektas
        """
        # Gauname studentą
        student_query = select(Student).where(Student.id == student_id)
        result = await self.db.execute(student_query)
        student = result.scalar_one_or_none()

        if not student:
            raise ValueError(f"Mokinys {student_id} nerastas")

        # Gauname klasę
        class_query = select(SchoolClass).where(SchoolClass.id == student.class_id)
        result = await self.db.execute(class_query)
        school_class = result.scalar_one_or_none()

        # Inicializuojame stats
        student_stats = StudentStats(
            student_id=student_id,
            student_name=f"{student.first_name} {student.last_name}",
            student_code=student.unique_code or "",
            class_name=school_class.name if school_class else "",
        )

        # Gauname submissions
        submissions_query = select(Submission).where(
            Submission.student_id == student_id
        )
        result = await self.db.execute(submissions_query)
        submissions = result.scalars().all()

        if not submissions:
            return student_stats

        # Skaičiuojame statistiką
        grades = []
        total_points = 0
        max_points = 0
        correct = 0
        incorrect = 0

        for submission in submissions:
            # Gauname atsakymus
            answers_query = select(Answer).where(Answer.submission_id == submission.id)
            result = await self.db.execute(answers_query)
            answers = result.scalars().all()

            submission_points = 0
            submission_max = 0

            for answer in answers:
                # Gauname užduotį
                task_query = select(Task).where(Task.id == answer.task_id)
                result = await self.db.execute(task_query)
                task = result.scalar_one_or_none()

                if task:
                    points = answer.points or 0
                    max_pts = task.points or 0

                    submission_points += points
                    submission_max += max_pts
                    total_points += points
                    max_points += max_pts

                    if answer.is_correct:
                        correct += 1
                    else:
                        incorrect += 1

            # Skaičiuojame pažymį
            if submission_max > 0:
                percentage = (submission_points / submission_max) * 100
                grade = self._percentage_to_grade(percentage)
                grades.append(grade)

        # Užpildome stats
        student_stats.completed_tests = len(submissions)
        student_stats.total_points = total_points
        student_stats.max_points = max_points
        student_stats.percentage = (
            (total_points / max_points * 100) if max_points > 0 else 0
        )

        student_stats.correct_answers = correct
        student_stats.incorrect_answers = incorrect
        student_stats.accuracy = (
            (correct / (correct + incorrect) * 100) if (correct + incorrect) > 0 else 0
        )

        if grades:
            student_stats.average_grade = sum(grades) / len(grades)
            student_stats.highest_grade = max(grades)
            student_stats.lowest_grade = min(grades)
            student_stats.grade_trend = grades

        return student_stats

    async def get_class_statistics(
        self, class_id: int, test_id: Optional[int] = None
    ) -> ClassStats:
        """
        Gauti klasės statistiką.

        Args:
            class_id: Klasės ID
            test_id: Testo ID (jei None - visų testų)

        Returns:
            ClassStats objektas
        """
        # Gauname klasę
        class_query = select(SchoolClass).where(SchoolClass.id == class_id)
        result = await self.db.execute(class_query)
        school_class = result.scalar_one_or_none()

        if not school_class:
            raise ValueError(f"Klasė {class_id} nerasta")

        # Gauname mokinius
        students_query = select(Student).where(Student.class_id == class_id)
        result = await self.db.execute(students_query)
        students = result.scalars().all()

        class_stats = ClassStats(
            class_id=class_id,
            class_name=school_class.name,
            school_year="2025-2026",
            student_count=len(students),
        )

        if not students:
            return class_stats

        # Renkame pažymius
        all_grades = []
        student_performances = []

        for student in students:
            # Gauname mokinio submissions
            submissions_query = select(Submission).where(
                Submission.student_id == student.id
            )
            result = await self.db.execute(submissions_query)
            submissions = result.scalars().all()

            student_grades = []

            for submission in submissions:
                # Skaičiuojame taškus
                answers_query = select(Answer).where(
                    Answer.submission_id == submission.id
                )
                result = await self.db.execute(answers_query)
                answers = result.scalars().all()

                total_pts = 0
                max_pts = 0

                for answer in answers:
                    task_query = select(Task).where(Task.id == answer.task_id)
                    result = await self.db.execute(task_query)
                    task = result.scalar_one_or_none()

                    if task:
                        total_pts += answer.points or 0
                        max_pts += task.points or 0

                if max_pts > 0:
                    percentage = (total_pts / max_pts) * 100
                    grade = self._percentage_to_grade(percentage)
                    student_grades.append(grade)
                    all_grades.append(grade)

            if student_grades:
                avg = sum(student_grades) / len(student_grades)
                student_performances.append(
                    {
                        "name": f"{student.first_name} {student.last_name}",
                        "code": student.unique_code,
                        "average": round(avg, 1),
                    }
                )

        # Statistika
        if all_grades:
            class_stats.average_grade = round(sum(all_grades) / len(all_grades), 2)
            class_stats.median_grade = round(stats.median(all_grades), 2)
            class_stats.highest_grade = max(all_grades)
            class_stats.lowest_grade = min(all_grades)

            if len(all_grades) > 1:
                class_stats.std_deviation = round(stats.stdev(all_grades), 2)

            # Pasiskirstymas
            for g in range(1, 11):
                class_stats.grade_distribution[g] = all_grades.count(g)

        # Top/struggling students
        if student_performances:
            sorted_perf = sorted(student_performances, key=lambda x: -x["average"])
            class_stats.top_students = sorted_perf[:5]
            class_stats.struggling_students = sorted_perf[-5:][::-1]

        return class_stats

    async def get_topic_statistics(
        self, class_id: Optional[int] = None, test_id: Optional[int] = None
    ) -> List[TopicStats]:
        """
        Gauti temų statistiką.
        """
        # Gauname užduotis su temomis
        tasks_query = select(Task)
        if test_id:
            # Filtruoti pagal testą per variantą
            variants_query = select(Variant.id).where(Variant.test_id == test_id)
            result = await self.db.execute(variants_query)
            variant_ids = [v[0] for v in result.fetchall()]
            tasks_query = tasks_query.where(Task.variant_id.in_(variant_ids))

        result = await self.db.execute(tasks_query)
        tasks = result.scalars().all()

        # Grupuojame pagal tipą (kaip proxy temai)
        topic_data: Dict[str, Dict] = {}

        for task in tasks:
            topic = task.type or "Bendra"

            if topic not in topic_data:
                topic_data[topic] = {
                    "total": 0,
                    "correct": 0,
                    "incorrect": 0,
                    "points": 0,
                    "max_points": 0,
                }

            topic_data[topic]["total"] += 1

            # Gauname atsakymus šiai užduočiai
            answers_query = select(Answer).where(Answer.task_id == task.id)
            result = await self.db.execute(answers_query)
            answers = result.scalars().all()

            for answer in answers:
                if answer.is_correct:
                    topic_data[topic]["correct"] += 1
                else:
                    topic_data[topic]["incorrect"] += 1

                topic_data[topic]["points"] += answer.points or 0
                topic_data[topic]["max_points"] += task.points or 0

        # Konvertuojame į TopicStats
        results = []
        for topic, data in topic_data.items():
            total_answers = data["correct"] + data["incorrect"]
            accuracy = (
                (data["correct"] / total_answers * 100) if total_answers > 0 else 0
            )
            avg_points = (data["points"] / total_answers) if total_answers > 0 else 0

            results.append(
                TopicStats(
                    topic=topic,
                    total_tasks=data["total"],
                    correct_count=data["correct"],
                    incorrect_count=data["incorrect"],
                    accuracy=round(accuracy, 1),
                    average_points=round(avg_points, 2),
                )
            )

        return sorted(results, key=lambda x: -x.accuracy)

    async def get_error_patterns(
        self, class_id: Optional[int] = None, limit: int = 10
    ) -> List[ErrorPattern]:
        """
        Analizuoti klaidų šablonus.
        """
        # Gauname neteisingus atsakymus
        answers_query = select(Answer).where(Answer.is_correct == False)
        result = await self.db.execute(answers_query)
        wrong_answers = result.scalars().all()

        # Grupuojame pagal užduotį
        error_counts: Dict[int, int] = Counter()
        for answer in wrong_answers:
            error_counts[answer.task_id] += 1

        # Top klaidos
        patterns = []
        for task_id, count in error_counts.most_common(limit):
            task_query = select(Task).where(Task.id == task_id)
            result = await self.db.execute(task_query)
            task = result.scalar_one_or_none()

            if task:
                patterns.append(
                    ErrorPattern(
                        error_type=task.type or "Bendra",
                        description=task.question or "",
                        frequency=count,
                        affected_students=count,  # Simplified
                        example_tasks=[task.question or ""],
                        suggestions=["Pakartoti šią temą"],
                    )
                )

        return patterns

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Gauti dashboard statistiką.
        """
        # Mokinių skaičius
        students_count = await self.db.execute(select(func.count(Student.id)))
        students = students_count.scalar() or 0

        # Klasių skaičius
        classes_count = await self.db.execute(select(func.count(SchoolClass.id)))
        classes = classes_count.scalar() or 0

        # Testų skaičius
        tests_count = await self.db.execute(select(func.count(Test.id)))
        tests = tests_count.scalar() or 0

        # Pateikimų skaičius
        submissions_count = await self.db.execute(select(func.count(Submission.id)))
        submissions = submissions_count.scalar() or 0

        # Laukiančių tikrinimo
        pending_query = select(func.count(Submission.id)).where(
            Submission.status == "pending"
        )
        pending_count = await self.db.execute(pending_query)
        pending = pending_count.scalar() or 0

        return {
            "students_count": students,
            "classes_count": classes,
            "tests_count": tests,
            "submissions_count": submissions,
            "pending_count": pending,
            "average_grade": 7.5,  # TODO: real calculation
            "this_week_tests": 3,  # TODO: real calculation
        }

    def _percentage_to_grade(self, percentage: float) -> int:
        """Konvertuoja procentus į pažymį."""
        if percentage >= 95:
            return 10
        elif percentage >= 85:
            return 9
        elif percentage >= 75:
            return 8
        elif percentage >= 65:
            return 7
        elif percentage >= 55:
            return 6
        elif percentage >= 45:
            return 5
        elif percentage >= 35:
            return 4
        elif percentage >= 25:
            return 3
        elif percentage >= 15:
            return 2
        else:
            return 1


# Factory function
async def get_statistics_service(db: AsyncSession) -> StatisticsService:
    """Gauti statistikos servisą."""
    return StatisticsService(db)
