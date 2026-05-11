from collections import Counter
from math import ceil
import re

import numpy as np

from utils.embedding import get_embedding
from utils.helpers import split_sentences


KEYWORD_BUCKETS = {
    'overseas': ['overseas', 'global', 'export', 'buyer', 'customer', 'sales', '영업', '해외', '수출', '바이어'],
    'north_america': ['north america', 'usa', 'u.s.', 'canada', '미국', '캐나다', '북미'],
    'manufacturing': ['manufacturing', 'factory', 'plant', 'production', 'product', '제조', '생산', '제품'],
    'coordination': ['negotiation', 'coordination', 'communication', 'schedule', '협상', '조율', '커뮤니케이션'],
}


def cosine_similarity(vec1, vec2) -> float:
    a = np.array(vec1)
    b = np.array(vec2)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def normalize_score(similarity: float) -> float:
    return max(0.0, round(similarity * 100, 2))


def tokenize_korean_english(text: str) -> list[str]:
    return re.findall(r'[A-Za-z]{2,}|[가-힣]{2,}', (text or '').lower())



def local_similarity(criteria_text: str, resume_text: str) -> float:
    criteria_tokens = tokenize_korean_english(criteria_text)
    resume_tokens = tokenize_korean_english(resume_text)
    if not criteria_tokens or not resume_tokens:
        return 0.0

    criteria_counts = Counter(criteria_tokens)
    resume_counts = Counter(resume_tokens)
    vocab = sorted(set(criteria_counts) | set(resume_counts))

    criteria_vec = np.array([criteria_counts[token] for token in vocab], dtype=float)
    resume_vec = np.array([resume_counts[token] for token in vocab], dtype=float)

    raw_similarity = cosine_similarity(criteria_vec, resume_vec)
    return min(1.0, raw_similarity * 2.5)



def score_resume(criteria_text: str, resume_text: str) -> tuple[float, float, str]:
    try:
        criteria_embedding = get_embedding(criteria_text)
        resume_embedding = get_embedding(resume_text)
        similarity = cosine_similarity(criteria_embedding, resume_embedding)
        return similarity, normalize_score(similarity), 'openai'
    except Exception:
        similarity = local_similarity(criteria_text, resume_text)
        return similarity, normalize_score(similarity), 'local'


def assign_group_labels(sorted_results: list[dict]) -> list[dict]:
    total = len(sorted_results)
    if total == 0:
        return sorted_results

    top_count = max(1, ceil(total * 0.3))
    mid_count = max(1, ceil(total * 0.3)) if total > 2 else max(0, total - top_count)
    if top_count + mid_count > total:
        mid_count = max(0, total - top_count)

    for idx, item in enumerate(sorted_results):
        if idx < top_count:
            item['group_label'] = '우선 검토 (상위 30%)'
        elif idx < top_count + mid_count:
            item['group_label'] = '보통 검토 (중간 30%)'
        else:
            item['group_label'] = '후순위 검토 (하위 40%)'
    return sorted_results


def build_summary_comment(criteria_text: str, resume_text: str, score: float) -> str:
    lowered = resume_text.lower()
    hits = {bucket: sum(keyword in lowered for keyword in keywords) for bucket, keywords in KEYWORD_BUCKETS.items()}

    if hits['overseas'] and hits['north_america'] and hits['manufacturing']:
        return '북미/해외영업과 제조업 제품 맥락이 함께 보여 우선 검토 가치가 높습니다.'
    if hits['overseas'] and hits['coordination']:
        return '해외 고객 대응 및 커뮤니케이션 관련 표현이 비교적 풍부합니다.'
    if hits['manufacturing']:
        return '제조업 맥락은 보이나 북미 해외영업 직접 경험은 추가 확인이 필요합니다.'
    if score >= 60:
        return '핵심 기준과 일정 수준의 유사성이 확인되어 검토 가치가 있습니다.'
    return '채용 기준과 직접 연결되는 경험 표현은 상대적으로 적어 보입니다.'


def find_relevant_sentences(criteria_text: str, resume_text: str, limit: int = 5) -> list[str]:
    criteria_keywords = set()
    for keywords in KEYWORD_BUCKETS.values():
        criteria_keywords.update(keywords)
    criteria_keywords.update([token.strip().lower() for token in criteria_text.split() if len(token.strip()) >= 3])

    ranked = []
    for sentence in split_sentences(resume_text):
        lowered = sentence.lower()
        score = sum(keyword in lowered for keyword in criteria_keywords)
        if score > 0:
            ranked.append((score, sentence))

    ranked.sort(key=lambda x: x[0], reverse=True)
    return [sentence for _, sentence in ranked[:limit]]
