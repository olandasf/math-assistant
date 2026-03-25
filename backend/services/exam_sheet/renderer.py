"""
HTML and PDF Rendering logic for Exam Sheets.
"""
import io
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger
from .models import ExamTask, ExamVariant, ExamSheet
from .styles import EXAM_CSS

# Bandome importuoti WeasyPrint (dažnai neveikia Windows)
WEASYPRINT_AVAILABLE = False
try:
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

try:
    import qrcode
    from qrcode.image.pil import PilImage

    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False



class ExamSheetGenerator:
    """Generuoja OCR-optimizuotus kontrolinių lapus."""

    EXPORTS_DIR = Path(__file__).parent.parent.parent / "exports" / "exams"

    def __init__(self):
        """Inicializuoja generatorių."""
        self.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

        if WEASYPRINT_AVAILABLE:
            self.backend = "weasyprint"
        elif REPORTLAB_AVAILABLE:
            self.backend = "reportlab"
            logger.info("Naudojamas ReportLab PDF generavimui")
        else:
            self.backend = None
            logger.warning(
                "Nei WeasyPrint, nei ReportLab neįdiegti. PDF generavimas neveiks."
            )

    def generate_html(self, exam: ExamSheet) -> str:
        """
        Generuoja HTML kontrolinio lapą.

        Args:
            exam: ExamSheet objektas

        Returns:
            HTML string
        """
        html_parts = []

        # HTML pradžia
        html_parts.append(self._html_start(exam))

        # Kiekvienam variantui
        for i, variant in enumerate(exam.variants):
            if i > 0:
                html_parts.append('<div class="page-break"></div>')

            html_parts.append(self._generate_variant_html(exam, variant))

        # HTML pabaiga
        html_parts.append(self._html_end())

        return "\n".join(html_parts)

    def generate_pdf(self, exam: ExamSheet, output_path: Optional[Path] = None) -> Path:
        """
        Generuoja PDF failą.

        Args:
            exam: ExamSheet objektas
            output_path: Išvesties kelias (optional)

        Returns:
            Path į sugeneruotą PDF
        """
        # Nustatyti išvesties kelią
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"exam_{exam.exam_id}_{timestamp}.pdf"
            output_path = self.EXPORTS_DIR / filename

        if self.backend == "weasyprint":
            html = self.generate_html(exam)
            html_doc = HTML(string=html)
            css = CSS(string=EXAM_CSS)
            html_doc.write_pdf(output_path, stylesheets=[css])
        elif self.backend == "reportlab":
            self._generate_pdf_reportlab(exam, output_path)
        else:
            raise RuntimeError("Nei WeasyPrint, nei ReportLab neįdiegti")

        logger.info(f"PDF sugeneruotas: {output_path}")
        return output_path

    def generate_pdf_bytes(self, exam: ExamSheet) -> bytes:
        """
        Generuoja PDF kaip bytes (API atsakymui).

        Args:
            exam: ExamSheet objektas

        Returns:
            PDF bytes
        """
        if self.backend == "weasyprint":
            html = self.generate_html(exam)
            html_doc = HTML(string=html)
            css = CSS(string=EXAM_CSS)
            return html_doc.write_pdf(stylesheets=[css])
        elif self.backend == "reportlab":
            buffer = io.BytesIO()
            self._generate_pdf_reportlab(exam, buffer)
            return buffer.getvalue()
        else:
            raise RuntimeError("Nei WeasyPrint, nei ReportLab neįdiegti")

    def _generate_pdf_reportlab(self, exam: ExamSheet, output) -> None:
        """
        Generuoja PDF naudojant ReportLab.

        Optimizuota autizmui/disleksijai ir OCR:
        - Open Sans šriftas (aiškus, plačios raidės)
        - Didesni šrifto dydžiai (12-14pt)
        - 1.5 eilučių tarpai
        - Kairė lygiuotė

        Args:
            exam: ExamSheet objektas
            output: Path arba BytesIO objektas
        """
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen import canvas

        # A4 matmenys
        page_width, page_height = A4
        margin = 12 * mm  # Šiek tiek didesnis margin

        # Registruojame Open Sans šriftą
        fonts_dir = Path(__file__).parent.parent / "assets" / "fonts"
        try:
            # Pirma bandome DejaVu Sans (pilnas lietuvių kalbos palaikymas)
            if (fonts_dir / "DejaVuSans.ttf").exists():
                pdfmetrics.registerFont(
                    TTFont("DejaVuSans", str(fonts_dir / "DejaVuSans.ttf"))
                )
                pdfmetrics.registerFont(
                    TTFont("DejaVuSans-Bold", str(fonts_dir / "DejaVuSans-Bold.ttf"))
                )
                FONT_REGULAR = "DejaVuSans"
                FONT_BOLD = "DejaVuSans-Bold"
                logger.debug("DejaVu Sans šriftas užregistruotas (LT palaikymas)")
            elif (fonts_dir / "OpenSans-Regular.ttf").exists():
                pdfmetrics.registerFont(
                    TTFont("OpenSans", str(fonts_dir / "OpenSans-Regular.ttf"))
                )
                pdfmetrics.registerFont(
                    TTFont("OpenSans-Bold", str(fonts_dir / "OpenSans-Bold.ttf"))
                )
                FONT_REGULAR = "OpenSans"
                FONT_BOLD = "OpenSans-Bold"
                logger.debug("Open Sans šriftas užregistruotas")
            else:
                FONT_REGULAR = "Helvetica"
                FONT_BOLD = "Helvetica-Bold"
        except Exception as e:
            logger.warning(f"Nepavyko užregistruoti šrifto: {e}")
            FONT_REGULAR = "Helvetica"
            FONT_BOLD = "Helvetica-Bold"

        # Šrifto dydžiai (didesni, draugiški autizmui/disleksijai)
        FONT_TITLE = 18  # Antraštė
        FONT_TASK_NUM = 14  # Užduoties numeris
        FONT_QUESTION = 12  # Uždavinio tekstas (ne 11!)
        FONT_INFO = 10  # Papildoma info
        FONT_SMALL = 8  # Mažas tekstas

        # Eilučių tarpai
        LINE_SPACING = 1.5

        c = canvas.Canvas(
            str(output) if isinstance(output, Path) else output, pagesize=A4
        )

        for variant_idx, variant in enumerate(exam.variants):
            if variant_idx > 0:
                c.showPage()

            # === ALIGNMENT MARKERIAI (OCR) ===
            marker_size = 5 * mm
            c.setFillColor(colors.black)
            # Top-left
            c.rect(
                5 * mm,
                page_height - 5 * mm - marker_size,
                marker_size,
                marker_size,
                fill=1,
            )
            # Top-right
            c.rect(
                page_width - 5 * mm - marker_size,
                page_height - 5 * mm - marker_size,
                marker_size,
                marker_size,
                fill=1,
            )
            # Bottom-left
            c.rect(5 * mm, 5 * mm, marker_size, marker_size, fill=1)
            # Bottom-right
            c.rect(
                page_width - 5 * mm - marker_size,
                5 * mm,
                marker_size,
                marker_size,
                fill=1,
            )

            # === ANTRAŠTĖ ===
            y = page_height - margin - 15 * mm

            # Pavadinimas (didelis, bold)
            c.setFont(FONT_BOLD, FONT_TITLE)
            c.drawString(margin, y, exam.title)
            y -= 7 * mm

            # Info (subject, grade, topic)
            c.setFont(FONT_REGULAR, FONT_INFO)
            info_text = f"{exam.subject}  •  {exam.grade} klasė"
            if exam.topic:
                info_text += f"  •  {exam.topic}"
            c.drawString(margin, y, info_text)
            y -= 5 * mm

            # Trukmė ir taškai
            c.drawString(
                margin,
                y,
                f"Trukmė: {exam.duration_minutes} min.  •  Maksimalūs taškai: {exam.total_points}",
            )

            # Exam ID dešinėje (monospace)
            c.setFont("Courier-Bold", 11)
            c.drawRightString(
                page_width - margin, page_height - margin - 15 * mm, exam.exam_id
            )

            # QR kodas su exam ID
            if QR_AVAILABLE:
                qr_size = 18 * mm
                qr_x = page_width - margin - qr_size
                qr_y = page_height - margin - 38 * mm
                self._draw_qr_code(c, exam.exam_id, qr_x, qr_y, qr_size)

            # Varianto pavadinimas (jei keli variantai)
            if len(exam.variants) > 1:
                y -= 12 * mm
                c.setFont(FONT_BOLD, 14)
                c.setFillColor(colors.HexColor("#1976d2"))
                c.drawCentredString(page_width / 2, y, f"{variant.name} variantas")
                c.setFillColor(colors.black)

            # === MOKINIO INFO LAUKAI ===
            y -= 14 * mm
            c.setFont(FONT_REGULAR, FONT_INFO)
            c.setFillColor(colors.HexColor("#333333"))

            # Vardas
            c.drawString(margin, y, "Vardas, Pavardė:")
            c.setStrokeColor(colors.black)
            c.setLineWidth(0.5)
            c.line(margin + 35 * mm, y - 1 * mm, margin + 85 * mm, y - 1 * mm)

            # Klasė
            c.drawString(margin + 90 * mm, y, "Klasė:")
            c.line(margin + 105 * mm, y - 1 * mm, margin + 125 * mm, y - 1 * mm)

            # Data
            c.drawString(margin + 130 * mm, y, "Data:")
            c.line(margin + 143 * mm, y - 1 * mm, margin + 175 * mm, y - 1 * mm)

            c.setFillColor(colors.black)

            # Linija po antrašte
            y -= 6 * mm
            c.setStrokeColor(colors.HexColor("#cccccc"))
            c.setLineWidth(1)

            c.line(margin, y, page_width - margin, y)

            # === UŽDAVINIAI (optimizuotas lapo užpildymas) ===
            y -= 8 * mm

            # Paskaičiuojame kiek vietos turime puslapyje
            first_page_start_y = y
            content_start_y = page_height - margin - 10 * mm  # Naujo puslapio pradžia
            footer_margin = margin + 20 * mm  # Vieta footeriui

            # Grupuojame uždavinius į puslapius
            task_pages = []  # [[task1, task2], [task3], ...]
            current_page_tasks = []
            current_page_y = first_page_start_y

            # Minimalūs uždavinio aukščiai (header + min workspace)
            MIN_TASK_HEIGHT = 15 * mm + 35 * mm  # Header + minimalus workspace
            TASK_GAP = 3 * mm  # Tarpas tarp uždavinių

            for task_idx, task in enumerate(variant.tasks):
                # Minimalus reikalingas aukštis
                min_task_height = MIN_TASK_HEIGHT

                # Ar telpa dar vienas uždavinys šiame puslapyje?
                remaining_space = current_page_y - footer_margin

                if remaining_space >= min_task_height:
                    # Telpa - pridedame
                    current_page_tasks.append(task)
                    current_page_y -= min_task_height + TASK_GAP
                else:
                    # Netelpa - uždarome puslapį ir pradedame naują
                    if current_page_tasks:
                        task_pages.append(current_page_tasks)
                    current_page_tasks = [task]
                    current_page_y = content_start_y - min_task_height - TASK_GAP

            # Paskutinis puslapis
            if current_page_tasks:
                task_pages.append(current_page_tasks)

            # Dabar piešiame puslapius su dinamiškai paskirstytu aukščiu
            is_first_page = True

            for page_tasks in task_pages:
                if not is_first_page:
                    c.showPage()
                    y = content_start_y
                    # Markeriai naujame puslapyje
                    c.setFillColor(colors.black)
                    c.rect(
                        5 * mm,
                        page_height - 5 * mm - marker_size,
                        marker_size,
                        marker_size,
                        fill=1,
                    )
                    c.rect(
                        page_width - 5 * mm - marker_size,
                        page_height - 5 * mm - marker_size,
                        marker_size,
                        marker_size,
                        fill=1,
                    )
                    c.rect(5 * mm, 5 * mm, marker_size, marker_size, fill=1)
                    c.rect(
                        page_width - 5 * mm - marker_size,
                        5 * mm,
                        marker_size,
                        marker_size,
                        fill=1,
                    )
                else:
                    y = first_page_start_y

                is_first_page = False

                # Paskaičiuojame dinamišką aukštį kiekvienam uždaviniui
                num_tasks = len(page_tasks)
                available_height = y - footer_margin
                total_gaps = (num_tasks - 1) * TASK_GAP
                height_per_task = (available_height - total_gaps) / num_tasks

                # Užtikriname minimalų aukštį
                height_per_task = max(height_per_task, MIN_TASK_HEIGHT)

                for task in page_tasks:
                    # Naudojame dinamišką aukštį (ne task.workspace_height_mm)
                    task_height = height_per_task
                    header_height = 8 * mm
                    question_space = 15 * mm  # Klausimo tekstui
                    answer_box_height = 12 * mm
                    workspace_height = (
                        task_height - header_height - question_space - answer_box_height
                    )

                    card_top = y
                    card_width = page_width - 2 * margin

                    # Kortelės rėmelis
                    c.setStrokeColor(colors.black)
                    c.setLineWidth(1)
                    c.roundRect(
                        margin, y - task_height, card_width, task_height, 3 * mm
                    )

                    # Header (su fonu)
                    c.setFillColor(colors.HexColor("#f5f5f5"))
                    c.rect(
                        margin,
                        y - header_height,
                        card_width,
                        header_height,
                        fill=1,
                        stroke=0,
                    )
                    c.line(
                        margin,
                        y - header_height,
                        margin + card_width,
                        y - header_height,
                    )

                    # Task number
                    c.setFillColor(colors.black)
                    c.setFont(FONT_BOLD, FONT_TASK_NUM)
                    num_box_size = 7 * mm
                    c.rect(
                        margin + 2 * mm,
                        y - header_height + 1 * mm,
                        num_box_size,
                        num_box_size - 1 * mm,
                        fill=1,
                    )
                    c.setFillColor(colors.white)
                    c.drawCentredString(
                        margin + 2 * mm + num_box_size / 2,
                        y - header_height + 2 * mm,
                        task.number,
                    )

                    # Points
                    c.setFillColor(colors.gray)
                    c.setFont(FONT_REGULAR, FONT_INFO)
                    c.drawRightString(
                        margin + card_width - 2 * mm,
                        y - header_height + 2 * mm,
                        f"({task.points} tšk.)",
                    )

                    # Question text
                    c.setFillColor(colors.black)
                    c.setFont(FONT_REGULAR, FONT_QUESTION)
                    question_y = y - header_height - 5 * mm
                    # Supaprastintas teksto rodymas (pašalinti HTML)
                    clean_text = task.text.replace("<strong>", "").replace(
                        "</strong>", ""
                    )
                    c.drawString(
                        margin + 4 * mm, question_y, clean_text[:80]
                    )  # Pirmos 80 simbolių
                    if len(clean_text) > 80:
                        c.drawString(
                            margin + 4 * mm, question_y - 4 * mm, clean_text[80:160]
                        )

                    # Workspace zona su grid
                    workspace_top = question_y - 10 * mm
                    workspace_bottom = workspace_top - workspace_height

                    # Grid linijos
                    c.setStrokeColor(colors.HexColor("#e5e7eb"))
                    c.setLineWidth(0.5)
                    grid_step = 5 * mm

                    # Horizontalios
                    grid_y = workspace_top
                    while grid_y > workspace_bottom:
                        c.line(
                            margin + 2 * mm,
                            grid_y,
                            margin + card_width - 2 * mm,
                            grid_y,
                        )
                        grid_y -= grid_step

                    # Vertikalios
                    grid_x = margin + 2 * mm
                    while grid_x < margin + card_width - 2 * mm:
                        c.line(grid_x, workspace_top, grid_x, workspace_bottom)
                        grid_x += grid_step

                    # "Sprendimas:" label
                    c.setFillColor(colors.HexColor("#999999"))
                    c.setFont(FONT_REGULAR, FONT_SMALL)
                    c.drawString(margin + 3 * mm, workspace_top - 3 * mm, "Sprendimas:")

                    # Answer box
                    answer_box_width = 35 * mm
                    answer_x = margin + card_width - answer_box_width - 4 * mm
                    answer_y = y - task_height + 2 * mm

                    c.setStrokeColor(colors.black)
                    c.setLineWidth(2)
                    c.rect(answer_x, answer_y, answer_box_width, 10 * mm)

                    c.setFillColor(colors.black)
                    c.setFont(FONT_BOLD, FONT_INFO)
                    c.drawRightString(
                        answer_x - 2 * mm, answer_y + 3 * mm, "Atsakymas:"
                    )

                    # Jei mokytojo versija - parodyti atsakymą
                    if exam.teacher_version and task.answer:
                        c.setFillColor(colors.HexColor("#2e7d32"))
                        c.setFont(FONT_BOLD, FONT_QUESTION)
                        c.drawCentredString(
                            answer_x + answer_box_width / 2,
                            answer_y + 3 * mm,
                            task.answer,
                        )

                    c.setFillColor(colors.black)
                    y -= task_height + TASK_GAP

            # === FOOTER ===
            c.setFont(FONT_REGULAR, FONT_SMALL)
            c.setFillColor(colors.gray)
            c.drawString(margin, 12 * mm, f"ID: {exam.exam_id}")
            c.drawRightString(page_width - margin, 12 * mm, f"{exam.school_year} m.m.")

        c.save()

    def _draw_qr_code(self, c, data: str, x: float, y: float, size: float) -> None:
        """
        Piešia QR kodą PDF dokumente.

        Args:
            c: ReportLab canvas
            data: Duomenys QR kodui
            x, y: Pozicija (bottom-left)
            size: QR kodo dydis
        """
        if not QR_AVAILABLE:
            return

        try:
            from PIL import Image as PILImage
            from reportlab.lib.utils import ImageReader

            # Sukurti QR kodą
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=1,
            )
            qr.add_data(data)
            qr.make(fit=True)

            # Konvertuoti į PIL Image
            qr_img = qr.make_image(fill_color="black", back_color="white")

            # Konvertuoti į bytes
            img_buffer = io.BytesIO()
            qr_img.save(img_buffer, format="PNG")
            img_buffer.seek(0)

            # Piešti PDF
            img_reader = ImageReader(img_buffer)
            c.drawImage(img_reader, x, y, width=size, height=size)

        except Exception as e:
            logger.warning(f"Nepavyko sugeneruoti QR kodo: {e}")
            # Piešti placeholder
            c.setStrokeColor(colors.gray)
            c.setLineWidth(0.5)
            c.rect(x, y, size, size)
            c.setFont("Helvetica", 6)
            c.setFillColor(colors.gray)
            c.drawCentredString(x + size / 2, y + size / 2, "QR")

    # ============================================================
    # PRIVATE METODAI
    # ============================================================

    def _html_start(self, exam: ExamSheet) -> str:
        """HTML dokumento pradžia."""
        teacher_badge = ""
        if exam.teacher_version:
            teacher_badge = '<div class="teacher-badge">MOKYTOJO VERSIJA</div>'

        return f"""<!DOCTYPE html>
<html lang="lt">
<head>
    <meta charset="UTF-8">
    <title>{exam.title}</title>
</head>
<body>
    {teacher_badge}

    <!-- Alignment markeriai OCR -->
    <div class="alignment-markers">
        <div class="marker marker-tl"></div>
        <div class="marker marker-tr"></div>
        <div class="marker marker-bl"></div>
        <div class="marker marker-br"></div>
    </div>
"""

    def _html_end(self) -> str:
        """HTML dokumento pabaiga."""
        return """
</body>
</html>"""

    def _generate_variant_html(self, exam: ExamSheet, variant: ExamVariant) -> str:
        """Generuoja vieno varianto HTML."""
        parts = []

        # Antraštė
        parts.append(self._generate_header(exam, variant))

        # Mokinio info laukai
        parts.append(self._generate_student_info())

        # Instrukcijos
        parts.append(self._generate_instructions(exam))

        # Varianto pavadinimas
        if len(exam.variants) > 1:
            parts.append(f'<div class="variant-header">{variant.name} variantas</div>')

        # Uždaviniai
        for task in variant.tasks:
            parts.append(self._generate_task_card(task, exam))

        # Poraštė
        parts.append(self._generate_footer(exam))

        return "\n".join(parts)

    def _generate_header(self, exam: ExamSheet, variant: ExamVariant) -> str:
        """Generuoja antraštę."""
        date_str = exam.date or datetime.now().strftime("%Y-%m-%d")

        return f"""
    <div class="exam-header">
        <div class="header-left">
            <div class="exam-title">{exam.title}</div>
            <div class="exam-info">
                {exam.subject} | {exam.grade} klasė | {exam.topic or ""}
            </div>
            <div class="exam-info">
                Trukmė: {exam.duration_minutes} min. | Maks. taškai: {exam.total_points}
            </div>
        </div>
        <div class="header-right">
            <div class="exam-id">{exam.exam_id}</div>
            <div class="qr-placeholder">QR</div>
            <div class="exam-info" style="margin-top: 2mm;">{date_str}</div>
        </div>
    </div>
"""

    def _generate_student_info(self) -> str:
        """Generuoja mokinio info laukus."""
        return """
    <div class="student-info">
        <div class="info-field">
            <span class="info-label">Vardas, Pavardė:</span>
            <span class="info-input"></span>
        </div>
        <div class="info-field">
            <span class="info-label">Klasė:</span>
            <span class="info-input short"></span>
        </div>
        <div class="info-field">
            <span class="info-label">Data:</span>
            <span class="info-input short"></span>
        </div>
    </div>
"""

    def _generate_instructions(self, exam: ExamSheet) -> str:
        """Generuoja instrukcijas."""
        return """
    <div class="instructions">
        <div class="instructions-title">📝 Instrukcijos:</div>
        <div class="instructions-list">
            • Sprendimą rašykite pildomoje zonoje (su tinkleliu)<br>
            • <strong>Galutinį atsakymą</strong> įrašykite į "Atsakymas" langelį<br>
            • Rašykite aiškiai ir įskaitomai
        </div>
    </div>
"""

    def _generate_task_card(self, task: ExamTask, exam: ExamSheet) -> str:
        """Generuoja uždavinio kortelę."""
        # Workspace dydis
        workspace_class = "task-workspace"
        if exam.show_grid:
            workspace_class += " with-grid"

        if task.workspace_height_mm <= 35:
            workspace_class += " workspace-small"
        elif task.workspace_height_mm <= 55:
            workspace_class += " workspace-medium"
        elif task.workspace_height_mm <= 85:
            workspace_class += " workspace-large"
        else:
            workspace_class += " workspace-xlarge"

        # Atsakymo dėžutė
        answer_content = ""
        answer_class = "answer-input"
        if exam.teacher_version and task.answer:
            answer_content = task.answer_latex or task.answer
            answer_class += " teacher-answer"

        return f"""
    <div class="task-card">
        <div class="task-header">
            <span class="task-number">{task.number}</span>
            <span class="task-points">({task.points} tšk.)</span>
        </div>
        <div class="task-question">
            {task.text}
        </div>
        <div class="{workspace_class}" style="min-height: {task.workspace_height_mm}mm;">
            <span class="workspace-label">Sprendimas:</span>
        </div>
        <div class="answer-section">
            <div class="answer-box">
                <span class="answer-label">Atsakymas:</span>
                <div class="{answer_class}">{answer_content}</div>
            </div>
        </div>
    </div>
"""

    def _generate_footer(self, exam: ExamSheet) -> str:
        """Generuoja poraštę."""
        return f"""
    <div class="exam-footer">
        <span>ID: {exam.exam_id}</span>
        <span>{exam.school_year} m.m.</span>
        <span>Puslapis 1</span>
    </div>
"""


