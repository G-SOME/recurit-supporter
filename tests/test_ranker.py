from core.matching.ranker import rank_candidates


def test_rank_candidates():
    rows = [{"final_score": 10}, {"final_score": 20}]
    out = rank_candidates(rows, top_n=1)
    assert out[0]["final_score"] == 20
