# 🗄️ DUOMENŲ BAZĖS SCHEMA
## Matematikos Mokytojo Asistentas

---

## 1. DUOMENŲ BAZĖS TECHNOLOGIJA

| Parametras | Reikšmė |
|------------|---------|
| **DBMS** | SQLite 3.x |
| **Failas** | `database/matematika.db` |
| **ORM** | SQLAlchemy 2.0 |
| **Migracijos** | Alembic |
| **Ateitis** | PostgreSQL (serverio versija) |

---

## 2. ER DIAGRAMA

```
┌─────────────────┐       ┌─────────────────┐
│   SchoolYear    │       │    Settings     │
│─────────────────│       │─────────────────│
│ id (PK)         │       │ id (PK)         │
│ name            │       │ key             │
│ start_date      │       │ value           │
│ end_date        │       │ updated_at      │
│ is_active       │       └─────────────────┘
│ created_at      │
└────────┬────────┘
         │ 1
         │
         │ ∞
┌────────┴────────┐       ┌─────────────────┐
│     Class       │       │  ErrorTemplate  │
│─────────────────│       │─────────────────│
│ id (PK)         │       │ id (PK)         │
│ school_year_id  │───────│ name            │
│ name            │       │ description_lt  │
│ grade_level     │       │ topic_id (FK)   │
│ created_at      │       │ created_at      │
└────────┬────────┘       └─────────────────┘
         │ 1                      │
         │                        │
         │ ∞                      │
┌────────┴────────┐       ┌───────┴─────────┐
│    Student      │       │     Topic       │
│─────────────────│       │─────────────────│
│ id (PK)         │       │ id (PK)         │
│ class_id (FK)   │       │ name            │
│ unique_code     │       │ grade_levels    │
│ first_name      │       │ description     │
│ last_name       │       │ created_at      │
│ created_at      │       └─────────────────┘
│ is_active       │
└────────┬────────┘
         │ 1
         │
         │ ∞
┌────────┴────────┐       ┌─────────────────┐
│   Submission    │       │      Test       │
│─────────────────│       │─────────────────│
│ id (PK)         │       │ id (PK)         │
│ student_id (FK) │       │ class_id (FK)   │
│ test_id (FK)    │───────│ topic_id (FK)   │
│ variant_id (FK) │       │ name            │
│ original_file   │       │ date            │
│ processed_file  │       │ max_points      │
│ ocr_result      │       │ created_at      │
│ status          │       └────────┬────────┘
│ total_points    │                │ 1
│ percentage      │                │
│ grade           │                │ ∞
│ created_at      │       ┌────────┴────────┐
│ processed_at    │       │    Variant      │
└────────┬────────┘       │─────────────────│
         │ 1              │ id (PK)         │
         │                │ test_id (FK)    │
         │ ∞              │ name            │
┌────────┴────────┐       │ created_at      │
│     Answer      │       └────────┬────────┘
│─────────────────│                │ 1
│ id (PK)         │                │
│ submission_id   │                │ ∞
│ task_id (FK)    │       ┌────────┴────────┐
│ student_answer  │       │      Task       │
│ is_correct      │       │─────────────────│
│ points_earned   │       │ id (PK)         │
│ created_at      │       │ variant_id (FK) │
└────────┬────────┘       │ number          │
         │ 1              │ sub_number      │
         │                │ question_text   │
         │ ∞              │ correct_answer  │
┌────────┴────────┐       │ correct_solution│
│     Error       │       │ max_points      │
│─────────────────│       │ created_at      │
│ id (PK)         │       └─────────────────┘
│ answer_id (FK)  │
│ error_type      │
│ description     │
│ explanation_lt  │
│ position        │
│ created_at      │
└─────────────────┘
```

---

## 3. LENTELIŲ DETALĖS

### 3.1 school_years (Mokslo metai)

