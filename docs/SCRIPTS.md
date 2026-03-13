# 🔧 Paleidimo Skriptai

Matematikos Mokytojo Asistentas turi keturis pagrindinius skriptus, kurie palengvina sistemos valdymą.

---

## 📋 Skriptų apžvalga

| Skriptas | Paskirtis | Kada naudoti |
|----------|-----------|--------------|
| `SETUP.bat` | Pirminis nustatymas | Tik pirmą kartą arba po atnaujinimų |
| `START.bat` | Paleidimas | Kiekvieną kartą norint naudoti sistemą |
| `STOP.bat` | Sustabdymas | Norint sustabdyti sistemą |
| `CHECK.bat` | Patikrinimas | Norint patikrinti ar viskas veikia |

---

## 🔨 SETUP.bat - Pirminis nustatymas

### Kada naudoti?
- Pirmą kartą įdiegiant sistemą
- Po Python/Node.js atnaujinimų
- Po priklausomybių atnaujinimų (requirements.txt, package.json)
- Jei sistema neveikia ir reikia "švarios" instaliacijos

### Ką daro?

1. **Tikrina priklausomybes**
   - Python 3.11+
   - Node.js 18+
   - npm

2. **Sukuria .env failą**
   - Kopijuoja iš .env.example
   - Klausia ar perrašyti jei jau egzistuoja

3. **Sukuria katalogus**
   - database/
   - backend/logs/
   - backend/uploads/
   - backend/exports/

4. **Backend setup**
   - Sukuria Python virtual environment (venv)
   - Įdiegia visas priklausomybes iš requirements.txt
   - Gali užtrukti 2-5 minutes

5. **Frontend setup**
   - Įdiegia Node.js priklausomybes (npm install)
   - Gali užtrukti 2-5 minutes

6. **Duomenų bazės inicializacija**
   - Sukuria SQLite duomenų bazę
   - Paleidžia Alembic migracijas

### Pavyzdys

```batch
SETUP.bat
```

**Išvestis:**
```
══════════════════════════════════════════════════════════════
       MATEMATIKOS MOKYTOJO ASISTENTAS
       Pirminis nustatymas
══════════════════════════════════════════════════════════════

[1/6] Tikrinamos priklausomybes...
[✅] Python rastas: 3.11.5
[✅] Node.js rastas: v18.17.0
[✅] npm rastas: 9.8.1

[2/6] Kuriamas .env failas...
[✅] .env failas sukurtas

[3/6] Kuriami reikalingi katalogai...
[✅] Visi katalogai sukurti

[4/6] Nustatomas backend...
[INFO] Kuriamas Python virtual environment...
[✅] Virtual environment sukurtas
[INFO] Diegiamos Python priklausomybes...
[✅] Python priklausomybes idiegtos

[5/6] Nustatomas frontend...
[INFO] Diegiamos Node.js priklausomybes...
[✅] Frontend priklausomybes idiegtos

[6/6] Inicializuojama duomenu baze...
[✅] Duomenu baze sukurta

══════════════════════════════════════════════════════════════
  ✅ NUSTATYMAS SEKMINGAI BAIGTAS!
══════════════════════════════════════════════════════════════
```

---

## ▶️ START.bat - Paleidimas

### Kada naudoti?
- Kiekvieną kartą norint naudoti sistemą
- Po kompiuterio perkrovimo
- Po STOP.bat paleidimo

### Ką daro?

1. **Tikrina priklausomybes** (1/7)
   - Python, Node.js, npm
   - Jei trūksta - parodo klaidos pranešimą

2. **Tikrina failus ir katalogus** (2/7)
   - .env failas
   - backend/venv
   - frontend/node_modules
   - Jei trūksta - automatiškai sukuria/įdiegia

3. **Sustabdo senus procesus** (3/7)
   - Tikrina ar port 8000 ir 5173 laisvi
   - Jei užimti - sustabdo senus procesus

4. **Tikrina duomenų bazę** (4/7)
   - Jei nėra - sukuria automatiškai

5. **Paleidžia backend** (5/7)
   - Aktyvuoja Python venv
   - Paleidžia uvicorn serverį (port 8000)
   - Laukia kol pasileis (max 30 sek.)

6. **Paleidžia frontend** (6/7)
   - Paleidžia Vite dev serverį (port 5173)
   - Laukia kol pasileis (max 20 sek.)

7. **Atidaro naršyklę** (7/7)
   - Automatiškai atidaro http://localhost:5173

### Pavyzdys

```batch
START.bat
```

