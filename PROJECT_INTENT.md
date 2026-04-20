# Recruit Supporter - Project Intent

## Why this project exists
This project was initiated to build a practical AI-assisted recruiting support system for real hiring workflows.

The core motivation is:
- reduce manual resume screening time,
- improve first-pass candidate filtering quality,
- keep decision rationale visible and auditable.

## Product direction
Rather than building a fixed enterprise ATS from day one, the project starts as a fast MVP and evolves iteratively.

### MVP form (Phase 1)
- Streamlit-based internal web app
- JD/company competency setup
- Resume parsing (PDF/DOCX)
- Vector-based candidate filtering and ranking

### Planned evolution
- Phase 2: precision reranking (cross-encoder)
- Phase 3: LLM-based explanation, gap analysis, interview question generation

## Important decision principles
1. **Usability first**: choose tools already familiar to the team (Streamlit) for fast implementation.
2. **Explainability first**: always show score breakdown and evidence snippets.
3. **Human-in-the-loop**: this is a recommendation assistant, not an auto-reject engine.
4. **Iterative architecture**: start simple (local JSON/FAISS), then scale to service split (FastAPI + DB + auth).

## Candidate scoring philosophy
Vector similarity alone is insufficient due to:
- keyword stuffing risks,
- limited depth/experience distinction,
- weak context nuance handling.

Therefore the long-term target pipeline is:
1) embedding retrieval (recall),
2) reranker/cross-encoder (precision),
3) LLM reasoning layer (explanation/actionability).
