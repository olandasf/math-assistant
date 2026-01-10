# 📋 PROJEKTO SANTRAUKA (GREITAS KONTEKSTAS)

> **Šis failas yra trumpa santrauka AI asistentui greitam konteksto gavimui.**
> Jei reikia daugiau detalių - skaityk `docs/` katalogą.

---

## 🎯 KAS TAI?

**Matematikos mokytojo asistentas** - programa kontrolinių tikrinimui:

1. **Įkėlimas** → Skanuoti mokinių darbus (PDF/nuotraukos)
2. **OCR** → Atpažinti ranka rašytą matematiką (MathPix + Google Vision)
3. **Tikrinimas** → Palyginti su teisingais atsakymais (SymPy + WolframAlpha)
4. **Paaiškinimas** → Paaiškinti klaidas lietuviškai (Google Gemini)
5. **Ataskaita** → Generuoti PDF su įvertinimu ir paaiškinimais

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
| **Matematika** | SymPy, NumPy, KaTeX |
| **OCR** | MathPix API, Google Cloud Vision, Tesseract |
| **AI** | Google Gemini (paaiškinimai), WolframAlpha (tikrinimas) |

---

## 📁 STRUKTŪRA

```
d:\MATEMATIKA 2026\
├── docs/           ← Visa dokumentacija (6 failai)
├── backend/        ← Python FastAPI serveris
├── frontend/       ← React aplikacija
├── database/       ← SQLite duomenų bazė
├── uploads/        ← Įkelti mokinių darbai
└── exports/        ← Sugeneruotos PDF ataskaitos
```

---

## 📚 DOKUMENTACIJA

| Failas | Turinys |
|--------|---------|
| `docs/PROJECT.md` | Projekto vizija, reikalavimai, matematikos temos |
| `docs/TECHNICAL_SPEC.md` | Architektūra, API endpoints, failų struktūra |
| `docs/UI_DESIGN.md` | Spalvos, komponentai, wireframes |
| `docs/DATABASE.md` | 15 lentelių schema su SQL |
| `docs/API_INTEGRATIONS.md` | MathPix, Google, WolframAlpha kodas |
| `docs/TASKS.md` | **181 užduotis** su statusais |

---

## ✅ SVARBIAUSI PRINCIPAI

1. **UI tekstai** → TIK lietuviškai
2. **Kodo komentarai** → Angliškai arba lietuviškai
3. **Kintamųjų vardai** → Angliškai
4. **Type hints** → VISADA (Python ir TypeScript)
5. **GDPR** → Mokinių vardai anonimizuojami prieš siunčiant į API

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

## 📊 PROGRESAS

- **Dokumentacija:** ✅ Baigta
- **Projekto setup:** ☐ Nepradėta
- **Backend:** ☐ Nepradėta
- **Frontend:** ☐ Nepradėta
- **OCR integracija:** ☐ Nepradėta
- **AI integracija:** ☐ Nepradėta

**Detalus progresas:** `docs/TASKS.md`

---

## ⚡ GREITAS STARTAS

1. Perskaityk `SESSION_GUIDE.md`
2. Patikrink `docs/TASKS.md` - kur sustota
3. Pradėk nuo pirmos ☐ užduoties

---

*Paskutinis atnaujinimas: 2026-01-10*
