"""
Skriptas VISŲ Task ištrynimui.

Ištrina visus uždavinius iš tasks lentelės.
DĖMESIO: Tai ištrins visus kontrolinius darbus!
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from models.task import Task
from models.test import Test
from models.variant import Variant
from sqlalchemy import delete, select

from database import async_session_maker


async def delete_all_tasks(dry_run: bool = True):
    """Ištrina visus Task."""
    logger.info("=" * 70)
    logger.info("VISŲ TASK TRYNIMAS")
    if dry_run:
        logger.warning("DRY RUN REŽIMAS - nieko nebus ištrinta!")
    logger.info("=" * 70)

    async with async_session_maker() as db:
        # Suskaičiuoti kiek yra
        query = select(Task)
        result = await db.execute(query)
        tasks = result.scalars().all()

        logger.info(f"\nRasta Task: {len(tasks)}")

        if len(tasks) == 0:
            logger.info("Nėra ką trinti!")
            return

        # Parodyti keletą pavyzdžių
        logger.info("\nPirmieji 5 Task:")
        for i, task in enumerate(tasks[:5], 1):
            logger.info(
                f"  {i}. ID: {task.id} | #{task.number} | {task.text[:80] if task.text else '(tuščias)'}..."
            )

        if len(tasks) > 5:
            logger.info(f"  ... ir dar {len(tasks) - 5} Task")

        # Suskaičiuoti Variant ir Test
        query = select(Variant)
        result = await db.execute(query)
        variants = result.scalars().all()

        query = select(Test)
        result = await db.execute(query)
        tests = result.scalars().all()

        logger.info(f"\nBus paveikta:")
        logger.info(f"  - Task: {len(tasks)}")
        logger.info(f"  - Variant: {len(variants)}")
        logger.info(f"  - Test: {len(tests)}")

        if dry_run:
            logger.warning("\n⚠️  DRY RUN - NIEKO nebus ištrinta!")
            logger.info("Paleiskite su --confirm, kad tikrai ištrintumėte")
        else:
            # Ištrinti VISKĄ
            logger.warning("\n🗑️  TRINAMI VISI DUOMENYS...")

            # 1. Ištrinti visus Task
            await db.execute(delete(Task))
            logger.info(f"  ✅ Ištrinta {len(tasks)} Task")

            # 2. Ištrinti visus Variant
            await db.execute(delete(Variant))
            logger.info(f"  ✅ Ištrinta {len(variants)} Variant")

            # 3. Ištrinti visus Test
            await db.execute(delete(Test))
            logger.info(f"  ✅ Ištrinta {len(tests)} Test")

            await db.commit()
            logger.success("\n✅ VISI DUOMENYS SĖKMINGAI IŠTRINTI!")
            logger.info(
                "\nDabar galite užkrauti naujus uždavinius su LOAD_PROBLEMS.bat"
            )


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Ištrinti VISUS Task, Variant ir Test")
    parser.add_argument(
        "--confirm", action="store_true", help="Patvirtinti trynimą (be šio - dry run)"
    )

    args = parser.parse_args()

    await delete_all_tasks(dry_run=not args.confirm)


if __name__ == "__main__":
    asyncio.run(main())
