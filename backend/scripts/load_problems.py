"""
Skriptas uždavinių užkrovimui iš HuggingFace ir kitų šaltinių.

Palaiko:
- GSM8K (8500 žodinių uždavinių, 6-8 klasė)
- Competition Math (olimpiadiniai, 10-12 klasė)
- Geometry (geometrijos uždaviniai, 9-12 klasė)
- NuminaMath (olimpiadiniai su CoT, 8-12 klasė)
- MathInstruct (įvairūs uždaviniai, 6-12 klasė)

Naudojimas:
    python scripts/load_problems.py gsm8k --limit 100 --translate
    python scripts/load_problems.py competition --limit 50
    python scripts/load_problems.py geometry --limit 50
    python scripts/load_problems.py numina --limit 100
    python scripts/load_problems.py instruct --limit 100
    python scripts/load_problems.py --stats
"""

import asyncio
import sys
from pathlib import Path

# Pridėti backend į path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse

from ai.gemini_client import GeminiClient
from loguru import logger
from services.huggingface_loader import get_huggingface_loader
from services.problem_bank_service import ProblemBankService

from database import async_session_maker


async def load_gsm8k(
    limit: int = 100,
    offset: int = 0,
    split: str = "train",
    translate: bool = True,
):
    """
    Užkrauna GSM8K uždavinius.

    Args:
        limit: Kiek uždavinių užkrauti
        offset: Kiek praleisti nuo pradžios
        split: "train" arba "test"
        translate: Ar versti į lietuvių kalbą
    """
    logger.info("=" * 70)
    logger.info(f"GSM8K UŽKROVIMAS ({split})")
    logger.info("=" * 70)
    logger.info(f"Limit: {limit}")
    logger.info(f"Offset: {offset}")
    logger.info(f"Versti: {translate}")
    logger.info("")

    loader = get_huggingface_loader()

    # Patikrinti ar yra kešas
    stats = loader.get_stats()
    logger.info("HuggingFace Loader statistika:")
    logger.info(f"  Cache dir: {stats['cache_dir']}")
    logger.info(f"  Datasets library: {stats['datasets_library_available']}")
    if stats["cached_files"]:
        logger.info("  Kešuoti failai:")
        for f in stats["cached_files"]:
            logger.info(f"    - {f['file']}: {f['count']} uždavinių")
    logger.info("")

    # Užkrauti
    async with async_session_maker() as db:
        service = ProblemBankService(db)

        logger.info("Kraunami uždaviniai...")
        stats = await service.import_from_huggingface(
            source="gsm8k",
            limit=limit,
            offset=offset,
            split=split,
            translate=translate,
            generate_variations=False,  # Kol kas be variacijų
            auto_offset=True,  # Automatiškai tęsti nuo paskutinio
        )

        logger.info("\n" + "=" * 70)
        logger.info("REZULTATAI:")
        logger.info("=" * 70)
        logger.info(f"  Užkrauta: {stats['loaded']}")
        logger.info(f"  Išsaugota: {stats['saved']}")
        logger.info(f"  Praleista: {stats['skipped']}")
        logger.info(f"  Klaidos: {stats['errors']}")

        if stats["errors"] > 0 and "error_details" in stats:
            logger.warning("\nKlaidų pavyzdžiai:")
            for i, error in enumerate(stats["error_details"][:5], 1):
                logger.warning(f"  {i}. {error}")


async def load_competition_math(
    limit: int = 50,
    translate: bool = True,
    split: str = "train",
):
    """
    Užkrauna Competition Math uždavinius.

    Args:
        limit: Kiek uždavinių užkrauti
        translate: Ar versti į lietuvių kalbą
        split: "train" arba "test"
    """
    logger.info("=" * 70)
    logger.info(f"COMPETITION MATH UŽKROVIMAS ({split})")
    logger.info("=" * 70)
    logger.info(f"Limit: {limit}")
    logger.info(f"Versti: {translate}")
    logger.info("")

    async with async_session_maker() as db:
        service = ProblemBankService(db)

        logger.info("Kraunami uždaviniai...")
        stats = await service.import_from_huggingface(
            source="competition_math",
            limit=limit,
            split=split,
            translate=translate,
            generate_variations=False,
            auto_offset=True,
        )

        logger.info("\n" + "=" * 70)
        logger.info("REZULTATAI:")
        logger.info("=" * 70)
        logger.info(f"  Užkrauta: {stats['loaded']}")
        logger.info(f"  Išsaugota: {stats['saved']}")
        logger.info(f"  Praleista: {stats['skipped']}")
        logger.info(f"  Klaidos: {stats['errors']}")


