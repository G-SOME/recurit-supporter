def rank_candidates(results: list[dict], top_n: int = 20) -> list[dict]:
    return sorted(results, key=lambda x: x.get("final_score", 0), reverse=True)[:top_n]
