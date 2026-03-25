"""
Problem Bank Service - uždavinių bazės valdymas.

Funkcionalumas:
- CRUD operacijos su ProblemBank
- Paieška pagal temą, sunkumą, klasę
- Atsitiktinių uždavinių gavimas
- Batch importas iš HuggingFace
"""

import json
from typing import Literal, Optional

from loguru import logger
from models.problem_bank import AchievementLevel, ProblemBank, ProblemDifficulty, ProblemSource
from services.huggingface_loader import (
    HuggingFaceLoader,
    get_huggingface_loader,
)
from services.task_translator import (
    TaskTranslator,
    TranslatedProblem,
    get_task_translator,
)
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class ProblemBankService:
    """
    Uždavinių bazės valdymo servisas.

    Naudojimas:
        service = ProblemBankService(db_session)

        # Gauti atsitiktinius uždavinius
        problems = await service.get_random(grade=6, count=5, difficulty="medium")

        # Importuoti iš HuggingFace
        stats = await service.import_from_huggingface(source="gsm8k", limit=100)
    """

    def __init__(
        self,
        db: AsyncSession,
        loader: Optional[HuggingFaceLoader] = None,
        translator: Optional[TaskTranslator] = None,
    ):
        """
        Inicializuoja servisą.

        Args:
            db: Duomenų bazės sesija
            loader: HuggingFace loaderis
            translator: Uždavinių vertėjas
        """
        self.db = db
        self._loader = loader
        self._translator = translator

    @property
    def loader(self) -> HuggingFaceLoader:
        if self._loader is None:
            self._loader = get_huggingface_loader()
        return self._loader

    @property
    def translator(self) -> TaskTranslator:
        if self._translator is None:
            self._translator = get_task_translator()
        return self._translator

    # === CRUD operacijos ===

    async def create(self, problem: TranslatedProblem) -> ProblemBank:
        """
        Sukuria naują uždavinį duomenų bazėje.

        Args:
            problem: Išverstas uždavinys

        Returns:
            Sukurtas ProblemBank objektas
        """
        # Konvertuoti difficulty string į enum
        difficulty_map = {
            "easy": ProblemDifficulty.EASY,
            "medium": ProblemDifficulty.MEDIUM,
            "hard": ProblemDifficulty.HARD,
            "olympiad": ProblemDifficulty.OLYMPIAD,
            "vbe": ProblemDifficulty.VBE,
        }

        source_map = {
            "gsm8k": ProblemSource.GSM8K,
            "competition_math": ProblemSource.COMPETITION_MATH,
            "geometry": ProblemSource.GEOMETRY,
            "numina_math": ProblemSource.NUMINA_MATH,
            "math_instruct": ProblemSource.MATH_INSTRUCT,
            "template": ProblemSource.TEMPLATE,
            "gemini": ProblemSource.GEMINI,
            "manual": ProblemSource.MANUAL,
            "khan": ProblemSource.KHAN_ACADEMY,
            "amps": ProblemSource.AMPS,
            "aops": ProblemSource.AOPS,
            "open_math": ProblemSource.OPEN_MATH,
            "metamath": ProblemSource.METAMATH,
            "kaggle_math": ProblemSource.KAGGLE_MATH,
        }

        db_problem = ProblemBank(
            source=source_map.get(problem.source, ProblemSource.GEMINI),
            source_id=problem.source_id,
            question_lt=problem.question_lt,
            question_en=problem.question_en,
            answer=problem.answer,
            answer_latex=problem.answer_latex,
            solution_steps=(
                json.dumps(problem.solution_steps, ensure_ascii=False)
                if problem.solution_steps
                else None
            ),
            grade_min=problem.grade_min,
            grade_max=problem.grade_max,
            difficulty=difficulty_map.get(problem.difficulty, ProblemDifficulty.MEDIUM),
            topic_id=problem.topic_id,
            tags=json.dumps(problem.tags, ensure_ascii=False) if problem.tags else None,
            is_active=True,
            is_verified=False,
            # BP 2022 klasifikacija (iš Gemini)
            global_topic=getattr(problem, "global_topic", None),
            global_subtopic=getattr(problem, "global_subtopic", None),
            achievement_level=(
                AchievementLevel(getattr(problem, "achievement_level", None))
                if getattr(problem, "achievement_level", None) in ("A", "B", "C")
                else None
            ),
            target_grade=getattr(problem, "target_grade", None),
            is_word_problem=getattr(problem, "is_word_problem", False),
        )

        self.db.add(db_problem)
        await self.db.commit()
        await self.db.refresh(db_problem)

        return db_problem

    async def get_by_id(self, problem_id: int) -> Optional[ProblemBank]:
        """Gauna uždavinį pagal ID."""
        result = await self.db.execute(
            select(ProblemBank).where(ProblemBank.id == problem_id)
        )
        return result.scalar_one_or_none()

    async def get_by_source_id(self, source_id: str) -> Optional[ProblemBank]:
        """Tikrina ar uždavinys jau egzistuoja pagal source_id."""
        result = await self.db.execute(
            select(ProblemBank).where(ProblemBank.source_id == source_id)
        )
        return result.scalar_one_or_none()

    async def update(self, problem_id: int, **kwargs) -> Optional[ProblemBank]:
        """Atnaujina uždavinį."""
        problem = await self.get_by_id(problem_id)
        if not problem:
            return None

        for key, value in kwargs.items():
            if hasattr(problem, key):
                setattr(problem, key, value)

        await self.db.commit()
        await self.db.refresh(problem)
        return problem

    async def delete(self, problem_id: int) -> bool:
        """Ištrina uždavinį (soft delete - deaktyvuoja)."""
        problem = await self.get_by_id(problem_id)
        if not problem:
            return False

        problem.is_active = False
        await self.db.commit()
        return True

    # === Paieška ===

    async def get_filtered(
        self,
        grade: Optional[int] = None,
        difficulty: Optional[str] = None,
        topic_id: Optional[str] = None,
        source: Optional[str] = None,
        verified_only: bool = False,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[ProblemBank], int]:
        """
        Gauna filtruotus uždavinius su total count.

        Returns:
            Tuple (uždavinių sąrašas, bendras kiekis)
        """
        base_query = select(ProblemBank).where(ProblemBank.is_active == True)
        count_query = select(func.count(ProblemBank.id)).where(
            ProblemBank.is_active == True
        )

        conditions = []

        if grade is not None:
            conditions.append(
                and_(ProblemBank.grade_min <= grade, ProblemBank.grade_max >= grade)
            )

        if difficulty:
            try:
                diff_enum = ProblemDifficulty(difficulty)
                conditions.append(ProblemBank.difficulty == diff_enum)
            except ValueError:
                pass

        if topic_id:
            conditions.append(ProblemBank.topic_id == topic_id)

        if source:
            try:
                source_enum = ProblemSource(source)
                conditions.append(ProblemBank.source == source_enum)
            except ValueError:
                pass

        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    ProblemBank.question_lt.ilike(search_pattern),
                    ProblemBank.tags.ilike(search_pattern),
                )
            )

        if verified_only:
            conditions.append(ProblemBank.is_verified == True)

        if conditions:
            base_query = base_query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # Total count
        total = (await self.db.execute(count_query)).scalar() or 0

        # Paginated results
        query = base_query.order_by(ProblemBank.created_at.desc())
        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)
        problems = list(result.scalars().all())

        return problems, total

    async def search(
        self,
        grade: Optional[int] = None,
        difficulty: Optional[str] = None,
        topic_id: Optional[str] = None,
        source: Optional[str] = None,
        search_text: Optional[str] = None,
        verified_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ProblemBank]:
        """
        Ieško uždavinių pagal kriterijus.

        Args:
            grade: Klasė (5-12)
            difficulty: Sunkumas (easy, medium, hard, olympiad, vbe)
            topic_id: Temos ID
            source: Šaltinis (gsm8k, competition_math, template, gemini)
            search_text: Paieškos tekstas
            verified_only: Tik patikrinti
            limit: Maksimalus rezultatų skaičius
            offset: Praleisti pirmų N rezultatų

        Returns:
            Uždavinių sąrašas
        """
        query = select(ProblemBank).where(ProblemBank.is_active == True)

        conditions = []

        if grade is not None:
            conditions.append(
                and_(ProblemBank.grade_min <= grade, ProblemBank.grade_max >= grade)
            )

        if difficulty:
            diff_enum = ProblemDifficulty(difficulty)
            conditions.append(ProblemBank.difficulty == diff_enum)

        if topic_id:
            conditions.append(ProblemBank.topic_id == topic_id)

        if source:
            source_enum = ProblemSource(source)
            conditions.append(ProblemBank.source == source_enum)

        if search_text:
            search_pattern = f"%{search_text}%"
            conditions.append(
                or_(
                    ProblemBank.question_lt.ilike(search_pattern),
                    ProblemBank.tags.ilike(search_pattern),
                )
            )

        if verified_only:
            conditions.append(ProblemBank.is_verified == True)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(ProblemBank.created_at.desc())
        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_random(
        self,
        grade: Optional[int] = None,
        difficulty: Optional[str] = None,
        topic_id: Optional[str] = None,
        global_subtopic: Optional[str] = None,
        global_topic: Optional[str] = None,
        exclude_ids: Optional[list[int]] = None,
        count: int = 5,
    ) -> list[ProblemBank]:
        """
        Gauna atsitiktinius uždavinius.

        Args:
            grade: Klasė
            difficulty: Sunkumas
            topic_id: Senas temos ID (legacy)
            global_subtopic: Potemės ID iš global_topics.py (pvz., "trupmenos")
            global_topic: Srities ID (pvz., "algebra")
            exclude_ids: ID, kuriuos praleisti
            count: Kiek uždavinių

        Returns:
            Atsitiktinių uždavinių sąrašas
        """
        query = select(ProblemBank).where(ProblemBank.is_active == True)

        conditions = []

        if grade is not None:
            conditions.append(
                and_(ProblemBank.grade_min <= grade, ProblemBank.grade_max >= grade)
            )

        if difficulty:
            diff_enum = ProblemDifficulty(difficulty)
            conditions.append(ProblemBank.difficulty == diff_enum)

        # Naujas filtravimas pagal global_subtopic (pirmenybė prieš seną topic_id)
        if global_subtopic:
            conditions.append(ProblemBank.global_subtopic == global_subtopic)
        elif global_topic:
            conditions.append(ProblemBank.global_topic == global_topic)
        elif topic_id:
            conditions.append(ProblemBank.topic_id == topic_id)

        if exclude_ids:
            conditions.append(ProblemBank.id.notin_(exclude_ids))

        if conditions:
            query = query.where(and_(*conditions))

        # Atsitiktinė tvarka
        query = query.order_by(func.random()).limit(count)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    # === Statistika ===

    async def get_stats(self) -> dict:
        """Grąžina statistiką apie uždavinių bazę."""
        # Bendras skaičius
        total_query = select(func.count(ProblemBank.id)).where(
            ProblemBank.is_active == True
        )
        total = (await self.db.execute(total_query)).scalar() or 0

        # Pagal šaltinį
        source_stats = {}
        for source in ProblemSource:
            count_query = select(func.count(ProblemBank.id)).where(
                and_(ProblemBank.source == source, ProblemBank.is_active == True)
            )
            count = (await self.db.execute(count_query)).scalar() or 0
            if count > 0:
                source_stats[source.value] = count

        # Pagal sunkumą
        difficulty_stats = {}
        for diff in ProblemDifficulty:
            count_query = select(func.count(ProblemBank.id)).where(
                and_(ProblemBank.difficulty == diff, ProblemBank.is_active == True)
            )
            count = (await self.db.execute(count_query)).scalar() or 0
            if count > 0:
                difficulty_stats[diff.value] = count

        # Pagal klases
        grade_stats = {}
        for grade in range(5, 13):
            count_query = select(func.count(ProblemBank.id)).where(
                and_(
                    ProblemBank.grade_min <= grade,
                    ProblemBank.grade_max >= grade,
                    ProblemBank.is_active == True,
                )
            )
            count = (await self.db.execute(count_query)).scalar() or 0
            if count > 0:
                grade_stats[str(grade)] = count

        # Patikrinti
        verified_query = select(func.count(ProblemBank.id)).where(
            and_(ProblemBank.is_verified == True, ProblemBank.is_active == True)
        )
        verified = (await self.db.execute(verified_query)).scalar() or 0

        return {
            "total_problems": total,
            "by_source": source_stats,
            "by_difficulty": difficulty_stats,
            "by_grade": grade_stats,
            "verified_count": verified,
            "active_count": total,
        }

    # === Importas iš HuggingFace ===

    async def import_from_huggingface(
        self,
        source: str = "gsm8k",
        limit: int = 100,
        offset: int = 0,
        split: Literal["train", "test"] = "train",
        translate: bool = True,
        generate_variations: bool = True,
        variations_count: int = 2,
        auto_offset: bool = True,
    ) -> dict:
        """
        Importuoja uždavinius iš HuggingFace ir išverčia.

        Args:
            source: "gsm8k" arba "competition_math"
            limit: Kiek uždavinių importuoti
            offset: Kiek praleisti nuo pradžios (jei auto_offset=False)
            split: Dataset split ("train" arba "test")
            translate: Ar versti su Gemini
            generate_variations: Ar generuoti variacijas
            variations_count: Kiek variacijų generuoti
            auto_offset: Ar automatiškai apskaičiuoti offset pagal esamų įrašų skaičių

        Returns:
            Importavimo statistika
        """
        logger.info(f"Pradedamas importas iš {source} ({split}), limit={limit}")

        stats = {
            "source": source,
            "split": split,
            "requested": limit,
            "fetched": 0,
            "translated": 0,
            "variations": 0,
            "saved": 0,
            "skipped": 0,
            "errors": 0,
            "loaded": 0,  # Alias for saved
            "error_details": [],
        }

        # Nustatyti offset
        if auto_offset:
            # Suskaičiuoti kiek jau yra iš šio šaltinio
            source_enum_map = {
                "gsm8k": ProblemSource.GSM8K,
                "competition_math": ProblemSource.COMPETITION_MATH,
                "geometry": ProblemSource.GEOMETRY,
                "numina_math": ProblemSource.NUMINA_MATH,
                "math_instruct": ProblemSource.MATH_INSTRUCT,
                "amps": ProblemSource.AMPS,
                "aops": ProblemSource.AOPS,
                "open_math": ProblemSource.OPEN_MATH,
                "metamath": ProblemSource.METAMATH,
                "kaggle_math": ProblemSource.KAGGLE_MATH,
            }
            source_enum = source_enum_map.get(source, ProblemSource.GSM8K)
            existing_count_query = select(func.count(ProblemBank.id)).where(
                ProblemBank.source == source_enum
            )
            existing_count = (await self.db.execute(existing_count_query)).scalar() or 0
            actual_offset = existing_count + offset
            logger.info(
                f"Jau yra {existing_count} uždavinių iš {source}, pradedame nuo {actual_offset}"
            )
        else:
            actual_offset = offset

        # Gauti raw uždavinius su offset
        if source == "gsm8k":
            raw_problems = list(
                self.loader.load_gsm8k(
                    split=split, limit=limit, offset=actual_offset, use_cache=False
                )
            )
        elif source == "competition_math":
            raw_problems = list(
                self.loader.load_competition_math(
                    split=split, limit=limit, offset=actual_offset, use_cache=False
                )
            )
        elif source == "geometry":
            raw_problems = list(
                self.loader.load_geometry(
                    split=split, limit=limit, offset=actual_offset, use_cache=False
                )
            )
        elif source == "numina_math":
            raw_problems = list(
                self.loader.load_numina_math(
                    limit=limit, offset=actual_offset, use_cache=False
                )
            )
        elif source == "math_instruct":
            raw_problems = list(
                self.loader.load_math_instruct(
                    limit=limit, offset=actual_offset, use_cache=False
                )
            )
        elif source == "amps":
            raw_problems = list(
                self.loader.load_amps(
                    limit=limit, offset=actual_offset, use_cache=False
                )
            )
        elif source == "aops":
            raw_problems = list(
                self.loader.load_aops(
                    limit=limit, offset=actual_offset, use_cache=False
                )
            )
        elif source == "open_math":
            raw_problems = list(
                self.loader.load_open_math(
                    limit=limit, offset=actual_offset, use_cache=False
                )
            )
        elif source == "metamath":
            raw_problems = list(
                self.loader.load_metamath(
                    limit=limit, offset=actual_offset, use_cache=False
                )
            )
        elif source == "kaggle_math":
            raw_problems = list(
                self.loader.load_kaggle_math(
                    limit=limit, offset=actual_offset, use_cache=False
                )
            )
        else:
            logger.error(f"Nežinomas šaltinis: {source}")
            return stats

        stats["fetched"] = len(raw_problems)
        logger.info(f"Gauta {len(raw_problems)} uždavinių iš {source}")

        for raw in raw_problems:
            try:
                # Tikrinti ar jau egzistuoja
                existing = await self.get_by_source_id(raw.source_id)
                if existing:
                    stats["skipped"] += 1
                    continue

                # Versti
                if translate:
                    translated = await self.translator.translate(raw)
                    stats["translated"] += 1
                else:
                    # Sukurti be vertimo
                    translated = TranslatedProblem(
                        question_lt=raw.question,
                        question_en=raw.question,
                        answer=raw.answer,
                        answer_latex=None,
                        solution_steps=raw.solution.split("\n") if raw.solution else [],
                        difficulty=raw.difficulty,
                        grade_min=raw.estimated_grade_min,
                        grade_max=raw.estimated_grade_max,
                        source=raw.source,
                        source_id=raw.source_id,
                        tags=["needs_translation"],
                    )

                # Išsaugoti pagrindinį
                await self.create(translated)
                stats["saved"] += 1

                # Generuoti variacijas
                if generate_variations and translate:
                    variations = await self.translator.generate_variations(
                        translated, count=variations_count
                    )

                    for var in variations:
                        await self.create(var)
                        stats["variations"] += 1
                        stats["saved"] += 1

            except Exception as e:
                error_msg = f"{raw.source_id}: {str(e)[:100]}"
                logger.error(f"Klaida importuojant {error_msg}")
                stats["errors"] += 1
                stats["error_details"].append(error_msg)

        # Alias for compatibility
        stats["loaded"] = stats["saved"]

        logger.info(f"Importas baigtas: {stats}")
        return stats

    async def mark_as_verified(self, problem_id: int) -> bool:
        """Pažymi uždavinį kaip patikrintą."""
        return await self.update(problem_id, is_verified=True) is not None

    async def increment_usage(self, problem_id: int) -> None:
        """Padidina panaudojimo skaitiklį."""
        problem = await self.get_by_id(problem_id)
        if problem:
            problem.times_used += 1
            await self.db.commit()


# Factory function
async def get_problem_bank_service(db: AsyncSession) -> ProblemBankService:
    """Sukuria ProblemBankService instanciją."""
    return ProblemBankService(db)
