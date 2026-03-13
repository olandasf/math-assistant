"""
HuggingFace Loader - parsiunčia matematikos uždavinių dataset'us.

Palaiko:
- gsm8k: 8500 žodinių uždavinių (6-8 klasė)
- competition_math: olimpiadiniai (10-12 klasė)
- geometry: geometrijos uždaviniai (9-12 klasė)
- numina_math: olimpiadiniai su CoT (8-12 klasė)
- math_instruct: įvairūs matematikos uždaviniai (6-12 klasė)
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Literal, Optional

from loguru import logger

# Cache direktorija
CACHE_DIR = Path(__file__).parent.parent / "data" / "huggingface_cache"


@dataclass
class RawProblem:
    """Neapdorotas uždavinys iš HuggingFace."""

    source: str  # "gsm8k" arba "competition_math"
    source_id: str  # Index arba ID
    question: str  # Uždavinio tekstas (EN)
    answer: str  # Atsakymas
    solution: Optional[str]  # Sprendimo žingsniai
    difficulty: str  # "easy", "medium", "hard", "olympiad"
    estimated_grade_min: int  # Numatoma min klasė
    estimated_grade_max: int  # Numatoma max klasė
    category: Optional[str] = None  # Kategorija (competition_math)


class HuggingFaceLoader:
    """
    Parsiunčia ir kešuoja HuggingFace matematinius dataset'us.

    Naudojimas:
        loader = HuggingFaceLoader()
        for problem in loader.load_gsm8k(limit=100):
            print(problem.question)
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Inicializuoja loaderį.

        Args:
            cache_dir: Kešo direktorija (default: backend/data/huggingface_cache)
        """
        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._datasets_available = self._check_datasets_library()

    def _check_datasets_library(self) -> bool:
        """Tikrina ar įdiegta 'datasets' biblioteka."""
        try:
            import datasets

            return True
        except ImportError:
            logger.warning(
                "HuggingFace 'datasets' biblioteka neįdiegta. "
                "Naudokite: pip install datasets"
            )
            return False

    def load_gsm8k(
        self,
        split: Literal["train", "test"] = "train",
        limit: Optional[int] = None,
        offset: int = 0,
        use_cache: bool = True,
    ) -> Iterator[RawProblem]:
        """
        Užkrauna GSM8K dataset'ą (Grade School Math 8K).

        8500 aukštos kokybės žodinių uždavinių su step-by-step sprendimais.
        Tinka 6-8 klasei.

        Args:
            split: "train" (7473) arba "test" (1319)
            limit: Maksimalus uždavinių skaičius
            offset: Kiek uždavinių praleisti nuo pradžios
            use_cache: Ar naudoti lokalų kešą

        Yields:
            RawProblem objektai
        """
        cache_file = self.cache_dir / f"gsm8k_{split}.json"

        # Bandyti iš kešo
        if use_cache and cache_file.exists():
            logger.info(f"Naudojamas GSM8K kešas: {cache_file}")
            yield from self._load_from_cache(cache_file, limit, offset)
            return

        if not self._datasets_available:
            logger.error("Negalima užkrauti GSM8K - trūksta 'datasets' bibliotekos")
            return

        # Parsisiųsti iš HuggingFace
        logger.info(f"Parsiunčiamas GSM8K dataset'as ({split})...")

        from datasets import load_dataset

        try:
            dataset = load_dataset("gsm8k", "main", split=split)
        except Exception as e:
            logger.error(f"Klaida siunčiant GSM8K: {e}")
            return

        problems = []
        count = 0
        skipped = 0

        for idx, item in enumerate(dataset):
            # Praleisti offset elementų
            if skipped < offset:
                skipped += 1
                continue

            if limit and count >= limit:
                break

            # Ištraukti atsakymą iš sprendimo
            answer_text = item.get("answer", "")
            # GSM8K formatas: "...#### 42" - atsakymas po ####
            answer = self._extract_gsm8k_answer(answer_text)
            solution_steps = self._extract_gsm8k_steps(answer_text)

            # Nustatyti sunkumą pagal žingsnių skaičių
            steps_count = len(solution_steps)
            if steps_count <= 2:
                difficulty = "easy"
                grade_min, grade_max = 5, 6
            elif steps_count <= 4:
                difficulty = "medium"
                grade_min, grade_max = 6, 7
            else:
                difficulty = "hard"
                grade_min, grade_max = 7, 8

            problem = RawProblem(
                source="gsm8k",
                source_id=f"gsm8k_{split}_{idx}",
                question=item.get("question", ""),
                answer=answer,
                solution="\n".join(solution_steps),
                difficulty=difficulty,
                estimated_grade_min=grade_min,
                estimated_grade_max=grade_max,
            )

            problems.append(problem)
            count += 1
            yield problem

        # Išsaugoti į kešą
        if use_cache and problems:
            self._save_to_cache(cache_file, problems)

    def load_competition_math(
        self,
        split: Literal["train", "test"] = "train",
        limit: Optional[int] = None,
        offset: int = 0,
        use_cache: bool = True,
    ) -> Iterator[RawProblem]:
        """
        Užkrauna MATH Competition dataset'ą.

        Olimpiadiniai uždaviniai, tinka 10-12 klasei ir A lygiui.

        Args:
            split: "train" arba "test"
            limit: Maksimalus uždavinių skaičius
            use_cache: Ar naudoti lokalų kešą

        Yields:
            RawProblem objektai
        """
        cache_file = self.cache_dir / f"competition_math_{split}.json"

        if use_cache and cache_file.exists():
            logger.info(f"Naudojamas Competition Math kešas: {cache_file}")
            yield from self._load_from_cache(cache_file, limit)
            return

        if not self._datasets_available:
            logger.error(
                "Negalima užkrauti Competition Math - trūksta 'datasets' bibliotekos"
            )
            return

        logger.info(f"Parsiunčiamas Competition Math dataset'as ({split})...")

        from datasets import load_dataset

        # Kategorijos (subsetai) EleutherAI/hendrycks_math
        # Tinkamos mokyklai: prealgebra, algebra, geometry, number_theory
        # Sudėtingos: intermediate_algebra, precalculus, counting_and_probability
        math_subsets = [
            "prealgebra",
            "algebra",
            "geometry",
            "number_theory",
            "counting_and_probability",
            "intermediate_algebra",
            "precalculus",
        ]

        problems = []
        count = 0
        skipped = 0
        global_idx = 0

        # Kategorijos -> sunkumo mapingas
        level_to_difficulty = {
            "Level 1": "medium",
            "Level 2": "medium",
            "Level 3": "hard",
            "Level 4": "olympiad",
            "Level 5": "olympiad",
        }

        for subset in math_subsets:
            if limit and count >= limit:
                break

            try:
                # Naudojame EleutherAI kopiją (veikia be scripts)
                dataset = load_dataset(
                    "EleutherAI/hendrycks_math", subset, split=split, streaming=True
                )

                for item in dataset:
                    if limit and count >= limit:
                        break

                    # Praleidžiame offset kiekį
                    if skipped < offset:
                        skipped += 1
                        global_idx += 1
                        continue

                    level = item.get("level", "Level 3")
                    difficulty = level_to_difficulty.get(level, "hard")

                    # Olimpiadiniai - 10-12 klasė
                    if difficulty == "olympiad":
                        grade_min, grade_max = 11, 12
                    else:
                        grade_min, grade_max = 10, 11

                    # Kategorija iš subset arba item
                    category = item.get("type", subset)

                    problem = RawProblem(
                        source="competition_math",
                        source_id=f"math_{split}_{subset}_{global_idx}",
                        question=item.get("problem", ""),
                        answer=item.get("solution", ""),  # solution turi atsakymą
                        solution=item.get("solution", ""),
                        difficulty=difficulty,
                        estimated_grade_min=grade_min,
                        estimated_grade_max=grade_max,
                        category=category,
                    )

                    problems.append(problem)
                    count += 1
                    global_idx += 1
                    yield problem

            except Exception as e:
                logger.warning(f"Nepavyko užkrauti subset '{subset}': {e}")
                continue

        if use_cache and problems:
            self._save_to_cache(cache_file, problems)

    def load_geometry(
        self,
        split: Literal["train", "test"] = "test",
        limit: Optional[int] = None,
        offset: int = 0,
        use_cache: bool = True,
    ) -> Iterator[RawProblem]:
        """
        Užkrauna TIKTAI geometrijos uždavinius iš hendrycks_math.

        Tinka 9-12 klasei. Apima: trikampius, apskritimus, plotus, kampus.

        Args:
            split: "train" arba "test"
            limit: Maksimalus uždavinių skaičius
            use_cache: Ar naudoti lokalų kešą

        Yields:
            RawProblem objektai
        """
        cache_file = self.cache_dir / f"geometry_{split}.json"

        if use_cache and cache_file.exists():
            logger.info(f"Naudojamas Geometry kešas: {cache_file}")
            yield from self._load_from_cache(cache_file, limit)
            return

        if not self._datasets_available:
            logger.error("Negalima užkrauti Geometry - trūksta 'datasets' bibliotekos")
            return

        logger.info(f"Parsiunčiamas Geometry dataset'as ({split})...")

        from datasets import load_dataset

        try:
            dataset = load_dataset(
                "EleutherAI/hendrycks_math", "geometry", split=split, streaming=True
            )
        except Exception as e:
            logger.error(f"Klaida siunčiant Geometry: {e}")
            return

        level_to_difficulty = {
            "Level 1": "easy",
            "Level 2": "medium",
            "Level 3": "medium",
            "Level 4": "hard",
            "Level 5": "olympiad",
        }

        problems = []
        count = 0
        skipped = 0

        for idx, item in enumerate(dataset):
            if limit and count >= limit:
                break

            # Praleidžiame offset kiekį
            if skipped < offset:
                skipped += 1
                continue

            level = item.get("level", "Level 3")
            difficulty = level_to_difficulty.get(level, "medium")

            # Geometrija: 9-12 klasė priklausomai nuo sunkumo
            if difficulty in ("easy", "medium"):
                grade_min, grade_max = 9, 10
            else:
                grade_min, grade_max = 10, 12

            problem = RawProblem(
                source="geometry",
                source_id=f"geometry_{split}_{idx}",
                question=item.get("problem", ""),
                answer=item.get("solution", ""),
                solution=item.get("solution", ""),
                difficulty=difficulty,
                estimated_grade_min=grade_min,
                estimated_grade_max=grade_max,
                category="geometry",
            )

            problems.append(problem)
            count += 1
            yield problem

        if use_cache and problems:
            self._save_to_cache(cache_file, problems)

    def load_numina_math(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        use_cache: bool = True,
        filter_source: Optional[str] = None,
    ) -> Iterator[RawProblem]:
        """
        Užkrauna NuminaMath-CoT dataset'ą - olimpiadiniai su Chain of Thought.

        ~860K uždavinių iš įvairių šaltinių (AMC, AIME, Olympiad).
        Tinka 8-12 klasei.

        Args:
            limit: Maksimalus uždavinių skaičius
            offset: Kiek praleisti nuo pradžios
            use_cache: Ar naudoti lokalų kešą
            filter_source: Filtruoti pagal šaltinį (pvz., "amc_aime", "olympiads")

        Yields:
            RawProblem objektai
        """
        cache_name = f"numina_math{'_' + filter_source if filter_source else ''}"
        cache_file = self.cache_dir / f"{cache_name}.json"

        if use_cache and cache_file.exists():
            logger.info(f"Naudojamas NuminaMath kešas: {cache_file}")
            yield from self._load_from_cache(cache_file, limit)
            return

        if not self._datasets_available:
            logger.error(
                "Negalima užkrauti NuminaMath - trūksta 'datasets' bibliotekos"
            )
            return

        logger.info("Parsiunčiamas NuminaMath-CoT dataset'as...")

        from datasets import load_dataset

        try:
            dataset = load_dataset(
                "AI-MO/NuminaMath-CoT", split="train", streaming=True
            )
        except Exception as e:
            logger.error(f"Klaida siunčiant NuminaMath: {e}")
            return

        problems = []
        count = 0
        skipped = 0

        for idx, item in enumerate(dataset):
            if limit and count >= limit:
                break

            source_name = item.get("source", "unknown")

            # Filtruoti pagal šaltinį jei nurodyta
            if filter_source and filter_source.lower() not in source_name.lower():
                continue

            # Praleidžiame offset kiekį (po filtravimo)
            if skipped < offset:
                skipped += 1
                continue

            # Nustatyti sunkumą pagal šaltinį
            source_lower = source_name.lower()
            if (
                "aime" in source_lower
                or "usamo" in source_lower
                or "imo" in source_lower
            ):
                difficulty = "olympiad"
                grade_min, grade_max = 11, 12
            elif "amc" in source_lower:
                difficulty = "hard"
                grade_min, grade_max = 10, 11
            elif "mathd" in source_lower or "cn_k12" in source_lower:
                difficulty = "medium"
                grade_min, grade_max = 8, 10
            else:
                difficulty = "hard"
                grade_min, grade_max = 9, 11

            problem = RawProblem(
                source="numina_math",
                source_id=f"numina_{idx}",
                question=item.get("problem", ""),
                answer=item.get("solution", ""),
                solution=item.get("solution", ""),
                difficulty=difficulty,
                estimated_grade_min=grade_min,
                estimated_grade_max=grade_max,
                category=source_name,
            )

            problems.append(problem)
            count += 1
            yield problem

        if use_cache and problems:
            self._save_to_cache(cache_file, problems)

    def load_math_instruct(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        use_cache: bool = True,
        filter_source: Optional[str] = None,
    ) -> Iterator[RawProblem]:
        """
        Užkrauna MathInstruct dataset'ą - įvairūs matematikos uždaviniai.

        ~260K uždavinių instrukcijų formatu.
        Tinka 6-12 klasei.

        Args:
            limit: Maksimalus uždavinių skaičius
            offset: Kiek praleisti nuo pradžios
            use_cache: Ar naudoti lokalų kešą
            filter_source: Filtruoti pagal šaltinį

        Yields:
            RawProblem objektai
        """
        cache_name = f"math_instruct{'_' + filter_source if filter_source else ''}"
        cache_file = self.cache_dir / f"{cache_name}.json"

        if use_cache and cache_file.exists():
            logger.info(f"Naudojamas MathInstruct kešas: {cache_file}")
            yield from self._load_from_cache(cache_file, limit)
            return

        if not self._datasets_available:
            logger.error(
                "Negalima užkrauti MathInstruct - trūksta 'datasets' bibliotekos"
            )
            return

        logger.info("Parsiunčiamas MathInstruct dataset'as...")

        from datasets import load_dataset

        try:
            dataset = load_dataset(
                "TIGER-Lab/MathInstruct", split="train", streaming=True
            )
        except Exception as e:
            logger.error(f"Klaida siunčiant MathInstruct: {e}")
            return

        problems = []
        count = 0
        skipped = 0

        for idx, item in enumerate(dataset):
            if limit and count >= limit:
                break

            source_name = item.get("source", "unknown")

            if filter_source and filter_source.lower() not in source_name.lower():
                continue

            # Praleidžiame offset kiekį
            if skipped < offset:
                skipped += 1
                continue

            instruction = item.get("instruction", "")
            output = item.get("output", "")

            # Nustatyti sunkumą pagal šaltinį ir turinį
            source_lower = source_name.lower()
            if "competition" in source_lower or "olympiad" in source_lower:
                difficulty = "olympiad"
                grade_min, grade_max = 10, 12
            elif "college" in source_lower:
                difficulty = "hard"
                grade_min, grade_max = 11, 12
            elif "gsm" in source_lower or "aqua" in source_lower:
                difficulty = "medium"
                grade_min, grade_max = 6, 8
            else:
                difficulty = "medium"
                grade_min, grade_max = 7, 10

            problem = RawProblem(
                source="math_instruct",
                source_id=f"instruct_{idx}",
                question=instruction,
                answer=output,
                solution=output,
                difficulty=difficulty,
                estimated_grade_min=grade_min,
                estimated_grade_max=grade_max,
                category=source_name,
            )

            problems.append(problem)
            count += 1
            yield problem

        if use_cache and problems:
            self._save_to_cache(cache_file, problems)

    def _extract_gsm8k_answer(self, answer_text: str) -> str:
        """Ištraukia atsakymą iš GSM8K formato (po ####)."""
        if "####" in answer_text:
            parts = answer_text.split("####")
            if len(parts) > 1:
                return parts[-1].strip()
        return answer_text.strip()

    def _extract_gsm8k_steps(self, answer_text: str) -> list[str]:
        """Ištraukia sprendimo žingsnius iš GSM8K formato."""
        if "####" in answer_text:
            solution_part = answer_text.split("####")[0]
        else:
            solution_part = answer_text

        # Padalinti į eilutes, filtruoti tuščias
        lines = [line.strip() for line in solution_part.split("\n") if line.strip()]
        return lines

    def _load_from_cache(
        self, cache_file: Path, limit: Optional[int] = None, offset: int = 0
    ) -> Iterator[RawProblem]:
        """Užkrauna iš lokalaus kešo."""
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            count = 0
            for i, item in enumerate(data):
                if i < offset:
                    continue
                if limit and count >= limit:
                    break
                yield RawProblem(**item)
                count += 1

        except Exception as e:
            logger.error(f"Klaida skaitant kešą {cache_file}: {e}")

    def _save_to_cache(self, cache_file: Path, problems: list[RawProblem]) -> None:
        """Išsaugo į lokalų kešą."""
        try:
            data = [
                {
                    "source": p.source,
                    "source_id": p.source_id,
                    "question": p.question,
                    "answer": p.answer,
                    "solution": p.solution,
                    "difficulty": p.difficulty,
                    "estimated_grade_min": p.estimated_grade_min,
                    "estimated_grade_max": p.estimated_grade_max,
                    "category": p.category,
                }
                for p in problems
            ]

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"Išsaugota {len(problems)} uždavinių į {cache_file}")

        except Exception as e:
            logger.error(f"Klaida saugant kešą {cache_file}: {e}")

    def get_stats(self) -> dict:
        """Grąžina statistiką apie kešuotus dataset'us."""
        stats = {
            "cache_dir": str(self.cache_dir),
            "datasets_library_available": self._datasets_available,
            "cached_files": [],
        }

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                stats["cached_files"].append(
                    {"file": cache_file.name, "count": len(data)}
                )
            except Exception:
                pass

        return stats


# Singleton instance
_loader_instance: Optional[HuggingFaceLoader] = None


def get_huggingface_loader() -> HuggingFaceLoader:
    """Grąžina HuggingFaceLoader singleton."""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = HuggingFaceLoader()
    return _loader_instance
