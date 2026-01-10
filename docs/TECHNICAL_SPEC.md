# 🔧 TECHNINĖS SPECIFIKACIJOS
## Matematikos Mokytojo Asistentas

---

## 1. TECHNOLOGIJŲ STACK'AS

### 1.1 Backend
| Technologija | Versija | Paskirtis |
|--------------|---------|-----------|
| **Python** | 3.11+ | Pagrindinė backend kalba |
| **FastAPI** | 0.109+ | REST API framework |
| **Uvicorn** | 0.27+ | ASGI serveris |
| **Pydantic** | 2.5+ | Duomenų validacija |
| **SQLAlchemy** | 2.0+ | ORM duomenų bazei |
| **Alembic** | 1.13+ | DB migracijos |

### 1.2 Frontend
| Technologija | Versija | Paskirtis |
|--------------|---------|-----------|
| **React** | 18.2+ | UI framework |
| **TypeScript** | 5.3+ | Tipizuota JavaScript |
| **Vite** | 5.0+ | Build įrankis |
| **TailwindCSS** | 3.4+ | CSS framework |
| **shadcn/ui** | latest | UI komponentai |
| **React Router** | 6.21+ | Navigacija |
| **TanStack Query** | 5.17+ | Duomenų fetching |
| **Zustand** | 4.4+ | State management |

### 1.3 Matematikos bibliotekos
| Biblioteka | Paskirtis |
|------------|-----------|
| **SymPy** | Simbolinė algebra, lygtys, suprastinimas |
| **NumPy** | Skaitiniai skaičiavimai |
| **SciPy** | Mokslininiai skaičiavimai |
| **mpmath** | Aukšto tikslumo aritmetika |
| **matplotlib** | Grafikai, brėžiniai (backend) |
| **Shapely** | Geometrinės figūros |

### 1.4 OCR ir vaizdo apdorojimas
| Įrankis | Tipas | Paskirtis |
|---------|-------|-----------|
| **MathPix API** | Cloud | Pagrindinis matematikos OCR |
| **Google Cloud Vision** | Cloud | Teksto OCR, rašysena |
| **Tesseract** | Lokalus | Backup OCR |
| **EasyOCR** | Lokalus | Rašysenos atpažinimas |
| **OpenCV** | Lokalus | Vaizdo apdorojimas |
| **Pillow** | Lokalus | Vaizdo manipuliacijos |

### 1.5 AI / NLP
| Įrankis | Paskirtis |
|---------|-----------|
| **Google Gemini API** | Klaidų aiškinimas, tekstiniai uždaviniai |
| **Google Vertex AI** | Alternatyva Gemini |
| **WolframAlpha API** | Sudėtingi matematikos tikrinimai |

### 1.6 PDF ir eksportas
| Biblioteka | Paskirtis |
|------------|-----------|
| **WeasyPrint** | PDF generavimas su CSS |
| **ReportLab** | PDF generavimas (backup) |
| **Jinja2** | HTML šablonai |

### 1.7 LaTeX renderinimas
| Biblioteka | Vieta | Paskirtis |
|------------|-------|-----------|
| **KaTeX** | Frontend | Greitas LaTeX render |
| **MathJax** | Frontend | Pilnas LaTeX (backup) |
| **latex2sympy** | Backend | LaTeX → SymPy |
| **sympy.latex()** | Backend | SymPy → LaTeX |

### 1.8 Duomenų bazė
| Technologija | Paskirtis |
|--------------|-----------|
| **SQLite** | Lokali duomenų bazė |
| **PostgreSQL** | Ateičiai (serveris) |

### 1.9 Testavimas
| Įrankis | Paskirtis |
|---------|-----------|
| **pytest** | Backend testai |
| **pytest-asyncio** | Async testai |
| **Vitest** | Frontend testai |
| **Playwright** | E2E testai |

---

