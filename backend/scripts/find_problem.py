"""
Skriptas uždavinio paieškai visose lentelėse.

Ieško teksto: "Iš 6 kg grūdų pagaminama 18 kg miltų"
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from models.problem_bank import ProblemBank
from models.task import Task
from models.test import Test
from models.variant import Variant
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from database import async_session_maker


async def search_everywhere(search_text: str = "grūdų"):
    """Ieško uždavinio visose lentelėse."""
    logger.info("=" * 70)
    logger.info(f"PAIEŠKA VISOSE LENTELĖSE: '{search_text}'")
    logger.info("=" * 70)

    async with async_session_maker() as db:
        total_found = 0

        # 1. ProblemBank
        logger.info("\n[1] Ieškoma PROBLEM_BANK lentelėje...")
        query = select(ProblemBank).where(
            or_(
                ProblemBank.question_lt.contains(search_text),
                (
                    ProblemBank.question_en.contains(search_text)
                    if ProblemBank.question_en
                    else False
                ),
            )
        )
        result = await db.execute(query)
        problems = result.scalars().all()

        if problems:
            logger.success(f"✅ Rasta {len(problems)} problem_bank:")
            for p in problems:
                logger.info(f"\n  ID: {p.id}")
                logger.info(f"  Šaltinis: {p.source.value}")
                logger.info(f"  Klausimas: {p.question_lt[:150]}...")
                logger.info(f"  Atsakymas: {p.answer}")
                total_found += 1
        else:
            logger.info("  Nerasta")

        # 2. Task (kontrolinių uždaviniai)
        logger.info("\n[2] Ieškoma TASK lentelėje (kontrolinių uždaviniai)...")
        query = select(Task).where(
            Task.text.isnot(None), Task.text.contains(search_text)
        )
        result = await db.execute(query)
        tasks = result.scalars().all()

        if tasks:
            logger.success(f"✅ Rasta {len(tasks)} task:")
            for t in tasks:
                logger.info(f"\n  Task ID: {t.id}")
                logger.info(f"  Variant ID: {t.variant_id}")
                logger.info(f"  Numeris: {t.number}")
                logger.info(f"  Tekstas: {t.text[:150]}...")
                logger.info(f"  Atsakymas: {t.correct_answer}")
                total_found += 1
        else:
            logger.info("  Nerasta")

        # 3. Variant (variantai per tasks relationship)
        logger.info("\n[3] Ieškoma VARIANT lentelėje (per tasks)...")
        query = select(Variant).options(selectinload(Variant.tasks))
        result = await db.execute(query)
        variants = result.scalars().all()

        found_in_variants = []
        for variant in variants:
            # Ieškoti per tasks relationship
            variant_tasks = [
                t for t in variant.tasks if t.text and search_text in t.text
            ]
            if variant_tasks:
                found_in_variants.append((variant, variant_tasks))

        if found_in_variants:
            logger.success(f"✅ Rasta {len(found_in_variants)} variantuose:")
            for v, v_tasks in found_in_variants:
                logger.info(f"\n  Variant ID: {v.id}")
                logger.info(f"  Test ID: {v.test_id}")
                logger.info(f"  Variantas: {v.name}")
                for task in v_tasks:
                    logger.info(f"    - Task #{task.number}: {task.text[:100]}...")
                    total_found += 1
        else:
            logger.info("  Nerasta")

        # 4. Test (kontroliniai) - per variants ir tasks
        logger.info("\n[4] Ieškoma TEST lentelėje (per variants)...")
        query = select(Test)
        result = await db.execute(query)
        tests = result.scalars().all()

        found_in_tests = []
        for test in tests:
            # Rasti visus test variants
            query = select(Variant).where(Variant.test_id == test.id)
            result = await db.execute(query)
            test_variants = result.scalars().all()

            # Ieškoti tasks su tekstu
            test_tasks = []
            for variant in test_variants:
                query = select(Task).where(
                    Task.variant_id == variant.id,
                    Task.text.isnot(None),
                    Task.text.contains(search_text),
                )
                result = await db.execute(query)
                variant_tasks = result.scalars().all()
                test_tasks.extend(variant_tasks)

            if test_tasks:
                found_in_tests.append((test, test_tasks))

        if found_in_tests:
            logger.success(f"✅ Rasta {len(found_in_tests)} testuose:")
            for test, test_tasks in found_in_tests:
                logger.info(f"\n  Test ID: {test.id}")
                logger.info(f"  Pavadinimas: {test.title}")
                logger.info(f"  Klasė: {test.class_id}")
                logger.info(f"  Data: {test.test_date}")
                logger.info(f"  Uždavinių su tekstu: {len(test_tasks)}")
                for task in test_tasks:
                    logger.info(f"    - Task #{task.number}: {task.text[:100]}...")
                total_found += len(test_tasks)
        else:
            logger.info("  Nerasta")

        # Rezultatas
        logger.info("\n" + "=" * 70)
        if total_found > 0:
            logger.success(f"IŠ VISO RASTA: {total_found} vietose")
        else:
            logger.warning("NERASTA NIEKUR!")
            logger.info("\nGalbūt:")
            logger.info("  1. Uždavinys jau ištrintas")
            logger.info("  2. Tekstas šiek tiek kitoks")
            logger.info("  3. Uždavinys buvo tik laikinai sugeneruotas")
        logger.info("=" * 70)


async def show_all_tasks():
    """Parodo visus uždavinius iš Task lentelės."""
    logger.info("=" * 70)
    logger.info("VISI UŽDAVINIAI IŠ TASK LENTELĖS")
    logger.info("=" * 70)

    async with async_session_maker() as db:
        query = select(Task).order_by(Task.id)
        result = await db.execute(query)
        tasks = result.scalars().all()

        logger.info(f"\nRasta: {len(tasks)} uždavinių\n")

        for i, t in enumerate(tasks, 1):
            logger.info(
                f"\n{i}. Task ID: {t.id} | Variant ID: {t.variant_id} | #{t.number}"
            )
            logger.info(f"   Tekstas: {t.text[:150] if t.text else '(tuščias)'}...")
            logger.info(f"   Atsakymas: {t.correct_answer}")


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Rasti uždavinį visose lentelėse")
    parser.add_argument("--search", type=str, default="grūdų", help="Paieškos tekstas")
    parser.add_argument("--all-tasks", action="store_true", help="Parodyti visus Task")

    args = parser.parse_args()

    if args.all_tasks:
        await show_all_tasks()
    else:
        await search_everywhere(args.search)


if __name__ == "__main__":
    asyncio.run(main())