# ============================================================


def create_sample_exam() -> ExamSheet:
    """Sukuria pavyzdinį kontrolinį testavimui."""
    tasks_v1 = [
        ExamTask(
            number="1",
            text="Apskaičiuokite: <strong>125 + 347 - 89</strong>",
            points=2,
            answer="383",
            workspace_height_mm=40,
        ),
        ExamTask(
            number="2",
            text="Jonas turi 45 obuolius. Jis atidavė 12 obuolių Petrui ir 18 obuolių Marijai. Kiek obuolių liko Jonui?",
            points=3,
            answer="15",
            workspace_height_mm=50,
        ),
        ExamTask(
            number="3a",
            text="Išspręskite lygtį: <strong>x + 15 = 42</strong>",
            points=2,
            answer="x = 27",
            workspace_height_mm=70,  # Lygtims daugiau vietos sprendimui
        ),
        ExamTask(
            number="3b",
            text="Išspręskite lygtį: <strong>3x = 24</strong>",
            points=2,
            answer="x = 8",
            workspace_height_mm=70,  # Lygtims daugiau vietos sprendimui
        ),
        ExamTask(
            number="4",
            text="Stačiakampio ilgis yra 12 cm, o plotis - 8 cm. Apskaičiuokite stačiakampio plotą ir perimetrą.",
            points=4,
            answer="S = 96 cm², P = 40 cm",
            workspace_height_mm=80,  # Sudėtingiems uždaviniams daugiau vietos
        ),
    ]

    tasks_v2 = [
        ExamTask(
            number="1",
            text="Apskaičiuokite: <strong>234 + 156 - 67</strong>",
            points=2,
            answer="323",
            workspace_height_mm=40,
        ),
        ExamTask(
            number="2",
            text="Ona turi 52 saldainius. Ji atidavė 15 saldainių broliui ir 22 saldainius sesei. Kiek saldainių liko Onai?",
            points=3,
            answer="15",
            workspace_height_mm=50,
        ),
        ExamTask(
            number="3a",
            text="Išspręskite lygtį: <strong>x + 23 = 51</strong>",
            points=2,
            answer="x = 28",
            workspace_height_mm=70,  # Lygtims daugiau vietos sprendimui
        ),
        ExamTask(
            number="3b",
            text="Išspręskite lygtį: <strong>4x = 32</strong>",
            points=2,
            answer="x = 8",
            workspace_height_mm=70,  # Lygtims daugiau vietos sprendimui
        ),
        ExamTask(
            number="4",
            text="Stačiakampio ilgis yra 15 cm, o plotis - 6 cm. Apskaičiuokite stačiakampio plotą ir perimetrą.",
            points=4,
            answer="S = 90 cm², P = 42 cm",
            workspace_height_mm=80,  # Sudėtingiems uždaviniams daugiau vietos
        ),
    ]

    return ExamSheet(
        title="Kontrolinis darbas Nr. 3",
        topic="Natūralieji skaičiai ir lygtys",
        grade=5,
        duration_minutes=45,
        total_points=13,
        variants=[
            ExamVariant(name="I", tasks=tasks_v1),
            ExamVariant(name="II", tasks=tasks_v2),
        ],
    )


