def hard_filter(result: dict) -> bool:
    if result.get("career_fit_score", 100) < 50:
        return False
    if result.get("must_have_score", 100) < 40:
        return False
    return True
