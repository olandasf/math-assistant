"""
PDF Generator - Ataskaitų generavimas
=====================================
Generuoja PDF ataskaitas mokiniams ir klasėms.
"""

import io
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# WeasyPrint išjungtas dėl GTK priklausomybių problemų Windows
WEASYPRINT_AVAILABLE = False
# try:
#     from weasyprint import CSS, HTML
#     from weasyprint.text.fonts import FontConfiguration
#     WEASYPRINT_AVAILABLE = True
# except (ImportError, OSError):
#     WEASYPRINT_AVAILABLE = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm, mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        Image,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from loguru import logger


@dataclass
class StudentResult:
    """Mokinio rezultatas."""

    student_name: str
    student_code: str
    class_name: str
    test_title: str
    test_date: str
    grade: float
    max_grade: float = 10.0
    points: float = 0.0
    max_points: float = 20.0
    tasks: List[Dict[str, Any]] = None
    errors: List[Dict[str, Any]] = None
    explanations: List[str] = None
    teacher_comments: Optional[str] = None


@dataclass
class ClassResult:
    """Klasės rezultatas."""

    class_name: str
    test_title: str
    test_date: str
    student_results: List[StudentResult]
    average_grade: float
    median_grade: float
    highest_grade: float
    lowest_grade: float
    grade_distribution: Dict[str, int]  # {"10": 2, "9": 5, ...}


