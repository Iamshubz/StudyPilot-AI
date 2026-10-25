"""Document text extraction helpers for uploaded study material."""

from io import BytesIO
from pathlib import Path
from typing import Any


SUPPORTED_UPLOAD_TYPES = ["txt", "md", "pdf", "png", "jpg", "jpeg", "webp"]
IMAGE_UPLOAD_TYPES = {"png", "jpg", "jpeg", "webp"}


def extract_uploaded_text(uploaded_file: Any) -> str:
    """Extract readable text from a Streamlit uploaded file.

    PDFs are parsed for embedded text. Images use local Tesseract OCR so
    uploaded study material is not sent anywhere before summarization.
    """
    file_name = getattr(uploaded_file, "name", "uploaded file")
    suffix = Path(file_name).suffix.lower().lstrip(".")
    file_bytes = uploaded_file.getvalue()

    if suffix in {"txt", "md"}:
        return file_bytes.decode("utf-8-sig")

    if suffix == "pdf":
        try:
            from pypdf import PdfReader
            from pypdf.errors import PdfReadError
        except ImportError as exc:
            raise RuntimeError(
                "PDF support is not installed. Run `pip install -r requirements.txt` "
                "and restart Streamlit."
            ) from exc

        try:
            reader = PdfReader(BytesIO(file_bytes))
        except (PdfReadError, OSError, ValueError) as exc:
            raise RuntimeError(
                f"Could not read PDF file '{file_name}'. Please upload a valid, readable PDF."
            ) from exc
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(page.strip() for page in pages if page.strip())

    if suffix in IMAGE_UPLOAD_TYPES:
        try:
            from PIL import Image
            import pytesseract
        except ImportError as exc:
            raise RuntimeError(
                "Image OCR support is not installed. Run `pip install -r requirements.txt` "
                "and restart Streamlit."
            ) from exc

        try:
            image = Image.open(BytesIO(file_bytes))
            return pytesseract.image_to_string(image).strip()
        except pytesseract.pytesseract.TesseractNotFoundError as exc:
            raise RuntimeError(
                "Image text extraction requires the Tesseract OCR engine. "
                "Install it with `brew install tesseract`, then restart Streamlit."
            ) from exc
        except (OSError, ValueError) as exc:
            raise RuntimeError(f"Could not read image file '{file_name}'.") from exc

    raise ValueError(
        f"Unsupported file type '.{suffix or 'unknown'}'. "
        "Upload a TXT, Markdown, PDF, PNG, JPG, JPEG, or WEBP file."
    )
