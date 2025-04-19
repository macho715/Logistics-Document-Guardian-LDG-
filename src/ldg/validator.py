"""Module for validating OCR results against a truth set."""

import csv
import logging
from pathlib import Path
from typing import List, Dict, Any

# Assuming src is in PYTHONPATH or using editable install
from src.ocr.engine import extract_text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

def validate(pdf_dir: Path, truth_csv: Path) -> List[Dict[str, Any]]:
    """Compares OCR output for PDFs against expected values in a truth CSV.

    Args:
        pdf_dir: Directory containing the PDF files.
        truth_csv: Path to the CSV file containing truth data.
                   Expected columns: 'file_name', 'page', 'field_name', 'expected_text'.

    Returns:
        A list of dictionaries, where each dictionary represents a row
        from the truth CSV that resulted in a mismatch.
    """
    mismatches: List[Dict[str, Any]] = []
    processed_files = 0
    total_rows = 0

    if not truth_csv.exists():
        log.error(f"Truth CSV file not found: {truth_csv}")
        raise FileNotFoundError(f"Truth CSV file not found: {truth_csv}")

    try:
        with truth_csv.open(encoding="utf-8", newline='') as f:
            reader = csv.DictReader(f)
            # Check for required headers
            required_headers = {"file_name", "page", "field_name", "expected_text"}
            if not required_headers.issubset(reader.fieldnames or []):
                missing = required_headers - set(reader.fieldnames or [])
                log.error(f"Truth CSV missing required headers: {missing} in {truth_csv}")
                raise ValueError(f"Truth CSV missing required headers: {missing}")

            for row in reader:
                total_rows += 1
                try:
                    file_name = row["file_name"]
                    page_str = row.get("page", "1") # Default to page 1 if missing
                    expected_text = row["expected_text"]

                    pdf_path = pdf_dir / file_name
                    if not pdf_path.exists():
                        log.warning(f"PDF file referenced in truth CSV not found: {pdf_path}")
                        row["validation_error"] = f"PDF not found: {pdf_path}"
                        mismatches.append(row)
                        continue

                    # Attempt to parse page number
                    try:
                        page = int(page_str)
                    except ValueError:
                        log.warning(f"Invalid page number '{page_str}' in row for {file_name}, defaulting to 1.")
                        page = 1

                    # Run OCR on the specified page
                    log.info(f"Running OCR for {pdf_path} (Page {page})")
                    ocr_text = extract_text(pdf_path, page=page)
                    processed_files += 1

                    # Simple substring check for validation
                    # More sophisticated checks (regex, normalization) could be added here
                    if expected_text not in ocr_text:
                        log.warning(f"Mismatch found for {file_name} (Page {page}): Expected '{expected_text}' not in OCR output.")
                        row["validation_error"] = "Mismatch"
                        row["ocr_output_snippet"] = ocr_text[:200] + ("..." if len(ocr_text) > 200 else "") # Add snippet for context
                        mismatches.append(row)
                    else:
                        log.info(f"Match found for {file_name} (Page {page})")

                except FileNotFoundError as e:
                    log.error(f"Error during validation for row {row}: {e}")
                    row["validation_error"] = str(e)
                    mismatches.append(row)
                except Exception as e:
                    log.error(f"Unexpected error validating row {row}: {e}")
                    row["validation_error"] = f"Unexpected error: {e}"
                    mismatches.append(row)

        log.info(f"Validation complete. Processed {processed_files} OCR operations based on {total_rows} truth rows.")
        log.info(f"Found {len(mismatches)} mismatches.")
        return mismatches

    except Exception as e:
        log.error(f"Failed to process truth CSV {truth_csv}: {e}")
        raise # Re-raise critical errors

# Example usage (optional)
# if __name__ == '__main__':
#     data_dir = Path('../data')
#     pdf_dir = data_dir / 'pdf'
#     truth_file = data_dir / 'truth' / 'truth_sample.csv'
#     if pdf_dir.exists() and truth_file.exists():
#         try:
#             results = validate(pdf_dir, truth_file)
#             if results:
#                 print("--- Mismatches Found ---")
#                 for mismatch in results:
#                     print(mismatch)
#             else:
#                 print("--- No Mismatches Found ---")
#         except Exception as e:
#             print(f"Error during example validation: {e}")
#     else:
#         print(f"Required directories/files not found for testing: {pdf_dir}, {truth_file}")
