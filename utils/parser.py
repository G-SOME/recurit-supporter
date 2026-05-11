import io
import os
import re

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


def _clean_file_stem(file_name: str) -> str:
    stem = os.path.splitext(file_name)[0]
    stem = stem.replace('_', ' ').replace('-', ' ')
    stem = re.sub(r'\b(resume|cv|이력서|지원서|국문|영문|최종|ver\d+|v\d+)\b', ' ', stem, flags=re.IGNORECASE)
    stem = re.sub(r'\d{4}[._-]?\d{1,2}[._-]?\d{1,2}', ' ', stem)
    stem = re.sub(r'\b\d+\b', ' ', stem)
    stem = re.sub(r'\s+', ' ', stem).strip(' ._')

    korean_name = re.search(r'([가-힣]{2,4})', stem)
    if korean_name:
        return korean_name.group(1)

    english_name = re.search(r'([A-Za-z]+(?:\s+[A-Za-z]+){1,2})', stem)
    if english_name:
        return english_name.group(1).strip()
    return stem



def _extract_name_from_text(raw_text: str) -> str | None:
    if not raw_text:
        return None

    compact = ' '.join(raw_text.split())
    head = compact[:400]

    korean_label = re.search(r'(?:이름|성명)\s*[:：]?\s*([가-힣]{2,4})', head)
    if korean_label:
        return korean_label.group(1).strip()

    english_label = re.search(r'(?:Name|NAME)\s*[:：]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,1})', head)
    if english_label:
        return english_label.group(1).strip()

    korean_candidates = re.findall(r'(?<![가-힣])([가-힣]{2,4})(?![가-힣])', head)
    blocked_words = {
        '이력서', '자기소개', '지원자', '경력기술', '경력사항', '학력사항', '보유역량', '연락처', '성명', '이름', '주소',
        '해외영업', '지원서', '주식회사', '프로젝트', '자격증', '포트폴리오', '요약', '소개서'
    }
    for candidate in korean_candidates:
        if candidate not in blocked_words:
            return candidate

    english_match = re.search(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b', head)
    if english_match:
        return english_match.group(1).strip()

    return None



def infer_candidate_name(file_name: str, raw_text: str) -> str:
    text_name = _extract_name_from_text(raw_text)
    if text_name:
        return text_name

    stem = _clean_file_stem(file_name)
    if stem:
        return stem
    return 'Unknown Candidate'
