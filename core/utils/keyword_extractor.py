from typing import List

DEFAULT_KEYWORDS = [
    "HRM", "인사", "평가", "보상", "조직문화", "채용", "노무", "프로세스", "데이터"
]


def extract_keywords(text: str, candidates: List[str] | None = None) -> List[str]:
    pool = candidates or DEFAULT_KEYWORDS
    found = [k for k in pool if k.lower() in text.lower()]
    return sorted(list(set(found)))
