"""
Egzaminų, testų ir užduočių generatorius
===================================================

PASTABA: Šis failas yra plonas wrapper atgaliniam suderinamumui.
Paskirstytas į smulkesnius failus esančius services/test_gen/.
- models.py: Duomenų klasės (GeneratedTask, GeneratedTest ir kt.)
- fallbacks.py: Atsarginiai offline uždavinių generatoriai
- prompts.py: Prompt'ų kūrimas AI modeliams
- generator.py: Pagrindinė TestGenerator klasė
"""

from services.test_gen.models import (  # noqa: F401
    GeneratedTask,
    GeneratedVariant,
    GeneratedTest,
)
from services.test_gen.generator import TestGenerator, get_test_generator  # noqa: F401