## 2. SISTEMOS ARCHITEKTŪRA

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND                                    │
│                         React + TypeScript                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │   │
│  │  │  Home   │ │ Upload  │ │ Compare │ │ Results │ │ Reports │  │   │
│  │  │  Page   │ │  Page   │ │  Page   │ │  Page   │ │  Page   │  │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    KOMPONENTAI                                   │   │
│  │  ImageViewer │ MathRenderer │ ErrorMarker │ PDFPreview │ ...   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    STATE (Zustand)                               │   │
│  │  Students │ Classes │ Tests │ CurrentWork │ Settings            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │ HTTP/REST
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              BACKEND                                     │
│                           FastAPI + Python                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        API ROUTES                                │   │
│  │  /api/v1/students │ /api/v1/classes │ /api/v1/tests             │   │
│  │  /api/v1/upload   │ /api/v1/process │ /api/v1/reports           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        SERVICES                                  │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │   │
│  │  │ OCR Service │ │ Math Engine │ │ AI Service  │               │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘               │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │   │
│  │  │ PDF Service │ │ Stats Svc   │ │ Image Proc  │               │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        MODELS (SQLAlchemy)                       │   │
│  │  SchoolYear │ Class │ Student │ Test │ Task │ Submission │ ...  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │ SQL
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            DATABASE                                      │
│                             SQLite                                       │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ school_years │ classes │ students │ tests │ variants │ tasks     │ │
│  │ submissions │ answers │ errors │ grades │ statistics │ settings  │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │
┌───────────────────────────────────┴─────────────────────────────────────┐
│                         IŠORINĖS API                                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │   MathPix   │ │Google Cloud │ │   Gemini    │ │ WolframAlpha│       │
│  │     API     │ │   Vision    │ │     API     │ │     API     │       │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. PROJEKTO FAILŲ STRUKTŪRA

