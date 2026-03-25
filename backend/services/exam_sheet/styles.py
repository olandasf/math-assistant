# CSS STILIAI
# ============================================================

EXAM_CSS = """
/* === PAGRINDINIS STILIUS === */
@page {
    size: A4;
    margin: 10mm;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', 'Helvetica Neue', sans-serif;
    font-size: 11pt;
    line-height: 1.4;
    color: #000;
}

/* === ALIGNMENT MARKERIAI (OCR) === */
.alignment-markers {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
    z-index: 1000;
}

.marker {
    position: absolute;
    width: 5mm;
    height: 5mm;
    background: #000;
}

.marker-tl { top: 5mm; left: 5mm; }
.marker-tr { top: 5mm; right: 5mm; }
.marker-bl { bottom: 5mm; left: 5mm; }
.marker-br { bottom: 5mm; right: 5mm; }

/* === ANTRAŠTĖ === */
.exam-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 8mm;
    padding-bottom: 4mm;
    border-bottom: 2px solid #000;
}

.header-left {
    flex: 1;
}

.header-right {
    text-align: right;
}

.exam-title {
    font-size: 16pt;
    font-weight: bold;
    margin-bottom: 2mm;
}

.exam-info {
    font-size: 9pt;
    color: #333;
}

.exam-id {
    font-family: 'Courier New', monospace;
    font-size: 10pt;
    font-weight: bold;
    padding: 2mm 4mm;
    border: 1px solid #000;
    background: #f0f0f0;
}

/* === MOKINIO INFO === */
.student-info {
    display: flex;
    gap: 10mm;
    margin-bottom: 6mm;
    padding: 3mm;
    background: #fafafa;
    border: 1px solid #ddd;
    border-radius: 2mm;
}

.info-field {
    display: flex;
    align-items: center;
    gap: 2mm;
}

.info-label {
    font-size: 9pt;
    color: #666;
}

.info-input {
    border-bottom: 1px solid #000;
    min-width: 40mm;
    height: 6mm;
}

.info-input.short {
    min-width: 20mm;
}

/* === UŽDAVINIO KORTELĖ === */
.task-card {
    border: 1px solid #000;
    border-radius: 3mm;
    margin-bottom: 5mm;
    page-break-inside: avoid;
    overflow: hidden;
}

/* Uždavinio antraštė */
.task-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2mm 4mm;
    background: #f5f5f5;
    border-bottom: 1px solid #ccc;
}

.task-number {
    font-size: 12pt;
    font-weight: bold;
    background: #000;
    color: #fff;
    padding: 1mm 3mm;
    border-radius: 2mm;
    min-width: 8mm;
    text-align: center;
}

.task-points {
    font-size: 9pt;
    color: #666;
}

/* Uždavinio tekstas */
.task-question {
    padding: 3mm 4mm;
    font-size: 11pt;
    line-height: 1.5;
    border-bottom: 1px solid #eee;
}

/* Sprendimo zona (su grid) */
.task-workspace {
    position: relative;
    min-height: 50mm;
    padding: 2mm;
}

.task-workspace.with-grid {
    background-image:
        linear-gradient(#e5e7eb 1px, transparent 1px),
        linear-gradient(90deg, #e5e7eb 1px, transparent 1px);
    background-size: 5mm 5mm;
    background-position: 0 0;
}

.workspace-label {
    position: absolute;
    top: 1mm;
    left: 2mm;
    font-size: 7pt;
    color: #999;
}

/* Atsakymo dėžutė */
.answer-section {
    display: flex;
    justify-content: flex-end;
    padding: 2mm 4mm;
    background: #fff;
    border-top: 1px solid #ccc;
}

.answer-box {
    display: flex;
    align-items: center;
    gap: 2mm;
}

.answer-label {
    font-size: 10pt;
    font-weight: bold;
}

.answer-input {
    border: 2px solid #000;
    min-width: 35mm;
    height: 10mm;
    background: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
}

.answer-input.teacher-answer {
    background: #e8f5e9;
    color: #2e7d32;
    font-weight: bold;
    font-size: 12pt;
}

/* === PORAŠTĖ === */
.exam-footer {
    position: fixed;
    bottom: 10mm;
    left: 10mm;
    right: 10mm;
    display: flex;
    justify-content: space-between;
    font-size: 8pt;
    color: #666;
    border-top: 1px solid #ccc;
    padding-top: 2mm;
}

/* === PUSLAPIO PERTRAUKIMAS === */
.page-break {
    page-break-after: always;
}

/* === VARIANTO ANTRAŠTĖ === */
.variant-header {
    text-align: center;
    font-size: 14pt;
    font-weight: bold;
    margin: 4mm 0;
    padding: 2mm;
    background: #e3f2fd;
    border: 1px solid #2196f3;
    border-radius: 2mm;
}

/* === MOKYTOJO VERSIJA === */
.teacher-badge {
    position: fixed;
    top: 15mm;
    right: 15mm;
    background: #f44336;
    color: white;
    padding: 2mm 5mm;
    font-size: 10pt;
    font-weight: bold;
    border-radius: 2mm;
    transform: rotate(15deg);
    z-index: 999;
}

/* === INSTRUKCIJOS === */
.instructions {
    margin-bottom: 5mm;
    padding: 3mm;
    background: #fff3e0;
    border: 1px solid #ff9800;
    border-radius: 2mm;
    font-size: 9pt;
}

.instructions-title {
    font-weight: bold;
    margin-bottom: 1mm;
}

.instructions-list {
    margin-left: 5mm;
}

/* === QR/BARKODO VIETA === */
.qr-placeholder {
    width: 20mm;
    height: 20mm;
    border: 1px dashed #999;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 7pt;
    color: #999;
}

/* === RESPONSIVE WORKSPACE HEIGHT === */
.workspace-small { min-height: 30mm; }
.workspace-medium { min-height: 50mm; }
.workspace-large { min-height: 70mm; }
.workspace-xlarge { min-height: 100mm; }
"""


# ============================================================
