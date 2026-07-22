"""Pull the text out of contract PDFs."""

from pathlib import Path

import pdfplumber


def extract_text(pdf_path: str) -> str:
    """Read every page of a PDF as text.

    Args:
        pdf_path: Path to the PDF.

    Returns:
        The pages joined by newlines. Empty if the PDF holds no text layer,
        which is what a scan looks like: it needs OCR first.
    """
    with pdfplumber.open(pdf_path) as pdf:
        pages = [page.extract_text() for page in pdf.pages]
    return "\n".join(page for page in pages if page)


def load_contracts(folder: str) -> list[dict]:
    """Read every PDF in a folder.

    Args:
        folder: Directory to scan, not recursive.

    Returns:
        One entry per PDF, in filename order, each with `filename` and `text`.
    """
    return [
        {"filename": path.name, "text": extract_text(str(path))}
        for path in sorted(Path(folder).glob("*.pdf"))
    ]
