# 📐 Matematikos Mokytojo Asistentas

Moderni programinė įranga, padedanti matematikos mokytojams automatizuoti mokinių ranka rašytų kontrolinių darbų tikrinimą.

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![Version](https://img.shields.io/badge/version-0.0.1-blue)
![License](https://img.shields.io/badge/license-Private-red)

---

## 🎯 Apie projektą

Šis įrankis sukurtas padėti matematikos mokytojams:
- **Sutaupyti laiką** - vietoj ~4 val. vienos klasės kontrolinio tikrinimas užtrunka ~30-60 min
- **Pagerinti kokybę** - automatinis klaidų aptikimas ir paaiškinimų generavimas
- **Sekti progresą** - statistika pagal mokinius, klases ir temas

### Pagrindinės funkcijos

✅ Ranka rašytų darbų nuskaitymas (OCR)  
✅ Matematinių formulių atpažinimas  
✅ Automatinis sprendimų tikrinimas  
✅ Klaidų paaiškinimas lietuvių kalba  
✅ Alternatyvių sprendimų generavimas  
✅ PDF ataskaitos mokiniams ir klasėms  
✅ Statistika ir progreso sekimas  

---

## 🏗️ Technologijos

### Backend
- **Python 3.11+** - pagrindinė kalba
- **FastAPI** - REST API framework
- **SQLAlchemy** - ORM
- **SQLite** - duomenų bazė

### Frontend
- **React 18** - UI framework
- **TypeScript** - tipizuota JavaScript
- **TailwindCSS** - stiliai
- **shadcn/ui** - UI komponentai

### OCR & AI
- **MathPix API** - matematikos OCR
- **Google Cloud Vision** - teksto OCR
- **Google Gemini** - AI paaiškinimai
- **SymPy** - matematikos tikrinimas
- **WolframAlpha API** - sudėtingi skaičiavimai

---

## 📁 Projekto struktūra

```
d:\MATEMATIKA 2026\
├── SESSION_GUIDE.md          # ← Pradėti čia!
├── docs/                     # Dokumentacija
│   ├── PROJECT.md            # Projekto aprašymas
│   ├── TECHNICAL_SPEC.md     # Techninės specifikacijos
│   ├── UI_DESIGN.md          # UI/UX dizainas
│   ├── DATABASE.md           # Duomenų bazės schema
│   ├── API_INTEGRATIONS.md   # API integracijos
│   └── TASKS.md              # Užduotys ir progresas
├── backend/                  # Python FastAPI
├── frontend/                 # React aplikacija
├── database/                 # SQLite duomenų bazė
└── tests/                    # Testai
```

---

## 🚀 Greitas startas

### Reikalavimai
- Windows 11
- Python 3.11+
- Node.js 18+
- Git

### Instalacija

```powershell
# 1. Klonuoti/atsidaryti projektą
cd "d:\MATEMATIKA 2026"

# 2. Backend
cd backend
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt

# 3. Frontend
cd ..\frontend
npm install

# 4. Sukonfigūruoti .env
copy .env.example .env
# Redaguoti .env ir pridėti API raktus
```

### Paleidimas

```powershell
# Terminal 1 - Backend
cd backend
.\venv\Scripts\Activate
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Atidaryti naršyklėje: http://localhost:5173

---

## 📖 Dokumentacija

| Dokumentas | Aprašymas |
|------------|-----------|
| [SESSION_GUIDE.md](SESSION_GUIDE.md) | Kaip pradėti naują darbo sesiją |
| [docs/PROJECT.md](docs/PROJECT.md) | Projekto vizija ir reikalavimai |
| [docs/TECHNICAL_SPEC.md](docs/TECHNICAL_SPEC.md) | Techninės specifikacijos |
| [docs/UI_DESIGN.md](docs/UI_DESIGN.md) | UI/UX dizaino specifikacija |
| [docs/DATABASE.md](docs/DATABASE.md) | Duomenų bazės schema |
| [docs/API_INTEGRATIONS.md](docs/API_INTEGRATIONS.md) | Išorinių API integracijos |
| [docs/TASKS.md](docs/TASKS.md) | Užduočių sąrašas su progres |

---

## 🔧 Konfigūracija

Sukurkite `.env` failą iš `.env.example` ir užpildykite API raktus:

```env
# MathPix (matematikos OCR)
MATHPIX_APP_ID=your_app_id
MATHPIX_APP_KEY=your_app_key

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=./credentials/google-cloud.json
GEMINI_API_KEY=your_gemini_key

# WolframAlpha
WOLFRAM_APP_ID=your_wolfram_app_id
```

---

## 📊 Progresas

Dabartinis projekto statusas: **Planavimas baigtas, pradedama implementacija**

Detalų progresą žiūrėkite: [docs/TASKS.md](docs/TASKS.md)

---

## 👥 Komanda

- **Projekto savininkas** - [Jūsų vardas]
- **Galutinis vartotojas** - Matematikos mokytoja
- **Programuotojas** - AI asistentas (GitHub Copilot)

---

## 📄 Licencija

Šis projektas yra privatus ir skirtas asmeniniam naudojimui.

---

## 📞 Kontaktai

Klausimai? Susisiekite su projekto savininku.

---

**Sukurta su ❤️ matematikos mokytojams**
