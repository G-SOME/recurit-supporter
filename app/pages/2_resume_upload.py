import uuid
from pathlib import Path
import streamlit as st

from core.config import RESUMES_RAW_DIR, RESUMES_PARSED_DIR
from core.schemas import ParsedResume
from core.parser.resume_parser import parse_resume
from core.utils.io import save_json

st.title("2) 이력서 업로드 & 파싱")

uploaded_files = st.file_uploader(
    "PDF/DOCX 파일 업로드", type=["pdf", "docx", "doc"], accept_multiple_files=True
)

if st.button("파싱 실행", type="primary"):
    if not uploaded_files:
        st.warning("먼저 파일을 업로드하세요.")
        st.stop()

    for f in uploaded_files:
        try:
            candidate_id = f"cand_{uuid.uuid4().hex[:8]}"
            raw_path = RESUMES_RAW_DIR / f"{candidate_id}_{f.name}"
            with open(raw_path, "wb") as out:
                out.write(f.read())

            parsed = parse_resume(str(raw_path))
            payload = ParsedResume(
                candidate_id=candidate_id,
                name="",
                resume_file_name=f.name,
                raw_text=parsed["raw_text"],
                sections=parsed["sections"],
                parsed_years_exp=parsed["parsed_years_exp"],
                skill_keywords=parsed["skill_keywords"],
                embedding_id=f"vec_{candidate_id}",
            ).model_dump()

            out_json = RESUMES_PARSED_DIR / f"{candidate_id}.json"
            save_json(out_json, payload)

            st.success(f"완료: {f.name} -> {out_json.name}")
            with st.expander(f"미리보기: {f.name}"):
                st.write(payload["sections"]["summary"][:500])
                st.write("키워드:", payload["skill_keywords"])

        except Exception as e:
            st.error(f"실패: {f.name} / 오류: {e}")

st.divider()
st.caption(f"원본 저장 폴더: {RESUMES_RAW_DIR}")
st.caption(f"파싱 JSON 폴더: {RESUMES_PARSED_DIR}")
