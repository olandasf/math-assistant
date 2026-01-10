# 🎨 UI/UX DIZAINO SPECIFIKACIJA
## Matematikos Mokytojo Asistentas

---

## 1. DIZAINO FILOSOFIJA

### Principai
1. **Paprastumas** - intuityvus, be mokymosi kreivės
2. **Efektyvumas** - mažiausiai paspaudimų pasiekti tikslui
3. **Aiškumas** - viskas matoma, nieko nereikia ieškoti
4. **Modernumas** - šiuolaikiška, maloni akiai
5. **Lietuviška** - 100% lokalizuota

---

## 2. SPALVŲ PALETĖ

### Pagrindinės spalvos
```css
:root {
  /* Pagrindinė - mėlyna (švietimo, pasitikėjimo) */
  --primary-50: #eff6ff;
  --primary-100: #dbeafe;
  --primary-200: #bfdbfe;
  --primary-300: #93c5fd;
  --primary-400: #60a5fa;
  --primary-500: #3b82f6;    /* Pagrindinė */
  --primary-600: #2563eb;
  --primary-700: #1d4ed8;
  --primary-800: #1e40af;
  --primary-900: #1e3a8a;

  /* Antrinė - žalia (sėkmė, teisingi atsakymai) */
  --success-50: #f0fdf4;
  --success-100: #dcfce7;
  --success-500: #22c55e;    /* Teisinga */
  --success-600: #16a34a;
  --success-700: #15803d;

  /* Klaidos - raudona */
  --error-50: #fef2f2;
  --error-100: #fee2e2;
  --error-500: #ef4444;      /* Klaida */
  --error-600: #dc2626;
  --error-700: #b91c1c;

  /* Įspėjimai - geltona */
  --warning-50: #fffbeb;
  --warning-100: #fef3c7;
  --warning-500: #f59e0b;    /* Įspėjimas */
  --warning-600: #d97706;

  /* Neutralios */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;

  /* Fonas */
  --background: #f8fafc;
  --surface: #ffffff;
  --surface-hover: #f1f5f9;
}
```

### Tamsus režimas (ateičiai)
```css
.dark {
  --background: #0f172a;
  --surface: #1e293b;
  --surface-hover: #334155;
}
```

---

## 3. TIPOGRAFIJA

### Šriftai
```css
:root {
  /* Pagrindinis šriftas */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  
  /* Matematikai */
  --font-math: 'KaTeX_Main', 'Times New Roman', serif;
  
  /* Kodui */
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
}
```

### Dydžiai
```css
:root {
  --text-xs: 0.75rem;     /* 12px */
  --text-sm: 0.875rem;    /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg: 1.125rem;    /* 18px */
  --text-xl: 1.25rem;     /* 20px */
  --text-2xl: 1.5rem;     /* 24px */
  --text-3xl: 1.875rem;   /* 30px */
  --text-4xl: 2.25rem;    /* 36px */
}
```

### Svoriai
```css
:root {
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
}
```

---

## 4. TARPAI IR DYDŽIAI

### Spacing sistema (8px grid)
```css
:root {
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
}
```

### Kampų apvalinimas
```css
:root {
  --radius-sm: 0.25rem;   /* 4px */
  --radius-md: 0.375rem;  /* 6px */
  --radius-lg: 0.5rem;    /* 8px */
  --radius-xl: 0.75rem;   /* 12px */
  --radius-2xl: 1rem;     /* 16px */
  --radius-full: 9999px;
}
```

### Šešėliai
```css
:root {
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
}
```

---

## 5. LAYOUT STRUKTŪRA

