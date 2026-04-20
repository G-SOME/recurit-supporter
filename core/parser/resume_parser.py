from pathlib import Path

from core.parser.pdf_parser import parse_pdf
from core.parser.docx_parser import parse_docx
from core.parser.section_splitter import split_sections
from core.utils.text_cleaner import clean_text
from core.utils.keyword_extractor import extract_keywords


def parse_resume(file_path: str) -> dict:
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        raw_text = parse_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        raw_text = parse_docx(file_path)
    else:
        raise ValueError(f"지원하지 않는 파일 형식: {ext}")

    raw_text = clean_text(raw_text)
    sections = split_sections(raw_text)
    keywords = extract_keywords(raw_text)

    # D1: 경력연차 추정은 임시값
    parsed_years_exp = 0.0

    return {
        "raw_text": raw_text,
        "sections": sections,
        "parsed_years_exp": parsed_years_exp,
        "skill_keywords": keywords,
    }
