from services.huggingface_loader import RawProblem
from services.task_translator import get_task_translator, TranslatedProblem
from models.problem_bank import ProblemBank
from database import async_session_maker
import asyncio
import sys
import argparse
import json
from pathlib import Path
from loguru import logger
from sqlalchemy import select

# Pridėti backend į path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def run_translation(limit: int = 100):
    logger.info(f"Pradedu masinį vertimą (Limit: {limit})")
    translator = get_task_translator()

    # Pirmiausia gauname ID sąrašą
    async with async_session_maker() as session:
        query = select(ProblemBank.id).where(
            ProblemBank.tags.like("%needs_translation%")
        ).limit(limit)

        result = await session.execute(query)
        problem_ids = list(result.scalars().all())

    if not problem_ids:
        logger.info("Nėra uždavinių, kuriems reikėtų vertimo!")
        return

    logger.info(f"Rasta uždavinių vertimui: {len(problem_ids)}")
    translated_count = 0
    error_count = 0

    # Iteruojame po vieną ID ir kuriame naują sesiją, kad išvengtume lazy-load klaidų po rollback
    for pid in problem_ids:
        async with async_session_maker() as session:
            try:
                db_prob = (await session.execute(select(ProblemBank).where(ProblemBank.id == pid))).scalar_one()

                # Build RawProblem from DB
                raw = RawProblem(
                    source=db_prob.source.value,
                    source_id=db_prob.source_id,
                    question=db_prob.question_en if db_prob.question_en else db_prob.question_lt,
                    answer=db_prob.answer,
                    solution="\n".join(db_prob.solution_steps_list) if db_prob.solution_steps else "",
                    difficulty=db_prob.difficulty.value,
                    estimated_grade_min=db_prob.grade_min,
                    estimated_grade_max=db_prob.grade_max
                )

                # Translate
                translated: TranslatedProblem = await translator.translate(raw, detect_topic=False)

                # Update DB model
                db_prob.question_lt = translated.question_lt
                db_prob.answer = translated.answer
                db_prob.answer_latex = translated.answer_latex
                db_prob.solution_steps = json.dumps(translated.solution_steps,
                                                    ensure_ascii=False) if translated.solution_steps else None
                db_prob.global_topic = translated.global_topic
                db_prob.global_subtopic = translated.global_subtopic
                db_prob.achievement_level = translated.achievement_level
                db_prob.target_grade = translated.target_grade
                db_prob.is_word_problem = translated.is_word_problem

                # Update tags: remove 'needs_translation' and add new ones
                current_tags = db_prob.tags_list
                if "needs_translation" in current_tags:
                    current_tags.remove("needs_translation")

                # Add newly generated tags (like 'needs_review' etc.)
                for t in (translated.tags or []):
                    if t not in current_tags:
                        current_tags.append(t)

                db_prob.tags = json.dumps(current_tags, ensure_ascii=False)

                await session.commit()
                translated_count += 1
                logger.info(f"Išversta [{translated_count}]: {db_prob.source_id}")

            except Exception as e:
                logger.error(f"Klaida verčiant problem_id={pid}: {e}")
                error_count += 1
                await session.rollback()

    logger.info(f"Baigta. Išversta: {translated_count}, Klaidos: {error_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Masinis uždavinių vertimas iš DB")
    parser.add_argument("--limit", type=int, default=10, help="Kiek uždavinių išversti (default 10)")
    args = parser.parse_args()

    asyncio.run(run_translation(args.limit))