**Išvestis:**
```
══════════════════════════════════════════════════════════════
       MATEMATIKOS MOKYTOJO ASISTENTAS
       Paleidziama sistema...
══════════════════════════════════════════════════════════════

[1/7] Tikrinamos priklausomybes...
[OK] Python rastas: 3.11.5
[OK] Node.js rastas: v18.17.0
[OK] npm rastas

[2/7] Tikrinami failai ir katalogai...
[OK] .env failas rastas
[OK] Backend venv rastas
[OK] Frontend node_modules rastas
[OK] Visi reikalingi katalogai sukurti

[3/7] Stabdomi seni procesai...
[OK] Seni procesai sustabdyti

[4/7] Tikrinama duomenu baze...
[OK] Duomenu baze rasta

[5/7] Paleidziamas backend serveris...
[INFO] Laukiama kol backend pasileis...
[OK] Backend serveris paleistas!

[6/7] Paleidziamas frontend serveris...
[INFO] Laukiama kol frontend pasileis...
[OK] Frontend serveris paleistas!

[7/7] Sistema paleista!

══════════════════════════════════════════════════════════════
  ✅ SISTEMA SEKMINGAI PALEISTA!
══════════════════════════════════════════════════════════════

  📱 Frontend:  http://localhost:5173
  🔧 Backend:   http://localhost:8000
  📚 API Docs:  http://localhost:8000/docs

  ⚠️  SVARBU:
  - Nepamirskite nustatyti API raktus (Nustatymai)
  - Uzdarykite Backend/Frontend langus noredami sustabdyti
  - Arba paleiskite STOP.bat

══════════════════════════════════════════════════════════════
```

### Atidaryti langai

Po paleidimo matysite 3 langus:

1. **START.bat langas** - galite uždaryti (serveriai liks veikti)
2. **Backend Server** - Python uvicorn serveris (port 8000)
3. **Frontend Server** - Vite dev serveris (port 5173)

---

## ⏹️ STOP.bat - Sustabdymas

### Kada naudoti?
- Norint sustabdyti sistemą
- Prieš kompiuterio išjungimą
- Jei reikia perkrauti serverius

### Ką daro?

1. **Ieško veikiančių procesų**
   - Tikrina port 8000 (backend)
   - Tikrina port 5173 (frontend)

2. **Sustabdo procesus**
   - Backend serverį (Python/uvicorn)
   - Frontend serverį (Node.js/Vite)
   - Backup: sustabdo pagal PID

3. **Uždaro langus**
   - Backend Server langą
   - Frontend Server langą

4. **Ištrina laikinus failus**
   - _run_backend.bat
   - _run_frontend.bat

### Pavyzdys

```batch
STOP.bat
```

**Išvestis:**
```
══════════════════════════════════════════════════════════════
       SUSTABDOMAS MATEMATIKOS MOKYTOJO ASISTENTAS
══════════════════════════════════════════════════════════════

[INFO] Ieskoma veikianciu procesu...

[INFO] Stabdomas backend serveris (PID: 12345)
[INFO] Stabdomas frontend serveris (PID: 67890)
[INFO] Istrintas _run_backend.bat
[INFO] Istrintas _run_frontend.bat

══════════════════════════════════════════════════════════════
  ✅ Sustabdyta procesu: 2
══════════════════════════════════════════════════════════════
```

---

## ✅ CHECK.bat - Patikrinimas

### Kada naudoti?
- Norint patikrinti ar sistema paruošta darbui
- Jei kažkas neveikia
- Po SETUP.bat paleidimo

### Ką daro?

1. **Tikrina priklausomybes** (1/6)
   - Python versija
   - Node.js versija
   - npm versija

2. **Tikrina failus ir katalogus** (2/6)
   - .env failas
   - database/ katalogas
   - Duomenų bazė (math_teacher.db)

3. **Tikrina backend** (3/6)
   - venv katalogas
   - FastAPI paketas
   - SQLAlchemy paketas
   - Google Generative AI paketas
   - main.py failas
   - requirements.txt failas

4. **Tikrina frontend** (4/6)
   - node_modules katalogas
   - package.json failas
   - index.html failas
   - vite.config.ts failas

5. **Tikrina portus** (5/6)
   - Port 8000 (backend)
   - Port 5173 (frontend)
   - Ar laisvi ar užimti

6. **Tikrina darbo katalogus** (6/6)
   - logs/
   - uploads/
   - exports/

### Pavyzdys

```batch
CHECK.bat
```

