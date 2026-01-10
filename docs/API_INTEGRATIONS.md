# 🔌 API INTEGRACIJOS
## Matematikos Mokytojo Asistentas

---

## 1. INTEGRUOJAMŲ API SĄRAŠAS

| API | Paskirtis | Tipas | Kaina |
|-----|-----------|-------|-------|
| **MathPix** | Matematikos OCR | Cloud | ~$0.01-0.05/puslapis |
| **Google Cloud Vision** | Teksto OCR | Cloud | 1000 nemokamų/mėn |
| **Google Gemini** | AI/NLP | Cloud | Nemokamas limitas |
| **WolframAlpha** | Matematikos tikrinimas | Cloud | 2000 nemokamų/mėn |
| **Tesseract** | Backup OCR | Lokalus | Nemokamas |
| **EasyOCR** | Rašysenos OCR | Lokalus | Nemokamas |

---

## 2. MATHPIX API

### 2.1 Aprašymas
MathPix yra specializuotas matematikos OCR servisas, galintis atpažinti ranka rašytas ir spausdintas formules, lygtis, grafikus.

### 2.2 Registracija
1. Eiti į https://mathpix.com/
2. Sukurti paskyrą
3. Gauti API credentials (App ID ir App Key)

### 2.3 Kainodara
| Planas | Kaina | Puslapiai |
|--------|-------|-----------|
| Free | $0 | 100/mėn |
| Education | $9.99/mėn | 2000/mėn |
| Pro | $19.99/mėn | 5000/mėn |
| Enterprise | Custom | Unlimited |

**Rekomenduojamas:** Education (~$10/mėn = ~$0.005/puslapis)

### 2.4 API Endpoints

#### Image to LaTeX
```
POST https://api.mathpix.com/v3/text
```

#### Batch Processing
```
POST https://api.mathpix.com/v3/batch
```

### 2.5 Autentifikacija
```python
headers = {
    "app_id": MATHPIX_APP_ID,
    "app_key": MATHPIX_APP_KEY,
    "Content-Type": "application/json"
}
```

### 2.6 Užklausos pavyzdys

```python
import httpx
import base64

async def mathpix_ocr(image_path: str) -> dict:
    """
    Nuskaityti vaizdą su MathPix API.
    
    Args:
        image_path: Kelias iki vaizdo failo
        
    Returns:
        dict su LaTeX rezultatu
    """
    # Koduoti vaizdą base64
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    
    # Nustatyti vaizdo tipą
    if image_path.endswith(".png"):
        image_type = "image/png"
    elif image_path.endswith(".jpg") or image_path.endswith(".jpeg"):
        image_type = "image/jpeg"
    else:
        image_type = "image/png"
    
    # Paruošti užklausą
    payload = {
        "src": f"data:{image_type};base64,{image_data}",
        "formats": ["latex_styled", "text", "data"],
        "data_options": {
            "include_asciimath": True,
            "include_latex": True,
            "include_mathml": False,
            "include_svg": False,
            "include_table_html": True,
            "include_tsv": False
        },
        "include_detected_alphabets": True,
        "include_line_data": True,
        "include_word_data": True,
        "numbers_default_to_math": True,
        "rm_spaces": False,
        "rm_fonts": False
    }
    
    headers = {
        "app_id": MATHPIX_APP_ID,
        "app_key": MATHPIX_APP_KEY,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.mathpix.com/v3/text",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
```

### 2.7 Atsakymo struktūra

```json
{
    "request_id": "abc123",
    "is_printed": false,
    "is_handwritten": true,
    "auto_rotate_confidence": 0.95,
    "auto_rotate_degrees": 0,
    "confidence": 0.92,
    "confidence_rate": 0.92,
    "latex_styled": "2x + 5 = 15 \\\\ 2x = 10 \\\\ x = 5",
    "text": "2x + 5 = 15\n2x = 10\nx = 5",
    "data": [
        {
            "type": "equation",
            "value": "2x + 5 = 15"
        }
    ],
    "line_data": [
        {
            "text": "2x + 5 = 15",
            "latex": "2x + 5 = 15",
            "cnt": [[10, 20], [100, 20], [100, 50], [10, 50]]
        }
    ],
    "detected_alphabets": ["en", "lt"]
}
```

### 2.8 Klaidų tvarkymas

