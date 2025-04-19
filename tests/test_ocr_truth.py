"""
OCR PoC — truth‑set validation.
Run with: pytest -q
"""

from pathlib import Path
import csv, pytest

PDF_DIR = Path("data/pdf")
TRUTH = Path("data/truth/truth_sample.csv")

@pytest.fixture(scope="session")
def rows():
    if not TRUTH.exists():
        pytest.skip(f"Truth CSV not found: {TRUTH}")
    with TRUTH.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = list(reader)
        if not data:
            pytest.skip(f"No data rows found in {TRUTH}")
        return data

def generate_test_ids(row):
    """Generates a readable ID for parametrized tests based on file_name."""
    return row.get("file_name", "unknown_file")

@pytest.mark.parametrize("row", rows(), ids=generate_test_ids)
def test_file_exists(row):
    """Simplest test: Check if the PDF file mentioned in the CSV exists."""
    file_name = row.get("file_name")
    assert file_name, f"Missing 'file_name' in row: {row}"
    pdf_path = PDF_DIR / file_name
    assert pdf_path.exists(), f"PDF file specified in CSV not found: {pdf_path}"

# === Placeholder for future actual OCR tests ===
# You can add more test functions here later to validate specific fields
# using run_ocr and extract_field like in the previous version.
# Example:
#
# from src.ocr.engine import run_ocr # Assuming src/ocr/engine.py exists
#
# def extract_field(text: str, field: str) -> str:
#     # ... (your extraction logic here) ...
#     return "extracted_value"
#
# @pytest.mark.parametrize("row", rows(), ids=generate_test_ids)
# def test_field_value(row):
#     field_name = row.get("field_name")
#     expected_value = row.get("expected_text")
#
#     # Skip rows not meant for this specific test
#     if field_name != "InvoiceNumber": # Example: only test InvoiceNumber here
#         pytest.skip(f"Skipping test for field: {field_name}")
#
#     pdf_file = PDF_DIR / row["file_name"]
#     assert pdf_file.exists()
#
#     ocr_text = run_ocr(pdf_file)
#     actual_value = extract_field(ocr_text, field_name)
#
#     assert actual_value == expected_value, (
#         f"{field_name} mismatch in {row['file_name']}:\n" 
#         f"  Expected: '{expected_value}'\n" 
#         f"  Got:      '{actual_value}'"
#     )
