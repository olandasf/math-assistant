# 🧮 Math Teacher Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://react.dev/)

**An open-source AI-powered system that helps math teachers automate exam grading and exam creation for grades 5–12.** Built for the Lithuanian education system, it uses AI Vision models to recognize handwritten student work, SymPy for mathematically precise verification, and Gemini AI for student-friendly error explanations — all in Lithuanian.

### Why this matters

Math teachers in Lithuania spend **4+ hours per exam session** manually grading handwritten student work across multiple classes. This tool reduces grading time to **30–60 minutes** while providing each student with personalized AI-generated explanations of their mistakes — something impossible with manual grading at scale.

The system also generates curriculum-aligned exams using both an algorithmic problem generator (with correct Lithuanian grammar declensions built in) and AI, drawing from a bank of ~870K math problems adapted from international datasets (GSM8K, Competition Math, NuminaMath) and localized to Lithuanian cultural context.

> **Target users:** Public school math teachers in Lithuania, grades 5–12, ~150 students per teacher.

---

## 📸 Screenshots

### Dashboard
![Dashboard — statistics overview, quick actions, and recent work](docs/screenshots/dashboard.png)

### Exam Generation
![Exam generator — select grade, topic, and generation method (template or AI)](docs/screenshots/exam-generator.png)

### AI Vision OCR — Handwriting Recognition
![OCR results — scanned handwritten student work with recognized text and LaTeX formulas](docs/screenshots/ocr-results.png)

### LaTeX Editor — Side-by-side Review
![LaTeX editor — original scan alongside digitized math expressions for verification](docs/screenshots/latex-editor.png)

### Grading Results with AI Explanations
![Grading results — grade, score, error analysis, and AI-generated explanations in Lithuanian](docs/screenshots/grading-results.png)

---

## 🎯 Ką daro ši sistema? / What does this system do?

### 1. Tikrina mokinių kontrolinius darbus / Grades student exams

```
Skanuoti mokinių darbai → DI Vision OCR → Matematinis tikrinimas → Įvertinimas su paaiškinimais
```

- **DI Vision OCR** — atpažįsta ranka rašytą matematiką (Gemini Vision / OpenAI Vision / Novita Vision / Together.ai Vision)
- **SymPy + WolframAlpha** — tiksliai tikrina sprendimus ir atsakymus
- **Gemini AI** — paaiškina klaidas lietuviškai, su naudingais patarimais
- **PDF ataskaitos** — su įvertinimu, klaidų analize ir rekomendacijomis

### 2. Kuria kontrolinius darbus / Creates math exams

```
Klasė + Tema + Sudėtingumas → Uždavinių generavimas → OCR-optimizuotas PDF
```

- **Pagal LT programą** — 8 JSON failai su oficialiu matematikos turiniu (5-12 kl.)
- **Algoritminis generavimas** — 3490 eilučių generatorius su teisingais atsakymais ir lietuvių kalbos linksniavimais
- **Gemini AI generavimas** — tekstiniai uždaviniai su curriculum kontekstu
- **HuggingFace bazė** — ~870K uždavinių: GSM8K, Competition Math, NuminaMath, MathInstruct
- **Lokalizacija** — automatinis vertimas EN→LT su kultūriniu adaptavimu (vardai, valiuta, vienetai)
- **PDF su QR** — alignment markeriai, atsakymų dėžutės, variantai, mokytojo versija

---

## ✨ Key Features / Pagrindinės funkcijos

| Feature | Description |
|---------|-------------|
| 📷 **AI Vision OCR** | Recognizes handwritten student work — handles cross-outs, column calculations, mixed content |
| ✅ **Math verification** | SymPy → Newton API → WolframAlpha → Gemini AI (4-tier hierarchy) |
| 💬 **Error explanations** | AI explanations in Lithuanian with concrete solution steps |
| 📝 **Exam generation** | Based on official Lithuanian math curriculum, two generation methods |
| 📚 **Problem bank** | ~870K problems from HuggingFace + algorithmic generator with Lithuanian grammar |
| 🇱🇹 **Localization** | Automatic EN→LT translation with cultural adaptation (names, currency, units) |
| 📊 **Reports** | PDF with grades, error statistics, recommendations |
| 📄 **PDF exams** | OCR-optimized sheets with alignment markers and QR codes |
| 🔢 **LaTeX rendering** | Side-by-side KaTeX rendering for math expression review |
| 🤖 **Multi-provider OCR** | Gemini, OpenAI, Novita (Qwen), Together.ai — selectable with model dropdowns |

---

## 🛠️ Tech Stack

