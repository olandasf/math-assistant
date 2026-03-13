<p align="center">
  <h1 align="center">📐 Matematikos Mokytojo Asistentas<br><sub>Math Teacher Assistant</sub></h1>
  <p align="center">
    Moderni programa, padedanti matematikos mokytojams automatizuoti kontrolinių tikrinimą<br>
    <em>A modern tool helping math teachers automate exam grading</em>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-in%20development-yellow" alt="Status"/>
  <img src="https://img.shields.io/badge/version-0.1.0-blue" alt="Version"/>
  <img src="https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/react-18-61DAFB?logo=react&logoColor=white" alt="React"/>
  <img src="https://img.shields.io/badge/license-Private-red" alt="License"/>
</p>

---

## 🇱🇹 Lietuviškai

### 🎯 Apie projektą

Šis įrankis sukurtas **matematikos mokytojams**, padedantis:
- **Sutaupyti laiką** — vietoj ~4 val. vienos klasės kontrolinio tikrinimas užtrunka ~30–60 min
- **Pagerinti kokybę** — automatinis klaidų aptikimas ir paaiškinimų generavimas lietuvių kalba
- **Sekti progresą** — statistika pagal mokinius, klases ir temas

### ✨ Pagrindinės funkcijos

| Funkcija | Aprašymas |
|----------|-----------|
| 📷 **OCR nuskaitymas** | Ranka rašytų darbų atpažinimas (Gemini Vision / OpenAI Vision) |
| 🧮 **Matematikos tikrinimas** | Automatinis sprendimų tikrinimas (SymPy + WolframAlpha) |
| 🤖 **AI paaiškinimai** | Klaidų paaiškinimas lietuvių kalba (Google Gemini) |
| 📊 **Statistika** | Progreso sekimas pagal mokinius ir klases |
| 📄 **PDF ataskaitos** | Automatinis ataskaitų generavimas mokiniams ir klasėms |
| 📝 **Kontrolinių generavimas** | AI pagalba kuriant naujus kontrolinius darbus |
| 🔒 **GDPR** | Mokinių duomenų anonimizavimas prieš siunčiant į AI |

### 🏗️ Technologijos

```
Backend:      Python 3.11+ · FastAPI · SQLAlchemy 2.0 · SQLite
Frontend:     React 18 · TypeScript · Vite · TailwindCSS · shadcn/ui
OCR:          Gemini Vision · OpenAI Vision · Novita Vision
AI:           Google Gemini (paaiškinimai, generavimas)
Matematika:   SymPy (lokalus) · Newton API · WolframAlpha (backup)
```

### 🚀 Greitas startas

**Reikalavimai:** Windows 10/11, Python 3.11+, Node.js 18+

```batch
:: 1. Klonuoti repozitoriją
git clone https://github.com/olandasf/math-assistant.git
cd math-assistant

:: 2. Pirminis nustatymas (tik pirmą kartą)
SETUP.bat

:: 3. Paleisti programą
START.bat
```

Sistema automatiškai:
- ✅ Patikrina priklausomybes
- ✅ Paleidžia backend serverį (port 8000)
- ✅ Paleidžia frontend serverį (port 5173)
- ✅ Atidaro naršyklę

### ⚙️ Konfigūracija

Sukurkite `.env` failą iš `.env.example` ir užpildykite API raktus:

```env
# Google Gemini (OCR + AI paaiškinimai)
GOOGLE_GEMINI_API_KEY=your_gemini_key

# WolframAlpha (backup skaičiavimams)
WOLFRAM_ALPHA_APP_ID=your_wolfram_app_id
```

### 📁 Projekto struktūra

```
math-assistant/
├── backend/              # Python FastAPI serveris
│   ├── routers/          # API endpoints (14 routerių)
│   ├── models/           # SQLAlchemy modeliai (15)
│   ├── services/         # Verslo logika (19 servisų)
│   │   └── ocr/          # OCR tiekėjai (Gemini, OpenAI, Novita)
│   ├── ai/               # Google Gemini AI klientas
│   ├── math_checker/     # SymPy + WolframAlpha + Newton
│   ├── schemas/          # Pydantic schemos
│   └── utils/            # GDPR anonymizer, curriculum
├── frontend/             # React 18 aplikacija
│   └── src/
│       ├── pages/        # 15 puslapių
│       ├── components/   # UI komponentai (shadcn/ui)
│       ├── api/          # API sluoksnis (axios + React Query)
│       └── stores/       # Zustand state
├── database/             # SQLite duomenų bazė
├── docs/                 # Dokumentacija
├── SETUP.bat             # Pirminis nustatymas
├── START.bat             # Paleidimas
├── STOP.bat              # Sustabdymas
└── CHECK.bat             # Sistemos patikrinimas
```