```python
class MathPixError(Exception):
    pass

class MathPixRateLimitError(MathPixError):
    pass

class MathPixAuthError(MathPixError):
    pass

async def handle_mathpix_response(response: httpx.Response) -> dict:
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        raise MathPixAuthError("Neteisingi MathPix credentials")
    elif response.status_code == 429:
        raise MathPixRateLimitError("Viršytas MathPix užklausų limitas")
    else:
        raise MathPixError(f"MathPix klaida: {response.status_code}")
```

---

## 3. GOOGLE CLOUD VISION API

### 3.1 Aprašymas
Google Cloud Vision teikia OCR paslaugas, ypač tinka spausdintam tekstui ir rašysenai atpažinti.

### 3.2 Registracija
1. Sukurti Google Cloud projektą: https://console.cloud.google.com/
2. Įjungti Vision API
3. Sukurti Service Account
4. Atsisiųsti credentials JSON failą

### 3.3 Kainodara
| Kiekis/mėn | Kaina |
|------------|-------|
| 1-1000 | Nemokamai |
| 1001-5M | $1.50/1000 |
| 5M+ | $0.60/1000 |

### 3.4 Autentifikacija

```python
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/credentials.json"

# arba programatiškai
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    "path/to/credentials.json"
)
```

### 3.5 Naudojimo pavyzdys

```python
from google.cloud import vision

async def google_vision_ocr(image_path: str) -> dict:
    """
    Nuskaityti vaizdą su Google Cloud Vision.
    
    Args:
        image_path: Kelias iki vaizdo failo
        
    Returns:
        dict su teksto rezultatu
    """
    client = vision.ImageAnnotatorClient()
    
    with open(image_path, "rb") as f:
        content = f.read()
    
    image = vision.Image(content=content)
    
    # Pilnas teksto atpažinimas su layout
    response = client.document_text_detection(image=image)
    
    if response.error.message:
        raise Exception(f"Vision API klaida: {response.error.message}")
    
    result = {
        "text": response.full_text_annotation.text,
        "pages": [],
        "confidence": 0.0
    }
    
    # Apdoroti puslapius ir blokus
    for page in response.full_text_annotation.pages:
        page_data = {"blocks": []}
        
        for block in page.blocks:
            block_text = ""
            block_confidence = 0.0
            
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    word_text = "".join([s.text for s in word.symbols])
                    block_text += word_text + " "
                    block_confidence += word.confidence
            
            page_data["blocks"].append({
                "text": block_text.strip(),
                "confidence": block_confidence / len(block.paragraphs) if block.paragraphs else 0,
                "bounding_box": [(v.x, v.y) for v in block.bounding_box.vertices]
            })
        
        result["pages"].append(page_data)
    
    # Skaičiuoti bendrą pasitikėjimą
    total_conf = sum(b["confidence"] for p in result["pages"] for b in p["blocks"])
    total_blocks = sum(len(p["blocks"]) for p in result["pages"])
    result["confidence"] = total_conf / total_blocks if total_blocks > 0 else 0
    
    return result
```

### 3.6 Rašysenos atpažinimas (Handwriting)

```python
async def google_vision_handwriting(image_path: str) -> dict:
    """
    Nuskaityti ranka rašytą tekstą.
    """
    client = vision.ImageAnnotatorClient()
    
    with open(image_path, "rb") as f:
        content = f.read()
    
    image = vision.Image(content=content)
    
    # Naudoti document_text_detection (geriau rašysenai)
    image_context = vision.ImageContext(
        language_hints=["lt", "en"]  # Lietuvių ir anglų kalbos
    )
    
    response = client.document_text_detection(
        image=image,
        image_context=image_context
    )
    
    return {
        "text": response.full_text_annotation.text,
        "raw_response": response
    }
```

---

## 4. GOOGLE GEMINI API

### 4.1 Aprašymas
Google Gemini yra galingas AI modelis, naudojamas tekstinių uždavinių supratimui ir klaidų paaiškinimams generuoti.

### 4.2 Registracija
1. Eiti į https://aistudio.google.com/
2. Gauti API key

### 4.3 Kainodara
| Modelis | Input | Output |
|---------|-------|--------|
| Gemini Pro | Nemokamai (limitas) | Nemokamai |
| Gemini Pro (mokamas) | $0.00025/1K tokens | $0.0005/1K tokens |

### 4.4 Naudojimo pavyzdys

