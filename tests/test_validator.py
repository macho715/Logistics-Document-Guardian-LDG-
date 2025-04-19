from pathlib import Path
import csv
from unittest.mock import patch, call # Import call for checking multiple calls

import pytest

# Assuming src layout
from src.ldg.validator import validate

# Helper to create a dummy truth CSV file
def _make_truth(tmp_path: Path, rows):
    path = tmp_path / "truth.csv"
    # Ensure rows is not empty and get fieldnames from the first row
    if not rows:
        raise ValueError("Cannot create truth file with empty rows.")
    fieldnames = list(rows[0].keys())
    # Add validation_error and ocr_output_snippet if not present, for consistency
    if "validation_error" not in fieldnames:
        fieldnames.append("validation_error")
    if "ocr_output_snippet" not in fieldnames:
        fieldnames.append("ocr_output_snippet")
        
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        # Ensure all rows have the necessary keys before writing
        processed_rows = []
        for row in rows:
            full_row = {key: row.get(key, "") for key in fieldnames}
            processed_rows.append(full_row)
        writer.writerows(processed_rows)
    return path

# --- Test Cases ---

@patch("src.ldg.validator.extract_text") # Patch the imported function
def test_validator_match(mock_ocr, tmp_path: Path):
    """Test case where OCR output matches expected text."""
    mock_ocr.return_value = "InvoiceNumber: INV-1234"
    rows = [
        {"file_name": "dummy.pdf", "page": "1", "field_name": "InvoiceNumber", "expected_text": "INV-1234"}
    ]
    truth_csv = _make_truth(tmp_path, rows)
    # Create dummy PDF file referenced in truth data
    pdf_dir = tmp_path / "pdf"
    pdf_dir.mkdir()
    (pdf_dir / "dummy.pdf").touch()
    
    mismatches = validate(pdf_dir=pdf_dir, truth_csv=truth_csv)
    assert not mismatches # Expect no mismatches
    mock_ocr.assert_called_once_with(pdf_dir / "dummy.pdf", page=1)

@patch("src.ldg.validator.extract_text")
def test_validator_mismatch(mock_ocr, tmp_path: Path):
    """Test case where OCR output does NOT match expected text."""
    mock_ocr.return_value = "InvoiceNumber: INV-ABCD"
    rows = [
        {"file_name": "dummy.pdf", "page": "1", "field_name": "InvoiceNumber", "expected_text": "INV-1234"}
    ]
    truth_csv = _make_truth(tmp_path, rows)
    pdf_dir = tmp_path / "pdf"
    pdf_dir.mkdir()
    (pdf_dir / "dummy.pdf").touch()

    mismatches = validate(pdf_dir=pdf_dir, truth_csv=truth_csv)
    assert len(mismatches) == 1
    assert mismatches[0]["field_name"] == "InvoiceNumber"
    assert mismatches[0]["expected_text"] == "INV-1234"
    assert mismatches[0]["validation_error"] == "Mismatch"
    mock_ocr.assert_called_once_with(pdf_dir / "dummy.pdf", page=1)

@patch("src.ldg.validator.extract_text")
def test_validator_multi_page(mock_ocr, tmp_path: Path):
    """Test validation spanning multiple pages of the same PDF."""
    # Define different return values for consecutive calls to mock_ocr
    mock_ocr.side_effect = [
        "Page 1 text: Data-A",
        "Page 2 text: Data-B"
    ]
    rows = [
        {"file_name": "multi.pdf", "page": "1", "field_name": "FieldA", "expected_text": "Data-A"},
        {"file_name": "multi.pdf", "page": "2", "field_name": "FieldB", "expected_text": "Data-B"},
    ]
    truth_csv = _make_truth(tmp_path, rows)
    pdf_dir = tmp_path / "pdf"
    pdf_dir.mkdir()
    pdf_path = pdf_dir / "multi.pdf"
    pdf_path.touch()

    mismatches = validate(pdf_dir=pdf_dir, truth_csv=truth_csv)
    assert not mismatches # Expect no mismatches
    # Check that extract_text was called twice with correct page numbers
    assert mock_ocr.call_count == 2
    mock_ocr.assert_has_calls([
        call(pdf_path, page=1),
        call(pdf_path, page=2)
    ])

@patch("src.ldg.validator.extract_text")
def test_validator_mismatch_collects_all(mock_ocr, tmp_path: Path):
    """Test that multiple mismatches from the same file are collected."""
    mock_ocr.return_value = "FieldA: ValueA | FieldC: ValueC"
    rows = [
        {"file_name": "dummy.pdf", "page": "1", "field_name": "FieldA", "expected_text": "ValueA"}, # Match
        {"file_name": "dummy.pdf", "page": "1", "field_name": "FieldB", "expected_text": "MISSING"}, # Mismatch
        {"file_name": "dummy.pdf", "page": "1", "field_name": "FieldC", "expected_text": "WRONG"}, # Mismatch
    ]
    truth_csv = _make_truth(tmp_path, rows)
    pdf_dir = tmp_path / "pdf"
    pdf_dir.mkdir()
    (pdf_dir / "dummy.pdf").touch()

    mismatches = validate(pdf_dir=pdf_dir, truth_csv=truth_csv)
    assert len(mismatches) == 2
    assert mismatches[0]["field_name"] == "FieldB"
    assert mismatches[1]["field_name"] == "FieldC"
    # OCR should only be called once for page 1 of this file
    mock_ocr.assert_called_once_with(pdf_dir / "dummy.pdf", page=1)


def test_validator_missing_pdf(tmp_path: Path):
    """Test behavior when a PDF listed in truth CSV is missing."""
    rows = [
        {"file_name": "nonexistent.pdf", "page": "1", "field_name": "FieldA", "expected_text": "ValueA"}
    ]
    truth_csv = _make_truth(tmp_path, rows)
    pdf_dir = tmp_path / "pdf"
    pdf_dir.mkdir() # Ensure directory exists but file does not

    mismatches = validate(pdf_dir=pdf_dir, truth_csv=truth_csv)
    assert len(mismatches) == 1
    assert "PDF not found" in mismatches[0]["validation_error"]

@patch("src.ldg.validator.extract_text", side_effect=FileNotFoundError("OCR Failed"))
def test_validator_ocr_exception(mock_ocr, tmp_path: Path):
    """Test behavior when extract_text raises an exception."""
    rows = [
        {"file_name": "dummy.pdf", "page": "1", "field_name": "FieldA", "expected_text": "ValueA"}
    ]
    truth_csv = _make_truth(tmp_path, rows)
    pdf_dir = tmp_path / "pdf"
    pdf_dir.mkdir()
    (pdf_dir / "dummy.pdf").touch()

    mismatches = validate(pdf_dir=pdf_dir, truth_csv=truth_csv)
    assert len(mismatches) == 1
    assert "OCR Failed" in mismatches[0]["validation_error"] # Should record the exception message 