| Stulpelis | Tipas | Aprašymas |
|-----------|-------|-----------|
| `id` | INTEGER PK | Unikalus ID |
| `name` | VARCHAR(20) | Pavadinimas, pvz. "2025-2026" |
| `start_date` | DATE | Pradžios data |
| `end_date` | DATE | Pabaigos data |
| `is_active` | BOOLEAN | Ar aktyvūs metai |
| `created_at` | DATETIME | Sukūrimo data |
| `updated_at` | DATETIME | Atnaujinimo data |

**Indeksai:**
- `idx_school_years_active` ON (is_active)

**SQL:**
```sql
CREATE TABLE school_years (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) NOT NULL UNIQUE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

### 3.2 classes (Klasės)

| Stulpelis | Tipas | Aprašymas |
|-----------|-------|-----------|
| `id` | INTEGER PK | Unikalus ID |
| `school_year_id` | INTEGER FK | Mokslo metų ID |
| `name` | VARCHAR(10) | Klasės pavadinimas, pvz. "7a" |
| `grade_level` | INTEGER | Klasės lygis (5, 6, 7, 8, 9, 10) |
| `created_at` | DATETIME | Sukūrimo data |
| `updated_at` | DATETIME | Atnaujinimo data |

**Indeksai:**
- `idx_classes_school_year` ON (school_year_id)
- `idx_classes_grade` ON (grade_level)

**SQL:**
```sql
CREATE TABLE classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_year_id INTEGER NOT NULL,
    name VARCHAR(10) NOT NULL,
    grade_level INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_year_id) REFERENCES school_years(id) ON DELETE CASCADE,
    UNIQUE(school_year_id, name)
);
```

---

### 3.3 students (Mokiniai)

| Stulpelis | Tipas | Aprašymas |
|-----------|-------|-----------|
| `id` | INTEGER PK | Unikalus ID |
| `class_id` | INTEGER FK | Klasės ID |
| `unique_code` | VARCHAR(20) | Unikalus kodas GDPR (pvz. "M2026001") |
| `first_name` | VARCHAR(50) | Vardas |
| `last_name` | VARCHAR(50) | Pavardė |
| `is_active` | BOOLEAN | Ar aktyvus mokinys |
| `created_at` | DATETIME | Sukūrimo data |
| `updated_at` | DATETIME | Atnaujinimo data |

**Indeksai:**
- `idx_students_class` ON (class_id)
- `idx_students_code` ON (unique_code) UNIQUE
- `idx_students_name` ON (last_name, first_name)
- `idx_students_active` ON (is_active)

**SQL:**
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    unique_code VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
);
```

---

### 3.4 topics (Temos)

| Stulpelis | Tipas | Aprašymas |
|-----------|-------|-----------|
| `id` | INTEGER PK | Unikalus ID |
| `name` | VARCHAR(100) | Temos pavadinimas |
| `category` | VARCHAR(50) | Kategorija (algebra, geometrija, ...) |
| `grade_levels` | VARCHAR(50) | Klasės lygiai JSON, pvz. "[5,6,7]" |
| `description` | TEXT | Aprašymas |
| `created_at` | DATETIME | Sukūrimo data |

