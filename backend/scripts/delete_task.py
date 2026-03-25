"""
Skriptas konkretaus Task ištrynimui.

Ištrina Task ID 17 (nelogiškas uždavinys apie grūdus).
"""

from database import async_session_maker
from sqlalchemy import select
from models.task import Task
from loguru import logger
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


async def delete_task(task_id: int, dry_run: bool = True):
    """Ištrina konkretų Task."""
    logger.info("=" * 70)
    logger.info(f"TASK TRYNIMAS: ID {task_id}")
    if dry_run:
        logger.warning("DRY RUN REŽIMAS - nieko nebus ištrinta!")
    logger.info("=" * 70)

    async with async_session_maker() as db:
        # Rasti task
        query = select(Task).where(Task.id == task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            logger.error(f"Task ID {task_id} nerastas!")
            return

        # Parodyti informaciją
        logger.info(f"\nRastas Task:")
        logger.info(f"  ID: {task.id}")
        logger.info(f"  Variant ID: {task.variant_id}")
        logger.info(f"  Numeris: {task.number}")
        logger.info(f"  Tekstas: {task.text[:200] if task.text else '(tuščias)'}...")
        logger.info(f"  Atsakymas: {task.correct_answer}")
        logger.info(f"  Taškai: {task.points}")

        if dry_run:
            logger.warning("\n⚠️  DRY RUN - Task NEBUS ištrintas!")
            logger.info("Paleiskite su --confirm, kad tikrai ištrintumėte")
        else:
            # Ištrinti
            await db.delete(task)
            await db.commit()
            logger.success(f"\n✅ Task ID {task_id} sėkmingai ištrintas!")


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Ištrinti konkretų Task")
    parser.add_argument("--task-id", type=int, default=17, help="Task ID trynimui")
    parser.add_argument(
        "--confirm", action="store_true", help="Patvirtinti trynimą (be šio - dry run)"
    )

    args = parser.parse_args()

    await delete_task(args.task_id, dry_run=not args.confirm)


if __name__ == "__main__":
    asyncio.run(main())
