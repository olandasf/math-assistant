# 🔍 KODO AUDITO ATASKAITA
## Matematikos Mokytojo Asistentas

**Audito data:** 2026-01-17
**Auditorius:** GitHub Copilot (Claude Opus 4.5)
**Ankstesnis auditas:** 2026-01-13

---

## 📋 AUDITO APIMTIS

Atliktas pilnas projekto kodo auditas, apimantis:
- Backend (Python/FastAPI)
- Frontend (React/TypeScript)
- Duomenų bazės modelius
- API integracijas
- Dokumentaciją

---

## 🆕 NAUJI PAKEITIMAI NUO PASKUTINIO AUDITO (2026-01-13 → 2026-01-17)

### ✅ Pridėta nauja funkcionalybė

#### 1. OpenAI GPT Vision OCR integracija
```
backend/services/ocr/openai_vision.py (573 eilutės - NAUJAS)
```
- Pilnas OpenAI GPT Vision klientas kaip alternatyva Gemini Vision
- Palaiko GPT-5.2 modelį (numatytasis)
- Automatinis API rakto užkrovimas iš DB
- Analogiška architektūra kaip Gemini Vision

#### 2. OCR tiekėjo perjungimo sistema
```python
# backend/routers/settings.py - nauji endpoints
GET  /api/v1/settings/ocr-provider  # Gauti dabartinį tiekėją
POST /api/v1/settings/ocr-provider  # Nustatyti tiekėją (gemini/openai)
```
- Vartotojas gali pasirinkti OCR tiekėją per Settings puslapį
- Nustatymai saugomi DB ir išlieka po restarto

#### 3. Google Cloud Credentials palaikymas
```python
# backend/routers/settings.py
gemini_credentials_json  # Naujas laukas - JSON failo įkėlimas
```
- Galimybė įkelti Google Cloud credentials JSON failą
- Automatinis Vertex AI aktyvavimas su credentials
- Fallback į API key jei credentials nerastas

#### 4. Testai OCR srautui
```
backend/tests/test_ocr_flow.py (173 eilutės - NAUJAS)
backend/tests/test_duplicate_removal.py (NAUJAS)
backend/tests/test_debug_ocr.py (NAUJAS)
```
- Testai užduočių parsavimui iš LaTeX
- Separatoriaus (§§§) validacija
- Duplikatų šalinimo logika

#### 5. requirements.txt atnaujinimai
```pip-requirements
# Pridėta 2026-01-16:
google-genai>=1.0.0  # Naujesnis Gemini SDK

# Pašalinta (deprecated):
# pytesseract, easyocr, google-cloud-vision
```

### 🔄 Modifikuoti failai

#### backend/services/ocr/ocr_service.py
- Perdaryta architektūra: Gemini Vision ARBA OpenAI Vision
- Naujas `_get_ocr_provider_from_db()` metodas
- Dinaminis tiekėjo perjungimas

#### backend/services/ocr/gemini_vision.py
- Modelio atnaujinimas: `gemini-3-flash-preview` (Vertex AI)
- Fallback: `gemini-2.5-flash-preview-05-20` (API key)
- Pagerintas credentials aptikimas (keli keliai)

#### backend/ai/gemini_client.py
- Modelio atnaujinimas: `gemini-3-pro-preview`
- Pagerintas atsakymo ištraukimas su finishReason tikrinimas
- Safety filtrų diagnostika

#### frontend/src/pages/Settings/SettingsPage.tsx
- Pridėtas OpenAI sekcija
- Failų įkėlimo laukas Google Cloud credentials
- OCR tiekėjo pasirinkimo mygtukai
- localStorage migracijos valymas

#### frontend/package.json
- Atnaujintos priklausomybės (2026-01-17 versijos)

---

## ✅ TEIGIAMI ASPEKTAI

### 1. Architektūra ir struktūra
- **Aiški projekto struktūra** - backend ir frontend atskirti, logiškai organizuoti katalogai
- **Geras sluoksniavimas** - routers → services → models atskyrimas
- **Bazinis CRUD servisas** - `CRUDBase` klasė sumažina kodo dubliavimą
- **Singleton pattern** - teisingai naudojamas servisams (OCR, ImageProcessor, etc.)
- **🆕 Modulinė OCR sistema** - lengva pridėti naujus tiekėjus

### 2. Backend kokybė
- **Type hints** - naudojami visur, gerina kodo skaitomumą
- **Pydantic schemas** - validacija ir serializacija tvarkinga
- **Async/await** - teisingai naudojamas asinchroninis programavimas
- **Loguru logging** - struktūrizuotas logavimas su rotacija
- **CORS konfigūracija** - teisingai nustatyta
- **🆕 Keli OCR tiekėjai** - Gemini ir OpenAI palaikymas

### 3. Frontend kokybė
- **TypeScript** - tipai apibrėžti, nėra `any` piktnaudžiavimo
- **TanStack Query** - teisingai naudojamas duomenų fetching'ui
- **Komponentų organizacija** - puslapiai ir komponentai atskirti
- **API hooks** - centralizuoti, lengvai naudojami
- **🆕 Dinaminis UI** - OCR tiekėjo pasirinkimas realiu laiku

