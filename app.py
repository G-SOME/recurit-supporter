import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from utils.db import (
    delete_match_results,
    fetch_candidate_by_id,
    fetch_job_profile,
    fetch_job_profiles,
    fetch_match_results,
    fetch_resumes,
    init_db,
    insert_job_profile,
    insert_match_result,
    insert_resume,
)
from utils.helpers import get_extension, truncate_preview
from utils.matching import assign_group_labels, build_summary_comment, find_relevant_sentences, score_resume
from utils.parser import extract_text, infer_candidate_name

load_dotenv()

st.set_page_config(page_title='Recruit Supporter Dashboard', layout='wide')
init_db()

for key, default in {
    'selected_job_id': None,
    'parsed_resumes': [],
    'analysis_done': False,
    'selected_candidate_id': None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def load_sample_criteria():
    return {
        'title': '북미 해외영업',
        'job_description': '제조업 제품 세일즈 중심의 해외영업 포지션',
        'criteria_text': '북미 지역 고객을 대상으로 한 해외영업 수행 가능성이 높은 후보자를 우선 검토한다. 영어 기반 커뮤니케이션 역량, 바이어 대응 경험, 제조업 제품에 대한 이해, 수주형 영업 프로세스 적응력, 협상 및 일정 조율 능력, 대내외 커뮤니케이션 역량을 중요하게 본다. 단순 상품유통보다 제품 기반 제조업 세일즈 맥락을 더 높게 평가한다.',
        'preferred_text': '북미 거래처 대응 경험, 해외 전시회/출장 경험, 기술영업 또는 생산/품질/납기 협업 경험, 수출입 문서 및 무역 실무 이해',
    }


st.sidebar.title('Recruit Supporter Dashboard')
st.sidebar.caption('북미 해외영업 / 제조업 세일즈용 AI 이력서 스크리닝')

job_profiles = fetch_job_profiles()
job_options = {f"{row['title']} (ID: {row['id']})": row['id'] for row in job_profiles}

if st.session_state['selected_job_id']:
    selected_job = fetch_job_profile(st.session_state['selected_job_id'])
    selected_job_title = selected_job['title'] if selected_job else '없음'
else:
    selected_job_title = '없음'

st.sidebar.markdown(f'**현재 선택 기준:** {selected_job_title}')
st.sidebar.markdown(f"**업로드된 이력서 수:** {len(st.session_state['parsed_resumes'])}건")
st.sidebar.markdown(f"**분석 상태:** {'완료' if st.session_state['analysis_done'] else '분석 전'}")

if st.sidebar.button('전체 초기화'):
    st.session_state['selected_job_id'] = None
    st.session_state['parsed_resumes'] = []
    st.session_state['analysis_done'] = False
    st.session_state['selected_candidate_id'] = None
    st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(['기준 설정', '이력서 업로드', '분석 결과', '후보자 상세'])

with tab1:
    st.subheader('채용 기준 설정')
    st.caption('형식보다 실제 채용 의도를 자연어로 적는 것이 더 중요합니다.')

    sample = load_sample_criteria()
    if st.button('샘플 기준 불러오기'):
        st.session_state['criteria_form'] = sample

    form_defaults = st.session_state.get('criteria_form', {'title': '', 'job_description': '', 'criteria_text': '', 'preferred_text': ''})

    title = st.text_input('채용명', value=form_defaults.get('title', ''))
    job_description = st.text_area('직무 설명', value=form_defaults.get('job_description', ''), height=80)
    criteria_text = st.text_area('채용 기준 설명', value=form_defaults.get('criteria_text', ''), height=180)
    preferred_text = st.text_area('우대 요소 (선택)', value=form_defaults.get('preferred_text', ''), height=100)

    if st.button('기준 저장'):
        if not title.strip():
            st.warning('채용명을 입력해주세요.')
        elif not criteria_text.strip():
            st.warning('채용 기준 설명을 입력해주세요.')
        else:
            job_id = insert_job_profile(title.strip(), job_description.strip(), criteria_text.strip(), preferred_text.strip())
            st.session_state['selected_job_id'] = job_id
            st.success('기준이 저장되었습니다.')
            st.rerun()

    st.markdown('---')
    st.subheader('저장된 기준 목록')
    refreshed_profiles = fetch_job_profiles()
    if refreshed_profiles:
        for row in refreshed_profiles:
            st.markdown(f"**{row['title']}**  ")
            st.caption(truncate_preview(row['criteria_text'], 180))
    else:
        st.info('아직 저장된 기준이 없습니다.')

with tab2:
    st.subheader('이력서 업로드')
    st.caption('PDF, DOCX 파일을 여러 개 한 번에 올릴 수 있습니다.')

    selected_label = st.selectbox('적용할 채용 기준 선택', options=['선택하세요'] + list(job_options.keys()))
    if selected_label != '선택하세요':
        st.session_state['selected_job_id'] = job_options[selected_label]

    uploaded_files = st.file_uploader('이력서 업로드', type=['pdf', 'docx'], accept_multiple_files=True)

    if st.button('텍스트 추출'):
        if not st.session_state['selected_job_id']:
            st.warning('먼저 적용할 채용 기준을 선택해주세요.')
        elif not uploaded_files:
            st.warning('이력서를 1개 이상 업로드해주세요.')
        else:
            parsed_resumes = []
            for file in uploaded_files:
                extension = get_extension(file.name)
                try:
                    raw_text = extract_text(file, extension)
                    candidate_name = infer_candidate_name(file.name, raw_text)
                    parsed_resumes.append({
                        'candidate_name': candidate_name,
                        'file_name': file.name,
                        'file_type': extension,
                        'raw_text': raw_text,
                        'status': '성공' if raw_text else '부분 성공',
                    })
                except Exception as exc:
                    parsed_resumes.append({
                        'candidate_name': file.name,
                        'file_name': file.name,
                        'file_type': extension,
                        'raw_text': '',
                        'status': f'실패: {exc}',
                    })
            st.session_state['parsed_resumes'] = parsed_resumes
            st.session_state['analysis_done'] = False

    if st.session_state['parsed_resumes']:
        preview_df = pd.DataFrame([
            {
                '후보자명': row['candidate_name'],
                '파일명': row['file_name'],
                '형식': row['file_type'],
                '상태': row['status'],
                '미리보기': truncate_preview(row['raw_text'], 120),
            }
            for row in st.session_state['parsed_resumes']
        ])
        st.dataframe(preview_df, use_container_width=True)

    if st.button('분석 실행'):
        if not st.session_state['selected_job_id']:
            st.warning('먼저 적용할 채용 기준을 선택해주세요.')
        elif not st.session_state['parsed_resumes']:
            st.warning('먼저 텍스트 추출을 완료해주세요.')
        else:
            job_profile = fetch_job_profile(st.session_state['selected_job_id'])
            criteria_blob = f"{job_profile['criteria_text']}\n{job_profile['preferred_text'] or ''}".strip()

            try:
                delete_match_results(job_profile['id'])
                results = []
                analysis_modes = set()
                for resume in st.session_state['parsed_resumes']:
                    if not resume['raw_text']:
                        continue
                    resume_id = insert_resume(
                        job_profile['id'],
                        resume['candidate_name'],
                        resume['file_name'],
                        resume['file_type'],
                        resume['raw_text'],
                    )
                    similarity, score, mode = score_resume(criteria_blob, resume['raw_text'])
                    analysis_modes.add(mode)
                    results.append({
                        'candidate_resume_id': resume_id,
                        'candidate_name': resume['candidate_name'],
                        'file_name': resume['file_name'],
                        'score': score,
                        'similarity': similarity,
                        'summary_comment': build_summary_comment(criteria_blob, resume['raw_text'], score),
                    })

                results.sort(key=lambda x: x['score'], reverse=True)
                results = assign_group_labels(results)

                for result in results:
                    insert_match_result(
                        job_profile['id'],
                        result['candidate_resume_id'],
                        result['score'],
                        result['group_label'],
                        result['summary_comment'],
                    )

                st.session_state['analysis_done'] = True
                if analysis_modes == {'local'}:
                    st.warning('OpenAI API 대신 로컬 유사도 방식으로 분석했습니다. 데모/MVP 용도로는 충분하지만 정밀도는 임베딩 방식보다 낮을 수 있습니다.')
                elif 'local' in analysis_modes:
                    st.warning('일부 항목은 OpenAI 대신 로컬 유사도 방식으로 분석했습니다.')
                st.success('분석이 완료되었습니다. 결과 탭에서 확인하세요.')
            except Exception as exc:
                error_text = str(exc)
                st.error(f'분석 중 오류가 발생했습니다: {error_text}')

with tab3:
    st.subheader('분석 결과')
    if not st.session_state['selected_job_id']:
        st.info('먼저 채용 기준을 선택하거나 저장해주세요.')
    else:
        match_rows = fetch_match_results(st.session_state['selected_job_id'])
        if not match_rows:
            st.info('먼저 이력서 업로드 탭에서 분석을 실행해주세요.')
        else:
            rows = [dict(row) for row in match_rows]
            top_count = sum('우선 검토' in row['group_label'] for row in rows)
            mid_count = sum('보통 검토' in row['group_label'] for row in rows)
            low_count = sum('후순위 검토' in row['group_label'] for row in rows)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric('총 후보자 수', len(rows))
            col2.metric('상위 30%', top_count)
            col3.metric('중간 30%', mid_count)
            col4.metric('하위 40%', low_count)

            group_filter = st.multiselect('그룹 필터', ['우선 검토 (상위 30%)', '보통 검토 (중간 30%)', '후순위 검토 (하위 40%)'])
            search_term = st.text_input('이름/파일명 검색')
            sort_order = st.selectbox('정렬 기준', ['적합도 점수 높은순', '적합도 점수 낮은순'])

            filtered_rows = rows
            if group_filter:
                filtered_rows = [row for row in filtered_rows if row['group_label'] in group_filter]
            if search_term.strip():
                token = search_term.strip().lower()
                filtered_rows = [
                    row for row in filtered_rows
                    if token in (row['candidate_name'] or '').lower() or token in (row['file_name'] or '').lower()
                ]
            reverse = sort_order == '적합도 점수 높은순'
            filtered_rows = sorted(filtered_rows, key=lambda x: x['score'], reverse=reverse)

            result_df = pd.DataFrame([
                {
                    '후보자명': row['candidate_name'],
                    '파일명': row['file_name'],
                    '적합도 점수': row['score'],
                    '그룹': row['group_label'],
                    '요약 코멘트': row['summary_comment'],
                }
                for row in filtered_rows
            ])
            st.dataframe(result_df, use_container_width=True)

            candidate_options = {f"{row['candidate_name']} | {row['file_name']}": row['candidate_resume_id'] for row in filtered_rows}
            if candidate_options:
                detail_label = st.selectbox('상세보기 후보 선택', ['선택하세요'] + list(candidate_options.keys()))
                if detail_label != '선택하세요':
                    st.session_state['selected_candidate_id'] = candidate_options[detail_label]
                    st.success('후보자 상세 탭에서 확인할 수 있습니다.')

with tab4:
    st.subheader('후보자 상세')
    candidate_id = st.session_state.get('selected_candidate_id')
    if not candidate_id:
        st.info('분석 결과 탭에서 후보자를 선택해주세요.')
    else:
        candidate = fetch_candidate_by_id(candidate_id)
        job_profile = fetch_job_profile(st.session_state['selected_job_id']) if st.session_state['selected_job_id'] else None
        if not candidate or not job_profile:
            st.warning('후보자 정보를 불러올 수 없습니다.')
        else:
            match_rows = fetch_match_results(job_profile['id'])
            matched = next((dict(row) for row in match_rows if row['candidate_resume_id'] == candidate_id), None)

            st.markdown(f"### {candidate['candidate_name']}")
            col1, col2 = st.columns(2)
            col1.metric('적합도 점수', matched['score'] if matched else '-')
            col2.metric('그룹', matched['group_label'] if matched else '-')

            st.markdown('**파일명**')
            st.write(candidate['file_name'])

            if matched:
                st.markdown('**요약 코멘트**')
                st.write(matched['summary_comment'])

            st.markdown('**매칭 근거 문장**')
            evidence = find_relevant_sentences(job_profile['criteria_text'], candidate['raw_text'])
            if evidence:
                for sentence in evidence:
                    st.write(f'- {sentence}')
            else:
                st.caption('추출된 근거 문장이 없습니다.')

            st.markdown('**이력서 원문 미리보기**')
            st.text_area('resume_preview', value=candidate['raw_text'], height=260, label_visibility='collapsed')
