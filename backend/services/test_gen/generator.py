"""
Test Generator - Kontrolinių automatinis generavimas
=====================================================
Naudoja ProblemBank DB kaip pirminį šaltinį.
Šabloninis generatorius (math_problem_bank) kaip fallback kai DB tuščia.

Integruota su curriculum.py - Lietuvos matematikos bendrosios programos turiniu.
"""

import json
import random
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from loguru import logger
from services.math_problem_bank import Difficulty, MathProblem, MathProblemGenerator
from sqlalchemy.ext.asyncio import AsyncSession

# Curriculum modulis - Lietuvos BP turinio aprašymai
from utils.curriculum import (
    CURRICULUM_BY_GRADE,
    AchievementLevel,
    ContentArea,
    DifficultyLevel,
    GradeCurriculum,
    Subtopic,
    Topic,
    get_all_topics_for_grade,
    get_difficulty_for_grade_and_level,
    get_subtopic_by_id,
    get_topic_by_id,
    get_topics_for_api,
    search_topics,
)

import logging
import asyncio

from services.test_gen.models import GeneratedTask, GeneratedVariant, GeneratedTest
from services.test_gen.fallbacks import FallbackGeneratorsMixin


class TestGenerator(FallbackGeneratorsMixin):
    """
    Kontrolinių generatorius.
    
    Prioritetų grandinė:
    1. ProblemBank DB (jei perduota db sesija ir turi uždavinių)
    2. Šabloninis generatorius (MathProblemGenerator) - fallback
    
    DI naudojamas TIK importo pipeline (vertimas + klasifikavimas),
    NE uždavinių generavimui.
    """

    def __init__(self):
        """Inicializuoja generatorių."""
        pass

    # =========================================================================
    # CURRICULUM INTEGRACIJOS METODAI
    # =========================================================================

    def get_curriculum_topics(self, grade_level: int) -> List[Topic]:
        """Gauna visas temas iš curriculum.py pagal klasę."""
        return get_all_topics_for_grade(grade_level, include_review=True)

    def get_topic_subtopics(self, topic_id: str) -> List[Subtopic]:
        """Gauna temos potemes iš curriculum.py."""
        topic = get_topic_by_id(topic_id)
        if topic:
            return topic.subtopics
        return []

    def _get_curriculum_topic_info(
        self, topic_name: str, grade_level: int
    ) -> Optional[Topic]:
        """Randa curriculum.py temą pagal pavadinimą ar ID."""
        topic = get_topic_by_id(topic_name)
        if topic:
            return topic
        results = search_topics(topic_name, grade_level)
        if results:
            return results[0]
        return None

    # =========================================================================
    # PROBLEM BANK DB ŠALTINIS (1 prioritetas)
    # =========================================================================

    async def _fetch_from_problem_bank(
        self,
        db: AsyncSession,
        topics: list[str],
        grade: int,
        difficulty: str,
        count: int,
        exclude_ids: list[int] | None = None,
    ) -> list:
        """
        Ieško uždavinių ProblemBank lentelėje.

        Args:
            db: Duomenų bazės sesija
            topics: Temų ID sąrašas
            grade: Klasė (5-12)
            difficulty: Sunkumas (easy, medium, hard, mixed)
            count: Kiek uždavinių reikia
            exclude_ids: ID, kuriuos praleisti

        Returns:
            ProblemBank objektų sąrašas
        """
        from services.problem_bank_service import ProblemBankService

        service = ProblemBankService(db)

        # Jei mixed — imame mišriai
        if difficulty == "mixed":
            all_problems = []
            a_count = round(count * 0.4)
            b_count = round(count * 0.4)
            c_count = count - a_count - b_count

            for diff, cnt in [("easy", a_count), ("medium", b_count), ("hard", c_count)]:
                if cnt <= 0:
                    continue
                for topic_id in topics:
                    problems = await service.get_random(
                        grade=grade,
                        difficulty=diff,
                        global_subtopic=topic_id,  # Naudojame kaip global_subtopic
                        exclude_ids=exclude_ids or [],
                        count=cnt,
                    )
                    all_problems.extend(problems)
                    if len(all_problems) >= count:
                        break
                if len(all_problems) >= count:
                    break
            return all_problems[:count]

        # Vienas sunkumo lygis
        all_problems = []
        for topic_id in topics:
            problems = await service.get_random(
                grade=grade,
                difficulty=difficulty,
                global_subtopic=topic_id,  # Naudojame kaip global_subtopic
                exclude_ids=exclude_ids or [],
                count=count - len(all_problems),
            )
            all_problems.extend(problems)
            if len(all_problems) >= count:
                break

        # Jei nesurinko per temas — bandome be temos filtro
        if len(all_problems) < count:
            extra = await service.get_random(
                grade=grade,
                difficulty=difficulty if difficulty != "mixed" else None,
                exclude_ids=(exclude_ids or []) + [p.id for p in all_problems],
                count=count - len(all_problems),
            )
            all_problems.extend(extra)

        return all_problems[:count]

    def _build_tasks_from_db(
        self,
        problems: list,
        include_solutions: bool,
    ) -> list[GeneratedTask]:
        """Konvertuoja ProblemBank objektus į GeneratedTask formatą."""
        import json as json_mod

        tasks = []
        for i, prob in enumerate(problems):
            # Parse solution_steps from JSON string
            solution_steps = []
            if include_solutions and prob.solution_steps:
                try:
                    solution_steps = json_mod.loads(prob.solution_steps)
                    if not isinstance(solution_steps, list):
                        solution_steps = [str(solution_steps)]
                except (json_mod.JSONDecodeError, TypeError):
                    solution_steps = [prob.solution_steps] if prob.solution_steps else []

            tasks.append(
                GeneratedTask(
                    number=i + 1,
                    text=prob.question_lt,
                    answer=prob.answer,
                    answer_latex=prob.answer_latex or prob.answer,
                    points=prob.points or 2,
                    topic=prob.topic_id or "",
                    difficulty=prob.difficulty.value if prob.difficulty else "medium",
                    solution_steps=solution_steps,
                )
            )

        return tasks

    # =========================================================================
    # ŠABLONINIS GENERATORIUS (2 prioritetas / fallback)
    # =========================================================================

    def _generate_with_template_bank(
        self,
        topic: str,
        topics: list[str] | None,
        grade_level: int,
        task_count: int,
        variant_count: int,
        difficulty: str,
        include_solutions: bool,
    ) -> GeneratedTest:
        """
        Generuoja kontrolinį naudojant šabloninį generatorių (math_problem_bank).

        Privalumai:
        - 100% teisingi atsakymai
        - Greitas (nereikia AI)
        - Nemokamas
        - Kontroliuojamas sudėtingumas
        """
        logger.info("Naudojamas šabloninis generatorius (math_problem_bank)")

        topic_list = topics if topics else [topic]
        variants = []

        variant_names = ["I", "II", "III", "IV"]
        for v_idx in range(variant_count):
            variant_problems = MathProblemGenerator.generate_test(
                topics=topic_list,
                grade=grade_level,
                task_count=task_count,
                difficulty=difficulty,
                include_solutions=include_solutions,
            )

            variant_tasks = []
            for i, prob in enumerate(variant_problems):
                task = GeneratedTask(
                    number=i + 1,
                    text=prob.text,
                    answer=prob.answer,
                    answer_latex=prob.answer,
                    points=prob.points,
                    topic=prob.topic,
                    difficulty=prob.difficulty.value,
                    solution_steps=prob.solution_steps if include_solutions else [],
                )
                variant_tasks.append(task)

            variants.append(
                GeneratedVariant(
                    variant_name=variant_names[v_idx] if v_idx < len(variant_names) else f"V{v_idx+1}",
                    tasks=variant_tasks,
                )
            )

        # Skaičiuojam taškus
        total_points = sum(task.points for task in variants[0].tasks) if variants else 0

        # Pavadinimas
        topic_display = (
            ", ".join(topic_list) if len(topic_list) <= 3 else f"{topic_list[0]} ir kt."
        )
        title = f"{topic_display.replace('_', ' ').title()} - {grade_level} klasė"

        return GeneratedTest(
            title=title,
            topic=topic_display,
            grade_level=grade_level,
            total_points=total_points,
            variants=variants,
            created_by="Šabloninis generatorius",
        )

    # =========================================================================
    # PAGRINDINIS GENERAVIMO METODAS
    # =========================================================================

    async def generate_test(
        self,
        topic: str,
        grade_level: int,
        task_count: int = 5,
        variant_count: int = 2,
        difficulty: str = "medium",
        include_solutions: bool = True,
        topics: list[str] | None = None,
        db: AsyncSession | None = None,
        **kwargs,  # Absorbuoja senus parametrus (use_template_generator, curriculum_context)
    ) -> GeneratedTest:
        """
        Generuoja kontrolinį darbą.

        Prioritetų grandinė:
        1. ProblemBank DB (jei db perduota ir turi uždavinių)
        2. Šabloninis generatorius (math_problem_bank) - fallback

        Args:
            topic: Matematikos tema (arba sujungtos temos)
            grade_level: Klasė (5-12)
            task_count: Uždavinių kiekis
            variant_count: Variantų kiekis (1-4)
            difficulty: Sudėtingumas ("easy", "medium", "hard", "mixed")
            include_solutions: Ar generuoti sprendimų žingsnius
            topics: Temų sąrašas (jei kelios temos)
            db: Duomenų bazės sesija (Optional - jei None, naudoja tik šablonus)

        Returns:
            GeneratedTest: Pilnas kontrolinis su variantais
        """
        topic_list = topics if topics else [topic]
        
        logger.info(
            f"Generuojamas kontrolinis: temos={topic_list}, klasė={grade_level}, "
            f"uždaviniai={task_count}, variantai={variant_count}, "
            f"DB={'Taip' if db else 'Ne'}"
        )

        # =====================================================================
        # 1 PRIORITETAS: ProblemBank DB
        # =====================================================================
        if db is not None:
            try:
                db_problems = await self._fetch_from_problem_bank(
                    db=db,
                    topics=topic_list,
                    grade=grade_level,
                    difficulty=difficulty,
                    count=task_count,
                )

                if db_problems and len(db_problems) >= task_count:
                    logger.info(
                        f"Rasta {len(db_problems)} uždavinių ProblemBank DB — "
                        f"naudojome tik DB"
                    )
                    return self._build_test_from_db_problems(
                        db_problems=db_problems,
                        topic_list=topic_list,
                        grade_level=grade_level,
                        variant_count=variant_count,
                        include_solutions=include_solutions,
                        db=db,
                    )
                elif db_problems:
                    logger.info(
                        f"Rasta {len(db_problems)}/{task_count} uždavinių DB — "
                        f"papildysime šablonais"
                    )
                    return self._build_test_mixed(
                        db_problems=db_problems,
                        topic_list=topic_list,
                        grade_level=grade_level,
                        task_count=task_count,
                        variant_count=variant_count,
                        difficulty=difficulty,
                        include_solutions=include_solutions,
                    )
                else:
                    logger.info("ProblemBank DB tuščia — naudojame šablonus")

            except Exception as e:
                logger.warning(f"ProblemBank DB klaida: {e} — naudojame šablonus")

        # =====================================================================
        # 2 PRIORITETAS: Šabloninis generatorius (fallback)
        # =====================================================================
        return self._generate_with_template_bank(
            topic=topic,
            topics=topics,
            grade_level=grade_level,
            task_count=task_count,
            variant_count=variant_count,
            difficulty=difficulty,
            include_solutions=include_solutions,
        )

    def _build_test_from_db_problems(
        self,
        db_problems: list,
        topic_list: list[str],
        grade_level: int,
        variant_count: int,
        include_solutions: bool,
        db: AsyncSession,
    ) -> GeneratedTest:
        """Sukuria pilną testą iš ProblemBank uždavinių."""
        tasks = self._build_tasks_from_db(db_problems, include_solutions)

        # Vienas variantas iš DB
        variant_i = GeneratedVariant(variant_name="I", tasks=tasks)
        variants = [variant_i]

        # Papildomi variantai — šabloninis generatorius
        if variant_count > 1:
            topic_display = ", ".join(topic_list) if len(topic_list) <= 3 else topic_list[0]
            for v_idx in range(1, variant_count):
                variant_names = ["II", "III", "IV"]
                if v_idx <= len(variant_names):
                    variant_problems = MathProblemGenerator.generate_test(
                        topics=topic_list,
                        grade=grade_level,
                        task_count=len(tasks),
                        difficulty="medium",
                        include_solutions=include_solutions,
                    )
                    variant_tasks = []
                    for i, prob in enumerate(variant_problems):
                        task = GeneratedTask(
                            number=i + 1,
                            text=prob.text,
                            answer=prob.answer,
                            answer_latex=prob.answer,
                            points=prob.points,
                            topic=prob.topic,
                            difficulty=prob.difficulty.value,
                            solution_steps=prob.solution_steps if include_solutions else [],
                        )
                        variant_tasks.append(task)
                    variants.append(
                        GeneratedVariant(
                            variant_name=variant_names[v_idx - 1],
                            tasks=variant_tasks,
                        )
                    )

        total_points = sum(task.points for task in tasks)
        topic_display = (
            ", ".join(topic_list) if len(topic_list) <= 3 else f"{topic_list[0]} ir kt."
        )
        title = f"{topic_display.replace('_', ' ').title()} - {grade_level} klasė"

        return GeneratedTest(
            title=title,
            topic=topic_display,
            grade_level=grade_level,
            total_points=total_points,
            variants=variants,
            created_by="Uždavinių bazė",
        )

    def _build_test_mixed(
        self,
        db_problems: list,
        topic_list: list[str],
        grade_level: int,
        task_count: int,
        variant_count: int,
        difficulty: str,
        include_solutions: bool,
    ) -> GeneratedTest:
        """Sukuria testą iš DB + template mišinio."""
        # DB uždaviniai
        db_tasks = self._build_tasks_from_db(db_problems, include_solutions)

        # Papildome šablonais
        remaining = task_count - len(db_tasks)
        if remaining > 0:
            template_problems = MathProblemGenerator.generate_test(
                topics=topic_list,
                grade=grade_level,
                task_count=remaining,
                difficulty=difficulty,
                include_solutions=include_solutions,
            )
            for prob in template_problems:
                db_tasks.append(
                    GeneratedTask(
                        number=len(db_tasks) + 1,
                        text=prob.text,
                        answer=prob.answer,
                        answer_latex=prob.answer,
                        points=prob.points,
                        topic=prob.topic,
                        difficulty=prob.difficulty.value,
                        solution_steps=prob.solution_steps if include_solutions else [],
                    )
                )

        # Maišom ir pernumeruojam
        random.shuffle(db_tasks)
        for i, task in enumerate(db_tasks):
            task.number = i + 1

        variant_i = GeneratedVariant(variant_name="I", tasks=db_tasks)
        variants = [variant_i]

        # Papildomi variantai — tik šablonais
        variant_names = ["II", "III", "IV"]
        for v_idx in range(1, variant_count):
            if v_idx <= len(variant_names):
                variant_problems = MathProblemGenerator.generate_test(
                    topics=topic_list,
                    grade=grade_level,
                    task_count=task_count,
                    difficulty=difficulty,
                    include_solutions=include_solutions,
                )
                variant_tasks = []
                for i, prob in enumerate(variant_problems):
                    variant_tasks.append(
                        GeneratedTask(
                            number=i + 1,
                            text=prob.text,
                            answer=prob.answer,
                            answer_latex=prob.answer,
                            points=prob.points,
                            topic=prob.topic,
                            difficulty=prob.difficulty.value,
                            solution_steps=prob.solution_steps if include_solutions else [],
                        )
                    )
                variants.append(
                    GeneratedVariant(variant_name=variant_names[v_idx - 1], tasks=variant_tasks)
                )

        total_points = sum(task.points for task in db_tasks)
        topic_display = (
            ", ".join(topic_list) if len(topic_list) <= 3 else f"{topic_list[0]} ir kt."
        )
        title = f"{topic_display.replace('_', ' ').title()} - {grade_level} klasė"

        return GeneratedTest(
            title=title,
            topic=topic_display,
            grade_level=grade_level,
            total_points=total_points,
            variants=variants,
            created_by="Uždavinių bazė + Šablonai",
        )


# Singleton
_generator: Optional[TestGenerator] = None

def get_test_generator() -> TestGenerator:
    """Gauna kontrolinių generatorių."""
    global _generator
    if _generator is None:
        _generator = TestGenerator()
    return _generator
