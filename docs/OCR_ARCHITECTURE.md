# 🔍 OCR Architektūra - Gemini Vision

**Atnaujinta:** 2026-01-16

---

## 📋 Apžvalga

Sistema naudoja **supaprastintą OCR architektūrą** su vienu šaltiniu:

```
┌─────────────────────────────────────────────────────────┐
│                    MOKINIO DARBAS                       │
│                   (PDF / Nuotrauka)                     │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              GEMINI VISION ("AKYS")                     │
│  • Multimodalus AI - supranta kontekstą                 │
│  • Ignoruoja braukymus ir stulpelinius skaičiavimus     │
│  • Grąžina struktūrizuotą JSON su užduotimis            │
│  • Lietuvių kalbos palaikymas                           │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                SYMPY ("SMEGENYS")                       │
│  • 100% tikslus matematikos tikrinimas                  │
│  • Simbolinė algebra                                    │
│  • Klaidos tipo identifikavimas                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🗑️ Pašalinti komponentai

Šie OCR servisai buvo **pašalinti** kaip nereikalingi:

| Failas | Priežastis |
|--------|------------|
| `tesseract_ocr.py` | Lokalus OCR - prastas matematikos atpažinimas |
| `google_vision.py` | Cloud Vision API - perteklinis, Gemini geriau |
| `mathpix_client.py` | Mokamas servisas - Gemini nemokamas su Vertex AI |

---

## 📁 Dabartinė struktūra

```
backend/services/ocr/
├── __init__.py          # Eksportai
├── gemini_vision.py     # Pagrindinis OCR servisas
└── ocr_service.py       # Wrapper su vieninga sąsaja
```

---

## 🔧 Gemini Vision konfigūracija

### Vertex AI (rekomenduojama)

```python
# Automatiškai naudoja credentials failą
# backend/mtematika-471410-e4cb6af744ea.json
```

### API Key (alternatyva)

```python
# Saugomas duomenų bazėje: settings.gemini_api_key
```

---

## 📤 OCR Rezultato formatas

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

### LaTeX formatas

Užduotys atskiriamos `§§§` separatoriumi:

```
1a) -\frac{5}{2} \cdot (-\frac{3}{13}) = 12 Ats. 12§§§1b) \frac{2}{3} \cdot (-16) = ? Ats. -368
```

---

## 🔄 Dublikatų šalinimas

Sistema automatiškai pašalina dublikatus keliose vietose:

1. **gemini_vision.py** - JSON lygmenyje
2. **upload.py** - sujungiant puslapius
3. **WorkReviewPage.tsx** - frontend'e

---

## 📊 Privalumai

| Aspektas | Senas (Multi-OCR) | Naujas (Gemini Only) |
|----------|-------------------|----------------------|
| Kompleksiškumas | Aukštas | Žemas |
| Palaikymas | Sudėtingas | Paprastas |
| Tikslumas | Vidutinis | Aukštas |
| Kaina | Mokama (MathPix) | Nemokama (Vertex AI) |
| Konteksto supratimas | Ne | Taip |

---

## 🚀 Naudojimas

```python
from services.ocr import get_ocr_service

ocr = get_ocr_service()
result = await ocr.recognize("image.png")

print(result.text)   # Atpažintas tekstas
print(result.latex)  # LaTeX formatas
```

---

*Dokumentas atnaujintas: 2026-01-16*
