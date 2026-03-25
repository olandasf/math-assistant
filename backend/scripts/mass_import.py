"""
Masinio uždavinių importo skriptas.
Naudoja PostgreSQL per DATABASE_URL iš .env.

Paleidimas:
  cd D:\MATEMATIKA 2026_2\backend
  venv\Scripts\python.exe scripts/mass_import.py
"""

import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger


async def run_import():
    """Pagrindinis importo procesas."""
    from database import init_db, async_session_maker, _is_sqlite
    from services.problem_bank_service import ProblemBankService

    db_type = "SQLite" if _is_sqlite else "PostgreSQL"
    logger.info(f"=== Masinis importas ===")
    logger.info(f"DB tipas: {db_type}")

    # Inicializuoti DB lenteles
    await init_db()
    logger.info("DB lentelės sukurtos/patikrintos")

    # Importo konfigūracija
    # translate=False — importuojame angliškai, vertimą atliksime vėliau su Gemini
    # Tai leidžia greitai užpildyti DB be API kvietimų
    sources = [
        ("gsm8k", 7500),           # ~7473 žodinių uždavinių (6-8 kl.) — visas dataset'as
        ("competition_math", 1000), # 1000 olimpiadinių (10-12 kl.)
        ("numina_math", 2000),      # 2000 NuminaMath olimpiadinių (8-12 kl.)
        ("math_instruct", 2000),    # 2000 įvairių (6-12 kl.)
        ("amps", 5000),             # 5000 Khan Academy su LaTeX (5-12 kl.)
        ("aops", 2000),             # 2000 AoPS olimpiadinių (8-12 kl.)
        ("open_math", 3000),        # 3000 nvidia OpenMathReasoning (9-12 kl.)
        ("metamath", 5000),         # 5000 MetaMathQA augmented (5-12 kl.)
        ("kaggle_math", 5000),      # 5000 Kaggle math reasoning (5-12 kl.)
    ]

    total_stats = {"fetched": 0, "saved": 0, "skipped": 0, "errors": 0}

    for source_name, limit in sources:
        logger.info(f"\n--- Importuojama: {source_name} (limit={limit}) ---")
        start_time = time.time()

        async with async_session_maker() as session:
            service = ProblemBankService(session)
            try:
                stats = await service.import_from_huggingface(
                    source=source_name,
                    limit=limit,
                    translate=False,          # Be vertimo — greitai
                    generate_variations=False, # Be variacijų
                    auto_offset=True,         # Tęsti nuo ten kur baigta
                )

                elapsed = time.time() - start_time
                logger.info(
                    f"  {source_name}: fetched={stats['fetched']}, "
                    f"saved={stats['saved']}, skipped={stats['skipped']}, "
                    f"errors={stats['errors']} ({elapsed:.1f}s)"
                )

                for key in total_stats:
                    total_stats[key] += stats.get(key, 0)

            except Exception as e:
                logger.error(f"  KLAIDA importuojant {source_name}: {e}")
                total_stats["errors"] += 1

    logger.info(f"\n=== VISO: {total_stats} ===")

    # Statistika
    async with async_session_maker() as session:
        service = ProblemBankService(session)
        db_stats = await service.get_stats()
        logger.info(f"DB statistika: {db_stats}")


if __name__ == "__main__":
    asyncio.run(run_import())
