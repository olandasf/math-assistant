# 🧮 Matematikos Mokytojo Asistentas

> **AI sistema Lietuvos matematikos mokytojams**: automatinis kontrolinių tikrinimas ir kūrimas nuo 5 iki 12 klasės.

---

## 🎯 Ką daro ši sistema?

### 1. Tikrina mokinių kontrolinius darbus

```
Skanuoti mokinių darbai → DI Vision OCR → Matematinis tikrinimas → Įvertinimas su paaiškinimais
```

- **DI Vision OCR** — atpažįsta ranka rašytą matematiką (Gemini Vision / OpenAI Vision / Novita Vision)
- **SymPy + WolframAlpha** — tiksliai tikrina sprendimus ir atsakymus
- **Gemini AI** — paaiškina klaidas lietuviškai, su naudingais patarimais
- **PDF ataskaitos** — su įvertinimu, klaidų analize ir rekomendacijomis

### 2. Kuria kontrolinius darbus

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

## ✨ Pagrindinės funkcijos

| Funkcija | Aprašymas |
|----------|-----------|
| 📷 **DI Vision OCR** | Atpažįsta ranka rašytus mokinių darbus — supranta braukymus, stulpelinius skaičiavimus, mišrų turinį |
| ✅ **Matematinis tikrinimas** | SymPy → Newton API → WolframAlpha → Gemini AI (4 lygių hierarchija) |
| 💬 **Klaidų paaiškinimai** | AI paaiškinimai lietuviškai su konkrečiais sprendimo žingsniais |
| 📝 **Kontrolinių generavimas** | Pagal oficialią LT programą, su dviem generavimo metodais |
| 📚 **Uždavinių bazė** | ~870K uždavinių iš HuggingFace + algoritminis generatorius |
| 🇱🇹 **Lokalizacija** | Automatinis EN→LT vertimas su kultūriniu adaptavimu |
| 📊 **Ataskaitos** | PDF su įvertinimu, klaidų statistika, rekomendacijomis |
| 🔢 **LaTeX ir KaTeX** | Matematinių formulių renderinimas |
| 📄 **PDF kontroliniai** | OCR-optimizuoti lapai su alignment markeriais ir QR kodais |

---

## 🛠️ Technologijos

### Backend
| Komponentas | Technologija |
|------------|--------------|
| Framework | Python 3.11, FastAPI, Uvicorn |
| Duomenų bazė | SQLAlchemy 2.0, SQLite (aiosqlite) |
| Matematika | SymPy, Newton API, WolframAlpha |
| OCR | Gemini Vision, OpenAI Vision, Novita Vision |
| AI | Google Gemini (paaiškinimai, generavimas, lokalizacija) |
| PDF | ReportLab (kontrolinių lapai), QR kodai |
| Migracijos | Alembic |

### Frontend
| Komponentas | Technologija |
|------------|--------------|
| Framework | React 18, TypeScript, Vite |
| UI | TailwindCSS, shadcn/ui, Radix UI |
| Formulės | KaTeX, react-katex |
| Grafika | Recharts (grafikai), Lucide (ikonos) |
| HTTP | Axios |

### Duomenų šaltiniai
| Šaltinis | Aprašymas |
|----------|-----------|
| Matematikos programa | 8 JSON failai (grade_5..12.json) — oficiali LT programa |
| GSM8K | 8500 žodinių uždavinių (6-8 kl.) |
| Competition Math | Olimpiadiniai uždaviniai (10-12 kl.) |
| NuminaMath-CoT | ~860K olimpiadinių su Chain of Thought (8-12 kl.) |
| MathInstruct | ~260K įvairių uždavinių instrukcijų formatu (6-12 kl.) |

---

## 📁 Projekto struktūra

```
├── backend/
│   ├── routers/          ← 14 API endpoint'ų (klasės, mokiniai, testai, OCR, ...)
│   ├── models/           ← 15 SQLAlchemy modelių
│   ├── services/
│   │   ├── ocr/          ← DI Vision OCR (Gemini, OpenAI, Novita)
│   │   ├── test_generator.py       ← Kontrolinių generavimas (2107 eil.)
│   │   ├── math_problem_bank.py    ← Algoritminis generatorius (3490 eil.)
│   │   ├── huggingface_loader.py   ← HuggingFace dataset'ų įkroviklis
│   │   ├── task_translator.py      ← EN→LT lokalizacija
│   │   └── exam_sheet_generator.py ← PDF kontrolinių lapai (1284 eil.)
│   ├── utils/
│   │   ├── curriculum.py           ← LT matematikos programa
│   │   ├── curriculum_loader.py    ← JSON programos įkroviklis
│   │   └── topics.py              ← 48 matematikos temų
│   └── math_checker/     ← SymPy + WolframAlpha + Newton API
├── frontend/
│   ├── src/pages/         ← Dashboard, Classes, Tests, Upload, Review, ...
│   ├── src/components/    ← UI komponentai (shadcn/ui)
│   └── src/api/           ← API servisai
├── Matematikos programa/  ← JSON failai pagal klases (5-12)
├── docs/                  ← 14 dokumentacijos failų
├── database/              ← SQLite DB
├── uploads/               ← Mokinių darbai (ne git)
└── exports/               ← Sugeneruotos ataskaitos (ne git)
```

