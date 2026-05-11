import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
DB_PATH = DATA_DIR / 'app.db'


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS job_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            job_description TEXT,
            criteria_text TEXT NOT NULL,
            preferred_text TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS candidate_resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_profile_id INTEGER,
            candidate_name TEXT,
            file_name TEXT NOT NULL,
            file_type TEXT,
            raw_text TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_profile_id) REFERENCES job_profiles(id)
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS match_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_profile_id INTEGER,
            candidate_resume_id INTEGER,
            score REAL,
            group_label TEXT,
            summary_comment TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_profile_id) REFERENCES job_profiles(id),
            FOREIGN KEY (candidate_resume_id) REFERENCES candidate_resumes(id)
        )
    ''')
    conn.commit()
    conn.close()


def insert_job_profile(title: str, job_description: str, criteria_text: str, preferred_text: str | None) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO job_profiles (title, job_description, criteria_text, preferred_text) VALUES (?, ?, ?, ?)',
        (title, job_description, criteria_text, preferred_text),
    )
    conn.commit()
    job_id = cur.lastrowid
    conn.close()
    return job_id


def fetch_job_profiles():
    conn = get_connection()
    rows = conn.execute('SELECT * FROM job_profiles ORDER BY created_at DESC').fetchall()
    conn.close()
    return rows


def fetch_job_profile(job_id: int):
    conn = get_connection()
    row = conn.execute('SELECT * FROM job_profiles WHERE id = ?', (job_id,)).fetchone()
    conn.close()
    return row


def insert_resume(job_profile_id: int, candidate_name: str, file_name: str, file_type: str, raw_text: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO candidate_resumes (job_profile_id, candidate_name, file_name, file_type, raw_text) VALUES (?, ?, ?, ?, ?)',
        (job_profile_id, candidate_name, file_name, file_type, raw_text),
    )
    conn.commit()
    resume_id = cur.lastrowid
    conn.close()
    return resume_id


def fetch_resumes(job_profile_id: int):
    conn = get_connection()
    rows = conn.execute('SELECT * FROM candidate_resumes WHERE job_profile_id = ? ORDER BY created_at DESC', (job_profile_id,)).fetchall()
    conn.close()
    return rows


def delete_match_results(job_profile_id: int) -> None:
    conn = get_connection()
    conn.execute('DELETE FROM match_results WHERE job_profile_id = ?', (job_profile_id,))
    conn.commit()
    conn.close()


def insert_match_result(job_profile_id: int, candidate_resume_id: int, score: float, group_label: str, summary_comment: str) -> None:
    conn = get_connection()
    conn.execute(
        'INSERT INTO match_results (job_profile_id, candidate_resume_id, score, group_label, summary_comment) VALUES (?, ?, ?, ?, ?)',
        (job_profile_id, candidate_resume_id, score, group_label, summary_comment),
    )
    conn.commit()
    conn.close()


def fetch_match_results(job_profile_id: int):
    conn = get_connection()
    rows = conn.execute('''
        SELECT mr.*, cr.candidate_name, cr.file_name, cr.raw_text
        FROM match_results mr
        JOIN candidate_resumes cr ON mr.candidate_resume_id = cr.id
        WHERE mr.job_profile_id = ?
        ORDER BY mr.score DESC
    ''', (job_profile_id,)).fetchall()
    conn.close()
    return rows


def fetch_candidate_by_id(candidate_id: int):
    conn = get_connection()
    row = conn.execute('SELECT * FROM candidate_resumes WHERE id = ?', (candidate_id,)).fetchone()
    conn.close()
    return row
