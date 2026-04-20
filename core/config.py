from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
CRITERIA_DIR = DATA_DIR / "criteria"
RESUMES_RAW_DIR = DATA_DIR / "resumes_raw"
RESUMES_PARSED_DIR = DATA_DIR / "resumes_parsed"

for d in [CRITERIA_DIR, RESUMES_RAW_DIR, RESUMES_PARSED_DIR]:
    d.mkdir(parents=True, exist_ok=True)
