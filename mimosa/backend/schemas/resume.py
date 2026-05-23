from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PersonalInfo(BaseModel):
    name: Optional[str] = None
    education: Optional[str] = None
    major: Optional[str] = None
    school: Optional[str] = None
    work_years: Optional[int] = None
    target_city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class SkillItem(BaseModel):
    skill_name: str
    proficiency: Optional[str] = None
    category: Optional[str] = None

class ProjectItem(BaseModel):
    project_name: str
    responsibilities: Optional[str] = None
    tech_stack: List[str] = []
    achievements: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class WorkExperience(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    responsibilities: Optional[str] = None

class ResumeParseResult(BaseModel):
    personal_info: PersonalInfo
    skills: List[SkillItem] = []
    projects: List[ProjectItem] = []
    work_experience: List[WorkExperience] = []
    raw_content: Optional[str] = None

class ResumeCreate(BaseModel):
    content: str = Field(description="简历文本内容")
    user_id: Optional[str] = None

class ResumeResponse(BaseModel):
    id: int
    user_id: Optional[str]
    parsed_data: ResumeParseResult
    created_at: datetime