from pathlib import Path

from docx import Document
from pypdf import PdfReader


def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    extracted_pages = []

    for page in reader.pages:
        extracted_pages.append(page.extract_text() or '')

    return '\n'.join(extracted_pages).strip()


def extract_text_from_docx(file_path):
    document = Document(file_path)
    paragraphs = [paragraph.text for paragraph in document.paragraphs]
    return '\n'.join(paragraphs).strip()


def extract_text_from_resume(file_path):
    suffix = Path(file_path).suffix.lower()

    if suffix == '.pdf':
        return extract_text_from_pdf(file_path)

    if suffix == '.docx':
        return extract_text_from_docx(file_path)

    return ''