---

## 🚀 Paleidimas

### Reikalavimai
- Python 3.11+
- Node.js 18+
- API raktai: Gemini (būtinas), WolframAlpha (rekomenduojamas)

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

### Konfigūracija

Sukurkite `.env` failą `backend/` kataloge:

```env
GEMINI_API_KEY=your_key_here
WOLFRAM_ALPHA_APP_ID=your_app_id_here
DATABASE_URL=sqlite+aiosqlite:///./database/math_assistant.db
```

OCR tiekėjų API raktai konfigūruojami per programos nustatymus.

---

## 📋 Kodėl DI Vision, o ne tradicinis OCR?

Mokinių (5-12 kl.) ranka rašyti darbai yra **netvarkingi**: braukymai, taisymai, stulpeliniai skaičiavimai, piešiniai šalia formulių. Tradiciniai OCR sprendimai (Tesseract, Google Cloud Vision, MathPix) nesugeba:

- Skirti braukymą nuo galutinio atsakymo
- Suprasti stulpelinę dalybą
- Atpažinti lietuvišką formatą ("Ats.", "Nr.", "Sprendimas:")

**DI Vision modeliai** (Gemini, OpenAI, Novita) yra multimodalūs — jie supranta **kontekstą**, ne tik simbolius. Detaliau: [`docs/OCR_ARCHITECTURE.md`](docs/OCR_ARCHITECTURE.md).

---

## 🔒 Saugumo pastabos

- 🔐 API raktai saugomi SQLite duomenų bazėje (rekomenduojama šifruoti produkcijoje)
- 📛 Mokinių vardai anonimizuojami prieš siunčiant į AI API
- 🚫 Autentifikacija dar neįdiegta (development režimas)
- 📄 GDPR — asmeniniai duomenys neišsiunčiami į trečiųjų šalių serverius nepakeisti

---

## 📄 Licencija

Privatus projektas. © 2025-2026

---

# 🧮 Math Teacher Assistant

> **AI system for Lithuanian math teachers**: automatic exam grading and creation for grades 5-12.

---

## 🎯 What does this system do?

### 1. Grades student exams

```
Scanned student work → AI Vision OCR → Math verification → Report with explanations
```

- **AI Vision OCR** — recognizes handwritten math (Gemini Vision / OpenAI Vision / Novita Vision)
- **SymPy + WolframAlpha** — precisely verifies solutions and answers
- **Gemini AI** — explains errors in Lithuanian with helpful tips
- **PDF reports** — with grades, error analysis, and recommendations

### 2. Creates math exams

```
Grade + Topic + Difficulty → Problem generation → OCR-optimized PDF
```

- **Aligned with Lithuanian curriculum** — 8 JSON files with official math content (grades 5-12)
- **Algorithmic generation** — 3490-line generator with correct answers and Lithuanian grammar
- **Gemini AI generation** — word problems with curriculum context
- **HuggingFace problem bank** — ~870K problems: GSM8K, Competition Math, NuminaMath, MathInstruct
- **Localization** — automatic EN→LT translation with cultural adaptation (names, currency, units)
- **PDF with QR** — alignment markers, answer boxes, variants, teacher version

---

## ✨ Core features

| Feature | Description |
|---------|-------------|
| 📷 **AI Vision OCR** | Recognizes handwritten student work — handles cross-outs, column calculations, mixed content |
| ✅ **Math verification** | SymPy → Newton API → WolframAlpha → Gemini AI (4-tier hierarchy) |
| 💬 **Error explanations** | AI explanations in Lithuanian with concrete solution steps |
| 📝 **Exam generation** | Based on official Lithuanian math curriculum, two generation methods |
| 📚 **Problem bank** | ~870K problems from HuggingFace + algorithmic generator |
| 🇱🇹 **Localization** | Automatic EN→LT translation with cultural adaptation |
| 📊 **Reports** | PDF with grades, error statistics, recommendations |
| 📄 **PDF exams** | OCR-optimized sheets with alignment markers and QR codes |

---

## 🛠️ Tech stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy, SQLite
- **Frontend:** React 18, TypeScript, Vite, TailwindCSS, shadcn/ui
- **Math:** SymPy, Newton API, WolframAlpha, KaTeX
- **OCR:** Gemini Vision, OpenAI Vision, Novita Vision (AI Vision, not traditional OCR)
- **AI:** Google Gemini (explanations, generation, localization)
- **Data:** HuggingFace datasets, Lithuanian curriculum JSON files

---

## 📋 Why AI Vision instead of traditional OCR?

Student handwriting (grades 5-12) is **messy**: cross-outs, corrections, column calculations, drawings mixed with formulas. Traditional OCR (Tesseract, Google Cloud Vision, MathPix) fails at:

- Distinguishing cross-outs from final answers
- Understanding column long division
- Recognizing Lithuanian format ("Ats.", "Nr.", "Sprendimas:")

**AI Vision models** (Gemini, OpenAI, Novita) are multimodal — they understand **context**, not just symbols. Details: [`docs/OCR_ARCHITECTURE.md`](docs/OCR_ARCHITECTURE.md).

---

*Last updated: 2026-03-13*
