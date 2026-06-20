"""
Document Parser Module
========================
Unified resume/document ingestion supporting PDF, DOCX, and TXT inputs.
Returns plain text regardless of source format, so downstream NLP
preprocessing doesn't need to know what format the original file was in.
"""

import os
import pdfplumber
import docx


class UnsupportedFileTypeError(Exception):
    pass


def parse_txt(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def parse_docx(file_path):
    doc = docx.Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs)


def parse_pdf(file_path):
    text_chunks = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text)
    return "\n".join(text_chunks)


PARSERS = {
    ".txt": parse_txt,
    ".docx": parse_docx,
    ".pdf": parse_pdf,
}


def parse_document(file_path):
    """
    Dispatch to the correct parser based on file extension.
    Returns raw extracted text. Raises UnsupportedFileTypeError for
    anything outside .txt / .docx / .pdf.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in PARSERS:
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{ext}'. Supported types: {list(PARSERS.keys())}"
        )
    return PARSERS[ext](file_path)


if __name__ == "__main__":
    sample_dir = "/home/claude/skill-gap-system/data/sample_resume_files"
    for fname in sorted(os.listdir(sample_dir)):
        path = os.path.join(sample_dir, fname)
        text = parse_document(path)
        print(f"--- {fname} ({len(text)} chars) ---")
        print(text[:200])
        print()
