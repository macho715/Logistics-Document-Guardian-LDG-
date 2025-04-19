from pathlib import Path
from unittest.mock import patch
import subprocess # Needed for CalledProcessError

import pytest

# Assuming src layout, adjust if needed
from src.ocr import engine

@pytest.fixture()
def dummy_pdf(tmp_path: Path) -> Path:
    f = tmp_path / "file.pdf"
    f.touch()
    return f

# ── 기본 성공 ─────────────────────────────────────────────
@patch("src.ocr.engine._run_tesseract")
@patch("src.ocr.engine.subprocess.run") # Mock Ghostscript call
def test_extract_text_ok(mock_gs_run, mock_tess_run, dummy_pdf, monkeypatch, tmp_path):
    """Test successful extraction path."""
    # Mock the creation and reading of the temporary text file
    def mock_read_text(*args, **kwargs):
        # Simulate tesseract creating the output file
        txt_file = tmp_path / "page_1.txt"
        txt_file.write_text("HELLO", encoding="utf-8")
        return txt_file.read_text(*args, **kwargs)

    monkeypatch.setattr(Path, "read_text", mock_read_text)

    assert engine.extract_text(dummy_pdf) == "HELLO"
    mock_gs_run.assert_called_once()
    mock_tess_run.assert_called_once()

# ── 다중 페이지 호출 확인 ──────────────────────────────────
@patch("src.ocr.engine._run_tesseract")
@patch("src.ocr.engine.subprocess.run") # Mock Ghostscript call
def test_extract_text_second_page(mock_gs_run, mock_tess_run, dummy_pdf, monkeypatch, tmp_path):
    """Test that page=2 is passed correctly to Ghostscript."""
    # Mock the creation and reading of the temporary text file for page 2
    def mock_read_text(*args, **kwargs):
        txt_file = tmp_path / "page_2.txt"
        txt_file.write_text("PAGE 2 DATA", encoding="utf-8")
        return txt_file.read_text(*args, **kwargs)

    monkeypatch.setattr(Path, "read_text", mock_read_text)

    result = engine.extract_text(dummy_pdf, page=2)
    assert result == "PAGE 2 DATA"

    mock_gs_run.assert_called_once()
    # Check if the Ghostscript command includes the correct page arguments
    gs_command_args = mock_gs_run.call_args.args[0]
    assert "-dFirstPage=2" in gs_command_args
    assert "-dLastPage=2" in gs_command_args

    mock_tess_run.assert_called_once()

# ── Ghostscript 실패 시 빈 문자열 ─────────────────────────
@patch("src.ocr.engine.subprocess.run", side_effect=subprocess.CalledProcessError(1, "gswin64c", stderr=b"GS Error"))
def test_extract_text_gs_fail(mock_gs_run, dummy_pdf):
    """Test that an empty string is returned if Ghostscript fails."""
    assert engine.extract_text(dummy_pdf) == ""
    mock_gs_run.assert_called_once()

# --- Ghostscript FileNotFoundError --- 
@patch("src.ocr.engine.subprocess.run", side_effect=FileNotFoundError("gswin64c not found"))
def test_extract_text_gs_not_found(mock_gs_run, dummy_pdf):
    """Test empty string return if Ghostscript executable is not found."""
    assert engine.extract_text(dummy_pdf) == ""
    mock_gs_run.assert_called_once()

# ── Tesseract 실패 시 빈 문자열 ───────────────────────────
@patch("src.ocr.engine._run_tesseract", side_effect=subprocess.CalledProcessError(1, "tesseract", stderr=b"Tess Error"))
@patch("src.ocr.engine.subprocess.run") # Mock Ghostscript call (assuming it succeeds)
def test_extract_text_tess_fail(mock_gs_run, mock_tess_run, dummy_pdf):
    """Test that an empty string is returned if Tesseract fails."""
    assert engine.extract_text(dummy_pdf) == ""
    mock_gs_run.assert_called_once()
    mock_tess_run.assert_called_once()

# --- Tesseract FileNotFoundError ---
@patch("src.ocr.engine._run_tesseract", side_effect=FileNotFoundError("tesseract not found"))
@patch("src.ocr.engine.subprocess.run") # Mock Ghostscript call (assuming it succeeds)
def test_extract_text_tess_not_found(mock_gs_run, mock_tess_run, dummy_pdf):
    """Test empty string return if Tesseract executable is not found."""
    assert engine.extract_text(dummy_pdf) == ""
    mock_gs_run.assert_called_once()
    mock_tess_run.assert_called_once()

# --- Invalid Page Number --- 
def test_extract_text_invalid_page(dummy_pdf):
    """Test that ValueError is raised for page < 1."""
    with pytest.raises(ValueError, match="page must be ≥ 1"):
        engine.extract_text(dummy_pdf, page=0)
    with pytest.raises(ValueError, match="page must be ≥ 1"):
        engine.extract_text(dummy_pdf, page=-1)