```
d:\MATEMATIKA 2026\
│
├── 📄 SESSION_GUIDE.md                 # Sesijos pradžios instrukcija
├── 📄 .env                             # Aplinkos kintamieji (API raktai)
├── 📄 .env.example                     # Pavyzdinis .env
├── 📄 .gitignore                       # Git ignoruojami failai
├── 📄 README.md                        # Projekto README
│
├── 📁 docs/                            # Dokumentacija
│   ├── PROJECT.md                      # Projekto aprašymas
│   ├── TECHNICAL_SPEC.md               # Techninės specifikacijos
│   ├── UI_DESIGN.md                    # UI/UX dizainas
│   ├── DATABASE.md                     # Duomenų bazės schema
│   ├── API_INTEGRATIONS.md             # API integracijos
│   └── TASKS.md                        # Užduotys ir progresas
│
├── 📁 backend/                         # Python FastAPI
│   ├── 📄 main.py                      # Aplikacijos entry point
│   ├── 📄 requirements.txt             # Python priklausomybės
│   ├── 📄 requirements-dev.txt         # Dev priklausomybės
│   ├── 📄 alembic.ini                  # Alembic konfigūracija
│   │
│   ├── 📁 app/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 config.py                # Konfigūracija
│   │   ├── 📄 database.py              # DB prisijungimas
│   │   │
│   │   ├── 📁 api/
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 deps.py              # Priklausomybės (DI)
│   │   │   └── 📁 v1/
│   │   │       ├── 📄 __init__.py
│   │   │       ├── 📄 router.py        # Pagrindinis router
│   │   │       ├── 📄 students.py      # Mokinių API
│   │   │       ├── 📄 classes.py       # Klasių API
│   │   │       ├── 📄 tests.py         # Kontrolinių API
│   │   │       ├── 📄 upload.py        # Įkėlimo API
│   │   │       ├── 📄 process.py       # Apdorojimo API
│   │   │       ├── 📄 reports.py       # Ataskaitų API
│   │   │       └── 📄 statistics.py    # Statistikos API
│   │   │
│   │   ├── 📁 models/                  # SQLAlchemy modeliai
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 school_year.py
│   │   │   ├── 📄 class_.py
│   │   │   ├── 📄 student.py
│   │   │   ├── 📄 test.py
│   │   │   ├── 📄 variant.py
│   │   │   ├── 📄 task.py
│   │   │   ├── 📄 submission.py
│   │   │   ├── 📄 answer.py
│   │   │   ├── 📄 error.py
│   │   │   └── 📄 settings.py
│   │   │
│   │   ├── 📁 schemas/                 # Pydantic schemos
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 student.py
│   │   │   ├── 📄 class_.py
│   │   │   ├── 📄 test.py
│   │   │   ├── 📄 submission.py
│   │   │   └── 📄 report.py
│   │   │
│   │   ├── 📁 services/                # Verslo logika
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 ocr_service.py       # OCR valdymas
│   │   │   ├── 📄 mathpix_client.py    # MathPix API
│   │   │   ├── 📄 google_vision.py     # Google Vision
│   │   │   ├── 📄 tesseract_ocr.py     # Tesseract
│   │   │   ├── 📄 easyocr_client.py    # EasyOCR
│   │   │   ├── 📄 image_processor.py   # Vaizdo apdorojimas
│   │   │   ├── 📄 math_engine.py       # Matematikos tikrinimas
│   │   │   ├── 📄 sympy_solver.py      # SymPy operacijos
│   │   │   ├── 📄 wolfram_client.py    # WolframAlpha
│   │   │   ├── 📄 ai_service.py        # AI/NLP
│   │   │   ├── 📄 gemini_client.py     # Google Gemini
│   │   │   ├── 📄 pdf_generator.py     # PDF kūrimas
│   │   │   ├── 📄 excel_importer.py    # Excel importas
│   │   │   ├── 📄 statistics.py        # Statistika
│   │   │   └── 📄 anonymizer.py        # Duomenų anonimizacija
│   │   │
│   │   ├── 📁 core/                    # Branduolys
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 security.py          # Saugumas
│   │   │   └── 📄 exceptions.py        # Išimtys
│   │   │
│   │   └── 📁 utils/                   # Pagalbinės funkcijos
│   │       ├── 📄 __init__.py
│   │       ├── 📄 file_utils.py
│   │       ├── 📄 math_utils.py
│   │       └── 📄 latex_utils.py
│   │
│   ├── 📁 alembic/                     # DB migracijos
│   │   ├── 📄 env.py
│   │   └── 📁 versions/
│   │
│   └── 📁 tests/                       # Backend testai
│       ├── 📄 __init__.py
│       ├── 📄 conftest.py
│       ├── 📁 api/
│       ├── 📁 services/
│       └── 📁 models/
│
├── 📁 frontend/                        # React aplikacija
│   ├── 📄 package.json
│   ├── 📄 tsconfig.json
│   ├── 📄 vite.config.ts
│   ├── 📄 tailwind.config.js
│   ├── 📄 postcss.config.js
│   ├── 📄 index.html
│   │
│   ├── 📁 public/
│   │   ├── 📄 favicon.ico
│   │   └── 📁 fonts/
│   │
│   └── 📁 src/
│       ├── 📄 main.tsx                 # Entry point
│       ├── 📄 App.tsx                  # Root komponentas
│       ├── 📄 index.css                # Global CSS
│       │
│       ├── 📁 components/              # UI komponentai
│       │   ├── 📁 ui/                  # shadcn/ui
│       │   │   ├── button.tsx
│       │   │   ├── input.tsx
│       │   │   ├── select.tsx
│       │   │   ├── dialog.tsx
│       │   │   ├── table.tsx
│       │   │   └── ...
│       │   │
│       │   ├── 📁 layout/
│       │   │   ├── Header.tsx
│       │   │   ├── Sidebar.tsx
│       │   │   ├── Footer.tsx
│       │   │   └── MainLayout.tsx
│       │   │
│       │   ├── 📁 students/
│       │   │   ├── StudentList.tsx
│       │   │   ├── StudentForm.tsx
│       │   │   ├── StudentImport.tsx
│       │   │   └── StudentCard.tsx
│       │   │
│       │   ├── 📁 classes/
│       │   │   ├── ClassList.tsx
│       │   │   ├── ClassForm.tsx
│       │   │   └── ClassCard.tsx
│       │   │
│       │   ├── 📁 tests/
│       │   │   ├── TestList.tsx
│       │   │   ├── TestForm.tsx
│       │   │   ├── VariantEditor.tsx
│       │   │   └── TaskEditor.tsx
│       │   │
│       │   ├── 📁 upload/
│       │   │   ├── UploadZone.tsx
│       │   │   ├── FilePreview.tsx
│       │   │   ├── OCRSettings.tsx
│       │   │   └── ProcessingStatus.tsx
│       │   │
│       │   ├── 📁 compare/
│       │   │   ├── CompareView.tsx
│       │   │   ├── ImageViewer.tsx
│       │   │   ├── MathRenderer.tsx
│       │   │   ├── MathEditor.tsx
│       │   │   └── SyncScroll.tsx
│       │   │
│       │   ├── 📁 results/
│       │   │   ├── ResultsView.tsx
│       │   │   ├── ErrorMarker.tsx
│       │   │   ├── SolutionDisplay.tsx
│       │   │   ├── ExplanationBox.tsx
│       │   │   └── GradeEditor.tsx
│       │   │
│       │   ├── 📁 reports/
│       │   │   ├── StudentReport.tsx
│       │   │   ├── ClassReport.tsx
│       │   │   ├── PDFPreview.tsx
│       │   │   └── PrintView.tsx
│       │   │
│       │   └── 📁 statistics/
│       │       ├── ProgressChart.tsx
│       │       ├── TopicAnalysis.tsx
│       │       └── ErrorPatterns.tsx
│       │
│       ├── 📁 pages/                   # Puslapiai
│       │   ├── HomePage.tsx
│       │   ├── StudentsPage.tsx
│       │   ├── ClassesPage.tsx
│       │   ├── TestsPage.tsx
│       │   ├── UploadPage.tsx
│       │   ├── ComparePage.tsx
│       │   ├── ResultsPage.tsx
│       │   ├── ReportsPage.tsx
│       │   ├── StatisticsPage.tsx
│       │   └── SettingsPage.tsx
│       │
│       ├── 📁 hooks/                   # Custom hooks
│       │   ├── useStudents.ts
│       │   ├── useClasses.ts
│       │   ├── useTests.ts
│       │   ├── useUpload.ts
│       │   ├── useOCR.ts
│       │   └── useMath.ts
│       │
│       ├── 📁 stores/                  # Zustand stores
│       │   ├── studentStore.ts
│       │   ├── classStore.ts
│       │   ├── testStore.ts
│       │   ├── uploadStore.ts
│       │   └── settingsStore.ts
│       │
│       ├── 📁 services/                # API klientai
│       │   ├── api.ts                  # Axios instance
│       │   ├── studentService.ts
│       │   ├── classService.ts
│       │   ├── testService.ts
│       │   ├── uploadService.ts
│       │   └── reportService.ts
│       │
│       ├── 📁 types/                   # TypeScript tipai
│       │   ├── student.ts
│       │   ├── class.ts
│       │   ├── test.ts
│       │   ├── submission.ts
│       │   └── report.ts
│       │
│       ├── 📁 utils/                   # Pagalbinės f-jos
│       │   ├── formatters.ts
│       │   ├── validators.ts
│       │   └── mathUtils.ts
│       │
│       └── 📁 i18n/                    # Lokalizacija
│           ├── lt.json                 # Lietuvių
│           └── index.ts
│
├── 📁 database/                        # Duomenų bazė
│   ├── 📄 matematika.db                # SQLite failas
│   └── 📁 backups/                     # Atsarginės kopijos
│
├── 📁 uploads/                         # Įkelti failai
│   ├── 📁 original/                    # Originalūs vaizdai
│   ├── 📁 processed/                   # Apdoroti vaizdai
│   └── 📁 temp/                        # Laikini failai
│
├── 📁 exports/                         # Eksportuoti failai
│   ├── 📁 pdf/                         # PDF ataskaitos
│   └── 📁 print/                       # Spausdinimui
│
└── 📁 tests/                           # E2E testai
    └── 📁 e2e/
        ├── upload.spec.ts
        ├── grading.spec.ts
        └── reports.spec.ts
```