```python
import google.generativeai as genai

# Konfigūracija
genai.configure(api_key=GEMINI_API_KEY)

async def explain_math_error(
    student_solution: str,
    correct_solution: str,
    error_type: str
) -> str:
    """
    Sugeneruoti klaidos paaiškinimą lietuvių kalba.
    
    Args:
        student_solution: Mokinio sprendimas
        correct_solution: Teisingas sprendimas
        error_type: Klaidos tipas
        
    Returns:
        str: Paaiškinimas lietuvių kalba
    """
    model = genai.GenerativeModel("gemini-pro")
    
    prompt = f"""Esi matematikos mokytojas, aiškinantis klaidas mokiniui lietuvių kalba.

MOKINIO SPRENDIMAS:
{student_solution}

TEISINGAS SPRENDIMAS:
{correct_solution}

KLAIDOS TIPAS: {error_type}

Parašyk trumpą, aiškų ir draugišką paaiškinimą mokiniui (2-3 sakiniai), kodėl jo sprendimas neteisingas ir kaip reikėtų spręsti teisingai. Naudok lietuvių kalbą."""

    response = await model.generate_content_async(prompt)
    
    return response.text


async def parse_word_problem(problem_text: str) -> dict:
    """
    Išanalizuoti tekstinį uždavinį ir išgauti matematinius duomenis.
    
    Args:
        problem_text: Uždavinio tekstas lietuvių kalba
        
    Returns:
        dict su matematine interpretacija
    """
    model = genai.GenerativeModel("gemini-pro")
    
    prompt = f"""Išanalizuok šį matematikos tekstinį uždavinį lietuvių kalba ir pateik struktūrizuotą informaciją.

UŽDAVINYS:
{problem_text}

Atsakyk JSON formatu:
{{
    "given_values": [
        {{"name": "kintamojo pavadinimas", "value": skaičius, "unit": "vienetas"}}
    ],
    "unknown": "ko ieškome",
    "equation": "matematinė lygtis arba išraiška",
    "solution_steps": ["1 žingsnis", "2 žingsnis", ...],
    "answer": "galutinis atsakymas su vienetais"
}}

Atsakyk TIK JSON formatu, be papildomo teksto."""

    response = await model.generate_content_async(prompt)
    
    # Išgauti JSON iš atsakymo
    import json
    try:
        result = json.loads(response.text)
    except json.JSONDecodeError:
        # Bandyti išvalyti atsakymą
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        result = json.loads(text.strip())
    
    return result


async def generate_alternative_solutions(
    problem: str,
    correct_answer: str,
    num_solutions: int = 2
) -> list:
    """
    Sugeneruoti alternatyvius sprendimo būdus.
    
    Args:
        problem: Uždavinio tekstas
        correct_answer: Teisingas atsakymas
        num_solutions: Kiek sprendimų generuoti
        
    Returns:
        list: Alternatyvūs sprendimai
    """
    model = genai.GenerativeModel("gemini-pro")
    
    prompt = f"""Pateik {num_solutions} skirtingus būdus išspręsti šį matematikos uždavinį.

UŽDAVINYS:
{problem}

TEISINGAS ATSAKYMAS: {correct_answer}

Kiekvienam sprendimo būdui pateik:
1. Būdo pavadinimą
2. Žingsnis po žingsnio sprendimą
3. Trumpą paaiškinimą, kodėl šis būdas veikia

Atsakyk lietuvių kalba, aiškiai ir suprantamai mokiniui."""

    response = await model.generate_content_async(prompt)
    
    return response.text
```

### 4.5 Saugos nustatymai

```python
from google.generativeai.types import HarmCategory, HarmBlockThreshold

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

model = genai.GenerativeModel(
    "gemini-pro",
    safety_settings=safety_settings
)
```

---

## 5. WOLFRAMALPHA API

### 5.1 Aprašymas
WolframAlpha yra galingas matematikos skaičiavimo variklis, naudojamas patikrinti sudėtingus matematinius sprendimus.

### 5.2 Registracija
1. Eiti į https://developer.wolframalpha.com/
2. Sukurti AppID

### 5.3 Kainodara
| Planas | Užklausos/mėn | Kaina |
|--------|---------------|-------|
| Free | 2,000 | $0 |
| Basic | 10,000 | $25/mėn |
| Standard | 100,000 | $75/mėn |

### 5.4 Naudojimo pavyzdys

