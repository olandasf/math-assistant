"""
OCR servisas - Gemini Vision arba OpenAI GPT Vision.
Supaprastinta architektūra: AI Vision = Akys, SymPy = Smegenys.
"""

import logging
import sqlite3
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from config import BASE_DIR

from .gemini_vision import GeminiVisionResult, get_gemini_vision_client
from .novita_vision import NovitaVisionResult, get_novita_vision_client
from .openai_vision import OpenAIVisionResult, get_openai_vision_client
from .together_vision import TogetherVisionResult, get_together_vision_client

logger = logging.getLogger(__name__)


class OCRSource(str, Enum):
    """OCR šaltiniai."""

    GEMINI_VISION = "gemini"
    OPENAI_VISION = "openai"
    NOVITA_VISION = "novita"
    TOGETHER_VISION = "together"


def _get_ocr_provider_from_db() -> str:
    """Gauti OCR tiekėją iš duomenų bazės."""
    try:
        db_path = BASE_DIR / "database" / "math_teacher.db"
        if not db_path.exists():
            return "gemini"
        conn = sqlite3.connect(str(db_path), timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'ocr_provider'")
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception as e:
        logger.warning(f"Nepavyko nuskaityti OCR tiekėjo iš DB: {e}")
    return "gemini"


@dataclass
class OCRResult:
    """OCR rezultatas."""

    text: str
    latex: Optional[str] = None
    confidence: float = 0.0
    source: Optional[OCRSource] = None
    processing_time_ms: int = 0
    is_math: bool = False
    gemini_result: Optional[GeminiVisionResult] = None
    openai_result: Optional[OpenAIVisionResult] = None
    novita_result: Optional[NovitaVisionResult] = None
    together_result: Optional[TogetherVisionResult] = None
    warnings: list[str] = field(default_factory=list)


class OCRService:
    """
    OCR servisas naudojantis Gemini Vision arba OpenAI GPT Vision.

    Architektūra:
    - AI Vision = "Akys" (supranta kontekstą, ignoruoja braukymus)
    - SymPy = "Smegenys" (tikrina matematiką 100% tiksliai)

    AI NIEKADA neskaičiuoja - tik transkribuoja.
    """

    def __init__(self):
        """Inicializuoja OCR servisą."""
        self.gemini_vision = get_gemini_vision_client()
        self.openai_vision = get_openai_vision_client()
        self.novita_vision = get_novita_vision_client()
        self.together_vision = get_together_vision_client()
        self.current_provider = _get_ocr_provider_from_db()

        available_providers = []
        if self.gemini_vision.available:
            available_providers.append("Gemini")
        if self.openai_vision.available:
            available_providers.append("OpenAI")
        if self.novita_vision.available:
            available_providers.append("Novita")
        if self.together_vision.available:
            available_providers.append("Together")

        if not available_providers:
            logger.warning("⚠️ Joks OCR tiekėjas nepasiekiamas! OCR neveiks.")
        else:
            logger.info(
                f"✅ OCR servisas paruoštas ({', '.join(available_providers)}), "
                f"aktyvus: {self.current_provider}"
            )

    @property
    def available(self) -> bool:
        """Ar OCR pasiekiamas."""
        return (
            self.gemini_vision.available
            or self.openai_vision.available
            or self.novita_vision.available
            or self.together_vision.available
        )

    def get_available_sources(self) -> list[OCRSource]:
        """Grąžina pasiekiamus OCR šaltinius."""
        sources = []
        if self.gemini_vision.available:
            sources.append(OCRSource.GEMINI_VISION)
        if self.openai_vision.available:
            sources.append(OCRSource.OPENAI_VISION)
        if self.novita_vision.available:
            sources.append(OCRSource.NOVITA_VISION)
        if self.together_vision.available:
            sources.append(OCRSource.TOGETHER_VISION)
        return sources

    def get_current_provider(self) -> str:
        """Grąžina dabartinį OCR tiekėją."""
        return _get_ocr_provider_from_db()

    async def recognize(
        self,
        image_path: str,
        prefer_source: Optional[OCRSource] = None,
        detect_math: bool = True,
    ) -> OCRResult:
        """
        Atpažįsta tekstą ir matematiką vaizde.

        Args:
            image_path: Kelias iki vaizdo
            prefer_source: Pageidaujamas šaltinis (jei None - naudoja nustatymą iš DB)
            detect_math: Ignoruojamas (visada tikrina matematiką)

        Returns:
            OCRResult su atpažinimo rezultatu
        """
        start = time.time()
        warnings = []

        # Nustatome kurį tiekėją naudoti
        provider = self.get_current_provider()
        if prefer_source:
            provider = prefer_source.value

        logger.info(f"🔍 OCR pradedamas su tiekėju: {provider}")

        # Lazy re-inicializacija jei klientas nepasiekiamas
        # (gali būti kad API raktas buvo nustatytas po inicializacijos)
        if provider == "openai" and not self.openai_vision.available:
            logger.info("🔄 OpenAI klientas nepasiekiamas, bandome re-inicializuoti...")
            self.openai_vision._try_api_key()
        elif provider == "gemini" and not self.gemini_vision.available:
            logger.info("🔄 Gemini klientas nepasiekiamas, bandome re-inicializuoti...")
            self.gemini_vision._try_api_key()
        elif provider == "novita" and not self.novita_vision.available:
            logger.info("🔄 Novita klientas nepasiekiamas, bandome re-inicializuoti...")
            self.novita_vision._try_api_key()
        elif provider == "together" and not self.together_vision.available:
            logger.info("🔄 Together klientas nepasiekiamas, bandome re-inicializuoti...")
            self.together_vision._try_api_key()

        # Bandome pasirinktą tiekėją
        result = await self._try_provider(provider, image_path, start, warnings)
        if result:
            return result

        # Pasirinktas tiekėjas neveikia - grąžiname klaidą SU tiekėjo vardu (BE fallback!)
        source_map = {
            "gemini": OCRSource.GEMINI_VISION,
            "openai": OCRSource.OPENAI_VISION,
            "novita": OCRSource.NOVITA_VISION,
            "together": OCRSource.TOGETHER_VISION,
        }
        error_msg = "; ".join(warnings) if warnings else f"OCR tiekėjas '{provider}' nepasiekiamas"
        logger.error(
            f"❌ OCR tiekėjas '{provider}' neveikia! "
            f"Gemini available: {self.gemini_vision.available}, "
            f"OpenAI available: {self.openai_vision.available}, "
            f"Novita available: {self.novita_vision.available}, "
            f"Together available: {self.together_vision.available}"
        )
        return OCRResult(
            text=f"Klaida: {error_msg}",
            source=source_map.get(provider),
            warnings=warnings or [f"OCR tiekėjas '{provider}' nepasiekiamas. Patikrinkite API raktus Nustatymuose."],
            processing_time_ms=int((time.time() - start) * 1000),
        )

    async def _try_provider(
        self,
        provider: str,
        image_path: str,
        start: float,
        warnings: list[str],
    ) -> Optional[OCRResult]:
        """Bando atlikti OCR su nurodytu tiekėju. Grąžina None jei nepavyko."""

        # Novita Vision
        if provider == "novita":
            if not self.novita_vision.available:
                logger.warning(
                    f"⚠️ Novita tiekėjas pasirinktas, bet nepasiekiamas! "
                    f"Patikrinkite ar API raktas nustatytas."
                )
                warnings.append("Novita API raktas nenurodytas arba neteisingas")
                return None
            try:
                novita_result = await self.novita_vision.recognize(image_path)
                processing_time = int((time.time() - start) * 1000)

                if novita_result.text:
                    logger.info(
                        f"✅ Novita OCR atliktas: {len(novita_result.text)} simbolių, "
                        f"{processing_time}ms"
                    )
                    return OCRResult(
                        text=novita_result.text,
                        latex=novita_result.latex,
                        confidence=novita_result.confidence,
                        source=OCRSource.NOVITA_VISION,
                        processing_time_ms=processing_time,
                        is_math=novita_result.is_math,
                        novita_result=novita_result,
                    )
                else:
                    warnings.append("Novita Vision negrąžino teksto")
            except Exception as e:
                logger.error(f"Novita OCR klaida: {e}")
                warnings.append(f"Novita klaida: {str(e)}")
            return None

        # OpenAI Vision
        if provider == "openai":
            if not self.openai_vision.available:
                logger.warning(
                    f"⚠️ OpenAI tiekėjas pasirinktas, bet nepasiekiamas! "
                    f"Patikrinkite ar API raktas nustatytas."
                )
                warnings.append("OpenAI API raktas nenurodytas arba neteisingas")
                return None
            try:
                openai_result = await self.openai_vision.recognize(image_path)
                processing_time = int((time.time() - start) * 1000)

                if openai_result.text:
                    logger.info(
                        f"✅ OpenAI OCR atliktas: {len(openai_result.text)} simbolių, "
                        f"{processing_time}ms"
                    )
                    return OCRResult(
                        text=openai_result.text,
                        latex=openai_result.latex,
                        confidence=openai_result.confidence,
                        source=OCRSource.OPENAI_VISION,
                        processing_time_ms=processing_time,
                        is_math=openai_result.is_math,
                        openai_result=openai_result,
                    )
                else:
                    warnings.append("OpenAI Vision negrąžino teksto")
            except Exception as e:
                logger.error(f"OpenAI OCR klaida: {e}")
                warnings.append(f"OpenAI klaida: {str(e)}")
            return None

        # Gemini Vision
        if provider == "gemini":
            if not self.gemini_vision.available:
                logger.warning(
                    f"⚠️ Gemini tiekėjas pasirinktas, bet nepasiekiamas! "
                    f"Patikrinkite ar API raktas arba credentials nustatyti."
                )
                warnings.append("Gemini API raktas/credentials nenurodyti")
                return None
            try:
                gemini_result = await self.gemini_vision.recognize(image_path)
                processing_time = int((time.time() - start) * 1000)

                if gemini_result.text:
                    logger.info(
                        f"✅ Gemini OCR atliktas: {len(gemini_result.text)} simbolių, "
                        f"{processing_time}ms"
                    )
                    return OCRResult(
                        text=gemini_result.text,
                        latex=gemini_result.latex,
                        confidence=gemini_result.confidence,
                        source=OCRSource.GEMINI_VISION,
                        processing_time_ms=processing_time,
                        is_math=gemini_result.is_math,
                        gemini_result=gemini_result,
                    )
                else:
                    warnings.append("Gemini Vision negrąžino teksto")
            except Exception as e:
                logger.error(f"Gemini OCR klaida: {e}")
                warnings.append(f"Gemini klaida: {str(e)}")
            return None

        # Together.ai Vision
        if provider == "together":
            if not self.together_vision.available:
                logger.warning(
                    f"⚠️ Together tiekėjas pasirinktas, bet nepasiekiamas! "
                    f"Patikrinkite ar API raktas nustatytas."
                )
                warnings.append("Together API raktas nenurodytas arba neteisingas")
                return None
            try:
                together_result = await self.together_vision.recognize(image_path)
                processing_time = int((time.time() - start) * 1000)

                if together_result.text:
                    logger.info(
                        f"✅ Together OCR atliktas: {len(together_result.text)} simbolių, "
                        f"{processing_time}ms"
                    )
                    return OCRResult(
                        text=together_result.text,
                        latex=together_result.latex,
                        confidence=together_result.confidence,
                        source=OCRSource.TOGETHER_VISION,
                        processing_time_ms=processing_time,
                        together_result=together_result,
                    )
                else:
                    warnings.append("Together Vision negrąžino teksto")
            except Exception as e:
                logger.error(f"Together OCR klaida: {e}")
                warnings.append(f"Together klaida: {str(e)}")
            return None

        logger.warning(f"Nežinomas OCR tiekėjas: {provider}")
        return None


# Singleton
_ocr_service: Optional[OCRService] = None


def get_ocr_service() -> OCRService:
    """Gauna OCR servisą."""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service


def reset_ocr_service():
    """Perkrauna OCR servisą IR visus vision klientus (naudojama kai keičiasi nustatymai)."""
    global _ocr_service
    _ocr_service = None

    # SVARBU: Taip pat perkrauname visus vision klientų singleton'us
    # kad nauji API raktai būtų paimti iš DB
    from .gemini_vision import get_gemini_vision_client
    from .novita_vision import reset_novita_vision_client
    from .openai_vision import get_openai_vision_client

    # Reset Gemini singleton
    import services.ocr.gemini_vision as _gv
    _gv._gemini_vision = None

    # Reset OpenAI singleton
    import services.ocr.openai_vision as _ov
    _ov._openai_vision = None

    # Reset Novita singleton
    reset_novita_vision_client()

    # Reset Together singleton
    from .together_vision import reset_together_vision_client
    reset_together_vision_client()

    logger.info("🔄 OCR servisas ir visi vision klientai perkrauti")