async def load_geometry(
    limit: int = 50,
    translate: bool = True,
    split: str = "test",
):
    """
    Užkrauna geometrijos uždavinius.

    Args:
        limit: Kiek uždavinių užkrauti
        translate: Ar versti į lietuvių kalbą
        split: "train" arba "test"
    """
    logger.info("=" * 70)
    logger.info(f"GEOMETRY UŽKROVIMAS ({split})")
    logger.info("=" * 70)
    logger.info(f"Limit: {limit}")
    logger.info(f"Versti: {translate}")
    logger.info("")

    async with async_session_maker() as db:
        service = ProblemBankService(db)

        logger.info("Kraunami geometrijos uždaviniai...")
        stats = await service.import_from_huggingface(
            source="geometry",
            limit=limit,
            split=split,
            translate=translate,
            generate_variations=False,
            auto_offset=True,
        )

        logger.info("\n" + "=" * 70)
        logger.info("REZULTATAI:")
        logger.info("=" * 70)
        logger.info(f"  Užkrauta: {stats['loaded']}")
        logger.info(f"  Išsaugota: {stats['saved']}")
        logger.info(f"  Praleista: {stats['skipped']}")
        logger.info(f"  Klaidos: {stats['errors']}")


async def load_numina_math(
    limit: int = 100,
    translate: bool = True,
    filter_source: str = None,
):
    """
    Užkrauna NuminaMath olimpiadinius uždavinius.

    Args:
        limit: Kiek uždavinių užkrauti
        translate: Ar versti į lietuvių kalbą
        filter_source: Filtras pagal šaltinį (amc, aime, olympiad)
    """
    logger.info("=" * 70)
    logger.info("NUMINA MATH UŽKROVIMAS")
    logger.info("=" * 70)
    logger.info(f"Limit: {limit}")
    logger.info(f"Versti: {translate}")
    if filter_source:
        logger.info(f"Filtras: {filter_source}")
    logger.info("")

    async with async_session_maker() as db:
        service = ProblemBankService(db)

        logger.info("Kraunami olimpiadiniai uždaviniai...")
        stats = await service.import_from_huggingface(
            source="numina_math",
            limit=limit,
            translate=translate,
            generate_variations=False,
            auto_offset=True,
        )

        logger.info("\n" + "=" * 70)
        logger.info("REZULTATAI:")
        logger.info("=" * 70)
        logger.info(f"  Užkrauta: {stats['loaded']}")
        logger.info(f"  Išsaugota: {stats['saved']}")
        logger.info(f"  Praleista: {stats['skipped']}")
        logger.info(f"  Klaidos: {stats['errors']}")


async def load_math_instruct(
    limit: int = 100,
    translate: bool = True,
):
    """
    Užkrauna MathInstruct uždavinius.

    Args:
        limit: Kiek uždavinių užkrauti
        translate: Ar versti į lietuvių kalbą
    """
    logger.info("=" * 70)
    logger.info("MATH INSTRUCT UŽKROVIMAS")
    logger.info("=" * 70)
    logger.info(f"Limit: {limit}")
    logger.info(f"Versti: {translate}")
    logger.info("")

    async with async_session_maker() as db:
        service = ProblemBankService(db)

        logger.info("Kraunami įvairūs uždaviniai...")
        stats = await service.import_from_huggingface(
            source="math_instruct",
            limit=limit,
            translate=translate,
            generate_variations=False,
            auto_offset=True,
        )

        logger.info("\n" + "=" * 70)
        logger.info("REZULTATAI:")
        logger.info("=" * 70)
        logger.info(f"  Užkrauta: {stats['loaded']}")
        logger.info(f"  Išsaugota: {stats['saved']}")
        logger.info(f"  Praleista: {stats['skipped']}")
        logger.info(f"  Klaidos: {stats['errors']}")


