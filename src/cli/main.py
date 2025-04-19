"""Typer CLI entrypoint for OCR + LDG validation workflow."""

import json

import typer

from ldg.validator import validate

app = typer.Typer()


@app.command()
def ocr_run(file: str, lang: str = "eng+kor") -> None:
    """Run OCR and LDG validation on FILE."""
    # text = run_ocr(file, lang=lang) # F841 - unused variable, OCR result needed later?
    # Placeholder JSON parse, to be implemented - using dummy data for now
    data = {"InvoiceNumber": "INV-0000-0000"}
    result = validate(data)
    typer.echo(json.dumps(result, indent=2))


if __name__ == "__main__":
    app()
