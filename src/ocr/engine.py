"""OCR 엔진 래퍼 (Tesseract).

- 다중 페이지 PDF: 1‑based `page` 인덱스 사용
- 실패 시 빈 문자열을 반환하고 logger warning 출력
"""

from __future__ import annotations
from pathlib import Path
import subprocess
import logging
import tempfile

log = logging.getLogger(__name__)

def _run_tesseract(image_path: Path, txt_path: Path, lang: str) -> None:
    """Invoke tesseract CLI; raise CalledProcessError on non‑zero exit."""
    subprocess.run(
        ["tesseract", str(image_path), str(txt_path.stem), "-l", lang, "--psm", "4"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

def extract_text(pdf_path: Path, page: int = 1, lang: str = "eng+kor") -> str:
    """Return OCR text of **one** page; empty string on failure."""
    if page < 1:
        raise ValueError("page must be ≥ 1")

    with tempfile.TemporaryDirectory() as tmpdir:
        png = Path(tmpdir) / f"page_{page}.png"
        txt = Path(tmpdir) / f"page_{page}.txt"

        # 1️⃣ PDF page → PNG via Ghostscript
        try:
            subprocess.run(
                [
                    "gswin64c",  # Windows ghostscript CLI; rename if needed
                    "-sDEVICE=png16m",
                    "-r300",
                    f"-dFirstPage={page}",
                    f"-dLastPage={page}",
                    "-o", str(png),
                    str(pdf_path),
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as exc:
            log.warning("Ghostscript rasterize failed: %s", exc.stderr.decode())
            return ""
        except FileNotFoundError:
            log.error("Ghostscript command (gswin64c) not found. Ensure Ghostscript is installed and in PATH.")
            return ""


        # 2️⃣ Tesseract OCR
        try:
            _run_tesseract(png, txt, lang)
            return txt.read_text(encoding="utf-8", errors="ignore")
        except subprocess.CalledProcessError as exc:
            log.warning("Tesseract OCR failed: %s", exc.stderr.decode())
            return ""
        except FileNotFoundError:
            log.error("Tesseract command not found. Ensure Tesseract is installed and in PATH.")
            return ""

def run_ocr(pdf_path: Path, lang: str = "eng", dpi: int = 300) -> str:
    """Provide a placeholder for the actual OCR engine logic."""
    print(f"INFO: OCR simulation for {pdf_path} with lang='{lang}', dpi={dpi}")
    # In a real scenario, this would invoke Tesseract or another OCR tool
    # and return the extracted text.
    # For now, returning dummy text based on filename:
    if "inv_0001" in pdf_path.name:
        return (
            "Dummy OCR text for inv_0001.pdf\n"
            "InvoiceNumber: INV-2025-0001\n"
            "Consignee: Samsung C&T\n..."
        )
    return f"Dummy OCR text for {pdf_path.name}"


def process_directory(input_dir: Path, output_dir: Path, lang: str = "eng", dpi: int = 300) -> None:
    """Process all PDFs in a directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for pdf_file in input_dir.glob("*.pdf"):
        print(f"Processing {pdf_file.name}...")
        text = run_ocr(pdf_file, lang=lang, dpi=dpi)
        output_file = output_dir / f"{pdf_file.stem}.txt"
        output_file.write_text(text, encoding="utf-8")
        print(f"  -> Saved text to {output_file}")