### Pagrindinis layout
```
┌─────────────────────────────────────────────────────────────┐
│                         HEADER                               │
│  ┌──────────┐  ┌─────────────────────────────────┐  ┌────┐ │
│  │   Logo   │  │         Navigacija               │  │User│ │
│  └──────────┘  └─────────────────────────────────┘  └────┘ │
├────────────────────┬────────────────────────────────────────┤
│                    │                                        │
│     SIDEBAR        │              CONTENT                   │
│                    │                                        │
│  ┌──────────────┐  │  ┌──────────────────────────────────┐ │
│  │ Mokslo metai │  │  │                                  │ │
│  └──────────────┘  │  │                                  │ │
│  ┌──────────────┐  │  │                                  │ │
│  │ Meniu        │  │  │         PAGE CONTENT             │ │
│  │ punktai      │  │  │                                  │ │
│  │              │  │  │                                  │ │
│  └──────────────┘  │  │                                  │ │
│                    │  │                                  │ │
│  ┌──────────────┐  │  └──────────────────────────────────┘ │
│  │ Nustatymai   │  │                                        │
│  └──────────────┘  │                                        │
│                    │                                        │
├────────────────────┴────────────────────────────────────────┤
│                         FOOTER                               │
│              © 2026 Matematikos Asistentas                  │
└─────────────────────────────────────────────────────────────┘
```

### Matmenys
```css
:root {
  --header-height: 64px;
  --sidebar-width: 260px;
  --sidebar-collapsed: 72px;
  --footer-height: 48px;
  --content-max-width: 1440px;
}
```

---

## 6. KOMPONENTAI

### 6.1 Mygtukai

#### Pirminis mygtukas
```
┌─────────────────────┐
│   ✓ Apdoroti       │  Mėlyna, balta tekstas
└─────────────────────┘
```
- Fonas: `--primary-500`
- Hover: `--primary-600`
- Tekstas: baltas
- Aukštis: 40px (default), 36px (sm), 48px (lg)
- Padding: 16px 24px

#### Antrinis mygtukas
```
┌─────────────────────┐
│   Atšaukti         │  Pilkas rėmelis
└─────────────────────┘
```
- Fonas: skaidrus
- Border: `--gray-300`
- Hover: `--gray-100`
- Tekstas: `--gray-700`

#### Pavojingas mygtukas
```
┌─────────────────────┐
│   🗑 Ištrinti       │  Raudona
└─────────────────────┘
```
- Fonas: `--error-500`
- Hover: `--error-600`
- Tekstas: baltas

#### Sėkmės mygtukas
```
┌─────────────────────┐
│   ✓ Išsaugoti      │  Žalia
└─────────────────────┘
```
- Fonas: `--success-500`
- Hover: `--success-600`
- Tekstas: baltas

### 6.2 Įvesties laukai

#### Tekstinis laukas
```
┌─────────────────────────────────────┐
│ Mokinio vardas                      │  Label viršuje
├─────────────────────────────────────┤
│ Jonas Jonaitis                      │  Input
└─────────────────────────────────────┘
  Įveskite mokinio vardą ir pavardę     Helper text
```
- Border: `--gray-300`
- Focus border: `--primary-500`
- Focus ring: `--primary-200`
- Border-radius: `--radius-lg`
- Aukštis: 40px
- Padding: 12px

#### Select laukas
```
┌─────────────────────────────────────┐
│ Klasė                           ▼  │
├─────────────────────────────────────┤
│ 5a                                  │
│ 5b                                  │
│ 6a                                  │
│ 6b                                  │
└─────────────────────────────────────┘
```

### 6.3 Kortelės (Cards)

#### Pagrindinė kortelė
```
┌──────────────────────────────────────────┐
│                                          │
│  📊 Kontrolinis darbas                   │  Pavadinimas
│                                          │
│  Algebra - 7a klasė                      │  Aprašymas
│  2026-01-15                              │  Data
│                                          │
│  ┌────────────┐  ┌────────────┐         │
│  │  Peržiūrėti │  │  Redaguoti │         │  Actions
│  └────────────┘  └────────────┘         │
│                                          │
└──────────────────────────────────────────┘
```
- Fonas: `--surface`
- Border: `--gray-200`
- Shadow: `--shadow-sm`
- Hover shadow: `--shadow-md`
- Border-radius: `--radius-xl`
- Padding: 24px

