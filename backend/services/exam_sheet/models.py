"""
Exam Sheet Generator - OCR optimizuotas kontrolinio lapas
==========================================================
Generuoja A4 PDF su:
- 4 juodais alignment markeriais kampuose
- Card-based uždavinių layout'u
- Grid sprendimų zonoje
- Aiškiomis "Atsakymas" dėžutėmis OCR nuskaitymui
"""

import io
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

# Bandome importuoti WeasyPrint (dažnai neveikia Windows)
WEASYPRINT_AVAILABLE = False
try:
    # Išjungta dėl GTK priklausomybių problemų Windows
    # from weasyprint import CSS, HTML
    # WEASYPRINT_AVAILABLE = True
    pass
except (ImportError, OSError):
    pass

# Bandome importuoti ReportLab
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Paragraph

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Bandome importuoti QR code
try:
    import qrcode
    from qrcode.image.pil import PilImage

    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False


# ============================================================
# DATA CLASSES
# ============================================================


@dataclass
class ExamTask:
    """Vienas kontrolinio uždavinys."""

    number: str  # "1", "1a", "2b" ir t.t.
    text: str  # Uždavinio tekstas
    text_latex: Optional[str] = None  # LaTeX versija jei reikia
    points: int = 1  # Taškai
    answer: Optional[str] = None  # Teisingas atsakymas (mokytojo versijai)
    answer_latex: Optional[str] = None
    solution_hint: Optional[str] = None  # Sprendimo užuomina
    workspace_height_mm: int = (
        70  # Sprendimo zonos aukštis mm (lygtims, dalybai reikia daugiau)
    )


@dataclass
class ExamVariant:
    """Vienas kontrolinio variantas."""

    name: str  # "I", "II", "A", "B"
    tasks: List[ExamTask] = field(default_factory=list)


@dataclass
class ExamSheet:
    """Pilnas kontrolinio lapas."""

    title: str  # "Kontrolinis darbas Nr. 3"
    subject: str = "Matematika"
    topic: Optional[str] = None  # "Trupmenos"
    grade: int = 5  # Klasė
    school_year: str = "2025-2026"
    date: Optional[str] = None
    duration_minutes: int = 45
    total_points: int = 20
    variants: List[ExamVariant] = field(default_factory=list)

    # Unikalus ID (QR/barkodui)
    exam_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())

    # Layout nustatymai
    show_grid: bool = True
    show_answer_boxes: bool = True
    teacher_version: bool = False  # Su atsakymais


# ============================================================
