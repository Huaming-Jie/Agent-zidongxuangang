from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class JobSkillItem(BaseModel):
    skill_name: str
    is_required: bool = False
    importance: float = 1.0

class JobParseResult(BaseModel):
    education: Optional[str] = None
    experience_required: Optional[str] = None
    major: Optional[str] = None
    required_certificates: List[str] = []
    required_skills: List[JobSkillItem] = []
    optional_skills: List[JobSkillItem] = []
    soft_skills: List[str] = []
    industry: Optional[str] = None
    job_type: Optional[str] = None
    salary_range: Optional[str] = None

class JobBase(BaseModel):
    title: str
    company: str
    company_size: Optional[str] = None
    industry: Optional[str] = None
    job_type: Optional[str] = None
    city: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    education: Optional[str] = None
    experience: Optional[str] = None
    raw_jd: Optional[str] = None
    posting_url: Optional[str] = None
    referral_code: Optional[str] = None

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    parsed_data: Optional[JobParseResult] = None
    hot_score: int = 0
    created_at: datetime

class MatchScoreDetail(BaseModel):
    skill_score: float = 0.0
    project_score: float = 0.0
    education_score: float = 0.0
    industry_score: float = 0.0
    keyword_score: float = 0.0

class MatchResultResponse(BaseModel):
    resume_id: int
    job_id: int
    total_score: float
    score_detail: MatchScoreDetail
    match_details: dict = {}
    created_at: datetime

class RecommendationItem(BaseModel):
    job_id: int
    title: str
    company: str
    city: Optional[str] = None
    salary_range: Optional[str] = None
    match_score: float
    recommendation_reason: str
    posting_url: Optional[str] = None
    referral_code: Optional[str] = None
    match_level: str = "potential"

class ApplicationCreate(BaseModel):
    resume_id: int
    job_id: int
    notes: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: int
    user_id: str
    resume_id: int
    job_id: int
    status: str
    applied_at: datetime
    last_updated: datetime