---

## 4. API ENDPOINTS STRUKTŪRA

### 4.1 Mokiniai
```
GET    /api/v1/students                 # Gauti visus mokinius
GET    /api/v1/students/{id}            # Gauti mokinį pagal ID
POST   /api/v1/students                 # Sukurti mokinį
PUT    /api/v1/students/{id}            # Atnaujinti mokinį
DELETE /api/v1/students/{id}            # Ištrinti mokinį
POST   /api/v1/students/import          # Importuoti iš Excel
GET    /api/v1/students/{id}/stats      # Mokinio statistika
```

### 4.2 Klasės
```
GET    /api/v1/classes                  # Gauti visas klases
GET    /api/v1/classes/{id}             # Gauti klasę
POST   /api/v1/classes                  # Sukurti klasę
PUT    /api/v1/classes/{id}             # Atnaujinti klasę
DELETE /api/v1/classes/{id}             # Ištrinti klasę
GET    /api/v1/classes/{id}/students    # Klasės mokiniai
GET    /api/v1/classes/{id}/stats       # Klasės statistika
```

### 4.3 Mokslo metai
```
GET    /api/v1/school-years             # Gauti visus metus
POST   /api/v1/school-years             # Sukurti metus
PUT    /api/v1/school-years/{id}        # Atnaujinti
DELETE /api/v1/school-years/{id}        # Ištrinti
GET    /api/v1/school-years/current     # Dabartiniai metai
```

