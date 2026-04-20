def compute_final_score(semantic: float, must_have: float, career_fit: float, keyword_evidence: float) -> float:
    return (0.50 * semantic) + (0.25 * must_have) + (0.15 * career_fit) + (0.10 * keyword_evidence)
