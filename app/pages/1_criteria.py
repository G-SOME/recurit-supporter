import streamlit as st
from datetime import datetime

from core.config import CRITERIA_DIR
from core.schemas import Criteria
from core.utils.io import save_json

st.title("1) 기준 설정")

job_title = st.text_input("포지션명", value="HR Operations Manager")
job_family = st.text_input("직군", value="HRM")
min_years = st.number_input("최소 경력(년)", min_value=0.0, value=3.0, step=0.5)
location = st.text_input("근무지", value="서울")
employment_type = st.selectbox("고용형태", ["정규직", "계약직"], index=0)

must_have_text = st.text_area("필수 역량(줄바꿈으로 구분)", value="인사 운영 프로세스 개선 경험\n평가 또는 보상 운영 경험\n부서 간 커뮤니케이션 및 조율 능력")
nice_to_have_text = st.text_area("우대 역량(줄바꿈으로 구분)", value="HR 데이터 분석 및 리포팅 경험\nATS/HRIS 사용 경험")
core_values_text = st.text_area("인재상/핵심가치(줄바꿈으로 구분)", value="주도성\n협업\n문제해결\n데이터 기반 의사결정")

if st.button("기준 저장", type="primary"):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_id = f"job_{ts}"

    criteria = Criteria(
        job_id=job_id,
        version=1,
        job_title=job_title,
        job_family=job_family,
        min_years=float(min_years),
        location=location,
        employment_type=employment_type,
        must_have=[x.strip() for x in must_have_text.splitlines() if x.strip()],
        nice_to_have=[x.strip() for x in nice_to_have_text.splitlines() if x.strip()],
        core_values=[x.strip() for x in core_values_text.splitlines() if x.strip()],
    )

    out_path = CRITERIA_DIR / f"{criteria.job_id}_v{criteria.version}.json"
    save_json(out_path, criteria.model_dump())
    st.success(f"저장 완료: {out_path}")

st.divider()
st.caption(f"기준 저장 폴더: {CRITERIA_DIR}")
