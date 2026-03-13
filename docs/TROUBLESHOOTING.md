# 🔍 TROUBLESHOOTING - Dažnos problemos ir sprendimai

> Greitas vadovas dažniausiai pasitaikančioms problemoms spręsti.

---

## 📋 TURINYS

1. [Backend problemos](#backend-problemos)
2. [Frontend problemos](#frontend-problemos)
3. [Duomenų bazės problemos](#duomenų-bazės-problemos)
4. [OCR/API problemos](#ocrapi-problemos)
5. [VS Code problemos](#vs-code-problemos)

---

## Backend problemos

### ❌ `ModuleNotFoundError: No module named 'xxx'`

**Priežastis:** Modulis neįdiegtas arba venv neaktyvuotas.

**Sprendimas:**
```powershell
cd backend
.\venv\Scripts\Activate
pip install xxx
# arba
pip install -r requirements.txt
```

---

### ❌ `uvicorn: command not found`

**Priežastis:** venv neaktyvuotas.

**Sprendimas:**
```powershell
cd backend
.\venv\Scripts\Activate
uvicorn main:app --reload
```

---

### ❌ `Address already in use (port 8000)`

**Priežastis:** Kitas procesas naudoja portą.

**Sprendimas:**
```powershell
# Rasti procesą
netstat -ano | findstr :8000

# Užmušti procesą (pakeisti PID)
taskkill /PID <PID> /F

# Arba naudoti kitą portą
uvicorn main:app --reload --port 8001
```

---

### ❌ `sqlalchemy.exc.OperationalError: unable to open database file`

**Priežastis:** Neegzistuoja `database/` katalogas arba nėra teisių.

**Sprendimas:**
```powershell
# Sukurti katalogą
mkdir database

# Patikrinti kelią .env faile
# DATABASE_URL=sqlite:///./database/math_teacher.db
```

---

## Frontend problemos

### ❌ `npm ERR! ENOENT: no such file or directory`

**Priežastis:** `node_modules` neįdiegti.

**Sprendimas:**
```powershell
cd frontend
npm install
```

---

### ❌ `TypeError: Cannot read properties of undefined`

**Priežastis:** Duomenys dar neužkrauti arba null.

**Sprendimas:**
```typescript
// Naudoti optional chaining
const name = data?.student?.name ?? 'Nežinomas';

// Arba early return
if (!data) return <Loading />;
```

---

### ❌ `Vite: Failed to resolve import`

**Priežastis:** Neteisingas importo kelias arba alias.

**Sprendimas:**
```typescript
// Patikrinti tsconfig.json ir vite.config.ts
// Turėtų būti:
// "@/*": ["./src/*"]

// Importai turėtų būti:
import { Button } from '@/components/ui/button';
```

---

### ❌ `CORS error: Access-Control-Allow-Origin`

**Priežastis:** Backend neturi CORS middleware.

**Sprendimas (backend/main.py):**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### ❌ `TailwindCSS stiliai neveikia`

**Priežastis:** Klasė nėra content sąraše.

**Sprendimas (tailwind.config.js):**
```javascript
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  // ...
}
```

---

## Duomenų bazės problemos

### ❌ `alembic.util.exc.CommandError: Can't locate revision identified by 'xxx'`

**Priežastis:** Migracijų istorija nesutampa.

**Sprendimas:**
```powershell
# Ištrinti DB ir pradėti iš naujo
Remove-Item database\math_teacher.db
alembic upgrade head
```

---

### ❌ `sqlite3.IntegrityError: UNIQUE constraint failed`

**Priežastis:** Bandoma įterpti dublikatą.

**Sprendimas:**
```python
# Patikrinti ar egzistuoja prieš insert
existing = await db.execute(select(Model).where(Model.unique_field == value))
if existing.scalar_one_or_none():
    raise HTTPException(400, "Įrašas jau egzistuoja")
```

---

### ❌ `sqlalchemy.exc.InvalidRequestError: This Session's transaction has been rolled back`

**Priežastis:** Klaida transakcijoje, sesija neatstatyta.

**Sprendimas:**
```python
# Naudoti try/except su rollback
try:
    await db.commit()
except Exception:
    await db.rollback()
    raise
```

---

## OCR/API problemos

### ❌ `MathPix: 401 Unauthorized`

**Priežastis:** Neteisingi API raktai.

**Sprendimas:**
1. Patikrinti `.env` faile:
   ```
   MATHPIX_APP_ID=your_app_id
   MATHPIX_APP_KEY=your_app_key
   ```
2. Patikrinti ar raktai galioja: https://dashboard.mathpix.com

---

### ❌ `MathPix: 429 Too Many Requests`

**Priežastis:** Viršytas API limitas.

**Sprendimas:**
- Palaukti minutę
- Naudoti rate limiting:
```python
import asyncio
await asyncio.sleep(1)  # Tarp užklausų
```

---

### ❌ `Google Vision: Permission denied`

**Priežastis:** Neteisingi credentials arba API neįjungtas.

**Sprendimas:**
1. Patikrinti `GOOGLE_APPLICATION_CREDENTIALS` kelią
2. Įjungti Vision API: https://console.cloud.google.com/apis

---

### ❌ `Google Gemini: Resource exhausted`

**Priežastis:** Viršytas nemokamas limitas.

**Sprendimas:**
- Palaukti iki kitos dienos (resetinasi)
- Arba upgrade į mokamą planą

---

### ❌ `WolframAlpha: Invalid appid`

**Priežastis:** Neteisingas APP ID.

**Sprendimas:**
1. Gauti naują: https://developer.wolframalpha.com
2. Atnaujinti per Settings puslapį arba tiesiai DB:
   ```powershell
   sqlite3 database\math_teacher.db "UPDATE settings SET value='YOUR_APP_ID' WHERE key='wolfram_app_id'"
   ```

---

### ❌ `Gemini: MAX_TOKENS / Empty response`

**Priežastis:** Netinkamas modelio pavadinimas arba per trumpas token limitas.

**Sprendimas:**
1. Patikrinti modelį duomenų bazėje:
   ```powershell
   sqlite3 database\math_teacher.db "SELECT key, value FROM settings WHERE key LIKE 'gemini%'"
   ```
2. Pakeisti į veikiantį modelį:
   ```powershell
   sqlite3 database\math_teacher.db "UPDATE settings SET value='gemini-2.5-pro-preview' WHERE key='gemini_model'"
   ```
3. Perkrauti backend serverį

**Veikiantys modeliai (2026-01):**
- `gemini-2.5-pro-preview` ✅
- `gemini-2.0-flash` ✅
- `gemini-1.5-pro` ✅

**NEVEIKIANTYS:**
- `gemini-3-pro-preview` ❌ (neegzistuoja)

---

### ❌ `Newton API: Connection refused`

**Priežastis:** Nėra interneto arba API laikinai neveikia.

**Sprendimas:**
- Patikrinti interneto ryšį
- Sistema automatiškai naudos kitą metodą (SymPy arba WolframAlpha)

---

### ❌ `TestGenerator naudoja fallback (primityvūs uždaviniai)`

**Priežastis:** Gemini API negauna atsakymo arba atsakymas netinkamai parsuojamas.

**Sprendimas:**
1. Patikrinti Gemini API raktą nustatymuose
2. Patikrinti Gemini modelį (turi būti `gemini-2.5-pro-preview`)
3. Patikrinti backend logus ar yra klaidos

---

## VS Code problemos

### ❌ `Python interpreter not found`

**Priežastis:** VS Code nemato venv.

**Sprendimas:**
1. `Ctrl+Shift+P` → "Python: Select Interpreter"
2. Pasirinkti `.\backend\venv\Scripts\python.exe`

---

### ❌ `ESLint/Prettier neveikia`

**Priežastis:** Extensions neįdiegti arba konfliktai.

**Sprendimas:**
1. Įdiegti extensions iš `.vscode/extensions.json`
2. `Ctrl+Shift+P` → "ESLint: Restart ESLint Server"
3. `Ctrl+Shift+P` → "Developer: Reload Window"

---

### ❌ `SQLite Viewer nerodo duomenų`

**Priežastis:** DB failas užrakintas.

**Sprendimas:**
1. Sustabdyti backend serverį
2. Atidaryti DB iš naujo
3. Paleisti serverį

---

### ❌ `Git: Permission denied (publickey)`

**Priežastis:** SSH raktas nesukonfigūruotas.

**Sprendimas:**
```powershell
# Naudoti HTTPS vietoj SSH
git remote set-url origin https://github.com/user/repo.git

# Arba sukonfigūruoti SSH
ssh-keygen -t ed25519 -C "your@email.com"
```

---

## 🆘 JEI NIEKAS NEPADEDA

1. **Restart everything:**
   ```powershell
   # Užmušti visus procesus
   taskkill /F /IM python.exe
   taskkill /F /IM node.exe

   # Išvalyti cache
   cd frontend && Remove-Item -Recurse node_modules\.cache

   # Paleisti iš naujo
   cd backend && .\venv\Scripts\Activate && uvicorn main:app --reload
   cd frontend && npm run dev
   ```

2. **Nuclear option (pradėti iš naujo):**
   ```powershell
   # Frontend
   Remove-Item -Recurse frontend\node_modules
   npm install

   # Backend
   Remove-Item -Recurse backend\venv
   python -m venv venv
   .\venv\Scripts\Activate
   pip install -r requirements.txt

   # Database
   Remove-Item database\math_teacher.db
   alembic upgrade head
   ```

3. **Klausti AI:**
   - Nukopijuoti tikslią klaidos žinutę
   - Aprašyti ką darėte prieš klaidą
   - Nurodyti kokiame faile/vietoje įvyko

---

*Paskutinis atnaujinimas: 2026-01-12*