### 4.4 Kontroliniai
```
GET    /api/v1/tests                    # Gauti visus kontrolinius
GET    /api/v1/tests/{id}               # Gauti kontrolinį
POST   /api/v1/tests                    # Sukurti kontrolinį
PUT    /api/v1/tests/{id}               # Atnaujinti
DELETE /api/v1/tests/{id}               # Ištrinti
POST   /api/v1/tests/{id}/variants      # Pridėti variantą
PUT    /api/v1/tests/{id}/variants/{v}  # Atnaujinti variantą
POST   /api/v1/tests/{id}/variants/{v}/tasks  # Pridėti užduotį
```

### 4.5 Įkėlimas ir apdorojimas
```
POST   /api/v1/upload                   # Įkelti failą
POST   /api/v1/upload/batch             # Įkelti kelis failus
DELETE /api/v1/upload/{id}              # Ištrinti įkeltą
GET    /api/v1/upload/{id}/status       # Įkėlimo statusas

POST   /api/v1/process                  # Pradėti apdorojimą
GET    /api/v1/process/{id}/status      # Apdorojimo statusas
GET    /api/v1/process/{id}/result      # Apdorojimo rezultatas
POST   /api/v1/process/{id}/reprocess   # Pakartotinis apdorojimas
```

### 4.6 Tikrinimas
```
POST   /api/v1/check                    # Tikrinti sprendimą
POST   /api/v1/check/task               # Tikrinti užduotį
GET    /api/v1/check/{id}/errors        # Gauti klaidas
POST   /api/v1/check/{id}/explain       # Gauti paaiškinimus
```

### 4.7 Pateikimai (submissions)
```
GET    /api/v1/submissions              # Visi pateikimai
GET    /api/v1/submissions/{id}         # Vienas pateikimas
PUT    /api/v1/submissions/{id}         # Atnaujinti
PUT    /api/v1/submissions/{id}/grade   # Atnaujinti įvertinimą
```

### 4.8 Ataskaitos
```
GET    /api/v1/reports/student/{id}     # Mokinio ataskaita
GET    /api/v1/reports/class/{id}       # Klasės ataskaita
GET    /api/v1/reports/test/{id}        # Kontrolinio ataskaita
POST   /api/v1/reports/student/{id}/pdf # Generuoti PDF
POST   /api/v1/reports/class/{id}/pdf   # Klasės PDF
```

### 4.9 Statistika
```
GET    /api/v1/statistics/student/{id}  # Mokinio statistika
GET    /api/v1/statistics/class/{id}    # Klasės statistika
GET    /api/v1/statistics/topics        # Temų analizė
GET    /api/v1/statistics/errors        # Klaidų analizė
```

### 4.10 Nustatymai
```
GET    /api/v1/settings                 # Gauti nustatymus
PUT    /api/v1/settings                 # Atnaujinti nustatymus
POST   /api/v1/settings/test-ocr        # Testuoti OCR
POST   /api/v1/settings/test-api        # Testuoti API ryšį
```

---

## 5. BACKEND PRIKLAUSOMYBĖS

### requirements.txt
```
# Core
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Database
sqlalchemy==2.0.25
alembic==1.13.1
aiosqlite==0.19.0

# OCR & Image Processing
opencv-python==4.9.0.80
Pillow==10.2.0
pytesseract==0.3.10
easyocr==1.7.1
pdf2image==1.17.0

# Mathematics
sympy==1.12
numpy==1.26.3
scipy==1.12.0
mpmath==1.3.0
matplotlib==3.8.2
shapely==2.0.2
latex2sympy2==1.9.1

# API Clients
httpx==0.26.0
google-cloud-vision==3.5.0
google-generativeai==0.3.2
wolframalpha==5.0.0

# PDF Generation
weasyprint==60.2
Jinja2==3.1.3

# Excel
openpyxl==3.1.2
pandas==2.1.4

# Utils
python-dotenv==1.0.0
aiofiles==23.2.1
```

### requirements-dev.txt
```
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0
black==23.12.1
isort==5.13.2
flake8==7.0.0
mypy==1.8.0
```

---

## 6. FRONTEND PRIKLAUSOMYBĖS

### package.json (dependencies)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.1",
    "@tanstack/react-query": "^5.17.0",
    "zustand": "^4.4.7",
    "axios": "^1.6.5",
    "katex": "^0.16.9",
    "react-katex": "^3.0.1",
    "react-pdf": "^7.6.0",
    "@react-pdf-viewer/core": "^3.12.0",
    "react-dropzone": "^14.2.3",
    "react-zoom-pan-pinch": "^3.3.0",
    "react-hot-toast": "^2.4.1",
    "date-fns": "^3.2.0",
    "lucide-react": "^0.303.0",
    "recharts": "^2.10.3",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.47",
    "@types/react-dom": "^18.2.18",
    "@types/katex": "^0.16.7",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.11",
    "tailwindcss": "^3.4.1",
    "postcss": "^8.4.33",
    "autoprefixer": "^10.4.16",
    "vitest": "^1.2.0",
    "@testing-library/react": "^14.1.2",
    "playwright": "^1.41.0"
  }
}
```

---

## 7. APLINKOS KINTAMIEJI (.env)

```env
# Application
APP_NAME=Matematikos Asistentas
APP_ENV=development
DEBUG=true

