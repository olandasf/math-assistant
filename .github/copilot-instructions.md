# 🤖 COPILOT INSTRUKCIJOS - Matematikos Mokytojo Asistentas

> Šis failas automatiškai perskaitomas kiekvienos sesijos pradžioje.
> Jis padeda AI asistentui suprasti projektą ir dirbti nuosekliai.

---

## 📋 SESIJOS PRADŽIA - PRIVALOMA

**Prieš pradedant bet kokį darbą, VISADA:**

1. Perskaityti `SESSION_GUIDE.md` - ten yra sesijos instrukcijos
2. Patikrinti `docs/TASKS.md` - rasti kur sustota
3. Jei reikia konteksto - skaityti atitinkamus `docs/` failus

---

## 🎯 APIE PROJEKTĄ

### Kas tai?
Matematikos mokytojo pagalbininkas - programa, kuri:
- Nuskaito mokinių ranka rašytus kontrolinius (OCR)
- Tikrina matematinius sprendimus
- Paaiškina klaidas lietuvių kalba
- Generuoja PDF ataskaitas

### Vartotojas
- Matematikos mokytoja
- Klasės: 5-8 (kartais 10)
- ~150 mokinių, 5 klasės
- Kalba: TIK lietuvių

### Tikslas
Sumažinti tikrinimo laiką nuo ~4 val. iki ~30-60 min. vienai klasei.

---

## 🛠️ TECHNOLOGIJOS (NEKEISTI!)

### Backend
```
Python 3.11+
FastAPI
SQLAlchemy 2.0
SQLite
Pydantic 2.x
```

### Frontend
```
React 18
TypeScript
Vite
TailwindCSS
shadcn/ui
Zustand
TanStack Query
```

### Matematika
```
SymPy - simbolinė matematika
NumPy - skaičiavimai
KaTeX - LaTeX renderinimas (frontend)
```

### OCR/AI
```
MathPix API - matematikos OCR (pagrindinis)
Google Cloud Vision - teksto OCR
Google Gemini - AI paaiškinimai
Tesseract - lokalus backup OCR
EasyOCR - rašysenos atpažinimas
WolframAlpha API - sudėtingi tikrinimai
```

---

## 📁 PROJEKTO STRUKTŪRA

```
d:\MATEMATIKA 2026\
├── docs/                    ← DOKUMENTACIJA (skaityti!)
│   ├── PROJECT.md           ← Projekto aprašymas
│   ├── TECHNICAL_SPEC.md    ← Techninės specifikacijos
│   ├── UI_DESIGN.md         ← UI dizainas
│   ├── DATABASE.md          ← DB schema
│   ├── API_INTEGRATIONS.md  ← API detalės
│   └── TASKS.md             ← UŽDUOTYS IR PROGRESAS
├── backend/                 ← Python FastAPI
├── frontend/                ← React aplikacija
├── database/                ← SQLite
├── uploads/                 ← Įkelti failai
└── exports/                 ← PDF ataskaitos
```

---

## ✅ KODAVIMO TAISYKLĖS

### Python (Backend)

```python
# VISADA naudoti type hints
def get_student(student_id: int) -> Student:
    ...

# VISADA async funkcijos API
async def create_student(data: StudentCreate) -> Student:
    ...

# Docstrings lietuviškai arba angliškai
def calculate_grade(points: float, max_points: float) -> int:
    """
    Apskaičiuoja pažymį pagal taškus.

    Args:
        points: Surinkti taškai
        max_points: Maksimalūs taškai

    Returns:
        Pažymys nuo 1 iki 10
    """
    ...
```

### TypeScript (Frontend)

```typescript
// VISADA tipizuoti
interface Student {
  id: number;
  firstName: string;
  lastName: string;
  classId: number;
}

// Komponentai su Props tipu
interface StudentCardProps {
  student: Student;
  onEdit: (id: number) => void;
}

export function StudentCard({ student, onEdit }: StudentCardProps) {
  ...
}
```

### Bendros taisyklės

1. **Kintamųjų vardai** - angliškai, aiškūs, prasmingi
2. **Komentarai** - lietuviškai arba angliškai
3. **UI tekstai** - TIK lietuviškai
4. **Klaidų pranešimai** - lietuviškai

---

## 🗄️ DUOMENŲ BAZĖ

### Pagrindinės lentelės
- `school_years` - mokslo metai
- `classes` - klasės
- `students` - mokiniai
- `tests` - kontroliniai
- `variants` - variantai (I, II)
- `tasks` - užduotys
- `submissions` - pateikti darbai
- `answers` - mokinio atsakymai
- `errors` - klaidos

### GDPR Svarbu!
- Mokiniai turi `unique_code` (pvz., M2026001)
- Prieš siunčiant į API - anonimizuoti vardus

---

## 🎨 UI DIZAINAS

### Spalvos (Tailwind)
```
primary: blue-500 (#3b82f6)
success: green-500 (#22c55e)
error: red-500 (#ef4444)
warning: amber-500 (#f59e0b)
```

### Komponentai
- Naudoti `shadcn/ui` komponentus
- Ikonos: `lucide-react`
- Matematika: `react-katex`

---

## 📝 UŽDUOČIŲ VALDYMAS

### Prieš pradedant užduotį:
1. Pakeisti statusą `docs/TASKS.md`: ☐ → 🔄
2. Pridėti datą

### Baigus užduotį:
1. Pakeisti statusą: 🔄 → ✅
2. Pridėti datą
3. Jei reikia - pridėti pastabas

### Statusai
- ☐ Nepradėta
- 🔄 Vykdoma
- ✅ Baigta
- ⏸️ Pristabdyta
- ❌ Atšaukta

---

## ⚠️ DAŽNOS KLAIDOS (VENGTI!)

### ❌ Negalima:
1. Keisti technologijų stack'o be aptarimo
2. Kurti naujų failų ne pagal struktūrą
3. Rašyti UI tekstus angliškai
4. Pamiršti atnaujinti TASKS.md
5. Naudoti `any` TypeScript'e
6. Pamiršti type hints Python'e

### ✅ Visada:
1. Laikytis esamos struktūros
2. Sekti dokumentaciją
3. Testuoti prieš žymint kaip baigtą
4. Atnaujinti progresą TASKS.md

---

## 🔧 KOMANDOS

### Backend
```powershell
cd backend
.\venv\Scripts\Activate
uvicorn main:app --reload --port 8000
```

### Frontend
```powershell
cd frontend
npm run dev
```

### Duomenų bazė
```powershell
cd backend
alembic upgrade head
```

---

## 📚 NUORODOS Į DOKUMENTACIJĄ

| Klausimas | Kur ieškoti |
|-----------|-------------|
| Kaip veikia sistema? | `docs/PROJECT.md` |
| Kokios technologijos? | `docs/TECHNICAL_SPEC.md` |
| Kaip atrodo UI? | `docs/UI_DESIGN.md` |
| Kokia DB schema? | `docs/DATABASE.md` |
| Kaip integruoti API? | `docs/API_INTEGRATIONS.md` |
| Ką daryti toliau? | `docs/TASKS.md` |

---

## 🆘 JEI NEAIŠKU

1. **Pirma** - ieškoti atsakymo dokumentacijoje
2. **Antra** - klausti vartotojo
3. **Trečia** - jei reikia priimti sprendimą, rinktis paprastesnį variantą

---

**Paskutinis atnaujinimas:** 2026-01-10
