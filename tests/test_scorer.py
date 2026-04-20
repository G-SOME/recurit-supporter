from core.matching.scorer import compute_final_score


def test_compute_final_score():
    s = compute_final_score(80, 70, 60, 50)
    assert round(s, 1) == 72.5