**SQL:**
```sql
CREATE TABLE topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    grade_levels VARCHAR(50),
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Pradiniai duomenys:**
```sql
INSERT INTO topics (name, category, grade_levels) VALUES
('Natūralieji skaičiai', 'aritmetika', '[5,6]'),
('Paprastosios trupmenos', 'trupmenos', '[5,6,7]'),
('Dešimtainės trupmenos', 'trupmenos', '[5,6,7]'),
('Procentai', 'procentai', '[6,7,8]'),
('Teigiami ir neigiami skaičiai', 'algebra', '[6,7]'),
('Lygtys', 'algebra', '[6,7,8]'),
('Lygčių sistemos', 'algebra', '[8,9,10]'),
('Nelygybės', 'algebra', '[7,8]'),
('Laipsniai', 'algebra', '[7,8]'),
('Šaknys', 'algebra', '[8,9]'),
('Reiškiniai', 'algebra', '[7,8]'),
('Funkcijos', 'algebra', '[8,9,10]'),
('Trikampiai', 'geometrija', '[5,6,7,8]'),
('Keturkampiai', 'geometrija', '[5,6,7,8]'),
('Apskritimas', 'geometrija', '[6,7,8]'),
('Plotas ir perimetras', 'geometrija', '[5,6,7]'),
('Tūris', 'geometrija', '[6,7,8]'),
('Koordinačių plokštuma', 'geometrija', '[7,8]'),
('Erdvinės figūros', 'geometrija', '[8,9,10]'),
('Tekstiniai uždaviniai', 'tekstiniai', '[5,6,7,8]');
```

---

### 3.5 tests (Kontroliniai darbai)

| Stulpelis | Tipas | Aprašymas |
|-----------|-------|-----------|
| `id` | INTEGER PK | Unikalus ID |
| `class_id` | INTEGER FK | Klasės ID |
| `topic_id` | INTEGER FK | Temos ID (neprivalomas) |
| `name` | VARCHAR(200) | Kontrolinio pavadinimas |
| `test_type` | VARCHAR(20) | Tipas: 'kontrolinis', 'savarankiskas' |
| `date` | DATE | Kontrolinio data |
| `max_points` | DECIMAL(5,2) | Maksimalūs taškai |
| `created_at` | DATETIME | Sukūrimo data |
| `updated_at` | DATETIME | Atnaujinimo data |

**Indeksai:**
- `idx_tests_class` ON (class_id)
- `idx_tests_date` ON (date)
- `idx_tests_topic` ON (topic_id)

**SQL:**
```sql
CREATE TABLE tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    topic_id INTEGER,
    name VARCHAR(200) NOT NULL,
    test_type VARCHAR(20) NOT NULL DEFAULT 'kontrolinis',
    date DATE NOT NULL,
    max_points DECIMAL(5,2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE SET NULL
);
```

---

### 3.6 variants (Kontrolinio variantai)

| Stulpelis | Tipas | Aprašymas |
|-----------|-------|-----------|
| `id` | INTEGER PK | Unikalus ID |
| `test_id` | INTEGER FK | Kontrolinio ID |
| `name` | VARCHAR(20) | Varianto pavadinimas, pvz. "I variantas" |
| `created_at` | DATETIME | Sukūrimo data |

**SQL:**
```sql
CREATE TABLE variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id INTEGER NOT NULL,
    name VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE,
    UNIQUE(test_id, name)
);
```

---

### 3.7 tasks (Užduotys)

| Stulpelis | Tipas | Aprašymas |
|-----------|-------|-----------|
| `id` | INTEGER PK | Unikalus ID |
| `variant_id` | INTEGER FK | Varianto ID |
| `number` | INTEGER | Užduoties numeris (1, 2, 3...) |
| `sub_number` | VARCHAR(5) | Papildomas numeris (a, b, c...) arba NULL |
| `question_text` | TEXT | Užduoties tekstas |
| `question_latex` | TEXT | Užduotis LaTeX formatu |
| `correct_answer` | TEXT | Teisingas atsakymas |
| `correct_answer_latex` | TEXT | Teisingas atsakymas LaTeX |
| `correct_solution` | TEXT | Pilnas teisingas sprendimas |
| `correct_solution_latex` | TEXT | Sprendimas LaTeX formatu |
| `max_points` | DECIMAL(4,2) | Maksimalūs taškai už užduotį |
| `created_at` | DATETIME | Sukūrimo data |
| `updated_at` | DATETIME | Atnaujinimo data |

**Indeksai:**
- `idx_tasks_variant` ON (variant_id)
- `idx_tasks_number` ON (variant_id, number, sub_number)

**SQL:**
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variant_id INTEGER NOT NULL,
    number INTEGER NOT NULL,
    sub_number VARCHAR(5),
    question_text TEXT,
    question_latex TEXT,
    correct_answer TEXT,
    correct_answer_latex TEXT,
    correct_solution TEXT,
    correct_solution_latex TEXT,
    max_points DECIMAL(4,2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (variant_id) REFERENCES variants(id) ON DELETE CASCADE
);
```

