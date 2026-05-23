from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas.resume import ResumeParseResult
from schemas.job import JobParseResult, RecommendationItem
from services.resume_parser import ResumeParserService
from services.jd_parser import JDParserService
from services.matching_engine import MatchingEngine
from services.resume_optimizer import ResumeOptimizerService
from services.recommendation_engine import RecommendationEngine
from services.application_tracker import ApplicationTrackerService
from utils.file_parser import parse_file
from app.database import engine, Base
import os
import json

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI简历优化与岗位匹配系统",
    description="面向应届生/转行人群的智能求职助手",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

resume_parser = ResumeParserService()
jd_parser = JDParserService()
matching_engine = MatchingEngine()
resume_optimizer = ResumeOptimizerService()
recommendation_engine = RecommendationEngine()
application_tracker = ApplicationTrackerService()

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/analyze", tags=["核心分析"])
async def analyze_resume(
    file: UploadFile = File(None),
    resume_text: str = Form(None),
    industry_preference: str = Form(None),
    city_preference: str = Form(None),
    salary_min: int = Form(0)
):
    content = None

    if file and file.filename:
        allowed_ext = ('.pdf', '.docx', '.doc', '.txt')
        if not file.filename.lower().endswith(allowed_ext):
            raise HTTPException(status_code=400, detail="仅支持 PDF / Word / TXT 格式")
        
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        content = parse_file(file_path)
        os.remove(file_path)

    if not content and resume_text:
        content = resume_text

    if not content:
        raise HTTPException(status_code=400, detail="请上传简历文件或粘贴简历内容")

    resume = resume_parser.parse(content)
    jobs = recommendation_engine.load_all_jobs()
    all_parsed_jobs = []

    for job_data in jobs:
        parsed_jd = jd_parser.parse(job_data.get('raw_jd', '') + ' ' + job_data.get('title', ''))
        match_result = matching_engine.calculate_match(resume, parsed_jd)

        salary_display = None
        if job_data.get('salary_min') and job_data.get('salary_max'):
            salary_display = f"{job_data['salary_min']//1000}-{job_data['salary_max']//1000}K"

        match_level = _get_match_level(match_result['total_score'])

        rec_item = {
            'job_id': job_data['id'],
            'title': job_data.get('title', ''),
            'company': job_data.get('company', ''),
            'company_size': job_data.get('company_size', ''),
            'industry': job_data.get('industry', ''),
            'city': job_data.get('city', ''),
            'salary_range': salary_display,
            'education': job_data.get('education', ''),
            'experience': job_data.get('experience', ''),
            'match_score': match_result['total_score'],
            'match_level': match_level,
            'match_details': match_result['match_details'],
            'recommendation_reason': _generate_reason(match_result, job_data),
            'posting_url': job_data.get('posting_url', ''),
            'referral_code': job_data.get('referral_code', ''),
            'hot_score': job_data.get('hot_score', 0)
        }
        all_parsed_jobs.append(rec_item)

    all_parsed_jobs.sort(key=lambda x: x['match_score'], reverse=True)

    best_job = all_parsed_jobs[0] if all_parsed_jobs else None
    optimized = None
    if best_job and best_job['match_score'] >= 30:
        best_jd = jd_parser.parse(
            jobs[0].get('raw_jd', '') + ' ' + jobs[0].get('title', '')
        )
        optimized = resume_optimizer.optimize(resume, best_jd)

    skill_analysis = _analyze_skills(resume, all_parsed_jobs[:5])

    return {
        'parsed_resume': resume.model_dump(),
        'skill_analysis': skill_analysis,
        'optimized_resume': optimized,
        'top_recommendations': all_parsed_jobs[:6],
        'all_jobs_count': len(all_parsed_jobs),
        'trend_skills': _extract_trend_skills(all_parsed_jobs[:10]),
        'industry_distribution': _calculate_industry_distribution(all_parsed_jobs)
    }

@app.post("/api/resume/parse", response_model=ResumeParseResult, tags=["简历解析"])
async def parse_resume(file: UploadFile = File(None), content: str = Form(None)):
    if not content and not file:
        raise HTTPException(status_code=400, detail="请提供简历内容或上传简历文件")

    if file:
        allowed_ext = ('.pdf', '.docx', '.doc', '.txt')
        if not file.filename.lower().endswith(allowed_ext):
            raise HTTPException(status_code=400, detail="仅支持 PDF / Word / TXT 格式")

        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        content = parse_file(file_path)
        os.remove(file_path)

    if not content:
        raise HTTPException(status_code=400, detail="无法解析简历内容")

    result = resume_parser.parse(content)
    return result

