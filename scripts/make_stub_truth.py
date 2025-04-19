"""Utility to generate a stub truth_sample.csv from PDF filenames."""

# scripts/make_stub_truth.py
import csv
from pathlib import Path
from typing import List, Dict, Any # Ensure typing is imported

PDF_DIR = Path("data/pdf")
TRUTH = Path("data/truth/truth_sample.csv")
TRUTH.parent.mkdir(parents=True, exist_ok=True)

rows: List[Dict[str, Any]] = []
pdf_files = list(PDF_DIR.glob("*.pdf"))  # Get list of PDFs first

fieldnames: List[str]

if not pdf_files:
    print(f"⚠️ No PDF files found in {PDF_DIR}. Creating an empty truth file with header.")
    fieldnames = ["file_name", "page", "field_name", "expected_text"]
else:
    rows = [
        {
            "file_name": pdf.name,
            "page": 1,
            "field_name": "FileNameCheck",
            "expected_text": pdf.stem,  # ex) inv_0001
        }
        for pdf in pdf_files
    ]
    # Ensure fieldnames is a list[str] derived from keys
    fieldnames = list(rows[0].keys())

with TRUTH.open("w", newline="", encoding="utf-8") as f:
    # Pass the correctly typed fieldnames list
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    if rows:
        writer.writerows(rows)

print(f"✅ Stub truth written → {TRUTH}, rows={len(rows)}")
