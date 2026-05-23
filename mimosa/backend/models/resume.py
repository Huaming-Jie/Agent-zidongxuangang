from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from datetime import datetime
from app.database import Base

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    raw_content = Column(Text)
    parsed_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ResumeSkill(Base):
    __tablename__ = "resume_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer)
    skill_name = Column(String, index=True)
    proficiency = Column(String)
    category = Column(String)

class ProjectExperience(Base):
    __tablename__ = "project_experiences"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer)
    project_name = Column(String)
    responsibilities = Column(Text)
    tech_stack = Column(JSON)
    achievements = Column(Text)
    start_date = Column(String)
    end_date = Column(String)