# Database
DATABASE_URL=sqlite:///./database/matematika.db

# API Keys
MATHPIX_APP_ID=your_mathpix_app_id
MATHPIX_APP_KEY=your_mathpix_app_key

GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

GEMINI_API_KEY=your_gemini_api_key

WOLFRAM_APP_ID=your_wolfram_app_id

# OCR Settings
DEFAULT_OCR_MODE=hybrid
TESSERACT_PATH=C:/Program Files/Tesseract-OCR/tesseract.exe

# Upload Settings
MAX_UPLOAD_SIZE=52428800
UPLOAD_DIR=./uploads
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf

# PDF Settings
PDF_TEMPLATE_DIR=./templates/pdf

# Frontend
VITE_API_URL=http://localhost:8000/api/v1
```

---

## 8. VAIZDO APDOROJIMO PIPELINE

```
Originalus vaizdas (JPG/PNG/PDF)
            │
            ▼
    ┌───────────────────┐
    │ 1. Normalizacija  │
    │ - Dydžio keitimas │
    │ - DPI 300         │
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────┐
    │ 2. Pilkumo skalė  │
    │ cv2.cvtColor      │
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────┐
    │ 3. Kontrastas     │
    │ CLAHE algoritmas  │
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────┐
    │ 4. Triukšmo       │
    │    šalinimas      │
    │ cv2.fastNlMeans   │
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────┐
    │ 5. Binarizacija   │
    │ Adaptive threshold│
    └─────────┬─────────┘
              │
              ▼
    ┌───────────────────┐
    │ 6. Deskew         │
    │ Pasukimo taisymas │
    └─────────┬─────────┘
              │
              ▼
    Apdorotas vaizdas → OCR
```

---

## 9. OCR STRATEGIJA

```
                    Įvestis
                       │
                       ▼
              ┌─────────────────┐
              │ Pasirinktas     │
              │ režimas?        │
              └────────┬────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   ┌─────────┐   ┌─────────┐   ┌─────────┐
   │ Lokalus │   │Hibridinis│   │ Pilnas  │
   │         │   │         │   │  Cloud  │
   └────┬────┘   └────┬────┘   └────┬────┘
        │             │             │
        ▼             ▼             ▼
   Tesseract    MathPix API    MathPix API
   + EasyOCR   + Tesseract    + Google Vision
        │      (validacija)    + Gemini
        │             │             │
        └──────────────┴──────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Rezultatų       │
              │ sujungimas      │
              └────────┬────────┘
                       │
                       ▼
              LaTeX + Tekstas
```

---

## 10. MATEMATIKOS TIKRINIMO PIPELINE

```
OCR Rezultatas (LaTeX)
         │
         ▼
┌─────────────────────┐
│ LaTeX → SymPy       │
│ latex2sympy         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Užduoties tipas?    │
└──────────┬──────────┘
           │
    ┌──────┴──────┬───────────┬────────────┐
    ▼             ▼           ▼            ▼
┌───────┐   ┌─────────┐  ┌─────────┐  ┌─────────┐
│Lygtis │   │Reiškinys│  │Geometr. │  │Tekstinis│
└───┬───┘   └────┬────┘  └────┬────┘  └────┬────┘
    │            │            │            │
    ▼            ▼            ▼            ▼
sympy.solve  sympy.simplify  Shapely    Gemini
sympy.Eq     sympy.expand    formules   NLP→Math
    │            │            │            │
    └────────────┴────────────┴────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Palyginimas su  │
              │ teisingu atsak. │
              └────────┬────────┘
                       │
           ┌───────────┴───────────┐
           ▼                       ▼
      ┌─────────┐            ┌─────────┐
      │ Teisinga│            │ Klaida  │
      └─────────┘            └────┬────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Klaidos tipas   │
                         │ ir vieta        │
                         └─────────────────┘
```

---

**Dokumentas sukurtas:** 2026-01-10
**Paskutinis atnaujinimas:** 2026-01-10
**Versija:** 1.0