---

### 3.8 submissions (Pateikti darbai)

| Stulpelis | Tipas | Aprašymas |
|-----------|-------|-----------|
| `id` | INTEGER PK | Unikalus ID |
| `student_id` | INTEGER FK | Mokinio ID |
| `test_id` | INTEGER FK | Kontrolinio ID |
| `variant_id` | INTEGER FK | Varianto ID |
| `original_files` | TEXT | JSON su originalių failų keliais |
| `processed_files` | TEXT | JSON su apdorotų failų keliais |
| `ocr_raw_result` | TEXT | Neapdorotas OCR rezultatas |
| `ocr_processed_result` | TEXT | Apdorotas OCR rezultatas (LaTeX) |
| `ocr_method` | VARCHAR(20) | OCR metodas: 'local', 'hybrid', 'full' |
| `status` | VARCHAR(20) | Statusas (žr. žemiau) |
| `total_points` | DECIMAL(5,2) | Surinkti taškai |
| `max_points` | DECIMAL(5,2) | Maksimalūs taškai |
| `percentage` | DECIMAL(5,2) | Procentai |
| `grade` | INTEGER | Pažymys (1-10) |
| `grade_override` | INTEGER | Mokytojo pakeistas pažymys |
| `teacher_comment` | TEXT | Mokytojo komentaras |
| `created_at` | DATETIME | Sukūrimo data |
| `processed_at` | DATETIME | Apdorojimo data |
| `checked_at` | DATETIME | Patikrinimo data |

**Statusai:**
- `uploaded` - Failas įkeltas
- `processing` - Apdorojamas (OCR)
- `processed` - OCR baigtas
- `checking` - Tikrinamas (matematika)
- `checked` - Patikrintas
- `reviewed` - Peržiūrėtas mokytojo
- `completed` - Baigtas
- `error` - Klaida

**Indeksai:**
- `idx_submissions_student` ON (student_id)
- `idx_submissions_test` ON (test_id)
- `idx_submissions_status` ON (status)
- `idx_submissions_date` ON (created_at)

**SQL:**
```sql
CREATE TABLE submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    test_id INTEGER NOT NULL,
    variant_id INTEGER NOT NULL,
    original_files TEXT,
    processed_files TEXT,
    ocr_raw_result TEXT,
    ocr_processed_result TEXT,
    ocr_method VARCHAR(20),
    status VARCHAR(20) DEFAULT 'uploaded',
    total_points DECIMAL(5,2),
    max_points DECIMAL(5,2),
    percentage DECIMAL(5,2),
    grade INTEGER,
    grade_override INTEGER,
    teacher_comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME,
    checked_at DATETIME,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES variants(id) ON DELETE CASCADE,
    UNIQUE(student_id, test_id)
);
```

---

### 3.9 answers (Mokinio atsakymai)

| Stulpelis | Tipas | Aprašymas |
|-----------|-------|-----------|
| `id` | INTEGER PK | Unikalus ID |
| `submission_id` | INTEGER FK | Pateikimo ID |
| `task_id` | INTEGER FK | Užduoties ID |
| `student_answer` | TEXT | Mokinio atsakymas (tekstas) |
| `student_answer_latex` | TEXT | Mokinio atsakymas (LaTeX) |
| `student_solution` | TEXT | Mokinio sprendimas (tekstas) |
| `student_solution_latex` | TEXT | Mokinio sprendimas (LaTeX) |
| `is_correct` | BOOLEAN | Ar teisingas |
| `is_partially_correct` | BOOLEAN | Ar dalinai teisingas |
| `points_earned` | DECIMAL(4,2) | Gauti taškai |
| `auto_checked` | BOOLEAN | Ar automatiškai patikrintas |
| `teacher_override` | BOOLEAN | Ar mokytojas pakeitė |
| `created_at` | DATETIME | Sukūrimo data |
| `updated_at` | DATETIME | Atnaujinimo data |

