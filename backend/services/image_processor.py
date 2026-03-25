"""
Vaizdo apdorojimo servisas.
Normalizuoja ir paruošia vaizdus OCR apdorojimui.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Tuple

# Tipizavimui - tik linting metu
if TYPE_CHECKING:
    import numpy as np

try:
    import cv2
    import numpy as np
    from PIL import Image

    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    cv2 = None
    np = None
    Image = None

logger = logging.getLogger(__name__)


class ImageFormat(Enum):
    """Palaikomi vaizdo formatai."""

    JPEG = "jpeg"
    PNG = "png"
    TIFF = "tiff"
    BMP = "bmp"
    WEBP = "webp"


@dataclass
class ProcessedImage:
    """Apdoroto vaizdo rezultatas."""

    original_path: str
    processed_path: str
    width: int
    height: int
    dpi: Optional[int] = None
    is_rotated: bool = False
    rotation_angle: float = 0.0
    preprocessing_applied: list = None

    def __post_init__(self):
        if self.preprocessing_applied is None:
            self.preprocessing_applied = []


class ImageProcessor:
    """Vaizdo apdorojimo klasė."""

    # Rekomenduojami parametrai OCR
    TARGET_DPI = 300
    MIN_DPI = 150
    MAX_IMAGE_SIZE = 4096  # Max dimensija pikseliais

    def __init__(self, output_dir: Path = None):
        """
        Inicializuoja vaizdo procesorių.

        Args:
            output_dir: Apdorotų vaizdų išsaugojimo direktorija
        """
        if not HAS_CV2:
            logger.warning("OpenCV neįdiegtas. Vaizdo apdorojimas bus ribotas.")

        self.output_dir = output_dir or Path("uploads/processed")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_image(
        self,
        image_path: str,
        normalize: bool = True,
        enhance_contrast: bool = True,
        remove_noise: bool = True,
        deskew: bool = True,
        binarize: bool = False,
    ) -> ProcessedImage:
        """
        Apdoroja vaizdą OCR atpažinimui.

        Args:
            image_path: Kelias iki originalaus vaizdo
            normalize: Ar normalizuoti spalvas
            enhance_contrast: Ar gerinti kontrastą
            remove_noise: Ar šalinti triukšmą
            deskew: Ar koreguoti pasukimą
            binarize: Ar konvertuoti į juoda-balta

        Returns:
            ProcessedImage objektas su informacija apie apdorojimą
        """
        if not HAS_CV2:
            # Grąžiname originalų vaizdą be apdorojimo
            logger.warning("OpenCV neįdiegtas, grąžinamas originalus vaizdas")
            return ProcessedImage(
                original_path=image_path,
                processed_path=image_path,
                width=0,
                height=0,
            )

        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Vaizdas nerastas: {image_path}")

        # Nuskaitome vaizdą
        image = cv2.imread(str(path))
        if image is None:
            raise ValueError(f"Nepavyko nuskaityti vaizdo: {image_path}")

        preprocessing = []
        original_height, original_width = image.shape[:2]

        # 1. Konvertuojame į pilką skalę darbui
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 2. Normalizuojame
        if normalize:
            gray = self._normalize(gray)
            preprocessing.append("normalize")

        # 3. Šaliname triukšmą
        if remove_noise:
            gray = self._remove_noise(gray)
            preprocessing.append("denoise")

        # 4. Koreguojame pasukimą
        rotation_angle = 0.0
        is_rotated = False
        if deskew:
            gray, rotation_angle = self._deskew(gray)
            is_rotated = abs(rotation_angle) > 0.5
            if is_rotated:
                preprocessing.append(f"deskew({rotation_angle:.1f}°)")

        # 5. Geriname kontrastą
        if enhance_contrast:
            gray = self._enhance_contrast(gray)
            preprocessing.append("contrast")

        # 6. Binarizuojame (pasirinktinai)
        if binarize:
            gray = self._binarize(gray)
            preprocessing.append("binarize")

        # Išsaugome apdorotą vaizdą
        # Konvertuojame atgal į 3 kanalų (BGR) vaizdą, nes kai kurios Vision API
        # nepalaiko 1-kanalo grayscale PNG formatų
        output_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        output_name = f"processed_{path.stem}.png"
        output_path = self.output_dir / output_name
        cv2.imwrite(str(output_path), output_image)

        height, width = gray.shape[:2]

        logger.info(f"Vaizdas apdorotas: {image_path} -> {output_path}")
        logger.debug(f"Pritaikyti apdorojimai: {preprocessing}")

        return ProcessedImage(
            original_path=str(path),
            processed_path=str(output_path),
            width=width,
            height=height,
            is_rotated=is_rotated,
            rotation_angle=rotation_angle,
            preprocessing_applied=preprocessing,
        )

    def _normalize(self, image: Any) -> Any:
        """Normalizuoja vaizdo intensyvumą."""
        return cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)

    def _remove_noise(self, image: Any) -> Any:
        """Šalina triukšmą naudojant Gaussian blur ir morphology."""
        # Lengvas Gaussian blur
        denoised = cv2.GaussianBlur(image, (3, 3), 0)
        return denoised

    def _enhance_contrast(self, image: Any) -> Any:
        """Gerina kontrastą naudojant CLAHE."""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(image)

    def _binarize(self, image: Any) -> Any:
        """Konvertuoja į juoda-balta naudojant adaptyvų slenkstį."""
        return cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,  # Block size
            2,  # C constant
        )

    def _deskew(self, image: Any) -> Tuple[Any, float]:
        """
        Koreguoja vaizdo pasukimą.

        Returns:
            Tuple[koreguotas vaizdas, pasukimo kampas]
        """
        # Aptinkame kraštines
        edges = cv2.Canny(image, 50, 150, apertureSize=3)

        # Hough transformacija linijoms rasti
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)

        if lines is None or len(lines) == 0:
            return image, 0.0

        # Apskaičiuojame vidutinį kampą
        angles = []
        for line in lines[:20]:  # Naudojame tik pirmas 20 linijų
            rho, theta = line[0]
            angle = np.degrees(theta) - 90
            if -45 < angle < 45:  # Ignoruojame vertikalias linijas
                angles.append(angle)

        if not angles:
            return image, 0.0

        median_angle = np.median(angles)

        # Sukame vaizdą
        if abs(median_angle) > 0.5:  # Sukame tik jei kampas didesnis nei 0.5°
            height, width = image.shape[:2]
            center = (width // 2, height // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
            rotated = cv2.warpAffine(
                image,
                rotation_matrix,
                (width, height),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE,
            )
            return rotated, median_angle

        return image, 0.0

    def resize_for_ocr(
        self,
        image_path: str,
        max_dimension: int = None,
    ) -> ProcessedImage:
        """
        Keičia vaizdo dydį optimaliam OCR apdorojimui.

        Args:
            image_path: Kelias iki vaizdo
            max_dimension: Maksimali dimensija (plotis arba aukštis)

        Returns:
            ProcessedImage su pakeisto dydžio vaizdu
        """
        if not HAS_CV2:
            return ProcessedImage(
                original_path=image_path,
                processed_path=image_path,
                width=0,
                height=0,
            )

        max_dim = max_dimension or self.MAX_IMAGE_SIZE

        image = cv2.imread(image_path)
        height, width = image.shape[:2]

        # Skaičiuojame naują dydį
        if width > max_dim or height > max_dim:
            scale = max_dim / max(width, height)
            new_width = int(width * scale)
            new_height = int(height * scale)

            resized = cv2.resize(
                image,
                (new_width, new_height),
                interpolation=cv2.INTER_AREA,
            )

            path = Path(image_path)
            output_name = f"resized_{path.stem}.png"
            output_path = self.output_dir / output_name
            cv2.imwrite(str(output_path), resized)

            return ProcessedImage(
                original_path=image_path,
                processed_path=str(output_path),
                width=new_width,
                height=new_height,
                preprocessing_applied=["resize"],
            )

        return ProcessedImage(
            original_path=image_path,
            processed_path=image_path,
            width=width,
            height=height,
        )

    def extract_regions(
        self,
        image_path: str,
        regions: list[Tuple[int, int, int, int]],
    ) -> list[str]:
        """
        Iškerpa nurodytas sritis iš vaizdo.

        Args:
            image_path: Kelias iki vaizdo
            regions: Lista sričių (x, y, width, height)

        Returns:
            Lista kelių iki iškarpytų vaizdų
        """
        if not HAS_CV2:
            return []

        image = cv2.imread(image_path)
        extracted_paths = []

        for i, (x, y, w, h) in enumerate(regions):
            region = image[y: y + h, x: x + w]

            path = Path(image_path)
            output_name = f"region_{i}_{path.stem}.png"
            output_path = self.output_dir / output_name
            cv2.imwrite(str(output_path), region)

            extracted_paths.append(str(output_path))

        return extracted_paths


# Singleton instance
_processor: Optional[ImageProcessor] = None


def get_image_processor() -> ImageProcessor:
    """Grąžina ImageProcessor singleton instanciją."""
    global _processor
    if _processor is None:
        _processor = ImageProcessor()
    return _processor