### 4. Matematikos tikrinimas
- **SymPy integracija** - gerai implementuota, palaiko įvairius uždavinių tipus
- **Hibridinis workflow** - SymPy → Newton → Wolfram → Gemini
- **Geometrijos tikrinimas** - atskiras modulis su formulėmis
- **Klaidos identifikavimas** - automatinis klaidos tipo nustatymas

### 5. AI integracija
- **Gemini klientas** - gerai struktūrizuotas, palaiko lietuvių kalbą
- **🆕 OpenAI klientas** - alternatyva Gemini
- **Prompt engineering** - pritaikyti 5-10 klasių mokiniams
- **Error handling** - tvarkingas klaidų apdorojimas

### 6. Dokumentacija
- **Išsami dokumentacija** - 10 dokumentų docs/ kataloge
- **TASKS.md** - detalus užduočių sekimas (78% užbaigta)
- **API dokumentacija** - Swagger/OpenAPI automatiškai generuojama
- **⚠️ Dokumentacija atsilikusi** - kai kurie pakeitimai neaprašyti

---

## ⚠️ PROBLEMOS IR REKOMENDACIJOS

### 1. KRITINĖS PROBLEMOS

#### 1.1 Saugumo problemos ⚠️ NEPAKEISTA
```python
# backend/config.py - SECRET_KEY hardcoded
SECRET_KEY: str = Field(
    default="dev-secret-key-change-in-production",  # ❌ PAVOJINGA
    ...
)
```
**Rekomendacija:** Pašalinti default reikšmę, reikalauti .env konfigūracijos.

#### 1.2 API raktų saugojimas ⚠️ NEPAKEISTA
```python
# API raktai saugomi DB kaip plain text
# backend/models/setting.py
value = Column(Text, nullable=True)  # ❌ Nešifruota
```
**Rekomendacija:** Šifruoti jautrius duomenis (API raktus) prieš saugant į DB.

#### 1.3 Trūksta autentifikacijos ⚠️ NEPAKEISTA
- Nėra jokios autentifikacijos sistemos
- Visi API endpoint'ai prieinami be prisijungimo
**Rekomendacija:** Pridėti bent bazinę autentifikaciją (JWT arba session-based).

### 2. VIDUTINĖS PROBLEMOS

