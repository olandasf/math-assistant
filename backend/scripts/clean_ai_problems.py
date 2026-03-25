"""
Skriptas senų AI generuotų uždavinių išvalymui.

Ištrina:
- Gemini AI sugeneruotus uždavinius (source='gemini')
- Nepatikrintus uždavinius su žema kokybe
- Dublikatus

Naudojimas:
    python scripts/clean_ai_problems.py [--dry-run] [--all-ai] [--unverified]
"""

from database import async_session_maker
from sqlalchemy import func, select
from models.problem_bank import ProblemBank, ProblemSource
from loguru import logger
import argparse
import asyncio
import sys
from pathlib import Path

# Pridėti backend į path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def clean_ai_problems(
    dry_run: bool = True,
    all_ai: bool = False,
    unverified_only: bool = False,
    quality_threshold: float = 0.3,
):
    """
    Išvalo senus AI generuotus uždavinius.

    Args:
        dry_run: Jei True, tik parodo ką ištrins, bet neištrina
        all_ai: Jei True, ištrina visus AI generuotus (ne tik Gemini)
        unverified_only: Jei True, ištrina tik nepatikrintus
        quality_threshold: Ištrina uždavinius su kokybe žemesne už šį slenkstį
    """
    logger.info("=" * 70)
    logger.info("SENŲ AI UŽDAVINIŲ VALYMAS")
    logger.info("=" * 70)

    async with async_session_maker() as db:
        # 1. Suskaičiuoti kiek yra iš viso
        total_result = await db.execute(select(func.count(ProblemBank.id)))
        total_count = total_result.scalar()
        logger.info(f"Iš viso uždavinių bazėje: {total_count}")

        # 2. Rasti AI generuotus
        query = select(ProblemBank)

        if all_ai:
            # Visi AI šaltiniai
            query = query.where(ProblemBank.source == ProblemSource.GEMINI)
            logger.info("Ieškoma VISŲ AI generuotų uždavinių (Gemini)")
        else:
            # Tik Gemini
            query = query.where(ProblemBank.source == ProblemSource.GEMINI)
            logger.info("Ieškoma Gemini AI generuotų uždavinių")

        if unverified_only:
            query = query.where(ProblemBank.is_verified == False)
            logger.info("Filtruojama: tik nepatikrinti")

        if quality_threshold > 0:
            query = query.where(
                (ProblemBank.quality_score < quality_threshold)
                | (ProblemBank.quality_score.is_(None))
            )
            logger.info(f"Filtruojama: kokybė < {quality_threshold}")

        result = await db.execute(query)
        problems_to_delete = result.scalars().all()

        logger.info(f"\nRasta uždavinių trynimui: {len(problems_to_delete)}")

        if len(problems_to_delete) == 0:
            logger.info("Nėra ką trinti!")
            return

        # 3. Parodyti pavyzdžius
        logger.info("\n" + "=" * 70)
        logger.info("PAVYZDŽIAI (pirmi 5):")
        logger.info("=" * 70)

        for i, problem in enumerate(problems_to_delete[:5], 1):
            logger.info(f"\n{i}. ID: {problem.id}")
            logger.info(f"   Šaltinis: {problem.source.value}")
            logger.info(f"   Klasė: {problem.grade_min}-{problem.grade_max}")
            logger.info(f"   Sunkumas: {problem.difficulty.value}")
            logger.info(f"   Patikrintas: {problem.is_verified}")
            logger.info(f"   Kokybė: {problem.quality_score}")
            logger.info(f"   Klausimas: {problem.question_lt[:100]}...")

        # 4. Statistika pagal šaltinį
        logger.info("\n" + "=" * 70)
        logger.info("STATISTIKA PAGAL ŠALTINĮ:")
        logger.info("=" * 70)

        sources = {}
        for p in problems_to_delete:
            sources[p.source.value] = sources.get(p.source.value, 0) + 1

        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {source}: {count}")

        # 5. Statistika pagal klasę
        logger.info("\n" + "=" * 70)
        logger.info("STATISTIKA PAGAL KLASĘ:")
        logger.info("=" * 70)

        grades = {}
        for p in problems_to_delete:
            grade_range = f"{p.grade_min}-{p.grade_max}"
            grades[grade_range] = grades.get(grade_range, 0) + 1

        for grade, count in sorted(grades.items()):
            logger.info(f"  {grade} klasė: {count}")

        # 6. Trynimas
        if dry_run:
            logger.warning("\n" + "=" * 70)
            logger.warning("DRY RUN REŽIMAS - NIEKO NETRINAMA!")
            logger.warning("=" * 70)
            logger.warning(
                f"Būtų ištrinta {len(problems_to_delete)} uždavinių iš {total_count}"
            )
            logger.warning("Paleiskite be --dry-run flag, kad iš tikrųjų ištrintų")
        else:
            logger.warning("\n" + "=" * 70)
            logger.warning("TRINAMA...")
            logger.warning("=" * 70)

            # Trinti po vieną (kad būtų cascade)
            deleted_count = 0
            for problem in problems_to_delete:
                await db.delete(problem)
                deleted_count += 1

                if deleted_count % 100 == 0:
                    logger.info(f"Ištrinta: {deleted_count}/{len(problems_to_delete)}")

            await db.commit()

            logger.success(f"\n✅ IŠTRINTA: {deleted_count} uždavinių")

            # Patikrinti kiek liko
            total_result = await db.execute(select(func.count(ProblemBank.id)))
            remaining = total_result.scalar()
            logger.info(f"Liko bazėje: {remaining} uždavinių")


