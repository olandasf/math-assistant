# 🔍 OCR Architektūra — DI Vision

**Atnaujinta:** 2026-03-13

---

## 📋 Apžvalga

Sistema naudoja **DI (dirbtinio intelekto) Vision modelius** vietoj tradicinių OCR sprendimų.
Tai sąmoningas architektūrinis sprendimas — žr. [Kodėl ne tradicinis OCR?](#-kodėl-ne-tradicinis-ocr)

```
┌─────────────────────────────────────────────────────────┐
│                    MOKINIO DARBAS                        │
│                   (PDF / Nuotrauka)                      │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│           DI VISION TIEKĖJAI ("AKYS")                   │
│                                                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ Gemini       │ │ OpenAI GPT   │ │ Novita       │    │
│  │ Vision       │ │ Vision       │ │ Vision       │    │
│  │ (default)    │ │ (alternatyva)│ │ (alternatyva)│    │
│  └──────────────┘ └──────────────┘ └──────────────┘    │
│                                                         │
│  • Multimodalūs AI — supranta kontekstą                 │
│  • Ignoruoja braukymus ir taisymus                      │
│  • Grąžina struktūrizuotą JSON su užduotimis            │
│  • Lietuvių kalbos palaikymas                           │
│  • Fallback mechanizmas tarp tiekėjų                    │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                SYMPY ("SMEGENYS")                       │
│  • 100% tikslus matematikos tikrinimas                  │
│  • Simbolinė algebra                                    │
│  • Klaidos tipo identifikavimas                         │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│             GEMINI AI (PAAIŠKINIMAI)                    │
│  • Klaidos paaiškinimas lietuvių kalba                  │
│  • Patarimai kaip ištaisyti                             │
└─────────────────────────────────────────────────────────┘
```

---

## ❓ Kodėl ne tradicinis OCR?

Projekto tikslinė auditorija — **mokiniai nuo 5 iki 12 klasės**. Jų ranka rašyti darbai turi specifinių iššūkių, su kuriais tradiciniai OCR sprendimai (MathPix, Google Cloud Vision, Tesseract) nesusitvarko:

| Iššūkis | Tradicinis OCR | DI Vision |
|---------|----------------|-----------|
| **Netvarkingas raštas** — 11-metis rašo kitaip nei suaugęs | ❌ Prastas atpažinimas | ✅ Supranta kontekstą |
| **Braukymai ir taisymai** — mokiniai dažnai taiso atsakymus | ❌ Bando atpažinti viską | ✅ Ignoruoja braukymus, paima galutinį |
| **Stulpeliniai skaičiavimai** — dalyba, daugyba "stulpeliu" | ❌ Neskiria nuo atsakymo | ✅ Skiria darbo eigą nuo atsakymo |
| **Mišrus turinys** — piešiniai, formulės, tekstas viename lape | ❌ Painioja tipus | ✅ Supranta kiekvieną elementą atskirai |
| **Lietuviška matematika** — "Ats.", "Sprendimas:", "Nr." | ❌ Neatpažįsta struktūros | ✅ Supranta lietuvišką formatą |

### Pašalinti komponentai

| Failas | Priežastis |
|--------|------------|
| `tesseract_ocr.py` | Lokalus OCR — prastas ranka rašyto teksto atpažinimas |
| `google_vision.py` | Cloud Vision API — neatpažįsta braukymų konteksto |
| `mathpix_client.py` | Mokamas, optimizuotas tipografiniams šriftams, ne ranka rašytiems |

---

## 📁 Dabartinė struktūra

```
backend/services/ocr/
├── __init__.py          # Eksportai
├── ocr_service.py       # Pagrindinis OCR servisas (dispatcher + fallback)
├── gemini_vision.py     # Google Gemini Vision (37 KB)
├── openai_vision.py     # OpenAI GPT-4 Vision (21 KB)
└── novita_vision.py     # Novita AI Vision (22 KB)
```

---

## 🔧 Tiekėjų konfigūracija

Aktyvus tiekėjas pasirenkamas per **nustatymus UI** arba duomenų bazės lentelę `settings`:

```python
# OCR tiekėjas saugomas DB:
# settings.ocr_provider = "gemini" | "openai" | "novita"
```

Kiekvienas tiekėjas turi savo API raktą (`gemini_api_key`, `openai_api_key`, `novita_api_key`), saugomą `settings` lentelėje.

### Fallback logika

```
Pasirinktas tiekėjas → Jei nepavyko → Gemini Vision (default fallback)
```

Jei nei vienas tiekėjas nepasiekiamas, grąžinamas tuščias `OCRResult` su `warnings`.

---

## 📤 OCR rezultato formatas

### JSON (struktūrizuotas)

```json
{
  "tasks": [
    {
      "number": "1a",
      "question_text": null,
      "student_work": "-52 * (-3/13) = 52 * 3/13 = 12",
      "final_answer": "12"
    }
  ]
}
```

### LaTeX

Užduotys atskiriamos `§§§` separatoriumi:

```
1a) -\frac{5}{2} \cdot (-\frac{3}{13}) = 12 Ats. 12§§§1b) ...
```

---

## 🔑 Principas: AI NIEKADA neskaičiuoja

> **AI Vision = „Akys"** — tik transkribuoja tai, ką mato lape.
> **SymPy = „Smegenys"** — tikrina matematiką 100% tiksliai.
>
> Šis atskyrimas užtikrina, kad AI haluciacijos neįtakoja tikrinimo rezultatų.

---

## 🔄 Dublikatų šalinimas

Sistema automatiškai pašalina dublikatus keliose vietose:

1. **gemini_vision.py** — JSON lygmenyje
2. **upload.py** — sujungiant puslapius
3. **WorkReviewPage.tsx** — frontende

---

## 🚀 Naudojimas

```python
from services.ocr import get_ocr_service

ocr = get_ocr_service()
result = await ocr.recognize("image.png")

print(result.text)       # Atpažintas tekstas
print(result.latex)      # LaTeX formatas
print(result.source)     # "gemini" | "openai" | "novita"
print(result.confidence) # 0.0 - 1.0
```

---

*Dokumentas atnaujintas: 2026-03-13*
