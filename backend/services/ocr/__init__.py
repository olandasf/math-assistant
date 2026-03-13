"""
OCR servisai - Gemini Vision, OpenAI GPT Vision, Novita.ai Vision.

Supaprastinta architektūra (2026-01-16):
- AI Vision = "Akys" (multimodalus, supranta kontekstą)
- SymPy = "Smegenys" (tikrina matematiką 100% tiksliai)

Palaikomi tiekėjai:
- Gemini Vision (Google) - nemokamas su Vertex AI
- OpenAI GPT Vision (GPT-5.2) - mokamas, bet tikslus
- Novita.ai Vision (Qwen3 VL) - mokamas, OpenAI-suderinama API
"""

from .gemini_vision import (
    GeminiVisionClient,
    GeminiVisionResult,
    get_gemini_vision_client,
)
from .novita_vision import (
    NovitaVisionClient,
    NovitaVisionResult,
    get_novita_vision_client,
    reset_novita_vision_client,
)
from .ocr_service import (
    OCRResult,
    OCRService,
    OCRSource,
    get_ocr_service,
    reset_ocr_service,
)
from .openai_vision import (
    OpenAIVisionClient,
    OpenAIVisionResult,
    get_openai_vision_client,
)

__all__ = [
    # Gemini Vision
    "GeminiVisionClient",
    "GeminiVisionResult",
    "get_gemini_vision_client",
    # OpenAI Vision
    "OpenAIVisionClient",
    "OpenAIVisionResult",
    "get_openai_vision_client",
    # Novita Vision
    "NovitaVisionClient",
    "NovitaVisionResult",
    "get_novita_vision_client",
    "reset_novita_vision_client",
    # OCR Service
    "OCRService",
    "OCRSource",
    "OCRResult",
    "get_ocr_service",
    "reset_ocr_service",
]
