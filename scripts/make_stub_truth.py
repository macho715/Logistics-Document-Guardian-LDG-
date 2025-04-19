"""Utility to generate a stub truth_sample.csv from PDF filenames."""
# scripts/make_stub_truth.py
from pathlib import Path
import csv

PDF_DIR = Path("data/pdf")
TRUTH = Path("data/truth/truth_sample.csv")
TRUTH.parent.mkdir(parents=True, exist_ok=True)

rows = []
pdf_files = list(PDF_DIR.glob("*.pdf")) # Get list of PDFs first

if not pdf_files:
    print(f"⚠️ No PDF files found in {PDF_DIR}. Creating an empty truth file with header.")
    header = ["file_name", "page", "field_name", "expected_text"]
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
    header = rows[0].keys()

with TRUTH.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=header)
    writer.writeheader()
    if rows:
        writer.writerows(rows)

print(f"✅ Stub truth written → {TRUTH}, rows={len(rows)}") 