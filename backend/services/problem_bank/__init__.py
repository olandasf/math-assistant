"""
Problem Bank package — matematinių uždavinių generatoriai.

Paskirstytas iš monstrinio math_problem_bank.py (3490 eilučių):
  - common.py: Difficulty, MathProblem, lietuvių kalbos linksniai
  - grade_5_6.py: 5-6 klasės generatoriai
  - grade_7_8.py: 7-8 klasės generatoriai  
  - grade_9_10.py: 9-10 klasės generatoriai
  - grade_11_12.py: 11-12 klasės generatoriai (VBE)
  - additional.py: stereometrija, tikimybės, kombinatorika, vektoriai
  - generator.py: MathProblemGenerator orchestrator
"""

# Backward-compatible imports (senasis: from services.math_problem_bank import ...)
from services.problem_bank.common import (
    Difficulty,
    MathProblem,
    DeclinedName,
    get_random_name,
    get_male_name,
    get_female_name,
    get_two_names,
    random_name,
    male_name,
    female_name,
    random_in_context,
    get_item_form,
    skaitvardis,
    daiktavardis_kilm,
    NAMES_MALE,
    NAMES_FEMALE,
    NAMES_MALE_DECLINED,
    NAMES_FEMALE_DECLINED,
    ITEMS_DECLINED,
    NOUNS_BY_NUMBER,
    CONTEXT_LIMITS,
)
from services.problem_bank.grade_5_6 import Grade5_6_Generators
from services.problem_bank.grade_7_8 import Grade7_8_Generators
from services.problem_bank.grade_9_10 import Grade9_10_Generators
from services.problem_bank.grade_11_12 import Grade11_12_Generators
from services.problem_bank.additional import AdditionalGenerators
from services.problem_bank.generator import (
    MathProblemGenerator,
    get_math_problem_generator,
)
