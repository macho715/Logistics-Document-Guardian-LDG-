"""OCR 엔진 래퍼 (Google Cloud Document AI).

- Uses synchronous API (`process_document`).
- Requires GCP Project ID, Location, and Processor ID.
- Returns full document text; returns empty string on API error.
"""

from __future__ import annotations
from pathlib import Path
import logging

# Import the Google Cloud Document AI client library
try:
    from google.cloud import documentai_v1 as docai
    from google.api_core.exceptions import GoogleAPICallError
except ImportError:
    # Allow module to be imported even if library is not installed,
    # functions will raise ImportError on call.
    docai = None
    GoogleAPICallError = None
    print("WARNING: google-cloud-documentai library not found. OCR functions will fail.")


log = logging.getLogger(__name__)

def extract_text(
    pdf_path: Path,
    project_id: str,
    location: str,        # e.g., "us"
    processor_id: str,    # The processor ID from GCP console
    mime_type: str = "application/pdf",
) -> str:
    """Process a single document with Document AI, return full text.

    Args:
        pdf_path: Path to the local PDF file.
        project_id: GCP Project ID.
        location: GCP location for the Document AI processor (e.g., "us").
        processor_id: The ID of the Document AI processor.
        mime_type: MIME type of the file (default: "application/pdf").

    Returns:
        The full extracted text of the document, or an empty string
        if an error occurs during processing.
    """
    if docai is None:
        raise ImportError("google-cloud-documentai library is required but not installed.")

    log.info(f"Processing {pdf_path} with Document AI processor {processor_id} in {location}")

    try:
        # Instantiates a client
        # You must configure Application Default Credentials for this to work
        # See: https://cloud.google.com/docs/authentication/provide-credentials-adc
        client_options = {"api_endpoint": f"{location}-documentai.googleapis.com"}
        client = docai.DocumentProcessorServiceClient(client_options=client_options)

        # The full resource name of the processor
        # e.g. projects/project-id/locations/location/processors/processor-id
        name = client.processor_path(project_id, location, processor_id)

        # Read the file contents
        with pdf_path.open("rb") as file_content:
            pdf_content = file_content.read()

        # Load Binary Data into Document AI RawDocument Structure
        raw_document = docai.RawDocument(content=pdf_content, mime_type=mime_type)

        # Configure the process request
        request = docai.ProcessRequest(name=name, raw_document=raw_document)

        # Use the Document AI client to process the sample form
        result = client.process_document(request=request)
        document = result.document

        log.info(f"Document AI processing successful for {pdf_path}")
        return document.text or "" # Return empty string if text is None

    except GoogleAPICallError as e:
        log.error(f"Document AI API call failed for {pdf_path}: {e}")
        return ""
    except FileNotFoundError:
        log.error(f"Input file not found: {pdf_path}")
        # Re-raise standard FileNotFoundError for caller to handle
        raise
    except Exception as e:
        # Catch any other unexpected exceptions during processing
        log.error(f"An unexpected error occurred during Document AI processing for {pdf_path}: {e}", exc_info=True)
        return ""

# Note: The previous Tesseract/Ghostscript related functions are removed.
