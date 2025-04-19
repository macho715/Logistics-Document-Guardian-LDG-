"""
OCR PoC — truth‑set validation.
Run with: pytest -q
"""

from pathlib import Path
import csv, pytest

PDF_DIR = Path("data/pdf")
TRUTH_CSV_PATH = Path("data/truth/truth_sample.csv")


# Load CSV data at the module level for parametrization
def load_truth_data():
    if not TRUTH_CSV_PATH.exists():
        return []  # Return empty list if file not found
    try:
        with TRUTH_CSV_PATH.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = list(reader)
            # Basic check for header - assumes 'file_name' is essential
            if data and "file_name" not in data[0]:
                pytest.fail(f"Required column 'file_name' not found in {TRUTH_CSV_PATH}")
            return data
    except Exception as e:
        pytest.fail(f"Error reading {TRUTH_CSV_PATH}: {e}")
    return []  # Should not be reached, but for safety


TRUTH_DATA = load_truth_data()


# Optional: If you still need the data as a fixture elsewhere
@pytest.fixture(scope="session")
def rows():
    if not TRUTH_DATA:
        pytest.skip(f"No data loaded from {TRUTH_CSV_PATH} or file not found.")
    return TRUTH_DATA


def generate_test_ids(row):
    """Generates a readable ID for parametrized tests based on file_name."""
    # Handle cases where TRUTH_DATA might be empty or row is not a dict
    if isinstance(row, dict):
        return row.get("file_name", "invalid_row_data")
    return "invalid_row_format"


# Parametrize using the loaded data
@pytest.mark.parametrize("row", TRUTH_DATA, ids=generate_test_ids)
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
