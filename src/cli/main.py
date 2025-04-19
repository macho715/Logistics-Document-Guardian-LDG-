"""Main CLI interface for LDG."""

import typer
from pathlib import Path
import logging
import csv
import json
from typing import Optional

from src.ldg.validator import validate

# Configure basic logging for CLI visibility
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
log = logging.getLogger(__name__)

app = typer.Typer(
    name="ldg",
    help="Logistics Document Guardian (LDG) - OCR Validation Tool",
    add_completion=False,
)

# Default paths relative to a potential project root or execution context
DEFAULT_PDF_DIR = Path("data/pdf")
DEFAULT_TRUTH_CSV = Path("data/truth/truth_sample.csv")
DEFAULT_OUTPUT_DIR = Path("output")


@app.command()
def run_validation(
    pdf_dir: Path = typer.Option(
        DEFAULT_PDF_DIR,
        "--pdf-dir", "-p",
        help="Directory containing the PDF files to validate.",
        exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True
    ),
    truth_csv: Path = typer.Option(
        DEFAULT_TRUTH_CSV,
        "--truth-csv", "-t",
        help="Path to the truth CSV file.",
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
    ),
    output_csv: Optional[Path] = typer.Option(
        None,
        "--output-csv", "-oc",
        help="Optional path to save mismatch results as a CSV file.",
        file_okay=True, dir_okay=False, writable=True, resolve_path=True
    ),
    output_json: Optional[Path] = typer.Option(
        None,
        "--output-json", "-oj",
        help="Optional path to save mismatch results as a JSON file.",
        file_okay=True, dir_okay=False, writable=True, resolve_path=True
    ),
) -> None:
    """Run OCR validation against a truth set."""
    log.info(f"Starting validation...")
    log.info(f"  PDF Directory: {pdf_dir}")
    log.info(f"  Truth CSV: {truth_csv}")

    try:
        mismatches = validate(pdf_dir, truth_csv)

        if not mismatches:
            log.info("✅ Validation successful! No mismatches found.")
            typer.echo("\n✅ Validation successful! No mismatches found.")
            raise typer.Exit(code=0)

        log.warning(f"⚠️ Validation finished with {len(mismatches)} mismatch(es).")
        typer.echo(f"\n⚠️ Found {len(mismatches)} mismatch(es):")

        # Print mismatches to console
        for i, mismatch in enumerate(mismatches):
            typer.echo(f"\n--- Mismatch {i+1} ---")
            typer.echo(f"  File: {mismatch.get('file_name', 'N/A')}")
            typer.echo(f"  Page: {mismatch.get('page', 'N/A')}")
            typer.echo(f"  Field: {mismatch.get('field_name', 'N/A')}")
            typer.echo(f"  Expected Text: '{mismatch.get('expected_text', 'N/A')}'")
            if "validation_error" in mismatch:
                typer.echo(f"  Validation Error: {mismatch['validation_error']}")
            if "ocr_output_snippet" in mismatch:
                typer.echo(f"  OCR Snippet: '{mismatch['ocr_output_snippet']}'")

        # Save to output files if specified
        if output_csv:
            DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            output_path = DEFAULT_OUTPUT_DIR / output_csv if output_csv.is_relative_to(Path(".")) else output_csv
            log.info(f"Saving mismatches to CSV: {output_path}")
            try:
                with output_path.open('w', newline='', encoding='utf-8') as f:
                    # Use fieldnames from the first mismatch dict
                    fieldnames = list(mismatches[0].keys())
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(mismatches)
                typer.echo(f"\n💾 Mismatches saved to CSV: {output_path}")
            except Exception as e:
                log.error(f"Failed to write CSV output: {e}")
                typer.echo(f"\n❌ Error saving mismatches to CSV: {e}")

        if output_json:
            DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            output_path = DEFAULT_OUTPUT_DIR / output_json if output_json.is_relative_to(Path(".")) else output_json
            log.info(f"Saving mismatches to JSON: {output_path}")
            try:
                with output_path.open('w', encoding='utf-8') as f:
                    json.dump(mismatches, f, indent=4, ensure_ascii=False)
                typer.echo(f"\n💾 Mismatches saved to JSON: {output_path}")
            except Exception as e:
                log.error(f"Failed to write JSON output: {e}")
                typer.echo(f"\n❌ Error saving mismatches to JSON: {e}")

        # Exit with code 1 if mismatches were found
        raise typer.Exit(code=1)

    except FileNotFoundError as e:
        log.error(f"File not found error during validation: {e}")
        typer.echo(f"\n❌ Error: {e}", err=True)
        raise typer.Exit(code=2)
    except Exception as e:
        log.exception("An unexpected error occurred during validation.") # Log traceback
        typer.echo(f"\n❌ An unexpected error occurred: {e}", err=True)
        raise typer.Exit(code=3)


if __name__ == "__main__":
    app()
