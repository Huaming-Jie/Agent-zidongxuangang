from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Float
from datetime import datetime
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String)
    company_size = Column(String)
    industry = Column(String)
    job_type = Column(String)
    city = Column(String)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    education = Column(String)
    experience = Column(String)
    raw_jd = Column(Text)
    parsed_data = Column(JSON)
    posting_url = Column(String)
    referral_code = Column(String)
    hot_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class JobSkill(Base):
    __tablename__ = "job_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer)
    skill_name = Column(String, index=True)
    is_required = Column(Integer)
    importance = Column(Float)

class MatchResult(Base):
    __tablename__ = "match_results"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer)
    job_id = Column(Integer)
    total_score = Column(Float)
    skill_score = Column(Float)
    project_score = Column(Float)
    education_score = Column(Float)
    industry_score = Column(Float)
    keyword_score = Column(Float)
    match_details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class ApplicationRecord(Base):
    __tablename__ = "application_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    resume_id = Column(Integer)
    job_id = Column(Integer)
    status = Column(String, default="applied")
    applied_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)