class PDFGenerator:
    """PDF ataskaitų generatorius."""

    # Eksportų katalogas
    EXPORTS_DIR = Path(__file__).parent.parent.parent / "exports"

    def __init__(self):
        """Inicializuoja generatorių."""
        # Sukuriame eksportų katalogą jei nėra
        self.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

        # Nustatome kurį backend naudoti
        self.backend = None
        if WEASYPRINT_AVAILABLE:
            self.backend = "weasyprint"
        elif REPORTLAB_AVAILABLE:
            self.backend = "reportlab"
        else:
            logger.warning(
                "Nei WeasyPrint, nei ReportLab neįdiegti. PDF generavimas neveiks."
            )

    @property
    def is_available(self) -> bool:
        """Ar PDF generavimas galimas."""
        return self.backend is not None

    def _get_grade_color(self, grade: float) -> str:
        """Grąžina spalvą pagal pažymį."""
        if grade >= 9:
            return "#22c55e"  # green
        elif grade >= 7:
            return "#3b82f6"  # blue
        elif grade >= 5:
            return "#f59e0b"  # amber
        else:
            return "#ef4444"  # red

    def _generate_student_html(self, result: StudentResult) -> str:
        """Sugeneruoja HTML mokinio ataskaitai."""
        grade_color = self._get_grade_color(result.grade)

        # Užduočių lentelė
        tasks_html = ""
        if result.tasks:
            tasks_rows = ""
            for task in result.tasks:
                status_icon = "✓" if task.get("correct") else "✗"
                status_color = "#22c55e" if task.get("correct") else "#ef4444"
                tasks_rows += f"""
                <tr>
                    <td>{task.get('number', '-')}</td>
                    <td>{task.get('question', '-')[:50]}...</td>
                    <td>{task.get('student_answer', '-')}</td>
                    <td>{task.get('correct_answer', '-')}</td>
                    <td style="color: {status_color}; font-weight: bold;">{status_icon}</td>
                    <td>{task.get('points', 0)} / {task.get('max_points', 0)}</td>
                </tr>
                """

            tasks_html = f"""
            <h2>Užduočių rezultatai</h2>
            <table class="tasks-table">
                <thead>
                    <tr>
                        <th>Nr.</th>
                        <th>Užduotis</th>
                        <th>Atsakymas</th>
                        <th>Teisingas</th>
                        <th>Rezultatas</th>
                        <th>Taškai</th>
                    </tr>
                </thead>
                <tbody>
                    {tasks_rows}
                </tbody>
            </table>
            """

        # Klaidos ir paaiškinimai
        errors_html = ""
        if result.errors:
            errors_items = ""
            for error in result.errors:
                errors_items += f"""
                <div class="error-item">
                    <strong>Užduotis {error.get('task_number', '-')}:</strong>
                    <p>{error.get('explanation', 'Nėra paaiškinimo')}</p>
                </div>
                """

            errors_html = f"""
            <h2>Klaidos ir paaiškinimai</h2>
            <div class="errors-section">
                {errors_items}
            </div>
            """

        # Mokytojo komentarai
        comments_html = ""
        if result.teacher_comments:
            comments_html = f"""
            <h2>Mokytojo komentarai</h2>
            <div class="comments-section">
                <p>{result.teacher_comments}</p>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html lang="lt">
        <head>
            <meta charset="UTF-8">
            <title>Kontrolinio darbo ataskaita</title>
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                }}

                body {{
                    font-family: 'DejaVu Sans', 'Arial', sans-serif;
                    font-size: 11pt;
                    line-height: 1.4;
                    color: #333;
                }}

                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #1a3a2f;
                }}

                .header h1 {{
                    color: #1a3a2f;
                    margin: 0 0 10px 0;
                    font-size: 18pt;
                }}

                .header .subtitle {{
                    color: #666;
                    font-size: 12pt;
                }}

                .info-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin-bottom: 30px;
                }}

                .info-box {{
                    background: #f5f5f5;
                    padding: 15px;
                    border-radius: 8px;
                }}

                .info-box h3 {{
                    margin: 0 0 10px 0;
                    color: #1a3a2f;
                    font-size: 12pt;
                }}

                .info-box p {{
                    margin: 5px 0;
                }}

                .grade-box {{
                    text-align: center;
                    padding: 20px;
                    background: linear-gradient(135deg, {grade_color}22, {grade_color}11);
                    border: 2px solid {grade_color};
                    border-radius: 12px;
                }}

                .grade-box .grade {{
                    font-size: 48pt;
                    font-weight: bold;
                    color: {grade_color};
                }}

                .grade-box .label {{
                    color: #666;
                    font-size: 10pt;
                }}

                h2 {{
                    color: #1a3a2f;
                    font-size: 14pt;
                    margin-top: 30px;
                    padding-bottom: 8px;
                    border-bottom: 1px solid #ddd;
                }}

                .tasks-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 15px;
                }}

                .tasks-table th, .tasks-table td {{
                    padding: 10px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}

                .tasks-table th {{
                    background: #1a3a2f;
                    color: white;
                    font-weight: 500;
                }}

                .tasks-table tr:nth-child(even) {{
                    background: #f9f9f9;
                }}

                .error-item {{
                    background: #fff5f5;
                    border-left: 4px solid #ef4444;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 0 8px 8px 0;
                }}

                .comments-section {{
                    background: #f0f9ff;
                    border-left: 4px solid #3b82f6;
                    padding: 15px;
                    border-radius: 0 8px 8px 0;
                }}

                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    text-align: center;
                    font-size: 9pt;
                    color: #999;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Kontrolinio darbo ataskaita</h1>
                <div class="subtitle">{result.test_title}</div>
            </div>

            <div class="info-grid">
                <div class="info-box">
                    <h3>Mokinio informacija</h3>
                    <p><strong>Vardas:</strong> {result.student_name}</p>
                    <p><strong>Kodas:</strong> {result.student_code}</p>
                    <p><strong>Klasė:</strong> {result.class_name}</p>
                </div>

                <div class="grade-box">
                    <div class="grade">{result.grade:.0f}</div>
                    <div class="label">iš {result.max_grade:.0f}</div>
                    <div class="label" style="margin-top: 10px;">
                        Taškai: {result.points:.1f} / {result.max_points:.1f}
                    </div>
                </div>
            </div>

            <div class="info-box">
                <p><strong>Data:</strong> {result.test_date}</p>
            </div>

            {tasks_html}

            {errors_html}

            {comments_html}

            <div class="footer">
                Sugeneruota: {datetime.now().strftime('%Y-%m-%d %H:%M')} |
                Matematikos Mokytojo Asistentas
            </div>
        </body>
        </html>
        """

        return html

    def _generate_class_html(self, result: ClassResult) -> str:
        """Sugeneruoja HTML klasės ataskaitai."""
        # Mokinių lentelė
        students_rows = ""
        for i, student in enumerate(
            sorted(result.student_results, key=lambda x: -x.grade), 1
        ):
            grade_color = self._get_grade_color(student.grade)
            students_rows += f"""
            <tr>
                <td>{i}</td>
                <td>{student.student_name}</td>
                <td>{student.student_code}</td>
                <td style="color: {grade_color}; font-weight: bold;">{student.grade:.0f}</td>
                <td>{student.points:.1f} / {student.max_points:.1f}</td>
            </tr>
            """

        # Pažymių pasiskirstymo grafikas (supaprastintas)
        distribution_items = ""
        for grade in range(10, 0, -1):
            count = result.grade_distribution.get(str(grade), 0)
            bar_width = min(count * 30, 200)
            distribution_items += f"""
            <div class="dist-row">
                <span class="dist-grade">{grade}</span>
                <div class="dist-bar" style="width: {bar_width}px;"></div>
                <span class="dist-count">{count}</span>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html lang="lt">
        <head>
            <meta charset="UTF-8">
            <title>Klasės ataskaita</title>
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                }}

                body {{
                    font-family: 'DejaVu Sans', 'Arial', sans-serif;
                    font-size: 11pt;
                    line-height: 1.4;
                    color: #333;
                }}

                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #1a3a2f;
                }}

                .header h1 {{
                    color: #1a3a2f;
                    margin: 0 0 10px 0;
                }}

                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 15px;
                    margin-bottom: 30px;
                }}

                .stat-box {{
                    background: #f5f5f5;
                    padding: 15px;
                    border-radius: 8px;
                    text-align: center;
                }}

                .stat-box .value {{
                    font-size: 24pt;
                    font-weight: bold;
                    color: #1a3a2f;
                }}

                .stat-box .label {{
                    font-size: 10pt;
                    color: #666;
                }}

                h2 {{
                    color: #1a3a2f;
                    margin-top: 30px;
                    padding-bottom: 8px;
                    border-bottom: 1px solid #ddd;
                }}

                .students-table {{
                    width: 100%;
                    border-collapse: collapse;
                }}

                .students-table th, .students-table td {{
                    padding: 10px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}

                .students-table th {{
                    background: #1a3a2f;
                    color: white;
                }}

                .dist-row {{
                    display: flex;
                    align-items: center;
                    margin: 5px 0;
                }}

                .dist-grade {{
                    width: 30px;
                    font-weight: bold;
                }}

                .dist-bar {{
                    height: 20px;
                    background: #1a3a2f;
                    border-radius: 4px;
                    margin: 0 10px;
                }}

                .dist-count {{
                    color: #666;
                }}

                .footer {{
                    margin-top: 40px;
                    text-align: center;
                    font-size: 9pt;
                    color: #999;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{result.class_name} klasės ataskaita</h1>
                <div>{result.test_title} | {result.test_date}</div>
            </div>

            <div class="stats-grid">
                <div class="stat-box">
                    <div class="value">{result.average_grade:.1f}</div>
                    <div class="label">Vidurkis</div>
                </div>
                <div class="stat-box">
                    <div class="value">{result.median_grade:.1f}</div>
                    <div class="label">Mediana</div>
                </div>
                <div class="stat-box">
                    <div class="value">{result.highest_grade:.0f}</div>
                    <div class="label">Aukščiausias</div>
                </div>
                <div class="stat-box">
                    <div class="value">{result.lowest_grade:.0f}</div>
                    <div class="label">Žemiausias</div>
                </div>
            </div>

            <h2>Pažymių pasiskirstymas</h2>
            <div class="distribution">
                {distribution_items}
            </div>

            <h2>Mokinių rezultatai</h2>
            <table class="students-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Vardas, Pavardė</th>
                        <th>Kodas</th>
                        <th>Pažymys</th>
                        <th>Taškai</th>
                    </tr>
                </thead>
                <tbody>
                    {students_rows}
                </tbody>
            </table>

            <div class="footer">
                Sugeneruota: {datetime.now().strftime('%Y-%m-%d %H:%M')} |
                Mokinių skaičius: {len(result.student_results)}
            </div>
        </body>
        </html>
        """

        return html

    def generate_student_report(
        self, result: StudentResult, filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Sugeneruoja mokinio PDF ataskaitą.

        Args:
            result: Mokinio rezultatas
            filename: Failo pavadinimas (be .pdf)

        Returns:
            Kelias į PDF failą arba None jei nepavyko
        """
        if not self.is_available:
            logger.error("PDF generavimas negalimas - trūksta bibliotekų")
            return None

        # Failo pavadinimas
        if not filename:
            safe_name = result.student_code.replace(" ", "_")
            filename = (
                f"ataskaita_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

        filepath = self.EXPORTS_DIR / f"{filename}.pdf"

        try:
            html_content = self._generate_student_html(result)

            if self.backend == "weasyprint":
                HTML(string=html_content).write_pdf(str(filepath))
            else:
                # ReportLab alternatyva (paprastesnė)
                logger.warning(
                    "ReportLab backend dar neimplementuotas, naudokite WeasyPrint"
                )
                return None

            logger.info(f"PDF sukurtas: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Klaida generuojant PDF: {str(e)}")
            return None

    def generate_class_report(
        self, result: ClassResult, filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Sugeneruoja klasės PDF ataskaitą.

        Args:
            result: Klasės rezultatas
            filename: Failo pavadinimas

        Returns:
            Kelias į PDF failą arba None
        """
        if not self.is_available:
            logger.error("PDF generavimas negalimas")
            return None

        if not filename:
            safe_class = result.class_name.replace(" ", "_")
            filename = f"klase_{safe_class}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        filepath = self.EXPORTS_DIR / f"{filename}.pdf"

        try:
            html_content = self._generate_class_html(result)

            if self.backend == "weasyprint":
                HTML(string=html_content).write_pdf(str(filepath))
            else:
                logger.warning("ReportLab backend dar neimplementuotas")
                return None

            logger.info(f"Klasės PDF sukurtas: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Klaida generuojant klasės PDF: {str(e)}")
            return None

    def get_html_preview(self, result: StudentResult) -> str:
        """Grąžina HTML peržiūrai (be PDF generavimo)."""
        return self._generate_student_html(result)


# Singleton
_generator: Optional[PDFGenerator] = None


def get_pdf_generator() -> PDFGenerator:
    """Gauna PDF generatorių."""
    global _generator
    if _generator is None:
        _generator = PDFGenerator()
    return _generator


if __name__ == "__main__":
    # Testavimas
    print("=== PDF Generator Test ===\n")

    generator = PDFGenerator()

    if not generator.is_available:
        print("⚠️ PDF generavimas negalimas!")
        print("   Įdiekite: pip install weasyprint")
    else:
        print(f"✅ PDF backend: {generator.backend}")

        # Demo duomenys
        demo_result = StudentResult(
            student_name="Jonas Jonaitis",
            student_code="M2026001",
            class_name="5a",
            test_title="Trupmenų sudėtis ir atimtis",
            test_date="2026-01-10",
            grade=8,
            points=16,
            max_points=20,
            tasks=[
                {
                    "number": "1",
                    "question": "2/5 + 1/3",
                    "student_answer": "11/15",
                    "correct_answer": "11/15",
                    "correct": True,
                    "points": 2,
                    "max_points": 2,
                },
                {
                    "number": "2",
                    "question": "5/6 - 1/4",
                    "student_answer": "7/12",
                    "correct_answer": "7/12",
                    "correct": True,
                    "points": 2,
                    "max_points": 2,
                },
                {
                    "number": "3",
                    "question": "Suprastinkite 12/18",
                    "student_answer": "6/9",
                    "correct_answer": "2/3",
                    "correct": False,
                    "points": 1,
                    "max_points": 2,
                },
            ],
            errors=[
                {
                    "task_number": "3",
                    "explanation": "Trupmena suprastinta ne iki galo. 6/9 dar galima suprastinti iki 2/3.",
                }
            ],
            teacher_comments="Gerai sekasi su sudėtimi ir atimtimi! Atkreipk dėmesį į trupmenų suprastinimą.",
        )

        # Generuojame HTML peržiūrai
        html = generator.get_html_preview(demo_result)
        print(f"\n📄 HTML sugeneruotas ({len(html)} simbolių)")

        # Bandome generuoti PDF
        pdf_path = generator.generate_student_report(demo_result, "test_ataskaita")
        if pdf_path:
            print(f"✅ PDF sukurtas: {pdf_path}")
        else:
            print("❌ PDF generavimas nepavyko")

    print("\n✅ Testavimas baigtas!")