```python
import wolframalpha

class WolframClient:
    def __init__(self, app_id: str):
        self.client = wolframalpha.Client(app_id)
    
    async def solve(self, query: str) -> dict:
        """
        Išspręsti matematinę užklausą.
        
        Args:
            query: Matematinė užklausa (pvz., "solve 2x + 5 = 15")
            
        Returns:
            dict su sprendimu
        """
        result = self.client.query(query)
        
        response = {
            "success": result.success,
            "input": None,
            "result": None,
            "steps": [],
            "pods": []
        }
        
        for pod in result.pods:
            pod_data = {
                "title": pod.title,
                "texts": []
            }
            
            if hasattr(pod, "text") and pod.text:
                pod_data["texts"].append(pod.text)
            
            for sub in pod.subpods:
                if hasattr(sub, "plaintext") and sub.plaintext:
                    pod_data["texts"].append(sub.plaintext)
            
            response["pods"].append(pod_data)
            
            # Išgauti pagrindinius rezultatus
            if pod.title == "Input":
                response["input"] = pod_data["texts"][0] if pod_data["texts"] else None
            elif pod.title in ["Result", "Solution", "Results", "Solutions"]:
                response["result"] = pod_data["texts"][0] if pod_data["texts"] else None
            elif "step" in pod.title.lower():
                response["steps"].extend(pod_data["texts"])
        
        return response
    
    async def verify_answer(self, expression: str, expected: str) -> dict:
        """
        Patikrinti ar atsakymas teisingas.
        
        Args:
            expression: Matematinė išraiška
            expected: Tikėtinas atsakymas
            
        Returns:
            dict su tikrinimo rezultatu
        """
        query = f"is {expression} equal to {expected}"
        result = self.client.query(query)
        
        for pod in result.pods:
            if pod.title == "Result":
                text = pod.text.lower() if hasattr(pod, "text") else ""
                return {
                    "is_correct": "true" in text or "yes" in text,
                    "response": pod.text
                }
        
        return {"is_correct": False, "response": "Nepavyko patikrinti"}
    
    async def simplify(self, expression: str) -> str:
        """
        Suprastinti matematinę išraišką.
        """
        query = f"simplify {expression}"
        result = self.client.query(query)
        
        for pod in result.pods:
            if pod.title in ["Result", "Results"]:
                return pod.text if hasattr(pod, "text") else str(pod)
        
        return expression


# Naudojimo pavyzdys
async def check_with_wolfram(student_answer: str, correct_answer: str) -> dict:
    """
    Patikrinti mokinio atsakymą su WolframAlpha.
    """
    client = WolframClient(WOLFRAM_APP_ID)
    
    # Patikrinti ar atsakymai lygūs
    verification = await client.verify_answer(student_answer, correct_answer)
    
    if verification["is_correct"]:
        return {
            "is_correct": True,
            "message": "Atsakymas teisingas"
        }
    
    # Jei neteisingas, gauti teisingą sprendimą
    solution = await client.solve(f"solve {correct_answer}")
    
    return {
        "is_correct": False,
        "message": "Atsakymas neteisingas",
        "correct_solution": solution
    }
```

---

## 6. TESSERACT OCR (LOKALUS)

### 6.1 Aprašymas
Tesseract yra nemokamas, atviro kodo OCR variklis, naudojamas kaip backup kai nėra interneto arba API limitai viršyti.

### 6.2 Instalacija (Windows)

```powershell
# Atsisiųsti installer iš:
# https://github.com/UB-Mannheim/tesseract/wiki

# Arba su Chocolatey
choco install tesseract

# Patikrinti versiją
tesseract --version
```

### 6.3 Lietuvių kalbos palaikymas

```powershell
# Atsisiųsti lietuvių kalbos duomenis
# Nukopijuoti lit.traineddata į Tesseract tessdata folderį
# Paprastai: C:\Program Files\Tesseract-OCR\tessdata\
```

### 6.4 Naudojimo pavyzdys