**Išvestis (viskas gerai):**
```
══════════════════════════════════════════════════════════════
       MATEMATIKOS MOKYTOJO ASISTENTAS
       Sistemos patikrinimas
══════════════════════════════════════════════════════════════

[1] Tikrinamos priklausomybes...

[✅] Python: 3.11.5
[✅] Node.js: v18.17.0
[✅] npm: 9.8.1

[2] Tikrinami failai ir katalogai...

[✅] .env failas rastas
[✅] database/ katalogas rastas
[✅] Duomenu baze rasta (245760 bytes)

[3] Tikrinamas backend...

[✅] Backend venv rastas
[✅] FastAPI idiegtas
[✅] SQLAlchemy idiegtas
[✅] Google Generative AI idiegtas
[✅] main.py rastas
[✅] requirements.txt rastas

[4] Tikrinamas frontend...

[✅] node_modules rastas
[✅] package.json rastas
[✅] index.html rastas
[✅] vite.config.ts rastas

[5] Tikrinami portai...

[✅] Port 8000 laisvas (Backend)
[✅] Port 5173 laisvas (Frontend)

[6] Tikrinami darbo katalogai...

[✅] logs/ katalogas rastas
[✅] uploads/ katalogas rastas
[✅] exports/ katalogas rastas

══════════════════════════════════════════════════════════════
  ✅ SISTEMA PARUOSTA DARBUI!
══════════════════════════════════════════════════════════════

  Viskas veikia gerai. Galite paleisti START.bat

══════════════════════════════════════════════════════════════
```

**Išvestis (yra problemų):**
```
══════════════════════════════════════════════════════════════
  ⚠️  RASTOS PROBLEMOS: 3
══════════════════════════════════════════════════════════════

  Rekomenduojama paleisti SETUP.bat

══════════════════════════════════════════════════════════════
```

---

## 🔄 Tipiniai scenarijai

### Pirmą kartą naudojant

```batch
1. SETUP.bat    # Pirminis nustatymas (5-10 min)
2. CHECK.bat    # Patikrinti ar viskas gerai
3. START.bat    # Paleisti sistemą
```

### Kasdieninis naudojimas

```batch
1. START.bat    # Paleisti
   # ... dirbti su sistema ...
2. STOP.bat     # Sustabdyti
```

### Po atnaujinimų

```batch
1. STOP.bat     # Sustabdyti seną versiją
2. SETUP.bat    # Atnaujinti priklausomybes
3. CHECK.bat    # Patikrinti
4. START.bat    # Paleisti naują versiją
```

### Jei kažkas neveikia

```batch
1. STOP.bat     # Sustabdyti
2. CHECK.bat    # Patikrinti problemas
3. SETUP.bat    # Bandyti pataisyti
4. CHECK.bat    # Patikrinti ar pataisyta
5. START.bat    # Paleisti
```

---

## 🐛 Problemų sprendimas

### "Python nerastas"
- Įdiekite Python 3.11+ iš https://www.python.org/downloads/
- Įsitikinkite, kad Python pridėtas į PATH

### "Node.js nerastas"
- Įdiekite Node.js 18+ iš https://nodejs.org/
- Įsitikinkite, kad Node.js pridėtas į PATH

### "Port 8000 jau naudojamas"
- Paleiskite STOP.bat
- Arba rankiniu būdu: `netstat -ano | findstr :8000` ir `taskkill /F /PID <PID>`

### "Backend nepasileido"
- Patikrinkite backend/logs/ katalogą
- Paleiskite CHECK.bat
- Bandykite SETUP.bat iš naujo

### "Frontend nepasileido"
- Patikrinkite ar yra node_modules
- Paleiskite `cd frontend && npm install`
- Bandykite SETUP.bat iš naujo

### "Duomenų bazė nerasta"
- Paleiskite SETUP.bat
- Arba rankiniu būdu:
  ```batch
  cd backend
  venv\Scripts\activate
  python -c "from database import init_db; import asyncio; asyncio.run(init_db())"
  ```

---

## 📝 Pastabos

1. **Laikini failai**
   - `_run_backend.bat` ir `_run_frontend.bat` yra laikini
   - Sukuriami START.bat paleidimo metu
   - Ištrinami STOP.bat paleidimo metu

2. **Portai**
   - Backend: 8000
   - Frontend: 5173
   - Jei reikia pakeisti - redaguokite START.bat

3. **Logai**
   - Backend logai: `backend/logs/app_YYYY-MM-DD.log`
   - Frontend logai: Frontend Server lange

4. **API raktai**
   - Nustatomi per programos Nustatymus
   - Saugomi duomenų bazėje
   - .env failas naudojamas tik development

---

**Sukurta 2026-01-20**
