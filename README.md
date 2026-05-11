# Recruit Supporter Dashboard

북미 해외영업 / 제조업 제품 세일즈 포지션을 위한 **AI-assisted 이력서 1차 스크리닝 Streamlit MVP**입니다.

이 프로젝트는 채용 담당자가 자유 텍스트로 채용 기준을 입력하고, PDF/DOCX 이력서를 업로드해 **적합도 점수 + 상/중/하 그룹 분류 + 근거 문장 확인**까지 빠르게 수행할 수 있도록 설계되었습니다.

## 핵심 기능

- **자유 텍스트 채용 기준 저장**
  - 채용명
  - 직무 설명
  - 채용 기준 설명
  - 우대 요소
- **이력서 업로드 및 텍스트 추출**
  - PDF (`pdfplumber`)
  - DOCX (`python-docx`)
- **후보자 적합도 분석**
  - OpenAI 임베딩 기반 분석 우선 시도
  - API quota/billing이 없을 경우 **로컬 유사도 fallback** 자동 전환
- **후보자 그룹 분류**
  - 우선 검토 (상위 30%)
  - 보통 검토 (중간 30%)
  - 후순위 검토 (하위 40%)
- **후보자 상세 보기**
  - 점수/그룹
  - 요약 코멘트
  - 기준과 유사한 문장 근거

## 프로젝트 구조

```bash
recurit-supporter/
├─ app.py
├─ requirements.txt
├─ .env.example
├─ PROJECT_SUMMARY.md
├─ PROJECT_INTENT.md
├─ HISTORY.md
├─ run_recruit_supporter.bat
├─ data/
│  └─ .gitkeep
└─ utils/
   ├─ db.py
   ├─ parser.py
   ├─ embedding.py
   ├─ matching.py
   ├─ helpers.py
   └─ __init__.py
```

## 실행 방법

### 1) 패키지 설치
```bash
py -3 -m pip install -r requirements.txt
```

### 2) 환경변수 파일 생성
`.env.example`를 복사해 `.env` 파일을 만든 뒤 아래처럼 입력합니다.

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

> OpenAI API billing/quota가 없으면 앱은 자동으로 로컬 유사도 방식으로 fallback 됩니다.

### 3) 앱 실행
```bash
py -3 -m streamlit run app.py
```

또는 Windows에서는 `run_recruit_supporter.bat`를 더블클릭해 실행할 수 있습니다.

## 사용 흐름

1. **기준 설정** 탭에서 채용 기준 저장
2. **이력서 업로드** 탭에서 PDF/DOCX 업로드 후 텍스트 추출
3. **분석 실행** 클릭
4. **분석 결과** 탭에서 후보자 그룹/점수 확인
5. **후보자 상세** 탭에서 근거 문장 확인

## 기술 스택

- **Frontend**: Streamlit
- **Parsing**: pdfplumber, python-docx
- **Vector / Similarity**:
  - OpenAI Embedding (`text-embedding-3-small`)
  - Local token-overlap fallback similarity
- **Storage**: SQLite (`data/app.db`)
- **Language**: Python 3.13

## 현재 한계

- 로컬 fallback은 MVP/데모 목적이며 임베딩 기반보다 정밀도가 낮습니다.
- 후보자명은 현재 파일명 기반으로 추출합니다.
- 결과 CSV 다운로드, 면접 질문 추천, 자연어 검색은 아직 후속 단계입니다.

## 향후 확장 아이디어

- 자연어 검색 기반 후보 필터링
- 면접 질문 추천 / 검증 포인트 하이라이트
- 섹션별 점수(경력/프로젝트/스킬)
- CSV/엑셀 결과 다운로드
- FastAPI + DB + 권한관리 구조로 확장

## 주의

이 도구는 **추천/보조 시스템**이며 자동 탈락 결정용으로 사용하지 않습니다. 최종 판단은 반드시 사람 검토를 거쳐야 합니다.