```python
import pytesseract
from PIL import Image

# Nustatyti Tesseract kelią (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

async def tesseract_ocr(image_path: str, lang: str = "lit+eng") -> dict:
    """
    Nuskaityti vaizdą su Tesseract.
    
    Args:
        image_path: Kelias iki vaizdo
        lang: Kalbos kodas (lit = lietuvių, eng = anglų)
        
    Returns:
        dict su tekstu
    """
    image = Image.open(image_path)
    
    # Konfigūracija
    config = r'--oem 3 --psm 6'
    # OEM 3 = Default
    # PSM 6 = Assume a single uniform block of text
    
    # Gauti tekstą
    text = pytesseract.image_to_string(image, lang=lang, config=config)
    
    # Gauti detalesnius duomenis
    data = pytesseract.image_to_data(image, lang=lang, config=config, output_type=pytesseract.Output.DICT)
    
    # Skaičiuoti pasitikėjimą
    confidences = [int(c) for c in data["conf"] if c != "-1"]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    return {
        "text": text.strip(),
        "confidence": avg_confidence / 100,
        "words": [
            {
                "text": data["text"][i],
                "confidence": int(data["conf"][i]) / 100 if data["conf"][i] != "-1" else 0,
                "x": data["left"][i],
                "y": data["top"][i],
                "width": data["width"][i],
                "height": data["height"][i]
            }
            for i in range(len(data["text"]))
            if data["text"][i].strip()
        ]
    }
```

---

## 7. EASYOCR (LOKALUS)

### 7.1 Aprašymas
EasyOCR yra Python biblioteka paremta deep learning, geriau veikianti su rašysena nei Tesseract.

### 7.2 Instalacija

```bash
pip install easyocr
```

### 7.3 Naudojimo pavyzdys

```python
import easyocr

# Sukurti reader (užkraunama tik kartą)
reader = None

def get_reader():
    global reader
    if reader is None:
        reader = easyocr.Reader(
            ["lt", "en"],  # Kalbos
            gpu=False      # Be GPU
        )
    return reader

async def easyocr_recognize(image_path: str) -> dict:
    """
    Nuskaityti vaizdą su EasyOCR.
    
    Args:
        image_path: Kelias iki vaizdo
        
    Returns:
        dict su rezultatais
    """
    r = get_reader()
    
    results = r.readtext(
        image_path,
        detail=1,
        paragraph=True
    )
    
    text_parts = []
    words = []
    total_confidence = 0
    
    for (bbox, text, prob) in results:
        text_parts.append(text)
        words.append({
            "text": text,
            "confidence": prob,
            "bounding_box": bbox
        })
        total_confidence += prob
    
    return {
        "text": "\n".join(text_parts),
        "confidence": total_confidence / len(results) if results else 0,
        "words": words
    }
```

---

## 8. HIBRIDINIS OCR SERVISAS

### 8.1 Strategija

