from .models import GeminiVisionResult
from .client import GeminiVisionClient

_gemini_vision_client = None

def get_gemini_vision_client() -> GeminiVisionClient:
    """Gauna arba sukuria Gemini Vision API klientą (Singleton)."""
    global _gemini_vision_client
    if _gemini_vision_client is None:
        _gemini_vision_client = GeminiVisionClient()
    return _gemini_vision_client

__all__ = ["GeminiVisionResult", "GeminiVisionClient", "get_gemini_vision_client"]