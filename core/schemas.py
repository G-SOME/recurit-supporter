from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class Criteria(BaseModel):
    job_id: str
    version: int = 1
    job_title: str
    job_family: str = "HRM"
    min_years: float = 0
    location: str = ""
    employment_type: str = "정규직"
    must_have: List[str] = Field(default_factory=list)
    nice_to_have: List[str] = Field(default_factory=list)
    core_values: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ParsedResume(BaseModel):
    candidate_id: str
    name: str = ""
    resume_file_name: str
    raw_text: str
    sections: dict
    parsed_years_exp: float = 0.0
    skill_keywords: List[str] = Field(default_factory=list)
    embedding_id: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