#### Statistikos kortelė
```
┌─────────────────────┐
│  👥                 │
│  147                │  Didelis skaičius
│  Mokinių            │  Label
│  +5 šį mėnesį       │  Pokytis
└─────────────────────┘
```

### 6.4 Lentelės

```
┌────┬─────────────────────┬────────┬─────────┬──────────┐
│ #  │ Mokinys             │ Klasė  │ Pažymys │ Veiksmai │
├────┼─────────────────────┼────────┼─────────┼──────────┤
│ 1  │ Jonas Jonaitis      │ 7a     │ 8       │ 🔍 ✏️ 🗑 │
├────┼─────────────────────┼────────┼─────────┼──────────┤
│ 2  │ Ona Onaitė          │ 7a     │ 9       │ 🔍 ✏️ 🗑 │
├────┼─────────────────────┼────────┼─────────┼──────────┤
│ 3  │ Petras Petraitis    │ 7a     │ 6       │ 🔍 ✏️ 🗑 │
└────┴─────────────────────┴────────┴─────────┴──────────┘
```
- Header fonas: `--gray-50`
- Row hover: `--gray-50`
- Border: `--gray-200`
- Alternating rows: optional

### 6.5 Modaliniai langai

```
┌──────────────────────────────────────────────────┐
│  ✕                          Pridėti mokinį      │  Header
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ Vardas, pavardė                            │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ Klasė                                   ▼  │ │
│  └────────────────────────────────────────────┘ │
│                                                  │  Body
├──────────────────────────────────────────────────┤
│                    ┌───────────┐ ┌───────────┐  │
│                    │ Atšaukti  │ │ Išsaugoti │  │  Footer
│                    └───────────┘ └───────────┘  │
└──────────────────────────────────────────────────┘
```
- Max-width: 480px (sm), 640px (md), 800px (lg)
- Border-radius: `--radius-2xl`
- Backdrop: rgba(0, 0, 0, 0.5) su blur

### 6.6 Pranešimai (Toasts)

#### Sėkmės pranešimas
```
┌─────────────────────────────────────────┐
│ ✓  Mokinys sėkmingai pridėtas      ✕   │
└─────────────────────────────────────────┘
```
- Fonas: `--success-50`
- Border-left: 4px `--success-500`

#### Klaidos pranešimas
```
┌─────────────────────────────────────────┐
│ ✕  Nepavyko išsaugoti duomenų      ✕   │
└─────────────────────────────────────────┘
```
- Fonas: `--error-50`
- Border-left: 4px `--error-500`

### 6.7 Progress bar

```
Apdorojama: 65%
┌────────────────────────────────────────┐
│████████████████████░░░░░░░░░░░░░░░░░░░│
└────────────────────────────────────────┘
```
- Background: `--gray-200`
- Fill: `--primary-500`
- Height: 8px
- Border-radius: `--radius-full`

---

## 7. PUSLAPIŲ DIZAINAS

