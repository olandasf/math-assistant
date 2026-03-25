"""
Matematinių uždavinių bankas ir šabloninis generatorius.
=========================================================

PASTABA: Šis failas yra plonas wrapper backward-compatibility palaikymui.
Tikrasis kodas yra services/problem_bank/ pakete:
  - common.py: Difficulty, MathProblem, lietuvių kalbos linksniai
  - grade_5_6.py: 5-6 klasės generatoriai
  - grade_7_8.py: 7-8 klasės generatoriai
  - grade_9_10.py: 9-10 klasės generatoriai
  - grade_11_12.py: 11-12 klasės generatoriai (VBE)
  - additional.py: stereometrija, tikimybės, kombinatorika, vektoriai
  - generator.py: MathProblemGenerator orkestratorius
"""

# Re-export everything for backward compatibility
from services.problem_bank import (  # noqa: F401
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
    Grade5_6_Generators,
    Grade7_8_Generators,
    Grade9_10_Generators,
    Grade11_12_Generators,
    AdditionalGenerators,
    MathProblemGenerator,
    get_math_problem_generator,
)