---

## 🇬🇧 English

### 🎯 About

**Math Teacher Assistant** is a modern application designed to help math teachers automate the process of grading handwritten student exams.

**Key benefits:**
- **Save time** — reduce grading from ~4 hours to ~30–60 minutes per class
- **Improve quality** — automatic error detection with AI-generated explanations
- **Track progress** — statistics by student, class, and topic

### ✨ Features

| Feature | Description |
|---------|-------------|
| 📷 **OCR scanning** | Handwritten work recognition (Gemini Vision / OpenAI Vision) |
| 🧮 **Math verification** | Automatic solution checking (SymPy + WolframAlpha) |
| 🤖 **AI explanations** | Error explanations in Lithuanian (Google Gemini) |
| 📊 **Statistics** | Progress tracking by student and class |
| 📄 **PDF reports** | Auto-generated reports for students and classes |
| 📝 **Test generation** | AI-assisted creation of new math tests |
| 🔒 **GDPR compliance** | Student data anonymization before sending to AI |

### 🏗️ Tech Stack

```
Backend:      Python 3.11+ · FastAPI · SQLAlchemy 2.0 · SQLite
Frontend:     React 18 · TypeScript · Vite · TailwindCSS · shadcn/ui
OCR:          Gemini Vision · OpenAI Vision · Novita Vision
AI:           Google Gemini (explanations, generation)
Math:         SymPy (local) · Newton API · WolframAlpha (backup)
```

### 🚀 Quick Start

**Requirements:** Windows 10/11, Python 3.11+, Node.js 18+

```batch
:: 1. Clone the repository
git clone https://github.com/olandasf/math-assistant.git
cd math-assistant

:: 2. Initial setup (first time only)
SETUP.bat

:: 3. Start the application
START.bat
```

The system will automatically:
- ✅ Check dependencies
- ✅ Start the backend server (port 8000)
- ✅ Start the frontend dev server (port 5173)
- ✅ Open the browser

### ⚙️ Configuration

Create a `.env` file from `.env.example` and fill in your API keys:

```env
# Google Gemini (OCR + AI explanations)
GOOGLE_GEMINI_API_KEY=your_gemini_key

# WolframAlpha (backup calculations)
WOLFRAM_ALPHA_APP_ID=your_wolfram_app_id
```

### 📁 Project Structure

```
math-assistant/
├── backend/              # Python FastAPI server
│   ├── routers/          # API endpoints (14 routers)
│   ├── models/           # SQLAlchemy models (15)
│   ├── services/         # Business logic (19 services)
│   │   └── ocr/          # OCR providers (Gemini, OpenAI, Novita)
│   ├── ai/               # Google Gemini AI client
│   ├── math_checker/     # SymPy + WolframAlpha + Newton
│   ├── schemas/          # Pydantic schemas
│   └── utils/            # GDPR anonymizer, curriculum
├── frontend/             # React 18 application
│   └── src/
│       ├── pages/        # 15 pages
│       ├── components/   # UI components (shadcn/ui)
│       ├── api/          # API layer (axios + React Query)
│       └── stores/       # Zustand state management
├── database/             # SQLite database
├── docs/                 # Documentation
├── SETUP.bat             # Initial setup
├── START.bat             # Start servers
├── STOP.bat              # Stop servers
└── CHECK.bat             # System health check
```

### Manual Start

```powershell
# Terminal 1 — Backend
cd backend
.\venv\Scripts\Activate
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Open in browser: http://localhost:5173

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| `docs/PROJECT.md` | Project vision & requirements |
| `docs/TECHNICAL_SPEC.md` | Technical specifications |
| `docs/OCR_ARCHITECTURE.md` | OCR architecture |
| `docs/UI_DESIGN.md` | UI/UX design spec |
| `docs/DATABASE.md` | Database schema (15 tables) |
| `docs/API_INTEGRATIONS.md` | External API integrations |
| `docs/TASKS.md` | Task list & progress |

---

## 👤 Target User

- **Who:** Math teacher (single user)
- **Grades:** 5–8 (occasionally 10), ~150 students, 5 classes
- **Language:** 100% Lithuanian UI
- **Goal:** Reduce grading time from ~4h to ~30–60min

---

## 📄 License

This project is private and intended for personal use.

---

<p align="center"><strong>Built with ❤️ for math teachers — Sukurta su ❤️ matematikos mokytojams</strong></p>
