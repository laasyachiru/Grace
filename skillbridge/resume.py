"""Read resumes (PDF or text) into plain text."""

from __future__ import annotations

import io
from pathlib import Path

from pypdf import PdfReader


def pdf_bytes_to_text(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def read_upload(uploaded) -> str:
    """Text from a Streamlit UploadedFile (PDF, TXT or MD)."""
    data = uploaded.getvalue()
    if uploaded.name.lower().endswith(".pdf"):
        return pdf_bytes_to_text(data)
    return data.decode("utf-8", errors="ignore")


def read_path(path: str | Path) -> str:
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        return pdf_bytes_to_text(path.read_bytes())
    return path.read_text(encoding="utf-8", errors="ignore")