#### 2.1 Testų padengimas 🟡 PAGERINTAS
- **backend/tests/** - pridėti 3 testų failai (OCR flow, duplicate removal, debug)
- **Vis dar trūksta:** unit testų servisams, API endpoint testų
- **Padengimas:** ~5% (buvo 0%)
**Rekomendacija:** Pridėti pytest testus visiems kritiniams servisams.

#### 2.2 Error handling neišbaigtas
```python
# backend/routers/math_checker.py
except Exception as e:
    logger.error(f"Klaida: {str(e)}")
    # ❌ Grąžina generic error, prarandama informacija
```
**Rekomendacija:** Sukurti custom exception klases, grąžinti struktūrizuotas klaidas.

#### 2.3 Database migrations ⚠️ NEPAKEISTA
```python
# Alembic sukonfigūruotas, bet nenaudojamas
# Naudojamas auto-create, kas pavojinga produkcijoje
```
**Rekomendacija:** Sukurti ir naudoti Alembic migracijas.

#### 2.4 Dokumentacija atsilikusi 🆕 NAUJA PROBLEMA
```markdown
# docs/API_INTEGRATIONS.md ir TECHNICAL_SPEC.md neturi:
- OpenAI GPT Vision dokumentacijos
- OCR tiekėjo perjungimo dokumentacijos
- Naujų Gemini modelių (gemini-3-*) aprašymo
```
**Rekomendacija:** Atnaujinti dokumentaciją su naujausiais pakeitimais.

### 3. MAŽOS PROBLEMOS

#### 3.1 Kodo dubliavimas
- `gemini_vision.py` ir `openai_vision.py` turi panašią struktūrą
- Galima sukurti bazinę `VisionClient` klasę
**Rekomendacija:** Refaktorinti į OOP su bendru interface

#### 3.2 Sinchroninis DB prieiga OCR servisuose 🆕
```python
# backend/services/ocr/gemini_vision.py
conn = sqlite3.connect(str(db_path))  # ❌ Blokuoja async
```
**Rekomendacija:** Naudoti async DB prieigą arba cache nustatymus

#### 3.3 Magic numbers
```python
# backend/services/upload_service.py
MAX_FILE_SIZE = 50 * 1024 * 1024  # Geriau būtų config
```

#### 3.4 Hardcoded modelių vardai
```python
# Skirtingi modeliai skirtinguose failuose:
# gemini_vision.py: "gemini-3-flash-preview", "gemini-2.5-flash-preview-05-20"
# gemini_client.py: "gemini-3-pro-preview"
# openai_vision.py: "gpt-5.2"
```
**Rekomendacija:** Centralizuoti modelių konfigūraciją į config.py

---

## 🔧 TECHNINĖS SKOLOS

### Backend
| Problema | Prioritetas | Statusas | Pastabos |
|----------|-------------|----------|----------|
| Testų trūkumas | Aukštas | 🟡 Pagerintas | 5% padengimas (buvo 0%) |
| Autentifikacija | Aukštas | ❌ Nepradėta | Nėra jokios |
| API raktų šifravimas | Aukštas | ❌ Nepradėta | Plain text DB |
| Dokumentacijos atnaujinimas | Vidutinis | 🆕 Nauja | Pakeitimai neaprašyti |
| Alembic migracijos | Vidutinis | ❌ Nepradėta | Nenaudojamos |
| Error handling | Vidutinis | ❌ Nepradėta | Generic errors |
| Sinchroninis DB OCR | Žemas | 🆕 Nauja | Blokuoja async |

### Frontend
| Problema | Prioritetas | Statusas | Pastabos |
|----------|-------------|----------|----------|
| Testų trūkumas | Aukštas | ❌ Nepradėta | 0% padengimas |
| Error boundaries | Vidutinis | ❌ Nepradėta | Nėra |
| Loading states | Žemas | ❌ Nepradėta | Kai kur trūksta |
| Accessibility | Žemas | ❌ Nepradėta | Reikia audito |

---

## 📊 KODO METRIKOS

### Backend (atnaujinta 2026-01-17)
| Metrika | Ankstesnė | Dabartinė | Pokytis |
|---------|-----------|-----------|---------|
| Failų skaičius | ~60 | ~65 | +5 |
| Kodo eilučių | ~8,000 | ~10,000 | +2,000 |
| Modelių | 14 | 14 | 0 |
| API endpoints | ~50 | ~55 | +5 |
| Servisų | 12 | 14 | +2 |
| Testų | 0 | 3 | +3 |

### Frontend (atnaujinta 2026-01-17)
| Metrika | Ankstesnė | Dabartinė | Pokytis |
|---------|-----------|-----------|---------|
| Failų skaičius | ~40 | ~42 | +2 |
| Komponentų | ~30 | ~30 | 0 |
| Puslapių | 15 | 15 | 0 |
| API hooks | ~40 | ~42 | +2 |

---

## 🎯 REKOMENDACIJOS PRIORITETŲ TVARKA

### Aukščiausias prioritetas (prieš produkciją)
1. ❌ Pridėti autentifikaciją
2. ❌ Šifruoti API raktus DB
3. ❌ Pašalinti hardcoded SECRET_KEY
4. 🟡 Pridėti bazinius testus (pradėta)

### Vidutinis prioritetas
5. 🆕 Atnaujinti dokumentaciją (API_INTEGRATIONS.md, TECHNICAL_SPEC.md)
6. Sukurti Alembic migracijas
7. Pagerinti error handling
8. Pridėti rate limiting
9. Sukurti backup sistemą

### Žemas prioritetas
10. Refaktorinti OCR klientus į OOP
11. Optimizuoti SQL queries
12. Pridėti caching
13. Pagerinti logging
14. Accessibility auditas

---

## 🏆 BENDRAS ĮVERTINIMAS

| Kategorija | Ankstesnė | Dabartinė | Komentaras |
|------------|-----------|-----------|------------|
| Architektūra | 8/10 | 8.5/10 | Modulinė OCR sistema |
| Kodo kokybė | 7/10 | 7.5/10 | Pridėti testai |
| Saugumas | 4/10 | 4/10 | Nepagerinta |
| Dokumentacija | 9/10 | 7/10 | ⬇️ Atsilikusi |
| Funkcionalumas | 8/10 | 8.5/10 | OpenAI integracija |
| Palaikomumas | 7/10 | 7.5/10 | Geresnė testavimo bazė |

**Bendras įvertinimas: 7.2/10** (buvo 7.2/10) - nėra pokyčio, nes dokumentacijos nuosmukis anuliuoja kodo pagerėjimą

---

## 📝 IŠVADOS

### Progresas nuo 2026-01-13
✅ **Pasiekimai:**
- OpenAI GPT Vision integracija (alternatyvus OCR)
- OCR tiekėjo perjungimo funkcionalumas
- Google Cloud credentials palaikymas
- Pradiniai testai OCR srautui
- Gemini modelių atnaujinimas (gemini-3-*)

⚠️ **Liko neišspręsta:**
- Autentifikacija
- API raktų šifravimas
- Alembic migracijos
- Pilnas testų padengimas

❌ **Nauja problema:**
- Dokumentacija atsilikusi nuo kodo

### Rekomendacija
**Prieš v1.0 release būtina:**
1. Atnaujinti dokumentaciją su visais naujais pakeitimais
2. Pridėti bent bazinę autentifikaciją
3. Padidinti testų padengimą iki 50%+

---

*Auditas atliktas: 2026-01-17*
*Ankstesnis auditas: 2026-01-13*
*Versija: 2.0*