async def show_stats():
    """Parodo uždavinių bazės statistiką."""
    logger.info("=" * 70)
    logger.info("UŽDAVINIŲ BAZĖS STATISTIKA")
    logger.info("=" * 70)

    async with async_session_maker() as db:
        service = ProblemBankService(db)
        stats = await service.get_stats()

        logger.info(f"\nIš viso uždavinių: {stats['total_problems']}")

        logger.info("\nPagal šaltinį:")
        for source, count in sorted(
            stats["by_source"].items(), key=lambda x: x[1], reverse=True
        ):
            logger.info(f"  {source}: {count}")

        logger.info("\nPagal sunkumą:")
        for difficulty, count in sorted(stats["by_difficulty"].items()):
            logger.info(f"  {difficulty}: {count}")

        logger.info("\nPagal klasę:")
        for grade, count in sorted(stats["by_grade"].items()):
            logger.info(f"  {grade} klasė: {count}")

        logger.info(f"\nPatikrinti: {stats['verified_count']}")
        logger.info(f"Aktyvūs: {stats['active_count']}")


async def test_translation():
    """Testuoja vertimą."""
    logger.info("=" * 70)
    logger.info("VERTIMO TESTAS")
    logger.info("=" * 70)

    test_problems = [
        "Janet's ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market?",
        "A robe takes 2 bolts of blue fiber and half that much white fiber. How many bolts in total does it take?",
        "Josh decides to try flipping a house. He buys a house for $80,000 and then puts in $50,000 in repairs. This increased the value of the house by 150%. How much profit did he make?",
    ]

    try:
        client = GeminiClient()

        for i, problem in enumerate(test_problems, 1):
            logger.info(f"\n{i}. Originalas (EN):")
            logger.info(f"   {problem}")

            # Versti
            translated = await client.translate_to_lithuanian(problem)

            logger.info(f"   Vertimas (LT):")
            logger.info(f"   {translated}")

    except Exception as e:
        logger.error(f"Vertimo klaida: {e}")
        logger.error("Patikrinkite ar nustatytas GEMINI_API_KEY")


async def main():
    """Pagrindinis skriptas."""
    parser = argparse.ArgumentParser(description="Užkrauna uždavinius iš HuggingFace")
    parser.add_argument(
        "source",
        nargs="?",
        choices=[
            "gsm8k",
            "competition",
            "geometry",
            "numina",
            "instruct",
            "stats",
            "test-translate",
        ],
        help="Šaltinis arba komanda",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Kiek uždavinių užkrauti (default: 100)",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Kiek praleisti nuo pradžios (default: 0)",
    )
    parser.add_argument(
        "--split",
        choices=["train", "test"],
        default="train",
        help="Dataset split (default: train)",
    )
    parser.add_argument(
        "--no-translate",
        action="store_true",
        help="Neversti į lietuvių kalbą",
    )
    parser.add_argument(
        "--filter",
        type=str,
        default=None,
        help="Filtruoti pagal šaltinį (numina: amc, aime, olympiad)",
    )

    args = parser.parse_args()

    if not args.source:
        parser.print_help()
        print("\n" + "=" * 60)
        print("GALIMI ŠALTINIAI:")
        print("=" * 60)
        print("  gsm8k       - 8500 žodinių uždavinių (6-8 klasė)")
        print("  competition - olimpiadiniai (10-12 klasė)")
        print("  geometry    - geometrijos uždaviniai (9-12 klasė)")
        print("  numina      - olimpiadiniai su CoT (8-12 klasė)")
        print("  instruct    - įvairūs uždaviniai (6-12 klasė)")
        print("  stats       - parodyti statistiką")
        print("  test-translate - testuoti vertimą")
        print("=" * 60)
        return

    if args.source == "stats":
        await show_stats()
    elif args.source == "test-translate":
        await test_translation()
    elif args.source == "gsm8k":
        await load_gsm8k(
            limit=args.limit,
            offset=args.offset,
            split=args.split,
            translate=not args.no_translate,
        )
    elif args.source == "competition":
        await load_competition_math(
            limit=args.limit,
            split=args.split,
            translate=not args.no_translate,
        )
    elif args.source == "geometry":
        await load_geometry(
            limit=args.limit,
            split=args.split,
            translate=not args.no_translate,
        )
    elif args.source == "numina":
        await load_numina_math(
            limit=args.limit,
            translate=not args.no_translate,
            filter_source=args.filter,
        )
    elif args.source == "instruct":
        await load_math_instruct(
            limit=args.limit,
            translate=not args.no_translate,
        )


if __name__ == "__main__":
    asyncio.run(main())