### 7.1 Pradinis puslapis (Dashboard)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  HEADER: Logo | Pagrindinis | Klasės | Mokiniai | Kontroliniai | [User]│
├──────────────────────┬──────────────────────────────────────────────────┤
│                      │                                                  │
│  SIDEBAR             │   👋 Sveiki, Mokytoja!                          │
│                      │                                                  │
│  📅 2025-2026        │   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │
│                      │   │  147   │ │   5    │ │   12   │ │  7.4   │   │
│  ──────────────      │   │Mokinių │ │Klasių  │ │Kontrol.│ │Vidurkis│   │
│                      │   └────────┘ └────────┘ └────────┘ └────────┘   │
│  🏠 Pagrindinis      │                                                  │
│  👥 Mokiniai         │   PASKUTINIAI KONTROLINIAI                       │
│  🏫 Klasės           │   ┌──────────────────────────────────────────┐   │
│  📝 Kontroliniai     │   │ 📄 Algebra - 7a │ 2026-01-10 │ ▶ Tikrinti │   │
│  📤 Įkelti darbą     │   ├──────────────────────────────────────────┤   │
│  📊 Statistika       │   │ 📄 Geometrija - 6b│ 2026-01-08│ ✓ Baigta  │   │
│  📑 Ataskaitos       │   └──────────────────────────────────────────┘   │
│                      │                                                  │
│  ──────────────      │   GREITOSIOS NUORODOS                            │
│                      │   ┌─────────────────┐ ┌─────────────────┐        │
│  ⚙️ Nustatymai       │   │ + Naujas        │ │ 📤 Įkelti       │        │
│                      │   │   kontrolinis   │ │    darbus       │        │
│                      │   └─────────────────┘ └─────────────────┘        │
│                      │                                                  │
└──────────────────────┴──────────────────────────────────────────────────┘
```

### 7.2 Darbo įkėlimo puslapis

```
┌─────────────────────────────────────────────────────────────────────────┐
│  HEADER                                                                  │
├──────────────────────┬──────────────────────────────────────────────────┤
│                      │                                                  │
│  SIDEBAR             │   📤 ĮKELTI MOKINIO DARBĄ                        │
│                      │                                                  │
│                      │   ┌───────────────────────────────────────────┐  │
│                      │   │  Kontrolinis darbas                    ▼  │  │
│                      │   └───────────────────────────────────────────┘  │
│                      │                                                  │
│                      │   ┌───────────────────────────────────────────┐  │
│                      │   │  Klasė                                 ▼  │  │
│                      │   └───────────────────────────────────────────┘  │
│                      │                                                  │
│                      │   ┌───────────────────────────────────────────┐  │
│                      │   │  Mokinys                               ▼  │  │
│                      │   └───────────────────────────────────────────┘  │
│                      │                                                  │
│                      │   ┌───────────────────────────────────────────┐  │
│                      │   │  Variantas                             ▼  │  │
│                      │   │  ○ I variantas  ○ II variantas            │  │
│                      │   └───────────────────────────────────────────┘  │
│                      │                                                  │
│                      │   ┌───────────────────────────────────────────┐  │
│                      │   │  OCR metodas                           ▼  │  │
│                      │   │  ○ Lokalus  ○ Hibridinis  ○ Pilnas       │  │
│                      │   └───────────────────────────────────────────┘  │
│                      │                                                  │
│                      │   ┌───────────────────────────────────────────┐  │
│                      │   │                                           │  │
│                      │   │     ┌─────────────────────────┐          │  │
│                      │   │     │     📄                  │          │  │
│                      │   │     │                         │          │  │
│                      │   │     │  Tempkite failus čia    │          │  │
│                      │   │     │  arba paspauskite       │          │  │
│                      │   │     │                         │          │  │
│                      │   │     │  JPG, PNG, PDF          │          │  │
│                      │   │     └─────────────────────────┘          │  │
│                      │   │                                           │  │
│                      │   └───────────────────────────────────────────┘  │
│                      │                                                  │
│                      │   ┌───────────────────────────────────────────┐  │
│                      │   │            🔄 APDOROTI DARBĄ             │  │
│                      │   └───────────────────────────────────────────┘  │
│                      │                                                  │
└──────────────────────┴──────────────────────────────────────────────────┘
```

### 7.3 Palyginimo langas

```
┌─────────────────────────────────────────────────────────────────────────┐
│  HEADER                                                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ← Atgal    📄 Jonas Jonaitis - Algebra - I variantas    [Išsaugoti]    │
│                                                                          │
├─────────────────────────────────┬───────────────────────────────────────┤
│                                 │                                       │
│   ORIGINALUS DARBAS             │   SKAITMENINĖ VERSIJA                 │
│                                 │                                       │
│   ┌─────────────────────────┐   │   ┌─────────────────────────────┐   │
│   │                         │   │   │                             │   │
│   │  [Skenuotas mokinio     │   │   │  1. Išspręskite lygtį:      │   │
│   │   darbas su ranka       │   │   │                             │   │
│   │   rašytais sprendimais] │   │   │     2x + 5 = 15             │   │
│   │                         │   │   │     2x = 15 - 5             │   │
│   │                         │   │   │     2x = 10                 │   │
│   │                         │   │   │     x = 5                   │   │
│   │                         │   │   │                             │   │
│   │                         │   │   │  2. Apskaičiuokite:         │   │
│   │                         │   │   │                             │   │
│   │                         │   │   │     √49 + 3² = 7 + 9 = 16   │   │
│   │                         │   │   │                             │   │
│   └─────────────────────────┘   │   └─────────────────────────────┘   │
│                                 │                                       │
│   🔍+ 🔍- 🔄90° 🔄180°          │   ✏️ Redaguoti                       │
│                                 │                                       │
├─────────────────────────────────┴───────────────────────────────────────┤
│                                                                          │
│            ┌──────────────────────────────────────────────┐             │
│            │          ▶ TIKRINTI UŽDUOTIS                 │             │
│            └──────────────────────────────────────────────┘             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.4 Rezultatų langas

