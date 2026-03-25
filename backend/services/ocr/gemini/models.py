"""Gemini Vision OCR data models."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class GeminiVisionResult:
    """Gemini Vision OCR rezultatas."""
    text: str
    latex: Optional[str] = None
    confidence: float = 0.85
    is_math: bool = False
    processing_time_ms: int = 0