**Indeksai:**
- `idx_answers_submission` ON (submission_id)
- `idx_answers_task` ON (task_id)
- `idx_answers_correct` ON (is_correct)

**SQL:**
```sql
CREATE TABLE answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    student_answer TEXT,
    student_answer_latex TEXT,
    student_solution TEXT,
    student_solution_latex TEXT,
    is_correct BOOLEAN,
    is_partially_correct BOOLEAN,
    points_earned DECIMAL(4,2),
    auto_checked BOOLEAN DEFAULT FALSE,
    teacher_override BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    UNIQUE(submission_id, task_id)
);
```

---

### 3.10 errors (Klaidos)

| Stulpelis | Tipas | Aprašymas |
|-----------|-------|-----------|
| `id` | INTEGER PK | Unikalus ID |
| `answer_id` | INTEGER FK | Atsakymo ID |
| `error_type` | VARCHAR(50) | Klaidos tipas (žr. žemiau) |
| `description` | TEXT | Trumpas klaidos aprašymas |
| `explanation_lt` | TEXT | Detalus paaiškinimas lietuviškai |
| `position_start` | INTEGER | Klaidos pradžia tekste |
| `position_end` | INTEGER | Klaidos pabaiga tekste |
| `severity` | VARCHAR(20) | Rimtumas: 'minor', 'major', 'critical' |
| `created_at` | DATETIME | Sukūrimo data |

**Klaidų tipai:**
- `calculation` - Skaičiavimo klaida
- `sign` - Ženklo klaida
- `order_of_operations` - Veiksmų eiliškumas
- `formula` - Formulės taikymas
- `logic` - Logikos klaida
- `simplification` - Suprastinimo klaida
- `unit` - Matavimo vienetai
- `transcription` - Perrašymo klaida
- `incomplete` - Nebaigtas sprendimas
- `other` - Kita

**SQL:**
```sql
CREATE TABLE errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    answer_id INTEGER NOT NULL,
    error_type VARCHAR(50) NOT NULL,
    description TEXT,
    explanation_lt TEXT,
    position_start INTEGER,
    position_end INTEGER,
    severity VARCHAR(20) DEFAULT 'major',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (answer_id) REFERENCES answers(id) ON DELETE CASCADE
);
```

---

### 3.11 alternative_solutions (Alternatyvūs sprendimai)

| Stulpelis | Tipas | Aprašymas |
|-----------|-------|-----------|
| `id` | INTEGER PK | Unikalus ID |
| `task_id` | INTEGER FK | Užduoties ID |
| `solution` | TEXT | Alternatyvus sprendimas |
| `solution_latex` | TEXT | Sprendimas LaTeX |
| `explanation` | TEXT | Paaiškinimas |
| `created_at` | DATETIME | Sukūrimo data |

**SQL:**
```sql
CREATE TABLE alternative_solutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    solution TEXT NOT NULL,
    solution_latex TEXT,
    explanation TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);
```

---

### 3.12 error_templates (Klaidų šablonai)

| Stulpelis | Tipas | Aprašymas |
|-----------|-------|-----------|
| `id` | INTEGER PK | Unikalus ID |
| `name` | VARCHAR(100) | Šablono pavadinimas |
| `error_type` | VARCHAR(50) | Klaidos tipas |
| `description_template` | TEXT | Aprašymo šablonas |
| `explanation_template_lt` | TEXT | Paaiškinimo šablonas LT |
| `topic_id` | INTEGER FK | Susijusi tema |
| `created_at` | DATETIME | Sukūrimo data |

