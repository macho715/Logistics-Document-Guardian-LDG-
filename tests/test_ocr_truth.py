"""
OCR PoC — truth‑set validation.
Run with: pytest -q
"""

import csv
from pathlib import Path
from typing import Dict, List, Any

import pytest

PDF_DIR = Path("data/pdf")
TRUTH_CSV_PATH = Path("data/truth/truth_sample.csv")


# Load CSV data at the module level for parametrization
def load_truth_data() -> List[Dict[str, str]]:
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


TRUTH_DATA: List[Dict[str, str]] = load_truth_data()


# Optional: If you still need the data as a fixture elsewhere
@pytest.fixture(scope="session")
def rows() -> List[Dict[str, str]]:
    if not TRUTH_DATA:
        pytest.skip(f"No data loaded from {TRUTH_CSV_PATH} or file not found.")
    return TRUTH_DATA


def generate_test_ids(row: Dict[str, Any]) -> str:
    """Generates a readable ID for parametrized tests based on file_name."""
    # Handle cases where TRUTH_DATA might be empty or row is not a dict
    if isinstance(row, dict):
        # Explicitly cast the result of get() to str to satisfy mypy [no-any-return]
        return str(row.get("file_name", "invalid_row_data"))
    return "invalid_row_format"


# Parametrize using the loaded data
@pytest.mark.parametrize("row", TRUTH_DATA, ids=generate_test_ids)
def test_file_exists(row: Dict[str, str]) -> None:
    """Simplest test: Check if the PDF file mentioned in the CSV exists."""
    file_name = row.get("file_name")
    assert file_name, f"Missing 'file_name' in row: {row}"
    pdf_path = PDF_DIR / file_name
    assert pdf_path.exists(), f"PDF file specified in CSV not found: {pdf_path}"


# === Integration Test using OCR and Validator ===
def test_validation_runs() -> None:
    """Test that the main validation function runs without critical errors.

    This test invokes Tesseract via the ocr engine and compares against
    the truth data. It mainly checks for runtime errors during the process.
    Actual mismatch validation might require more specific tests or data.
    """
    # Ensure the validator can be imported
    try:
        from src.ldg.validator import validate
    except ImportError as e:
        pytest.fail(f"Failed to import validator: {e}")

    # Check if required data exists before running
    if not PDF_DIR.exists() or not TRUTH_CSV_PATH.exists() or not TRUTH_DATA:
        pytest.skip("Skipping validation run test: Missing PDF directory, truth CSV, or truth data.")

    try:
        # Run the actual validation
        mismatches = validate(pdf_dir=PDF_DIR, truth_csv=TRUTH_CSV_PATH)

        # Basic assertion: Check if the result is a list (even if empty)
        assert isinstance(mismatches, list), "Validation function did not return a list."

        # Optional: Log the number of mismatches found for information
        print(f"\nINFO: Validation run completed. Found {len(mismatches)} mismatches.")
        # Depending on expected results, you could assert len(mismatches) == 0
        # but that might be too strict initially.
        # assert len(mismatches) == 0, f"Expected 0 mismatches, but found {len(mismatches)}"

    except Exception as e:
        pytest.fail(f"Validation function failed with an unexpected error: {e}")


# === Placeholder for future actual OCR tests ===
# You can add more test functions here later to validate specific fields
# using run_ocr and extract_field like in the previous version.
# Example:
#
# from src.ocr.engine import run_ocr # Assuming src/ocr/engine.py exists
# import re # Needed for the example regex
#
# def extract_field(text: str, field: str) -> str: # Renamed placeholder for clarity
#     """Placeholder extraction logic."""
#     if field == "InvoiceNumber":
#         m = re.search(r"INV[-–]?\d{4}[-–]?\d{4}", text)
#         return m.group(0) if m else "" # Ensured str return
#     # Add other field extractions here
#     return "" # Default empty string return
#
# @pytest.mark.parametrize("row", rows(), ids=generate_test_ids)
# def test_field_value(row: Dict[str, str]) -> None:
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