@app.post("/api/jd/parse", response_model=JobParseResult, tags=["JD解析"])
async def parse_jd(raw_jd: str = Form(...)):
    if not raw_jd:
        raise HTTPException(status_code=400, detail="请提供JD内容")
    result = jd_parser.parse(raw_jd)
    return result

@app.post("/api/match", tags=["智能匹配"])
async def calculate_match(resume_content: str = Form(...), jd_content: str = Form(...)):
    if not resume_content or not jd_content:
        raise HTTPException(status_code=400, detail="请提供简历和JD内容")
    resume = resume_parser.parse(resume_content)
    job = jd_parser.parse(jd_content)
    result = matching_engine.calculate_match(resume, job)
    return result

@app.post("/api/resume/optimize", tags=["简历优化"])
async def optimize_resume(resume_content: str = Form(...), jd_content: str = Form(...)):
    if not resume_content or not jd_content:
        raise HTTPException(status_code=400, detail="请提供简历和JD内容")
    resume = resume_parser.parse(resume_content)
    job = jd_parser.parse(jd_content)
    result = resume_optimizer.optimize(resume, job)
    return result

@app.get("/api/jobs", tags=["岗位查询"])
async def get_jobs():
    return recommendation_engine.load_all_jobs()

@app.post("/api/application/create", tags=["投递管理"])
async def create_application(user_id: str = Form(...), job_id: int = Form(...), notes: str = Form(None)):
    result = application_tracker.create_application(user_id, 0, job_id, notes)
    return result

@app.get("/api/application/user/{user_id}", tags=["投递管理"])
async def get_user_applications(user_id: str):
    return application_tracker.get_user_applications(user_id)

@app.put("/api/application/{application_id}/status", tags=["投递管理"])
async def update_application_status(application_id: int, status: str = Form(...)):
    success = application_tracker.update_application_status(application_id, status)
    if not success:
        raise HTTPException(status_code=404, detail="申请记录不存在")
    return {"message": "状态更新成功"}

@app.get("/api/application/stats/{user_id}", tags=["投递管理"])
async def get_application_stats(user_id: str):
    return application_tracker.get_application_stats(user_id)

@app.get("/")
async def root():
    return {"message": "AI简历优化与岗位匹配系统 API"}

def _get_match_level(score):
    if score >= 60:
        return "精准匹配"
    elif score >= 40:
        return "潜力匹配"
    elif score >= 20:
        return "跨界匹配"
    return "待提升"

def _generate_reason(match_result, job_data):
    reasons = []
    details = match_result.get('match_details', {})

    if details.get('education_match'):
        reasons.append("学历匹配")
    if details.get('industry_match'):
        reasons.append(f"符合{job_data.get('industry', '相关')}行业方向")

    missing = details.get('missing_required_skills', [])
    if not missing:
        reasons.append("核心技能全覆盖")
    elif len(missing) <= 2:
        reasons.append(f"核心技能基本满足（仅缺{len(missing)}项）")

    if not reasons:
        reasons.append("综合岗位契合度较高")
    return '，'.join(reasons)

def _analyze_skills(resume, top_jobs):
    resume_skills = [s.skill_name for s in resume.skills]
    demanded_skills = set()
    for job in top_jobs:
        for skill in job.get('match_details', {}).get('missing_required_skills', []):
            demanded_skills.add(skill)

    return {
        'your_skills': resume_skills[:10],
        'skill_count': len(resume_skills),
        'suggested_skills': list(demanded_skills)[:5],
        'skill_coverage': f"{min(100, len(resume_skills) * 10)}%"
    }

def _extract_trend_skills(top_jobs):
    skill_counter = {}
    for job in top_jobs:
        for skill in job.get('match_details', {}).get('missing_required_skills', []):
            skill_counter[skill] = skill_counter.get(skill, 0) + 1
    return sorted(skill_counter.items(), key=lambda x: x[1], reverse=True)[:6]

def _calculate_industry_distribution(jobs):
    dist = {}
    for job in jobs:
        industry = job.get('industry', '未知')
        dist[industry] = dist.get(industry, 0) + 1
    return dist

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