**SQL:**
```sql
CREATE TABLE error_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    error_type VARCHAR(50) NOT NULL,
    description_template TEXT,
    explanation_template_lt TEXT NOT NULL,
    topic_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE SET NULL
);
```

---

### 3.13 comment_templates (Komentarų šablonai)

| Stulpelis | Tipas | Aprašymas |
|-----------|-------|-----------|
| `id` | INTEGER PK | Unikalus ID |
| `name` | VARCHAR(100) | Šablono pavadinimas |
| `comment` | TEXT | Komentaro tekstas |
| `category` | VARCHAR(50) | Kategorija |
| `created_at` | DATETIME | Sukūrimo data |

**SQL:**
```sql
CREATE TABLE comment_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    comment TEXT NOT NULL,
    category VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

### 3.14 settings (Nustatymai)

| Stulpelis | Tipas | Aprašymas |
|-----------|-------|-----------|
| `id` | INTEGER PK | Unikalus ID |
| `key` | VARCHAR(100) | Nustatymo raktas |
| `value` | TEXT | Nustatymo reikšmė (JSON) |
| `description` | TEXT | Aprašymas |
| `updated_at` | DATETIME | Atnaujinimo data |

**SQL:**
```sql
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT,
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Pradiniai nustatymai:**
```sql
INSERT INTO settings (key, value, description) VALUES
('grading_scale', '{"10":[91,100],"9":[81,90],"8":[71,80],"7":[61,70],"6":[51,60],"5":[41,50],"4":[31,40],"3":[21,30],"2":[11,20],"1":[0,10]}', 'Vertinimo skalė'),
('default_ocr_method', '"hybrid"', 'Numatytasis OCR metodas'),
('mathpix_enabled', 'true', 'Ar MathPix įjungtas'),
('gemini_enabled', 'true', 'Ar Gemini įjungtas'),
('wolfram_enabled', 'true', 'Ar WolframAlpha įjungtas'),
('auto_check_enabled', 'true', 'Ar automatinis tikrinimas įjungtas'),
('student_code_prefix', '"M"', 'Mokinio kodo prefiksas'),
('student_code_year', 'true', 'Ar įtraukti metus į kodą');
```

---

### 3.15 statistics_cache (Statistikos cache)

| Stulpelis | Tipas | Aprašymas |
|-----------|-------|-----------|
| `id` | INTEGER PK | Unikalus ID |
| `entity_type` | VARCHAR(20) | Tipas: 'student', 'class', 'topic' |
| `entity_id` | INTEGER | Susijusio objekto ID |
| `period_start` | DATE | Periodo pradžia |
| `period_end` | DATE | Periodo pabaiga |
| `data` | TEXT | Statistikos JSON |
| `created_at` | DATETIME | Sukūrimo data |
| `expires_at` | DATETIME | Galiojimo pabaiga |

**SQL:**
```sql
CREATE TABLE statistics_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type VARCHAR(20) NOT NULL,
    entity_id INTEGER NOT NULL,
    period_start DATE,
    period_end DATE,
    data TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME
);
```

---

## 4. VIEWS (RODYKLĖS)

### 4.1 student_statistics_view

```sql
CREATE VIEW student_statistics_view AS
SELECT 
    s.id as student_id,
    s.first_name,
    s.last_name,
    s.unique_code,
    c.name as class_name,
    c.grade_level,
    COUNT(sub.id) as total_submissions,
    AVG(sub.percentage) as average_percentage,
    AVG(COALESCE(sub.grade_override, sub.grade)) as average_grade,
    MAX(sub.created_at) as last_submission_date
FROM students s
LEFT JOIN classes c ON s.class_id = c.id
LEFT JOIN submissions sub ON s.id = sub.student_id AND sub.status = 'completed'
GROUP BY s.id;
```