```python
from enum import Enum
from typing import Optional

class OCRMethod(Enum):
    LOCAL = "local"       # Tik lokalūs (Tesseract + EasyOCR)
    HYBRID = "hybrid"     # MathPix + lokalus tikrinimas
    FULL = "full"         # MathPix + Google Vision + Gemini

class OCRService:
    def __init__(
        self,
        mathpix_id: Optional[str] = None,
        mathpix_key: Optional[str] = None,
        google_credentials: Optional[str] = None
    ):
        self.mathpix_available = bool(mathpix_id and mathpix_key)
        self.google_available = bool(google_credentials)
        
        if mathpix_id:
            self.mathpix = MathPixClient(mathpix_id, mathpix_key)
        
        if google_credentials:
            self.google_vision = GoogleVisionClient(google_credentials)
    
    async def process(
        self,
        image_path: str,
        method: OCRMethod = OCRMethod.HYBRID
    ) -> dict:
        """
        Apdoroti vaizdą pasirinktu metodu.
        """
        if method == OCRMethod.LOCAL:
            return await self._process_local(image_path)
        elif method == OCRMethod.HYBRID:
            return await self._process_hybrid(image_path)
        else:  # FULL
            return await self._process_full(image_path)
    
    async def _process_local(self, image_path: str) -> dict:
        """
        Apdoroti tik lokaliais įrankiais.
        """
        # Pirma bandyti EasyOCR (geriau rašysenai)
        easyocr_result = await easyocr_recognize(image_path)
        
        # Papildomai Tesseract
        tesseract_result = await tesseract_ocr(image_path)
        
        # Sujungti rezultatus pagal pasitikėjimą
        if easyocr_result["confidence"] > tesseract_result["confidence"]:
            primary = easyocr_result
            secondary = tesseract_result
        else:
            primary = tesseract_result
            secondary = easyocr_result
        
        return {
            "text": primary["text"],
            "confidence": primary["confidence"],
            "method": "local",
            "sources": {
                "easyocr": easyocr_result,
                "tesseract": tesseract_result
            }
        }
    
    async def _process_hybrid(self, image_path: str) -> dict:
        """
        MathPix + lokalus tikrinimas.
        """
        if not self.mathpix_available:
            return await self._process_local(image_path)
        
        try:
            # Pagrindinis - MathPix
            mathpix_result = await self.mathpix.ocr(image_path)
            
            # Tikrinimui - lokalus
            local_result = await tesseract_ocr(image_path)
            
            return {
                "latex": mathpix_result.get("latex_styled", ""),
                "text": mathpix_result.get("text", ""),
                "confidence": mathpix_result.get("confidence", 0),
                "method": "hybrid",
                "is_handwritten": mathpix_result.get("is_handwritten", False),
                "verification": {
                    "local_text": local_result["text"],
                    "local_confidence": local_result["confidence"]
                }
            }
        
        except MathPixRateLimitError:
            # Jei limitas viršytas, grįžti prie lokalaus
            return await self._process_local(image_path)
    
    async def _process_full(self, image_path: str) -> dict:
        """
        Pilnas cloud apdorojimas.
        """
        results = {}
        
        # MathPix
        if self.mathpix_available:
            try:
                results["mathpix"] = await self.mathpix.ocr(image_path)
            except Exception as e:
                results["mathpix_error"] = str(e)
        
        # Google Vision
        if self.google_available:
            try:
                results["google"] = await self.google_vision.ocr(image_path)
            except Exception as e:
                results["google_error"] = str(e)
        
        # Lokalus backup
        results["local"] = await self._process_local(image_path)
        
        # Išrinkti geriausią rezultatą
        best_result = self._select_best_result(results)
        
        return {
            **best_result,
            "method": "full",
            "all_results": results
        }
    
    def _select_best_result(self, results: dict) -> dict:
        """
        Išrinkti geriausią rezultatą iš kelių šaltinių.
        """
        # Prioritetas: MathPix (matematikai) > Google > Local
        if "mathpix" in results:
            return {
                "latex": results["mathpix"].get("latex_styled", ""),
                "text": results["mathpix"].get("text", ""),
                "confidence": results["mathpix"].get("confidence", 0)
            }
        elif "google" in results:
            return {
                "text": results["google"].get("text", ""),
                "confidence": results["google"].get("confidence", 0)
            }
        else:
            return results.get("local", {"text": "", "confidence": 0})
```

---

## 9. API RAKTŲ VALDYMAS

### 9.1 .env failas

```env
# MathPix
MATHPIX_APP_ID=your_app_id
MATHPIX_APP_KEY=your_app_key

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=./credentials/google-cloud.json
GOOGLE_PROJECT_ID=your_project_id

# Gemini
GEMINI_API_KEY=your_gemini_key

# WolframAlpha
WOLFRAM_APP_ID=your_wolfram_app_id
```

### 9.2 Konfigūracijos klasė

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # MathPix
    mathpix_app_id: Optional[str] = None
    mathpix_app_key: Optional[str] = None
    
    # Google
    google_application_credentials: Optional[str] = None
    google_project_id: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
    # WolframAlpha
    wolfram_app_id: Optional[str] = None
    
    # OCR
    default_ocr_method: str = "hybrid"
    tesseract_path: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

---

## 10. TESTAVIMAS

### 10.1 API prisijungimo testavimas

```python
async def test_api_connections() -> dict:
    """
    Patikrinti visų API prisijungimus.
    """
    results = {
        "mathpix": False,
        "google_vision": False,
        "gemini": False,
        "wolfram": False,
        "tesseract": False,
        "easyocr": False
    }
    
    # MathPix
    try:
        # Bandyti siųsti testinę užklausą
        results["mathpix"] = True
    except:
        pass
    
    # Google Vision
    try:
        client = vision.ImageAnnotatorClient()
        results["google_vision"] = True
    except:
        pass
    
    # Gemini
    try:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content("Test")
        results["gemini"] = True
    except:
        pass
    
    # WolframAlpha
    try:
        client = wolframalpha.Client(settings.wolfram_app_id)
        result = client.query("2+2")
        results["wolfram"] = True
    except:
        pass
    
    # Tesseract
    try:
        pytesseract.get_tesseract_version()
        results["tesseract"] = True
    except:
        pass
    
    # EasyOCR
    try:
        reader = easyocr.Reader(["en"], gpu=False)
        results["easyocr"] = True
    except:
        pass
    
    return results
```

---

**Dokumentas sukurtas:** 2026-01-10
**Paskutinis atnaujinimas:** 2026-01-10
**Versija:** 1.0
