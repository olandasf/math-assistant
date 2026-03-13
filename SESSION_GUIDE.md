# 🎯 SESIJOS PRADŽIOS INSTRUKCIJA

## Kaip pradėti naują darbo sesiją

### 1️⃣ PIRMAS ŽINGSNIS: Perskaityti projekto aprašymą
```
Perskaityti: docs/PROJECT.md
```
Šis failas aprašo projekto viziją, tikslus ir bendrą architektūrą.

### 2️⃣ ANTRAS ŽINGSNIS: Peržiūrėti technines specifikacijas
```
Perskaityti: docs/TECHNICAL_SPEC.md
```
Čia rasite visas technines detales: technologijas, bibliotekas, API.

### 3️⃣ TREČIAS ŽINGSNIS: Susipažinti su UI dizainu
```
Perskaityti: docs/UI_DESIGN.md
```
Frontend dizaino specifikacijos: spalvos, komponentai, langai.

### 4️⃣ KETVIRTAS ŽINGSNIS: Peržiūrėti duomenų bazę
```
Perskaityti: docs/DATABASE.md
```
Duomenų bazės schema ir lentelių aprašymai.

### 5️⃣ PENKTAS ŽINGSNIS: Patikrinti užduočių statusą
```
Perskaityti: docs/TASKS.md
```
Užduočių sąrašas su statusais. Rasti kur sustota ir tęsti.

### 6️⃣ ŠEŠTAS ŽINGSNIS: Peržiūrėti API integracijas
```
Perskaityti: docs/API_INTEGRATIONS.md
```
Išorinių API detalės ir konfigūracijos.

---

## 📁 Projekto struktūra

```
d:\MATEMATIKA 2026\
├── 📄 SESSION_GUIDE.md          ← ŠIS FAILAS (pradėti čia!)
├── 📁 docs/                     ← Dokumentacija
│   ├── PROJECT.md               ← Projekto aprašymas
│   ├── TECHNICAL_SPEC.md        ← Techninės specifikacijos
│   ├── UI_DESIGN.md             ← UI/UX dizainas
│   ├── DATABASE.md              ← Duomenų bazės schema
│   ├── API_INTEGRATIONS.md      ← API integracijos
│   └── TASKS.md                 ← Užduotys ir progresas
├── 📁 backend/                  ← Python FastAPI serveris
├── 📁 frontend/                 ← React aplikacija
├── 📁 database/                 ← SQLite duomenų bazė
└── 📁 tests/                    ← Testai
```

---

## ⚡ Greita pradžia (jei jau pažįsti projektą)

1. Atidaryk `docs/TASKS.md`
2. Rask pirmą neatliktą užduotį (☐)
3. Pradėk darbą
4. Atlikus - pažymėk ✅ ir pridėk datą

---

## 🔧 Aplinkos paruošimas (pirmą kartą)

```powershell
# Backend
cd backend
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

---

## 🚀 Paleidimas (development)

```powershell
# Terminal 1 - Backend
cd backend
.\venv\Scripts\Activate
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

---

## 📝 Pastabos ir problemos

Jei sesijos metu kyla problemų ar yra svarbių pastabų, įrašyti čia:

| Data | Pastaba | Statusas |
|------|---------|----------|
| 2026-01-10 | Projektas pradėtas | ✅ |
| 2026-01-11 | UI dizainas pagerintas (Fury-like) | ✅ |
| 2026-01-11 | Gemini, SymPy, PDF, statistika sukurta | ✅ |
| 2026-01-12 | Newton API integruotas (nemokamas matematikos API) | ✅ |
| 2026-01-12 | Gemini modelis pakeistas į `gemini-2.5-pro-preview` | ✅ |
| 2026-01-12 | Hibridinis tikrinimo workflow: SymPy→Newton→Wolfram→Gemini | ✅ |
| 2026-01-12 | AI kontrolinių generavimas su Gemini | ✅ |

---

## 🎯 Dabartinis fokusas

**Projekto progresas: ~78% užbaigta**

✅ **Baigta:**
- Backend infrastruktūra (FastAPI, SQLAlchemy)
- Frontend UI (React, TailwindCSS, shadcn/ui)
- CRUD operacijos (mokiniai, klasės, kontroliniai)
- OCR servisai (MathPix, Google Vision, Tesseract)
- Matematikos tikrinimas (SymPy + Newton API + WolframAlpha)
- AI paaiškinimai ir kontrolinių generavimas (Gemini)
- PDF ataskaitos ir statistika

⏳ **Liko:**
- Testavimas (unit, integration, E2E)
- Vartotojo dokumentacija
- Deploy ir instaliacijos skriptas

---

**Paskutinis atnaujinimas:** 2026-01-12
