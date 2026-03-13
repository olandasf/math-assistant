# 📋 PROJEKTO SANTRAUKA (GREITAS KONTEKSTAS)

> **Šis failas yra trumpa santrauka AI asistentui greitam konteksto gavimui.**
> Jei reikia daugiau detalių - skaityk `docs/` katalogą.

---

## 🎯 KAS TAI?

**Matematikos mokytojo asistentas** — programa su dviem pagrindinėmis funkcijomis:

### 1. Kontrolinių tikrinimas (OCR → Tikrinimas → Paaiškinimas)
1. **Įkėlimas** → Skanuoti mokinių darbus (PDF / nuotraukos)
2. **DI Vision OCR** → Atpažinti ranka rašytą matematiką (Gemini / OpenAI / Novita Vision)
3. **Tikrinimas** → Palyginti su teisingais atsakymais (SymPy + WolframAlpha)
4. **Paaiškinimas** → Paaiškinti klaidas lietuviškai (Google Gemini)
5. **Ataskaita** → Generuoti PDF su įvertinimu ir paaiškinimais

### 2. Kontrolinių kūrimas (Generavimas → PDF)
1. **Temos pasirinkimas** → Pagal oficialią LT matematikos programą (5-12 kl.)
2. **Uždavinių generavimas** → Du metodai:
   - **Algoritminis** — `math_problem_bank.py` (3490 eil.) — garantuotai teisingi atsakymai, lietuvių kalbos linksniai
   - **Gemini AI** — `test_generator.py` (2107 eil.) — tekstiniai uždaviniai su curriculum kontekstu
3. **Uždavinių bazė** — HuggingFace dataset'ai (GSM8K, Competition Math, NuminaMath) + lokalizacija
4. **PDF generavimas** — OCR-optimizuoti kontroliniai su alignment markeriais, QR kodais

---

## 👤 VARTOTOJAS

- **Kas:** Matematikos mokytoja (1 žmogus)
- **Klasės:** 5-8 (kartais 10), ~150 mokinių, 5 klasės
- **Kalba:** 100% lietuvių
- **Tikslas:** Sumažinti tikrinimo laiką nuo ~4 val. iki ~30-60 min.

---

## 🛠️ TECH STACK

| Sluoksnis | Technologijos |
|-----------|---------------|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2.0, SQLite |
| **Frontend** | React 18, TypeScript, Vite, TailwindCSS, shadcn/ui |
| **Matematika** | SymPy (lokalus), Newton API (nemokamas), WolframAlpha (backup), KaTeX (renderinimas) |
| **OCR** | Gemini Vision, OpenAI Vision, Novita Vision — DI modeliai ranka rašytiems darbams |
| **AI** | Google Gemini (paaiškinimai, kontrolinių generavimas, uždavinių lokalizacija) |
| **Uždavinių bazė** | Algoritminis generatorius + HuggingFace (GSM8K, Competition Math, NuminaMath, MathInstruct) |
| **Curriculum** | Oficiali LT matematikos programa JSON formatu (8 failai, 5-12 kl.) |

### Matematikos tikrinimo hierarchija
```
SymPy → Newton API → WolframAlpha → Gemini AI
(lokalus)  (nemokamas)  (mokamas)    (semantinis)
```

### OCR pasirinkimo logika
```
Pasirinktas tiekėjas → Jei nepavyko → Gemini Vision (default)
    (gemini | openai | novita)
```

---

## 📁 STRUKTŪRA

```
d:\MATEMATIKA 2026_2\
├── docs/                    ← Visa dokumentacija (14 failų)
├── backend/                 ← Python FastAPI serveris
│   ├── routers/             ← 14 API routerių
│   ├── models/              ← 15 SQLAlchemy modelių
│   ├── services/            ← 19 servisų
│   │   ├── ocr/             ← DI Vision OCR (Gemini, OpenAI, Novita)
│   │   ├── test_generator.py       ← Kontrolinių generavimas su curriculum
│   │   ├── math_problem_bank.py    ← Algoritminis uždavinių generatorius
│   │   ├── huggingface_loader.py   ← HuggingFace dataset'ų įkroviklis
│   │   ├── task_translator.py      ← EN→LT lokalizacija su Gemini AI
│   │   └── exam_sheet_generator.py ← PDF kontrolinių lapai
│   ├── utils/
│   │   ├── curriculum.py           ← LT matematikos programa (102 KB)
│   │   ├── curriculum_loader.py    ← JSON programos įkroviklis
│   │   └── topics.py              ← 48 temų konstantos
│   └── math_checker/        ← SymPy + WolframAlpha + Newton
├── frontend/                ← React aplikacija
├── Matematikos programa/    ← JSON failai pagal klases (grade_5..12.json)
├── database/                ← SQLite duomenų bazė
├── uploads/                 ← Įkelti mokinių darbai
└── exports/                 ← Sugeneruotos PDF ataskaitos
```

---

## 📚 DOKUMENTACIJA

| Failas | Turinys |
|--------|---------|
| `docs/PROJECT.md` | Projekto vizija, reikalavimai, matematikos temos |
| `docs/TECHNICAL_SPEC.md` | Architektūra, API endpoints, failų struktūra |
| `docs/OCR_ARCHITECTURE.md` | DI Vision OCR architektūra ir motyvacija |
| `docs/UI_DESIGN.md` | Spalvos, komponentai, wireframes |
| `docs/DATABASE.md` | 15 lentelių schema su SQL |
| `docs/API_INTEGRATIONS.md` | Gemini, WolframAlpha, HuggingFace kodas |
| `docs/TASKS.md` | Užduočių sąrašas su statusais |

---

## ✅ SVARBIAUSI PRINCIPAI

1. **UI tekstai** → TIK lietuviškai
2. **Kodo komentarai** → Angliškai arba lietuviškai
3. **Kintamųjų vardai** → Angliškai
4. **Type hints** → VISADA (Python ir TypeScript)
5. **GDPR** → Mokinių vardai anonimizuojami prieš siunčiant į API
6. **OCR** → AI NIEKADA neskaičiuoja, tik transkribuoja. SymPy tikrina.

---

## 🚀 KOMANDOS

```powershell
# Backend
cd backend && .\venv\Scripts\Activate && uvicorn main:app --reload

# Frontend
cd frontend && npm run dev

# Migracija
cd backend && alembic upgrade head
```

---

## ⚡ GREITAS STARTAS

1. Perskaityk `SESSION_GUIDE.md`
2. Patikrink `docs/TASKS.md` - kur sustota
3. Pradėk nuo pirmos ☐ užduoties

---

*Paskutinis atnaujinimas: 2026-03-13*