```
┌─────────────────────────────────────────────────────────────────────────┐
│  HEADER                                                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ← Atgal    📊 REZULTATAI - Jonas Jonaitis              [📥 PDF]        │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  GALUTINIS ĮVERTINIMAS                                          │   │
│  │                                                                  │   │
│  │   ┌─────┐                                                        │   │
│  │   │  8  │   26/32 taškų (81.25%)                                │   │
│  │   └─────┘                                                        │   │
│  │                                                                  │   │
│  │   [✏️ Redaguoti pažymį]                                         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ═══════════════════════════════════════════════════════════════════    │
│                                                                          │
│  UŽDUOTIS 1 (8/8 taškų) ✓                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Išspręskite lygtį: 2x + 5 = 15                                 │   │
│  │                                                                  │   │
│  │  MOKINIO SPRENDIMAS:                                            │   │
│  │  2x + 5 = 15                                                    │   │
│  │  2x = 15 - 5                                                    │   │
│  │  2x = 10                                                        │   │
│  │  x = 5  ✓                                                       │   │
│  │                                                                  │   │
│  │  ✅ Sprendimas teisingas!                                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  UŽDUOTIS 2 (4/8 taškų) ⚠                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Apskaičiuokite: (12 + 8) ÷ 4 × 2                               │   │
│  │                                                                  │   │
│  │  MOKINIO SPRENDIMAS:                                            │   │
│  │  (12 + 8) ÷ 4 × 2                                               │   │
│  │  = 20 ÷ 4 × 2                                                   │   │
│  │  = 20 ÷ 8      ← ❌ KLAIDA: Neteisingas veiksmų eiliškumas     │   │
│  │  = 2.5                                                          │   │
│  │                                                                  │   │
│  │  ─────────────────────────────────────────────────────────────  │   │
│  │                                                                  │   │
│  │  ❌ KLAIDOS PAAIŠKINIMAS:                                       │   │
│  │  Dalybos ir daugybos veiksmai atliekami iš kairės į dešinę.    │   │
│  │  Todėl pirmiausia reikia padalinti 20 ÷ 4 = 5,                 │   │
│  │  o tada dauginti 5 × 2 = 10.                                    │   │
│  │                                                                  │   │
│  │  ─────────────────────────────────────────────────────────────  │   │
│  │                                                                  │   │
│  │  ✅ TEISINGI SPRENDIMO BŪDAI:                                   │   │
│  │                                                                  │   │
│  │  1 būdas:                      2 būdas:                         │   │
│  │  (12 + 8) ÷ 4 × 2              (12 + 8) ÷ 4 × 2                 │   │
│  │  = 20 ÷ 4 × 2                  = 20 × 2 ÷ 4                     │   │
│  │  = 5 × 2                       = 40 ÷ 4                         │   │
│  │  = 10 ✓                        = 10 ✓                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  UŽDUOTIS 3 (6/8 taškų) ⚠                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  ...                                                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ═══════════════════════════════════════════════════════════════════    │
│                                                                          │
│  APIBENDRINIMAS                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  📊 Stipriosios pusės:                                          │   │
│  │  • Lygčių sprendimas                                            │   │
│  │  • Trupmenų suprastinimas                                       │   │
│  │                                                                  │   │
│  │  ⚠️ Tobulintinos sritys:                                        │   │
│  │  • Veiksmų eiliškumas                                           │   │
│  │  • Laipsnių savybės                                             │   │
│  │                                                                  │   │
│  │  💡 Rekomendacijos:                                             │   │
│  │  Rekomenduojama pakartoti veiksmų su skliausteliais taisykles. │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │     📥 ATSISIŲSTI PDF     │     🖨️ SPAUSDINTI                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.5 Mokinių sąrašas

```
┌─────────────────────────────────────────────────────────────────────────┐
│  HEADER                                                                  │
├──────────────────────┬──────────────────────────────────────────────────┤
│                      │                                                  │
│  SIDEBAR             │   👥 MOKINIAI                [+ Pridėti] [📥]    │
│                      │                                                  │
│                      │   ┌─────────────────────────────────────────┐   │
│                      │   │ 🔍 Ieškoti...            │ Klasė: Visos ▼│   │
│                      │   └─────────────────────────────────────────┘   │
│                      │                                                  │
│                      │   ┌───┬──────────────────┬───────┬────────┬───┐│
│                      │   │ # │ Mokinys          │ Klasė │Vidurkis│   ││
│                      │   ├───┼──────────────────┼───────┼────────┼───┤│
│                      │   │ 1 │ Jonaitis Jonas   │  7a   │  7.8   │🔍✏🗑│
│                      │   │ 2 │ Onaitė Ona       │  7a   │  8.5   │🔍✏🗑│
│                      │   │ 3 │ Petraitis Petras │  7a   │  6.2   │🔍✏🗑│
│                      │   │ 4 │ Kazlauskaitė Ema │  7b   │  9.1   │🔍✏🗑│
│                      │   │...│ ...              │  ...  │  ...   │...││
│                      │   └───┴──────────────────┴───────┴────────┴───┘│
│                      │                                                  │
│                      │   ◀ 1 2 3 4 5 ▶   Rodoma: 1-20 iš 147           │
│                      │                                                  │
└──────────────────────┴──────────────────────────────────────────────────┘
```

### 7.6 Statistikos puslapis

```
┌─────────────────────────────────────────────────────────────────────────┐
│  HEADER                                                                  │
├──────────────────────┬──────────────────────────────────────────────────┤
│                      │                                                  │
│  SIDEBAR             │   📊 STATISTIKA                                  │
│                      │                                                  │
│                      │   Laikotarpis: [2025-09-01] - [2026-01-10]       │
│                      │   Klasė: [7a ▼]  Mokinys: [Visi ▼]               │
│                      │                                                  │
│                      │   ┌──────────────────────────────────────────┐   │
│                      │   │                                          │   │
│                      │   │        PAŽYMIŲ DINAMIKA                  │   │
│                      │   │                                          │   │
│                      │   │    10 ┤                     ╭─╮          │   │
│                      │   │     9 ┤           ╭─╮   ╭─╮ │ │          │   │
│                      │   │     8 ┤   ╭─╮ ╭─╮ │ │───│ ╰─╯ │          │   │
│                      │   │     7 ┤───│ ╰─╯ ╰─╯ │       │ │          │   │
│                      │   │     6 ┤   │         │       ╰─╯          │   │
│                      │   │       └───┴─────────┴────────────────    │   │
│                      │   │        Rugs Spal Lapkr Gruod Saus        │   │
│                      │   │                                          │   │
│                      │   └──────────────────────────────────────────┘   │
│                      │                                                  │
│                      │   ┌────────────────────┐ ┌────────────────────┐  │
│                      │   │ TEMŲ ANALIZĖ       │ │ KLAIDŲ TIPAI       │  │
│                      │   │                    │ │                    │  │
│                      │   │ Lygtys      ██████ │ │ Skaičiavimo  45%  │  │
│                      │   │ Trupmenos   ████   │ │ Ženklo       23%  │  │
│                      │   │ Geometrija  ███    │ │ Formulės     18%  │  │
│                      │   │ Procentai   ██     │ │ Logikos      14%  │  │
│                      │   └────────────────────┘ └────────────────────┘  │
│                      │                                                  │
└──────────────────────┴──────────────────────────────────────────────────┘
```

---

## 8. IKONOS

### Naudojama biblioteka
**Lucide React** - švarūs, modernūs, lengvi

### Pagrindinės ikonos
```
🏠 Home          → <Home />
👥 Users         → <Users />
🏫 School        → <School />
📝 FileText      → <FileText />
📤 Upload        → <Upload />
📊 BarChart      → <BarChart />
📑 FileReport    → <FileCheck />
⚙️ Settings      → <Settings />
🔍 Search        → <Search />
➕ Plus          → <Plus />
✏️ Edit          → <Pencil />
🗑️ Delete        → <Trash2 />
✓ Check         → <Check />
✕ X             → <X />
⚠️ Warning       → <AlertTriangle />
📥 Download      → <Download />
🖨️ Print         → <Printer />
📅 Calendar      → <Calendar />
🔄 Refresh       → <RefreshCw />
```

---

## 9. ANIMACIJOS

### Principai
- Subtilios, greitos (150-300ms)
- Natūralus easing: `ease-out`, `ease-in-out`
- Nemašalinti UX

### CSS animacijos
```css
/* Fade in */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Slide up */
@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(10px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

/* Scale */
@keyframes scale {
  from { transform: scale(0.95); }
  to { transform: scale(1); }
}

/* Spinner */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

### Tailwind config
```js
module.exports = {
  theme: {
    extend: {
      animation: {
        'fade-in': 'fadeIn 0.2s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'scale': 'scale 0.2s ease-out',
      }
    }
  }
}
```

---

## 10. RESPONSIVE BREAKPOINTS

```css
/* Tailwind defaults */
sm: 640px   /* Telefonai landscape */
md: 768px   /* Tabletai */
lg: 1024px  /* Mažesni laptopai */
xl: 1280px  /* Desktop */
2xl: 1536px /* Dideli ekranai */
```

### Elgsena
- **< 768px**: Sidebar paslepiamas, hamburger meniu
- **768px - 1024px**: Collapsed sidebar (tik ikonos)
- **> 1024px**: Full sidebar

---

## 11. ACCESSIBILITY (A11Y)

### Reikalavimai
- Kontrastas: min 4.5:1 (tekstas), 3:1 (UI elementai)
- Focus visible: aiškus outline
- Keyboard navigation: Tab, Enter, Escape
- ARIA labels: visiems interaktyviems elementams
- Alt tekstai: visiems vaizdams

### Focus stilius
```css
:focus-visible {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}
```

---

## 12. LOADING STATES

### Skeleton loaders
```
┌──────────────────────────────────────┐
│ ████████████████                     │  Animuotas pilkas fonas
│ ██████████                           │
│                                      │
│ ████████████████████████████████     │
│ ████████████████████████             │
└──────────────────────────────────────┘
```

### Spinner
```
    ◠◡◠
```
- Dydis: 24px (sm), 32px (md), 48px (lg)
- Spalva: `--primary-500`

### Progress bar (ilgiems veiksmams)
```
Apdorojama: 3/10 puslapių...
████████████░░░░░░░░░░░░░░░░░░░ 30%
```

---

## 13. ERROR STATES

### Tuščias sąrašas
```
┌──────────────────────────────────────┐
│                                      │
│           📭                         │
│                                      │
│    Mokinių sąrašas tuščias          │
│                                      │
│    [+ Pridėti mokinį]               │
│                                      │
└──────────────────────────────────────┘
```

### Klaida
```
┌──────────────────────────────────────┐
│                                      │
│           ⚠️                         │
│                                      │
│    Nepavyko užkrauti duomenų        │
│                                      │
│    [🔄 Bandyti dar kartą]           │
│                                      │
└──────────────────────────────────────┘
```

---

**Dokumentas sukurtas:** 2026-01-10
**Paskutinis atnaujinimas:** 2026-01-10
**Versija:** 1.0
