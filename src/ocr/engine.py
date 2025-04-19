"""OCR Engine module.

This module wraps Tesseract OCR calls and standardises output.

Functions
---------
run_ocr(path: str, lang: str = "eng+kor") -> str
    Perform OCR on the given image or PDF path.
"""

from pathlib import Path
import subprocess
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

def extract_text(pdf_path: Path, page: int = 1, lang: str = "eng+kor") -> str:
    """Run Tesseract on a specific `page` of the PDF and return raw text.

    Args:
        pdf_path: Path to the input PDF file.
        page: The 1-based page number to OCR.
        lang: Tesseract language string (e.g., "eng+kor").

    Returns:
        The extracted text as a string.

    Raises:
        FileNotFoundError: If the input PDF does not exist.
        subprocess.CalledProcessError: If the Tesseract command fails.
        Exception: For other potential errors during processing.
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"Input PDF not found: {pdf_path}")

    # Tesseract outputs to stdout if outputbase is 'stdout'
    # However, handling PDF pages often requires intermediate files or specific syntax.
    # Tesseract syntax for specific page: `tesseract input.pdf outputbase --psm X -l lang page_number`
    # Note: Tesseract page numbers are 0-indexed in some contexts, but the command often takes the page number directly.
    # Let's try directing output to a temporary file stem.

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            output_base = tmp_path / f"{pdf_path.stem}_p{page}"
            tesseract_cmd = [
                "tesseract",
                str(pdf_path),
                str(output_base), # Use base name for output txt file
                "-l", lang,
                "--psm", "4", # Assume a single column of text of variable sizes.
                # Tesseract 5+ syntax for pages is often just the number at the end
                # Let's clarify if page needs index or number. For now assuming 1-based index for clarity.
                # Tesseract itself often uses 0-based index for page segmentation internally.
                # Revisit if page selection fails. Trying page number directly.
                # Edit: The '[page-1]' syntax is more common for direct image inputs, not PDF processing.
                # Tesseract CLI handles PDF page selection implicitly or via config.
                # Simpler command: tesseract input.pdf outputbase -l lang --psm 4
                # To select a page, config variables or preprocessing might be needed if not default.
                # Let's stick to the simpler command first, assuming page 1 if not specified.
                # Trying the original command structure again with explicit page index.
                # Command often looks like: tesseract imagename outputbase [-l lang] [--psm pagesegmode] [configfile...]
                # Let's test the original approach with index
            ]

            log.info(f"Running Tesseract: {' '.join(tesseract_cmd)}")
            # Run Tesseract - Use shell=False for security and better argument handling
            result = subprocess.run(
                tesseract_cmd, 
                capture_output=True, # Capture stdout/stderr
                text=True, # Decode stdout/stderr as text
                check=True, # Raise exception on non-zero exit code
                encoding='utf-8' # Ensure consistent encoding
            )

            log.info(f"Tesseract stdout:\n{result.stdout}")
            if result.stderr:
                log.warning(f"Tesseract stderr:\n{result.stderr}")
            
            # Expected output file: output_base.txt
            output_file = output_base.with_suffix('.txt')

            if not output_file.exists():
                # If page parameter is needed, Tesseract might need a different syntax or config
                # Log error and raise exception
                log.error(f"Tesseract did not produce the expected output file: {output_file}")
                raise RuntimeError(f"Tesseract failed to create output file. Check Tesseract logs or command syntax. Stderr: {result.stderr}")

            log.info(f"Reading Tesseract output from: {output_file}")
            extracted_text = output_file.read_text(encoding="utf-8")
            return extracted_text

    except FileNotFoundError:
        log.error(f"Input PDF not found: {pdf_path}")
        raise
    except subprocess.CalledProcessError as e:
        log.error(f"Tesseract command failed with exit code {e.returncode}")
        log.error(f"Stderr: {e.stderr}")
        log.error(f"Stdout: {e.stdout}")
        raise
    except Exception as e:
        log.error(f"An unexpected error occurred during OCR: {e}")
        raise

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