### 4.2 class_statistics_view

```sql
CREATE VIEW class_statistics_view AS
SELECT 
    c.id as class_id,
    c.name as class_name,
    c.grade_level,
    sy.name as school_year,
    COUNT(DISTINCT s.id) as student_count,
    COUNT(DISTINCT t.id) as test_count,
    AVG(sub.percentage) as average_percentage,
    AVG(COALESCE(sub.grade_override, sub.grade)) as average_grade
FROM classes c
LEFT JOIN school_years sy ON c.school_year_id = sy.id
LEFT JOIN students s ON c.id = s.class_id AND s.is_active = TRUE
LEFT JOIN tests t ON c.id = t.class_id
LEFT JOIN submissions sub ON t.id = sub.test_id AND sub.status = 'completed'
GROUP BY c.id;
```

### 4.3 error_statistics_view

```sql
CREATE VIEW error_statistics_view AS
SELECT 
    e.error_type,
    t.name as topic_name,
    c.grade_level,
    COUNT(*) as error_count,
    COUNT(DISTINCT a.submission_id) as submission_count
FROM errors e
JOIN answers a ON e.answer_id = a.id
JOIN tasks tk ON a.task_id = tk.id
JOIN variants v ON tk.variant_id = v.id
JOIN tests ts ON v.test_id = ts.id
LEFT JOIN topics t ON ts.topic_id = t.id
JOIN classes c ON ts.class_id = c.id
GROUP BY e.error_type, t.id, c.grade_level;
```

---

## 5. TRIGGAI

### 5.1 Automatinis unique_code generavimas

```sql
CREATE TRIGGER generate_student_code
AFTER INSERT ON students
FOR EACH ROW
WHEN NEW.unique_code IS NULL
BEGIN
    UPDATE students 
    SET unique_code = 'M' || strftime('%Y', 'now') || printf('%04d', NEW.id)
    WHERE id = NEW.id;
END;
```

### 5.2 Automatinis updated_at atnaujinimas

```sql
CREATE TRIGGER update_student_timestamp
AFTER UPDATE ON students
FOR EACH ROW
BEGIN
    UPDATE students SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

### 5.3 Submission taškų perskaičiavimas

```sql
CREATE TRIGGER recalculate_submission_points
AFTER UPDATE ON answers
FOR EACH ROW
BEGIN
    UPDATE submissions 
    SET total_points = (
        SELECT SUM(points_earned) 
        FROM answers 
        WHERE submission_id = NEW.submission_id
    ),
    percentage = (
        SELECT SUM(points_earned) * 100.0 / max_points 
        FROM answers a
        JOIN submissions s ON a.submission_id = s.id
        WHERE s.id = NEW.submission_id
    )
    WHERE id = NEW.submission_id;
END;
```

---

## 6. MIGRACIJOS STRATEGIJA

### Alembic komandos

```bash
# Sukurti naują migraciją
alembic revision --autogenerate -m "Add new table"

# Vykdyti migracijas
alembic upgrade head

# Atšaukti paskutinę migraciją
alembic downgrade -1

# Parodyti istoriją
alembic history
```

### Pradinė migracija
Pradinė duomenų bazės struktūra bus sukurta pirmos migracijos metu iš SQLAlchemy modelių.

---

## 7. BACKUP STRATEGIJA

### Automatinis backup
```python
import shutil
from datetime import datetime

def backup_database():
    source = "database/matematika.db"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = f"database/backups/matematika_{timestamp}.db"
    shutil.copy2(source, dest)
```

### Backup tvarkaraštis
- Kasdien prieš pirmą naudojimą
- Po kiekvieno didelio importo
- Prieš atnaujinimus

---

**Dokumentas sukurtas:** 2026-01-10
**Paskutinis atnaujinimas:** 2026-01-10
**Versija:** 1.0
