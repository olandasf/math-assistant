"""
Skriptas uždavinių peržiūrai ir paieškai.

Naudojimas:
    python scripts/inspect_problems.py --all
    python scripts/inspect_problems.py --search "grūdų"
    python scripts/inspect_problems.py --source gemini
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse

from loguru import logger
from models.problem_bank import ProblemBank
from sqlalchemy import select

from database import async_session_maker


async def show_all_problems(limit: int = None):
    """Parodo visus uždavinius."""
    logger.info("=" * 70)
    logger.info("VISI UŽDAVINIAI BAZĖJE")
    logger.info("=" * 70)

    async with async_session_maker() as db:
        query = select(ProblemBank).order_by(ProblemBank.id)
        if limit:
            query = query.limit(limit)

        result = await db.execute(query)
        problems = result.scalars().all()

        logger.info(f"\nRasta: {len(problems)} uždavinių\n")

        for i, p in enumerate(problems, 1):
            logger.info(f"\n{'=' * 70}")
            logger.info(f"#{i} | ID: {p.id}")
            logger.info(f"{'=' * 70}")
            logger.info(f"Šaltinis: {p.source.value}")
            if p.source_id:
                logger.info(f"Source ID: {p.source_id}")
            logger.info(f"Klasė: {p.grade_min}-{p.grade_max}")
            logger.info(f"Sunkumas: {p.difficulty.value}")
            logger.info(f"Tema: {p.topic_id or 'N/A'}")
            logger.info(f"Patikrintas: {'Taip' if p.is_verified else 'Ne'}")
            logger.info(f"Aktyvus: {'Taip' if p.is_active else 'Ne'}")
            logger.info(f"Kokybė: {p.quality_score or 'N/A'}")
            logger.info(f"Panaudotas: {p.times_used} kartų")
            logger.info(f"\nKLAUSIMAS (LT):")
            logger.info(f"{p.question_lt}")
            if p.question_en:
                logger.info(f"\nKLAUSIMAS (EN):")
                logger.info(f"{p.question_en}")
            logger.info(f"\nATSAKYMAS:")
            logger.info(f"{p.answer}")
            if p.solution_steps:
                logger.info(f"\nSPRENDIMAS:")
                steps = p.solution_steps_list
                for j, step in enumerate(steps, 1):
                    logger.info(f"  {j}. {step}")


async def search_problems(search_text: str):
    """Ieško uždavinių pagal tekstą."""
    logger.info("=" * 70)
    logger.info(f"PAIEŠKA: '{search_text}'")
    logger.info("=" * 70)

    async with async_session_maker() as db:
        query = select(ProblemBank).where(
            ProblemBank.question_lt.contains(search_text)
            | ProblemBank.question_en.contains(search_text)
        )

        result = await db.execute(query)
        problems = result.scalars().all()

        logger.info(f"\nRasta: {len(problems)} uždavinių\n")

        for i, p in enumerate(problems, 1):
            logger.info(f"\n{'=' * 70}")
            logger.info(f"#{i} | ID: {p.id}")
            logger.info(f"{'=' * 70}")
            logger.info(f"Šaltinis: {p.source.value}")
            logger.info(f"Klasė: {p.grade_min}-{p.grade_max}")
            logger.info(f"\nKLAUSIMAS:")
            logger.info(f"{p.question_lt}")
            logger.info(f"\nATSAKYMAS:")
            logger.info(f"{p.answer}")


async def filter_by_source(source: str):
    """Filtruoja pagal šaltinį."""
    logger.info("=" * 70)
    logger.info(f"ŠALTINIS: {source.upper()}")
    logger.info("=" * 70)

    async with async_session_maker() as db:
        query = select(ProblemBank).where(ProblemBank.source == source.upper())

        result = await db.execute(query)
        problems = result.scalars().all()

        logger.info(f"\nRasta: {len(problems)} uždavinių\n")

        for i, p in enumerate(problems, 1):
            logger.info(f"\n{i}. ID: {p.id} | Klasė: {p.grade_min}-{p.grade_max}")
            logger.info(f"   {p.question_lt[:100]}...")


async def find_illogical():
    """Randa nelogiškus uždavinius (heuristika)."""
    logger.info("=" * 70)
    logger.info("NELOGIŠKŲ UŽDAVINIŲ PAIEŠKA")
    logger.info("=" * 70)
    logger.info("Ieškoma uždavinių su įtartinais žodžiais...\n")

    suspicious_patterns = [
        "pagaminama",
        "padidėja",
        "sumažėja",
        "išeiga",
        "daugiau nei",
        "mažiau nei",
    ]

    async with async_session_maker() as db:
        query = select(ProblemBank)
        result = await db.execute(query)
        problems = result.scalars().all()

        suspicious = []

        for p in problems:
            text = p.question_lt.lower()
            for pattern in suspicious_patterns:
                if pattern in text:
                    # Papildoma patikra - ar yra skaičiai
                    import re

                    numbers = re.findall(r"\d+", p.question_lt)
                    if len(numbers) >= 2:
                        suspicious.append((p, pattern, numbers))
                        break

        logger.info(f"Rasta įtartinų: {len(suspicious)}\n")

        for i, (p, pattern, numbers) in enumerate(suspicious, 1):
            logger.info(f"\n{'=' * 70}")
            logger.info(f"#{i} | ID: {p.id} | Įtartinas žodis: '{pattern}'")
            logger.info(f"{'=' * 70}")
            logger.info(f"Šaltinis: {p.source.value}")
            logger.info(f"Skaičiai: {', '.join(numbers)}")
            logger.info(f"\nKLAUSIMAS:")
            logger.info(f"{p.question_lt}")
            logger.info(f"\nATSAKYMAS:")
            logger.info(f"{p.answer}")

            # Bandyti aptikti nelogiškumą
            if len(numbers) >= 3:
                try:
                    nums = [int(n) for n in numbers[:3]]
                    # Patikra: ar išeiga > 100%
                    if nums[1] > nums[0] * 2:
                        logger.warning(
                            f"⚠️  ĮTARTINA: {nums[1]} iš {nums[0]} = {nums[1]/nums[0]*100:.0f}% išeiga!"
                        )
                except (ValueError, TypeError):
                    pass


async def delete_problem(problem_id: int, confirm: bool = False):
    """Ištrina uždavinį pagal ID."""
    async with async_session_maker() as db:
        query = select(ProblemBank).where(ProblemBank.id == problem_id)
        result = await db.execute(query)
        problem = result.scalar_one_or_none()

        if not problem:
            logger.error(f"Uždavinys ID {problem_id} nerastas!")
            return

        logger.info(f"\nUŽDAVINYS ID {problem_id}:")
        logger.info(f"Šaltinis: {problem.source.value}")
        logger.info(f"Klausimas: {problem.question_lt[:100]}...")

        if not confirm:
            logger.warning("\nNaudokite --confirm kad iš tikrųjų ištrintų")
            return

        await db.delete(problem)
        await db.commit()
        logger.success(f"✅ Uždavinys ID {problem_id} ištrintas!")


async def main():
    parser = argparse.ArgumentParser(description="Uždavinių peržiūra ir paieška")
    parser.add_argument("--all", action="store_true", help="Parodyti visus")
    parser.add_argument("--limit", type=int, help="Limitas (su --all)")
    parser.add_argument("--search", type=str, help="Ieškoti teksto")
    parser.add_argument("--source", type=str, help="Filtruoti pagal šaltinį")
    parser.add_argument(
        "--find-illogical", action="store_true", help="Rasti nelogiškus"
    )
    parser.add_argument("--delete", type=int, help="Ištrinti pagal ID")
    parser.add_argument("--confirm", action="store_true", help="Patvirtinti trynimą")

    args = parser.parse_args()

    if args.all:
        await show_all_problems(limit=args.limit)
    elif args.search:
        await search_problems(args.search)
    elif args.source:
        await filter_by_source(args.source)
    elif args.find_illogical:
        await find_illogical()
    elif args.delete:
        await delete_problem(args.delete, confirm=args.confirm)
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
