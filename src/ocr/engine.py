"""OCR Engine module.

This module wraps Tesseract OCR calls and standardises output.

Functions
---------
run_ocr(path: str, lang: str = "eng+kor") -> str
    Perform OCR on the given image or PDF path.
"""

from pathlib import Path


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
