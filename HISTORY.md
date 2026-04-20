# Development History

## 2026-04-20 - D1 bootstrap

### Scope completed
- Initialized project skeleton for `recruit-supporter`
- Added Streamlit app/pages structure
- Implemented criteria setup page (`1_criteria.py`)
- Implemented resume upload/parsing page (`2_resume_upload.py`)
- Added parser modules:
  - `pdf_parser.py`
  - `docx_parser.py`
  - `section_splitter.py`
  - `resume_parser.py`
- Added base schema/config/utils
- Added placeholder modules for D2/D3 (embedding/vector/matching detail)
- Added sample criteria JSON
- Added tests placeholders and basic score/ranker tests

### Key architectural decisions recorded
1. **MVP UI**: Streamlit chosen for speed and operator familiarity.
2. **Data storage (D1)**: JSON files for transparency and easy iteration.
3. **Vector strategy**: FAISS planned in D2 (placeholder in D1).
4. **Ranking strategy**:
   - D1/D2: hybrid score (semantic + must-have + career-fit + keyword evidence)
   - later: cross-encoder reranking for deeper semantic precision.
5. **LLM role (later phase)**:
   - resume summary,
   - fit explanation,
   - JD gap analysis,
   - interview question generation.

### Product reasoning trail
The design explicitly acknowledges limitations of vector-only filtering:
- keyword stuffing can inflate scores,
- depth/ownership level can be missed,
- nuanced context (e.g., exposure vs leadership) is hard to separate.

So the roadmap is intentionally staged as:
- retrieval first,
- reranking second,
- generation/analysis third.

### Commit log
- `feat: bootstrap D1 recruiter supporter skeleton with criteria and resume parsing`

