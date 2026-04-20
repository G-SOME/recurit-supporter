import pdfplumber


def parse_pdf(file_path: str) -> str:
    texts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            texts.append(page.extract_text() or "")
    return "\n".join(texts)