# ============================================================
# TESTAVIMAS
# ============================================================

if __name__ == "__main__":
    print("=== Exam Sheet Generator Test ===\n")

    # Sukurti pavyzdinį kontrolinį
    exam = create_sample_exam()
    print(f"Sukurtas: {exam.title}")
    print(f"Variantų: {len(exam.variants)}")
    print(f"Uždavinių (I var.): {len(exam.variants[0].tasks)}")
    print(
        f"Backend: {'weasyprint' if WEASYPRINT_AVAILABLE else 'reportlab' if REPORTLAB_AVAILABLE else 'none'}"
    )

    # Generuoti HTML
    generator = ExamSheetGenerator()
    html = generator.generate_html(exam)
    print(f"\nHTML ilgis: {len(html)} simbolių")

    # Išsaugoti HTML peržiūrai
    html_path = generator.EXPORTS_DIR / "test_exam.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(f"<style>{EXAM_CSS}</style>\n{html}")
    print(f"HTML išsaugotas: {html_path}")

    # Generuoti PDF
    if generator.backend:
        # Mokinio versija
        pdf_path = generator.generate_pdf(exam)
        print(f"PDF (mokinys): {pdf_path}")

        # Mokytojo versija
        exam.teacher_version = True
        exam.exam_id = exam.exam_id + "-T"
        pdf_teacher = generator.generate_pdf(exam)
        print(f"PDF (mokytojas): {pdf_teacher}")

        # Atidaryti PDF
        import os

        os.startfile(pdf_path)
    else:
        print("\n⚠️ PDF generatorius neįdiegtas")

    print("\n✅ Testas baigtas!")
