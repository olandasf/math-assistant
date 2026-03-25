"""
API Router - Failų įkėlimas ir OCR apdorojimas.
"""

from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from loguru import logger
from pydantic import BaseModel
from services.image_processor import get_image_processor
from services.ocr import OCRSource, get_ocr_service
from services.upload_service import get_upload_service

router = APIRouter(prefix="/upload", tags=["upload"])


# === Response Models ===


class UploadResponse(BaseModel):
    """Įkėlimo atsakymas."""

    file_id: str
    original_name: str
    file_type: str
    pages: int
    size_bytes: int
    message: str


class OCRRequest(BaseModel):
    """OCR užklausa."""

    file_id: str
    page: int = 1
    source: Optional[str] = None  # gemini_vision (vienintelis palaikomas)
    detect_math: bool = True


class OCRResponse(BaseModel):
    """OCR atsakymas."""

    file_id: str
    page: int
    text: str
    latex: Optional[str] = None
    confidence: float
    source: str
    is_math: bool
    processing_time_ms: int
    warnings: list[str] = []


class StorageStatsResponse(BaseModel):
    """Saugyklos statistika."""

    total_files: int
    total_size_bytes: int
    total_size_mb: float


# === Endpoints ===


@router.post("/", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    student_id: Optional[int] = Form(None),
    test_id: Optional[int] = Form(None),
):
    """
    Įkelia mokinių darbų failą.

    Palaiko formatus: JPG, PNG, TIFF, BMP, WEBP, PDF
    Maksimalus dydis: 50 MB
    """
    try:
        upload_service = get_upload_service()

        # Nuskaitome failo turinį
        content = await file.read()

        # Diagnostika
        logger.info(
            f"Įkeliamas failas: {file.filename}, dydis: {len(content)} bytes, content_type: {file.content_type}"
        )

        if len(content) == 0:
            raise ValueError("Failas tuščias")

        # Išsaugome
        result = await upload_service.save_file(
            file_content=content,
            filename=file.filename,
            student_id=student_id,
            test_id=test_id,
        )

        return UploadResponse(
            file_id=result.id,
            original_name=result.original_name,
            file_type=result.file_type,
            pages=result.pages,
            size_bytes=result.size_bytes,
            message="Failas sėkmingai įkeltas",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Įkėlimo klaida: {e}")
        raise HTTPException(status_code=500, detail="Nepavyko įkelti failo")


@router.post("/batch", response_model=list[UploadResponse])
async def upload_multiple_files(
    files: list[UploadFile] = File(...),
    test_id: Optional[int] = Form(None),
):
    """
    Įkelia kelis failus vienu metu.
    """
    upload_service = get_upload_service()
    results = []

    for file in files:
        try:
            content = await file.read()
            result = await upload_service.save_file(
                file_content=content,
                filename=file.filename,
                test_id=test_id,
            )
            results.append(
                UploadResponse(
                    file_id=result.id,
                    original_name=result.original_name,
                    file_type=result.file_type,
                    pages=result.pages,
                    size_bytes=result.size_bytes,
                    message="OK",
                )
            )
        except Exception as e:
            results.append(
                UploadResponse(
                    file_id="",
                    original_name=file.filename,
                    file_type="error",
                    pages=0,
                    size_bytes=0,
                    message=str(e),
                )
            )

    return results


@router.get("/stats/storage", response_model=StorageStatsResponse)
async def get_storage_stats():
    """
    Grąžina saugyklos statistiką.
    """
    upload_service = get_upload_service()
    stats = upload_service.get_storage_stats()

    return StorageStatsResponse(**stats)


@router.get("/ocr/sources")
async def get_ocr_sources():
    """
    Grąžina pasiekiamus OCR šaltinius.
    """
    try:
        logger.info("OCR sources endpoint called")
        ocr_service = get_ocr_service()
        logger.info(
            f"OCR service: {ocr_service}, available: {ocr_service.available if ocr_service else 'None'}"
        )
        sources = ocr_service.get_available_sources()
        logger.info(f"Sources: {sources}")

        return {
            "available": [s.value for s in sources],
            "recommended": "gemini_vision",
        }
    except Exception as e:
        import traceback

        logger.error(f"OCR sources klaida: {e}")
        logger.error(traceback.format_exc())
        return {
            "available": [],
            "recommended": "gemini_vision",
            "error": str(e),
        }


@router.get("/{file_id}")
async def get_file_info(file_id: str):
    """
    Grąžina įkelto failo informaciją.
    """
    upload_service = get_upload_service()
    result = await upload_service.get_file_info(file_id)

    if not result:
        raise HTTPException(status_code=404, detail="Failas nerastas")

    return {
        "file_id": result.id,
        "original_name": result.original_name,
        "file_type": result.file_type,
        "pages": result.pages,
        "size_bytes": result.size_bytes,
        "image_paths": result.image_paths,
    }


@router.get("/{file_id}/page/{page_num}")
async def get_page_image(file_id: str, page_num: int):
    """
    Grąžina konkretaus puslapio vaizdą.
    """
    upload_service = get_upload_service()
    file_info = await upload_service.get_file_info(file_id)

    if not file_info:
        raise HTTPException(status_code=404, detail="Failas nerastas")

    if page_num < 1 or page_num > len(file_info.image_paths):
        raise HTTPException(status_code=404, detail="Puslapis nerastas")

    image_path = file_info.image_paths[page_num - 1]
    return FileResponse(image_path)


@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """
    Ištrina įkeltą failą.
    """
    upload_service = get_upload_service()
    deleted = await upload_service.delete_file(file_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Failas nerastas")

    return {"message": "Failas ištrintas"}


class OCRAllPagesRequest(BaseModel):
    """OCR visų puslapių užklausa."""

    file_id: str
    detect_math: bool = True


class OCRAllPagesResponse(BaseModel):
    """OCR visų puslapių atsakymas."""

    file_id: str
    pages: int
    text: str  # Sujungtas tekstas iš visų puslapių
    latex: Optional[str] = None  # Sujungtas LaTeX
    confidence: float
    source: str
    is_math: bool
    processing_time_ms: int
    warnings: List[str] = []


@router.post("/ocr/all-pages", response_model=OCRAllPagesResponse)
async def perform_ocr_all_pages(request: OCRAllPagesRequest):
    """
    Atlieka OCR atpažinimą VISIEMS failo puslapiams ir sujungia rezultatus.
    """
    logger.info(f"🔍 OCR all-pages užklausa: file_id={request.file_id}")

    upload_service = get_upload_service()
    file_info = await upload_service.get_file_info(request.file_id)

    if not file_info:
        raise HTTPException(status_code=404, detail="Failas nerastas")

    logger.info(
        f"📄 Failas rastas: {file_info.original_name}, puslapių: {len(file_info.image_paths)}"
    )

    ocr_service = get_ocr_service()
    image_processor = get_image_processor()

    all_text = []
    all_latex = []
    all_warnings = []
    total_confidence = 0.0
    total_time = 0
    # Dinamiškai nustatome source pagal OCR provider iš DB
    source = "unknown"
    is_math = False

    # Apdorojame kiekvieną puslapį
    for page_num, image_path in enumerate(file_info.image_paths, 1):
        logger.info(
            f"📖 Apdorojamas puslapis {page_num}/{len(file_info.image_paths)}: {image_path}"
        )

        # Apdorojame vaizdą
        processed = image_processor.process_image(
            image_path,
            normalize=True,
            enhance_contrast=True,
            remove_noise=True,
            deskew=True,
        )

        # OCR - naudojame apdorotą vaizdą (visada PNG formatas, kurį visos API palaiko)
        result = await ocr_service.recognize(
            processed.processed_path,
            detect_math=request.detect_math,
        )

        logger.info(
            f"✅ Puslapis {page_num} OCR: {len(result.text)} simbolių, latex: {len(result.latex) if result.latex else 0}"
        )

        if result.text:
            all_text.append(f"--- Puslapis {page_num} ---\n{result.text}")
        if result.latex:
            all_latex.append(result.latex)

        total_confidence += result.confidence
        total_time += result.processing_time_ms
        all_warnings.extend(result.warnings)

        if result.is_math:
            is_math = True
        if result.source:
            source = result.source.value if hasattr(result.source, 'value') else str(result.source)

    # Sujungiame rezultatus
    combined_text = "\n\n".join(all_text)

    # PATAISYMAS: Prieš sujungiant, konvertuojame antro puslapio užduotis su tik raidėmis
    # į pilnus ID (pvz. "c)" -> "5c)" jei pirmo puslapio paskutinė užduotis buvo "5b)")
    import re

    def fix_letter_only_task_ids(latex_pages: list) -> list:
        """
        Patikrina ar antrame ir vėlesniuose puslapiuose yra užduočių su tik raidėmis
        (pvz. "c)", "d)", "e)") ir konvertuoja jas į pilnus ID pagal pirmo puslapio
        paskutinį užduoties numerį.
        """
        if len(latex_pages) < 2:
            return latex_pages

        fixed_pages = [latex_pages[0]]  # Pirmas puslapis lieka nepakeistas

        # Randame paskutinį užduoties numerį iš pirmo puslapio
        # SVARBU: Ieškome tik užduočių ID formatu - pradžioje eilutės arba po §§§
        # Pattern: (pradžia arba §§§) + tarpai + skaičius + raidė + )
        first_page = latex_pages[0]
        task_pattern = re.compile(r"(?:^|§§§)\s*(\d+)[a-z]?\)", re.IGNORECASE)
        matches = list(task_pattern.finditer(first_page))

        if not matches:
            logger.warning("fix_letter_only_task_ids: Pirmo puslapio užduočių nerasta")
            return latex_pages

        # Paskutinis numeris iš pirmo puslapio - imame didžiausią rastą
        last_task_num = max(int(m.group(1)) for m in matches)
        logger.info(
            f"fix_letter_only_task_ids: Pirmo puslapio paskutinis numeris: {last_task_num}"
        )

        # Apdorojame kitus puslapius
        for page_idx, page_latex in enumerate(latex_pages[1:], 2):
            # Ieškome užduočių su tik raidėmis: "c)", "d)", "e)" (bet ne "5c)", "6a)")
            # Pattern: pradžia arba §§§ + tarpai + VIENA raidė + )
            letter_only_pattern = re.compile(r"(^|§§§)\s*([a-z])\)", re.IGNORECASE)

            def replace_letter_only(match):
                prefix = match.group(1)  # "" arba "§§§"
                letter = match.group(2).lower()
                new_id = f"{prefix}{last_task_num}{letter})"
                logger.info(
                    f"fix_letter_only_task_ids: Konvertuota '{letter})' -> '{last_task_num}{letter})'"
                )
                return new_id

            fixed_page = letter_only_pattern.sub(replace_letter_only, page_latex)
            fixed_pages.append(fixed_page)

        return fixed_pages

    # Taikome pataisymą
    if len(all_latex) > 1:
        all_latex = fix_letter_only_task_ids(all_latex)

    # Naudojame §§§ separatorių tarp puslapių LaTeX (tas pats kaip tarp užduočių)
    combined_latex = "§§§".join(all_latex) if all_latex else None

    # DEBUG: Log combined latex
    if combined_latex:
        logger.info(
            f"📝 Combined LaTeX length: {len(combined_latex)}, has §§§: {'§§§' in combined_latex}"
        )
        logger.debug(f"📝 Combined LaTeX first 200 chars: {combined_latex[:200]}")

    # Pašaliname dublikatus iš LaTeX
    if combined_latex:
        import re

        # PIRMA: Pašaliname inline dublikatus (kai tas pats task ID kartojasi)
        # SVARBU: Task ID turi būti eilutės pradžioje arba po §§§ separatoriaus
        # Negalima atitikti skaičių LaTeX išraiškose kaip \frac{7}{15}
        def remove_inline_duplicates(text: str) -> str:
            if not text:
                return text

            # Skaidome pagal §§§ ir tikriname kiekvieną segmentą
            segments = text.split("§§§")
            seen_task_ids = set()
            unique_segments = []

            # Pattern: užduoties ID TIK segmento pradžioje (po strip)
            task_id_pattern = re.compile(r"^\s*(\d+[a-z]?)\)", re.IGNORECASE)

            for segment in segments:
                segment = segment.strip()
                if not segment:
                    continue

                # Tikriname ar segmentas prasideda užduoties ID
                match = task_id_pattern.match(segment)
                if match:
                    task_id = match.group(1).lower()
                    if task_id in seen_task_ids:
                        logger.info(f"Pašalintas inline dublikatas: {task_id})")
                        continue  # Praleidžiame dublikatą
                    seen_task_ids.add(task_id)

                unique_segments.append(segment)

            result = "§§§".join(unique_segments)
            logger.info(
                f"remove_inline_duplicates: {len(segments)} -> {len(unique_segments)} segmentų"
            )
            return result

        combined_latex = remove_inline_duplicates(combined_latex)

    avg_confidence = (
        total_confidence / len(file_info.image_paths) if file_info.image_paths else 0.0
    )

    # DEBUG: Final latex check
    if combined_latex:
        logger.info(
            f"🔚 FINAL LaTeX: length={len(combined_latex)}, has_separator={'§§§' in combined_latex}, separator_count={combined_latex.count('§§§')}"
        )

    return OCRAllPagesResponse(
        file_id=request.file_id,
        pages=len(file_info.image_paths),
        text=combined_text,
        latex=combined_latex,
        confidence=avg_confidence,
        source=source,
        is_math=is_math,
        processing_time_ms=total_time,
        warnings=all_warnings,
    )


@router.post("/ocr", response_model=OCRResponse)
async def perform_ocr(request: OCRRequest):
    """
    Atlieka OCR atpažinimą įkeltam failui.
    """
    upload_service = get_upload_service()
    file_info = await upload_service.get_file_info(request.file_id)

    if not file_info:
        raise HTTPException(status_code=404, detail="Failas nerastas")

    if request.page < 1 or request.page > len(file_info.image_paths):
        raise HTTPException(status_code=404, detail="Puslapis nerastas")

    image_path = file_info.image_paths[request.page - 1]

    # Apdorojame vaizdą
    image_processor = get_image_processor()
    processed = image_processor.process_image(
        image_path,
        normalize=True,
        enhance_contrast=True,
        remove_noise=True,
        deskew=True,
    )

    # OCR
    ocr_service = get_ocr_service()

    prefer_source = None
    if request.source:
        try:
            prefer_source = OCRSource(request.source)
        except ValueError:
            pass

    result = await ocr_service.recognize(
        processed.processed_path,
        prefer_source=prefer_source,
        detect_math=request.detect_math,
    )

    return OCRResponse(
        file_id=request.file_id,
        page=request.page,
        text=result.text,
        latex=result.latex,
        confidence=result.confidence,
        source=result.source.value,
        is_math=result.is_math,
        processing_time_ms=result.processing_time_ms,
        warnings=result.warnings,
    )
