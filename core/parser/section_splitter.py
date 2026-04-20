def split_sections(raw_text: str) -> dict:
    """D1: 간단한 규칙 기반 분리(없으면 raw_text fallback)."""
    text = raw_text or ""
    return {
        "summary": text[:800],
        "experience": text,
        "projects": "",
        "skills": "",
        "education": "",
    }
