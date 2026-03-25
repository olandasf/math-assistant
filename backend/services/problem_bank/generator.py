"""
Pagrindinis matematinių uždavinių generatorius.
Orkestruoja visus grade-based generatorius.
"""
import random
from typing import List, Optional

from services.problem_bank.common import Difficulty, MathProblem
from services.problem_bank.grade_5_6 import Grade5_6_Generators
from services.problem_bank.grade_7_8 import Grade7_8_Generators
from services.problem_bank.grade_9_10 import Grade9_10_Generators
from services.problem_bank.grade_11_12 import Grade11_12_Generators
from services.problem_bank.additional import AdditionalGenerators

class MathProblemGenerator:
    """
    Pagrindinis matematinių uždavinių generatorius.
    Naudoja šablonus ir algoritmus, ne AI.
    """

    # Visų generatorių registras pagal temas ir klases
    GENERATORS = {
        # 5-6 klasė
        "aritmetika": {
            "grades": [5, 6],
            "generators": [
                Grade5_6_Generators.addition_context,
                Grade5_6_Generators.subtraction_context,
                Grade5_6_Generators.multiplication_context,
                Grade5_6_Generators.division_context,
                Grade5_6_Generators.division_with_remainder,
            ],
        },
        "trupmenos": {
            "grades": [5, 6, 7],
            "generators": [
                Grade5_6_Generators.fraction_part_of_whole,
                Grade5_6_Generators.fraction_find_whole,
                Grade5_6_Generators.fraction_addition,
            ],
        },
        "procentai": {
            "grades": [6, 7, 8],
            "generators": [
                Grade5_6_Generators.percent_find_part,
                Grade5_6_Generators.percent_find_whole,
                Grade5_6_Generators.percent_discount,
                Grade5_6_Generators.percent_increase,
            ],
        },
        "geometrija_pagrindai": {
            "grades": [5, 6, 7],
            "generators": [
                Grade5_6_Generators.rectangle_perimeter,
                Grade5_6_Generators.rectangle_area,
                Grade5_6_Generators.square_perimeter_area,
                Grade5_6_Generators.triangle_area,
                Grade5_6_Generators.circle_circumference,
            ],
        },
        # 5 klasė - paprastos lygtys (TIK natūralieji skaičiai!)
        "lygtys_paprastos": {
            "grades": [5, 6],
            "generators": [
                Grade5_6_Generators.simple_equation_addition_5,
                Grade5_6_Generators.simple_equation_subtraction_5,
                Grade5_6_Generators.simple_equation_multiplication_5,
                Grade5_6_Generators.simple_equation_unknown_minuend_5,
                Grade5_6_Generators.equation_word_problem_5,
            ],
        },
        # 7-8 klasė - tiesinės lygtys (su neigiamais)
        "lygtys": {
            "grades": [7, 8],
            "generators": [
                Grade7_8_Generators.linear_equation_simple,
                Grade7_8_Generators.linear_equation_both_sides,
                Grade7_8_Generators.equation_word_problem_age,
                Grade7_8_Generators.equation_word_problem_purchase,
                Grade7_8_Generators.equation_word_problem_geometry,
            ],
        },
        "proporcijos": {
            "grades": [7, 8],
            "generators": [
                Grade7_8_Generators.ratio_simple,
                Grade7_8_Generators.proportion_direct,
                Grade7_8_Generators.proportion_inverse,
            ],
        },
        "funkcijos_pagrindai": {
            "grades": [8, 9],
            "generators": [
                Grade7_8_Generators.linear_function_value,
                Grade7_8_Generators.linear_function_zero,
            ],
        },
        # 9-10 klasė
        "kvadratines_lygtys": {
            "grades": [9, 10],
            "generators": [
                Grade9_10_Generators.quadratic_equation_simple,
                Grade9_10_Generators.quadratic_equation_factored,
                Grade9_10_Generators.quadratic_equation_incomplete,
            ],
        },
        "kvadratine_funkcija": {
            "grades": [9, 10],
            "generators": [
                Grade9_10_Generators.quadratic_function_vertex,
            ],
        },
        "trigonometrija": {
            "grades": [9, 10, 11, 12],
            "generators": [
                Grade9_10_Generators.trig_basic_values,
                Grade9_10_Generators.trig_right_triangle,
            ],
        },
        # 11-12 klasė (VBE)
        "logaritmai": {
            "grades": [10, 11, 12],
            "generators": [
                Grade11_12_Generators.logarithm_basic,
                Grade11_12_Generators.logarithm_equation,
                Grade11_12_Generators.exponential_equation,
            ],
        },
        "isvestines": {
            "grades": [11, 12],
            "generators": [
                Grade11_12_Generators.derivative_power,
                Grade11_12_Generators.derivative_polynomial,
                Grade11_12_Generators.derivative_at_point,
            ],
        },
        "progresijos": {
            "grades": [10, 11, 12],
            "generators": [
                Grade11_12_Generators.arithmetic_progression_nth,
                Grade11_12_Generators.arithmetic_progression_sum,
                Grade11_12_Generators.geometric_progression_nth,
            ],
        },
        # Papildomos temos
        "stereometrija": {
            "grades": [8, 9, 10, 11, 12],
            "generators": [
                AdditionalGenerators.rectangular_prism_volume,
                AdditionalGenerators.rectangular_prism_surface,
                AdditionalGenerators.cube_volume_surface,
                AdditionalGenerators.cylinder_volume,
                AdditionalGenerators.cone_volume,
                AdditionalGenerators.sphere_volume,
                AdditionalGenerators.pyramid_volume,
            ],
        },
        "tikimybes": {
            "grades": [8, 9, 10, 11, 12],
            "generators": [
                AdditionalGenerators.probability_simple,
                AdditionalGenerators.probability_complement,
            ],
        },
        "kombinatorika": {
            "grades": [10, 11, 12],
            "generators": [
                AdditionalGenerators.factorial_simple,
                AdditionalGenerators.permutations_simple,
                AdditionalGenerators.combinations_simple,
            ],
        },
        "vektoriai": {
            "grades": [10, 11, 12],
            "generators": [
                AdditionalGenerators.vector_addition,
                AdditionalGenerators.vector_subtraction,
                AdditionalGenerators.vector_scalar_multiplication,
                AdditionalGenerators.vector_dot_product,
                AdditionalGenerators.vector_length,
                AdditionalGenerators.vector_perpendicular_check,
            ],
        },
    }

    # Temų pavadinimai lietuviškai
    TOPIC_NAMES_LT = {
        "aritmetika": "Aritmetika",
        "trupmenos": "Trupmenos",
        "procentai": "Procentai",
        "geometrija_pagrindai": "Geometrijos pagrindai",
        "lygtys_paprastos": "Paprastos lygtys (5 kl.)",
        "lygtys": "Tiesinės lygtys",
        "proporcijos": "Proporcijos ir santykiai",
        "funkcijos_pagrindai": "Funkcijų pagrindai",
        "kvadratines_lygtys": "Kvadratinės lygtys",
        "kvadratine_funkcija": "Kvadratinė funkcija",
        "trigonometrija": "Trigonometrija",
        "logaritmai": "Logaritmai",
        "isvestines": "Išvestinės",
        "progresijos": "Progresijos",
        "stereometrija": "Stereometrija (erdvinės figūros)",
        "tikimybes": "Tikimybės",
        "kombinatorika": "Kombinatorika",
        "vektoriai": "Vektoriai",
    }

    @classmethod
    def get_topics_for_grade(cls, grade: int) -> List[str]:
        """Grąžina temas, tinkamas nurodytai klasei (įskaitant ankstesnių klasių temas)."""
        topics = []
        for topic_id, topic_data in cls.GENERATORS.items():
            if min(topic_data["grades"]) <= grade:
                topics.append(topic_id)
        return topics

    @classmethod
    def generate_problem(
        cls,
        topic: str,
        difficulty: Difficulty = Difficulty.MEDIUM,
        grade: Optional[int] = None,
    ) -> MathProblem:
        """
        Generuoja vieną uždavinį pagal temą ir sudėtingumą, atsižvelgiant į klasę.

        Args:
            topic: Temos ID (pvz., "lygtys", "trupmenos")
            difficulty: Sudėtingumo lygis
            grade: Klasė (naudojama generatorių filtravimui)

        Returns:
            MathProblem objektas
        """
        if topic not in cls.GENERATORS:
            # Bandome rasti panašią temą
            topic_lower = topic.lower()
            for t in cls.GENERATORS.keys():
                if t in topic_lower or topic_lower in t:
                    topic = t
                    break
            else:
                # Default - aritmetika
                topic = "aritmetika"

        generators = cls.GENERATORS[topic]["generators"]
        
        # Sukuriame instancijas ir ieškome labiausiai atitinkančių klasę
        best_problem = None
        
        # Pirmiausia pabandom rasti problemą išskirstyta pagal clasę
        if grade:
            # Sumaišome generatorius, kad nebūtų visada tie patys
            shuffled_generators = list(generators)
            random.shuffle(shuffled_generators)
            
            for generator in shuffled_generators:
                problem = generator(difficulty)
                if problem.grade_level == grade:
                    # Radome tobulo atitikimo
                    return problem
                
                # Saugome arčiausiai esantį kaip atsarginį variantą
                if best_problem is None or abs(problem.grade_level - grade) < abs(best_problem.grade_level - grade):
                    best_problem = problem

        # Jei nurodyta klasė, bet neradome tikslaus atitikimo, grąžiname geriausią
        if grade and best_problem:
            best_problem.grade_level = grade # priderinam rodymui
            return best_problem

        # Originalus elgesys, jei neradome jokio atitikimo ar klasė nenurodyta
        generator = random.choice(generators)
        problem = generator(difficulty)

        # Nustatom klasę jei nenurodyta
        if grade:
            problem.grade_level = grade

        return problem

    @classmethod
    def generate_test(
        cls,
        topics: List[str],
        grade: int,
        task_count: int = 5,
        difficulty: str = "medium",
        include_solutions: bool = True,
    ) -> List[MathProblem]:
        """
        Generuoja kontrolinio uždavinius.

        Args:
            topics: Temų sąrašas
            grade: Klasė
            task_count: Uždavinių kiekis
            difficulty: Sudėtingumas ("easy", "medium", "hard", "mixed")
            include_solutions: Ar įtraukti sprendimus

        Returns:
            Uždavinių sąrašas
        """
        problems = []

        # Konvertuojam difficulty
        if difficulty == "easy":
            diff = Difficulty.EASY
        elif difficulty == "hard":
            diff = Difficulty.HARD
        elif difficulty == "mixed":
            diff = None  # Bus pasirinktas atsitiktinai
        else:
            diff = Difficulty.MEDIUM

        # Filtruojam temas pagal klasę
        valid_topics = []
        for t in topics:
            t_lower = (
                t.lower()
                .replace(" ", "_")
                .replace("ė", "e")
                .replace("ų", "u")
                .replace("į", "i")
            )
            for topic_id, topic_data in cls.GENERATORS.items():
                if (topic_id in t_lower or t_lower in topic_id) and grade in topic_data["grades"]:
                    valid_topics.append(topic_id)
                    break

        if not valid_topics:
            # Jei nėra tinkamų temų, naudojam visas klasei tinkamas
            valid_topics = cls.get_topics_for_grade(grade)

        # Apskaičiuojame proporcijas A/B/C (40% / 40% / 20%) jei mixed
        if diff is None:
            a_count = round(task_count * 0.4)
            b_count = round(task_count * 0.4)
            # Tikriname, kad nebūtų 0 arba per daug
            if task_count == 1:
                a_count, b_count = 1, 0
            elif task_count <= 2:
                a_count, b_count = 1, 1
            c_count = task_count - a_count - b_count

        # Generuojam uždavinius
        for i in range(task_count):
            topic = random.choice(valid_topics) if valid_topics else "aritmetika"

            # Jei mixed - atitinkamas proporcijų sunkumas
            if diff is None:
                if i < a_count:
                    current_diff = Difficulty.EASY
                elif i < a_count + b_count:
                    current_diff = Difficulty.MEDIUM
                else:
                    current_diff = Difficulty.HARD
            else:
                current_diff = diff

            problem = cls.generate_problem(topic, current_diff, grade)
            problem.number = i + 1

            if not include_solutions:
                problem.solution_steps = []

            problems.append(problem)

        return problems

    @classmethod
    def get_all_topics(cls) -> dict:
        """Grąžina visas temas su pavadinimais."""
        return {
            topic_id: {
                "name": cls.TOPIC_NAMES_LT.get(topic_id, topic_id),
                "grades": data["grades"],
                "generator_count": len(data["generators"]),
            }
            for topic_id, data in cls.GENERATORS.items()
        }


# Singleton
_generator: Optional[MathProblemGenerator] = None


def get_math_problem_generator() -> MathProblemGenerator:
    """Gauna matematinių uždavinių generatorių."""
    global _generator
    if _generator is None:
        _generator = MathProblemGenerator()
    return _generator
