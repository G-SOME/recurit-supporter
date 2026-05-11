import io
from docx import Document
import pdfplumber

from utils.helpers import clean_text


def extract_text_from_pdf(uploaded_file) -> str:
    uploaded_file.seek(0)
    text_chunks = []
    with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
        for page in pdf.pages:
            text_chunks.append(page.extract_text() or '')
    uploaded_file.seek(0)
    return clean_text('\n'.join(text_chunks))


def extract_text_from_docx(uploaded_file) -> str:
    uploaded_file.seek(0)
    document = Document(io.BytesIO(uploaded_file.read()))
    text = '\n'.join([paragraph.text for paragraph in document.paragraphs])
    uploaded_file.seek(0)
    return clean_text(text)


def extract_text(uploaded_file, extension: str) -> str:
    if extension == 'pdf':
        return extract_text_from_pdf(uploaded_file)
    if extension == 'docx':
        return extract_text_from_docx(uploaded_file)
    raise ValueError(f'Unsupported file type: {extension}')


def infer_candidate_name(file_name: str, raw_text: str) -> str:
    stem = file_name.rsplit('.', 1)[0]
    stem = stem.replace('_', ' ').replace('-', ' ').strip()
    return stem or 'Unknown Candidate'