async def find_duplicates():
    """Randa dublikatus pagal klausimo tekstą."""
    logger.info("=" * 70)
    logger.info("DUBLIKATŲ PAIEŠKA")
    logger.info("=" * 70)

    async with async_session_maker() as db:
        # Rasti uždavinius su vienodais klausimais
        query = select(
            ProblemBank.question_lt, func.count(ProblemBank.id).label("count")
        ).group_by(ProblemBank.question_lt)

        result = await db.execute(query)
        duplicates = [row for row in result if row.count > 1]

        logger.info(f"Rasta dublikatų grupių: {len(duplicates)}")

        if duplicates:
            logger.info("\nPirmi 10 dublikatų:")
            for i, dup in enumerate(duplicates[:10], 1):
                logger.info(f"\n{i}. Kartojasi {dup.count} kartus:")
                logger.info(f"   {dup.question_lt[:100]}...")

                # Rasti visus šio klausimo ID
                query = select(ProblemBank).where(
                    ProblemBank.question_lt == dup.question_lt
                )
                result = await db.execute(query)
                problems = result.scalars().all()

                for p in problems:
                    logger.info(
                        f"     - ID: {p.id}, Šaltinis: {p.source.value}, "
                        f"Patikrintas: {p.is_verified}"
                    )


async def main():
    """Pagrindinis skriptas."""
    parser = argparse.ArgumentParser(
        description="Išvalo senus AI generuotus uždavinius"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Tik parodyti ką ištrins, bet netrinti",
    )
    parser.add_argument(
        "--all-ai",
        action="store_true",
        help="Trinti visus AI generuotus (ne tik Gemini)",
    )
    parser.add_argument(
        "--unverified",
        action="store_true",
        help="Trinti tik nepatikrintus",
    )
    parser.add_argument(
        "--quality",
        type=float,
        default=0.3,
        help="Kokybės slenkstis (default: 0.3)",
    )
    parser.add_argument(
        "--find-duplicates",
        action="store_true",
        help="Rasti dublikatus",
    )

    args = parser.parse_args()

    if args.find_duplicates:
        await find_duplicates()
    else:
        await clean_ai_problems(
            dry_run=args.dry_run,
            all_ai=args.all_ai,
            unverified_only=args.unverified,
            quality_threshold=args.quality,
        )


if __name__ == "__main__":
    asyncio.run(main())
