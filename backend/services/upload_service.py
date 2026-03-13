"""
Failų įkėlimo servisas.
Tvarko mokinių darbų įkėlimą ir saugojimą.
"""

import logging
import shutil
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

try:
    import fitz  # PyMuPDF
    from PIL import Image

    HAS_PDF_SUPPORT = True
except ImportError:
    HAS_PDF_SUPPORT = False
    Image = None
    fitz = None

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class UploadedFile:
    """Įkelto failo informacija."""

    id: str
    original_name: str
    saved_path: str
    file_type: str  # image, pdf
    size_bytes: int
    pages: int = 1
    image_paths: Optional[List[str]] = (
        None  # Keliai iki vaizdų (PDF atveju - kiekvieno puslapio)
    )

    def __post_init__(self):
        if self.image_paths is None:
            self.image_paths = [self.saved_path]


@dataclass
class ProcessingResult:
    """Apdorojimo rezultatas."""

    file_id: str
    success: bool
    message: str
    processed_images: Optional[List[str]] = None
    errors: Optional[List[str]] = None


class UploadService:
    """Failų įkėlimo ir apdorojimo servisas."""

    ALLOWED_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".tiff",
        ".tif",
        ".bmp",
        ".webp",
        ".pdf",
    }
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

    def __init__(self, upload_dir: Optional[Path] = None):
        """
        Inicializuoja upload servisą.

        Args:
            upload_dir: Įkeltų failų direktorija
        """
        self.upload_dir = upload_dir or Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        # Sukuriame subdirektorijas
        (self.upload_dir / "original").mkdir(exist_ok=True)
        (self.upload_dir / "processed").mkdir(exist_ok=True)
        (self.upload_dir / "pages").mkdir(exist_ok=True)

    async def save_file(
        self,
        file_content: bytes,
        filename: str,
        student_id: Optional[int] = None,
        test_id: Optional[int] = None,
    ) -> UploadedFile:
        """
        Išsaugo įkeltą failą.

        Args:
            file_content: Failo turinys
            filename: Originalus failo vardas
            student_id: Mokinio ID (pasirinktinai)
            test_id: Kontrolinio ID (pasirinktinai)

        Returns:
            UploadedFile objektas
        """
        # Validuojame
        extension = Path(filename).suffix.lower()
        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Nepalaikomas failo formatas: {extension}")

        if len(file_content) > self.MAX_FILE_SIZE:
            raise ValueError(
                f"Failas per didelis. Maksimalus dydis: {self.MAX_FILE_SIZE // 1024 // 1024} MB"
            )

        # Generuojame unikalų ID
        file_id = str(uuid.uuid4())

        # Sukuriame subdirektoriją pagal datą
        date_dir = datetime.now().strftime("%Y-%m-%d")
        save_dir = self.upload_dir / "original" / date_dir
        save_dir.mkdir(parents=True, exist_ok=True)

        # Sukuriame failo vardą
        safe_filename = f"{file_id}{extension}"
        save_path = save_dir / safe_filename

        logger.debug(f"Saugomas failas: {save_path}, dydis: {len(file_content)} bytes")

        # Išsaugome failą
        try:
            with open(save_path, "wb") as f:
                f.write(file_content)
        except OSError as e:
            logger.error(f"Failo išsaugojimo klaida: {e}, kelias: {save_path}")
            # Bandome su absoliučiu keliu
            abs_path = save_path.resolve()
            logger.info(f"Bandome su absoliučiu keliu: {abs_path}")
            with open(abs_path, "wb") as f:
                f.write(file_content)

        # Nustatome tipą
        file_type = "pdf" if extension == ".pdf" else "image"

        # Jei PDF - konvertuojame į vaizdus
        pages = 1
        image_paths = [str(save_path)]

        if file_type == "pdf" and HAS_PDF_SUPPORT:
            try:
                image_paths, pages = await self._convert_pdf_to_images(
                    save_path, file_id
                )
            except Exception as e:
                logger.error(f"PDF konvertavimo klaida: {e}")
                # Paliekame originalų PDF

        logger.info(f"Failas išsaugotas: {save_path} (ID: {file_id})")

        return UploadedFile(
            id=file_id,
            original_name=filename,
            saved_path=str(save_path),
            file_type=file_type,
            size_bytes=len(file_content),
            pages=pages,
            image_paths=image_paths,
        )

    async def _convert_pdf_to_images(
        self,
        pdf_path: Path,
        file_id: str,
        dpi: int = 200,
    ) -> tuple[list[str], int]:
        """
        Konvertuoja PDF į vaizdus.

        Args:
            pdf_path: Kelias iki PDF failo
            file_id: Failo ID
            dpi: Vaizdo kokybė

        Returns:
            Tuple[kelių sąrašas, puslapių skaičius]
        """
        if not HAS_PDF_SUPPORT:
            return [str(pdf_path)], 1

        pages_dir = self.upload_dir / "pages" / file_id
        pages_dir.mkdir(parents=True, exist_ok=True)

        image_paths = []
        doc = fitz.open(pdf_path)

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            # Konvertuojame į vaizdą
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat)

            # Išsaugome
            image_path = pages_dir / f"page_{page_num + 1:03d}.png"
            pix.save(str(image_path))

            image_paths.append(str(image_path))

        doc.close()

        return image_paths, len(image_paths)

    async def delete_file(self, file_id: str) -> bool:
        """
        Ištrina failą ir visus susijusius vaizdus.

        Args:
            file_id: Failo ID

        Returns:
            True jei pavyko ištrinti
        """
        deleted = False

        # Ieškome originalo
        for date_dir in (self.upload_dir / "original").iterdir():
            if date_dir.is_dir():
                for file in date_dir.iterdir():
                    if file.stem.startswith(file_id):
                        file.unlink()
                        deleted = True
                        break

        # Ištriname puslapius
        pages_dir = self.upload_dir / "pages" / file_id
        if pages_dir.exists():
            shutil.rmtree(pages_dir)
            deleted = True

        # Ištriname apdorotus
        processed_dir = self.upload_dir / "processed"
        for file in processed_dir.iterdir():
            if file.stem.startswith(file_id):
                file.unlink()
                deleted = True

        return deleted

    async def get_file_info(self, file_id: str) -> Optional[UploadedFile]:
        """
        Grąžina failo informaciją.

        Args:
            file_id: Failo ID

        Returns:
            UploadedFile arba None
        """
        # Ieškome originalo
        for date_dir in (self.upload_dir / "original").iterdir():
            if date_dir.is_dir():
                for file in date_dir.iterdir():
                    if file.stem == file_id:
                        extension = file.suffix.lower()
                        file_type = "pdf" if extension == ".pdf" else "image"

                        # Ieškome puslapių
                        pages_dir = self.upload_dir / "pages" / file_id
                        image_paths = [str(file)]
                        pages = 1

                        if pages_dir.exists():
                            image_paths = sorted(
                                [str(p) for p in pages_dir.glob("*.png")]
                            )
                            pages = len(image_paths)

                        return UploadedFile(
                            id=file_id,
                            original_name=file.name,
                            saved_path=str(file),
                            file_type=file_type,
                            size_bytes=file.stat().st_size,
                            pages=pages,
                            image_paths=image_paths,
                        )

        return None

    def get_storage_stats(self) -> dict:
        """Grąžina saugyklos statistiką."""
        total_files = 0
        total_size = 0

        for path in self.upload_dir.rglob("*"):
            if path.is_file():
                total_files += 1
                total_size += path.stat().st_size

        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
        }


# Singleton instance
_upload_service: Optional[UploadService] = None


def get_upload_service() -> UploadService:
    """Grąžina UploadService singleton instanciją."""
    global _upload_service
    if _upload_service is None:
        _upload_service = UploadService()
    return _upload_service
