import pdfplumber
from pathlib import Path


def extract_text(pdf_path: str) -> str:
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
    return "\n".join(text_parts)


def load_contracts(folder: str) -> list[dict]:
    contracts = []
    for path in sorted(Path(folder).glob("*.pdf")):
        text = extract_text(str(path))
        contracts.append({"filename": path.name, "text": text})
    return contracts