### Backend
| Component | Technology |
|-----------|------------|
| Framework | Python 3.11, FastAPI, Uvicorn |
| Database | SQLAlchemy 2.0, SQLite (aiosqlite) |
| Math | SymPy, Newton API, WolframAlpha |
| OCR | Gemini Vision, OpenAI Vision, Novita Vision (Qwen), Together.ai (Qwen, Llama) |
| AI | Google Gemini (explanations, generation, localization) |
| PDF | ReportLab (exam sheets), QR codes |
| Migrations | Alembic |

### Frontend
| Component | Technology |
|-----------|------------|
| Framework | React 18, TypeScript, Vite |
| UI | TailwindCSS, shadcn/ui, Radix UI |
| Math rendering | KaTeX, react-katex |
| Charts | Recharts, Lucide icons |
| HTTP | Axios |

### Data Sources
| Source | Description |
|--------|-------------|
| Lithuanian curriculum | 8 JSON files (grade_5..12.json) — official math program |
| GSM8K | 8,500 word problems (grades 6-8) |
| Competition Math | Olympiad problems (grades 10-12) |
| NuminaMath-CoT | ~860K olympiad problems with Chain of Thought (grades 8-12) |
| MathInstruct | ~260K instruction-format problems (grades 6-12) |

---

## 📁 Project Structure

```
├── backend/
│   ├── routers/          ← 14 API endpoints (classes, students, tests, OCR, ...)
│   ├── models/           ← 15 SQLAlchemy models
│   ├── services/
│   │   ├── ocr/          ← AI Vision OCR (Gemini, OpenAI, Novita, Together.ai)
│   │   ├── test_generator.py       ← Exam generation (2107 lines)
│   │   ├── math_problem_bank.py    ← Algorithmic generator (3490 lines)
│   │   ├── huggingface_loader.py   ← HuggingFace dataset loader
│   │   ├── task_translator.py      ← EN→LT localization
│   │   └── exam_sheet_generator.py ← PDF exam sheets (1284 lines)
│   ├── utils/
│   │   ├── curriculum.py           ← Lithuanian math curriculum
│   │   ├── curriculum_loader.py    ← JSON curriculum loader
│   │   └── topics.py              ← 48 math topics
│   └── math_checker/     ← SymPy + WolframAlpha + Newton API
├── frontend/
│   ├── src/pages/         ← Dashboard, Classes, Tests, Upload, Review, ...
│   ├── src/components/    ← UI components (shadcn/ui)
│   └── src/api/           ← API services
├── Matematikos programa/  ← JSON curriculum files by grade (5-12)
├── docs/                  ← Documentation + screenshots
├── database/              ← SQLite DB (not tracked)
├── uploads/               ← Student work uploads (not tracked)
└── exports/               ← Generated reports (not tracked)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- API keys: Gemini (required), WolframAlpha (recommended)

### One-command launch (Windows)

```bash
START.bat
```

This automatically installs dependencies, initializes the database, and launches both backend and frontend.

### Manual setup

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate
pip install -r requirements.txt
cp ../.env.example ../.env  # Edit with your API keys
alembic upgrade head
uvicorn main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Configuration

Copy `.env.example` to `.env` and fill in API keys:

```env
GEMINI_API_KEY=your_key_here          # Required - Google AI Studio
WOLFRAM_APP_ID=your_app_id_here       # Recommended - 2000 free/month
```

Additional OCR provider API keys (OpenAI, Novita, Together.ai) are configured through the in-app settings UI with model selection dropdowns.

---

## 📋 Why AI Vision instead of traditional OCR?

Students (grades 5–12) produce **messy handwriting**: cross-outs, corrections, column calculations, drawings mixed with formulas. Traditional OCR solutions (Tesseract, Google Cloud Vision, MathPix) fail at:

- Distinguishing cross-outs from final answers
- Understanding column long division
- Recognizing Lithuanian format ("Ats.", "Nr.", "Sprendimas:")

**AI Vision models** (Gemini, OpenAI, Novita, Together.ai) are multimodal — they understand **context**, not just symbols. Details: [`docs/OCR_ARCHITECTURE.md`](docs/OCR_ARCHITECTURE.md).

---

## 🔒 Security Notes

- 🔐 API keys stored in SQLite database (encryption recommended for production)
- 📛 Student names anonymized before sending to AI APIs
- 🚫 Authentication not yet implemented (development mode)
- 📄 GDPR compliant — personal data is never sent to third-party servers unmodified

---

## 🤝 Contributing

Contributions are welcome! Please see the [docs/](docs/) directory for technical specifications.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

*Last updated: 2026-03-15*
