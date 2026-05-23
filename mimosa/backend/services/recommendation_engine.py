from schemas.resume import ResumeParseResult
from schemas.job import JobResponse, RecommendationItem
from typing import List, Dict
import json
import os

class RecommendationEngine:
    def __init__(self):
        self.job_data_path = os.getenv("JD_DATA_PATH", "./data/job_data.json")
        self.jobs = self._load_jobs()

    def _load_jobs(self) -> List[Dict]:
        if os.path.exists(self.job_data_path):
            with open(self.job_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def load_all_jobs(self) -> List[Dict]:
        return self.jobs if self.jobs else self._load_jobs()

    def recommend(self, resume: ResumeParseResult, city_preference: str = None, salary_min: int = 0) -> List[RecommendationItem]:
        recommendations = []
        resume_skills = {s.skill_name.lower() for s in resume.skills}
        
        for job in self.jobs:
            if city_preference and job.get('city') != city_preference:
                continue
            if salary_min > 0 and job.get('salary_min', 0) < salary_min:
                continue

            job_skills = set()
            if job.get('raw_jd'):
                for skill in resume_skills:
                    if skill.lower() in job['raw_jd'].lower():
                        job_skills.add(skill)

            score = self._calculate_match_score(resume, job)
            match_level = self._get_match_level(score)
            reason = self._generate_reason(resume, job, score)

            recommendations.append(RecommendationItem(
                job_id=job['id'],
                title=job['title'],
                company=job['company'],
                city=job.get('city'),
                salary_range=f"{job.get('salary_min', 0)//1000}-{job.get('salary_max', 0)//1000}K" if job.get('salary_min') else None,
                match_score=score,
                recommendation_reason=reason,
                posting_url=job.get('posting_url'),
                referral_code=job.get('referral_code'),
                match_level=match_level
            ))

        recommendations.sort(key=lambda x: x.match_score, reverse=True)
        return recommendations[:10]

    def _calculate_match_score(self, resume: ResumeParseResult, job: Dict) -> float:
        score = 50.0
        
        resume_skills = {s.skill_name.lower() for s in resume.skills}
        
        job_text = job.get('raw_jd', '') + job.get('title', '') + job.get('industry', '')
        matched_skills = 0
        
        for skill in resume_skills:
            if skill in job_text.lower():
                matched_skills += 1
        
        if resume_skills:
            skill_match = matched_skills / len(resume_skills) * 40
            score += skill_match
        
        if job.get('experience') == '不限' or job.get('experience') == '应届':
            score += 10
        elif resume.personal_info.work_years:
            exp_text = job.get('experience', '')
            if str(resume.personal_info.work_years) in exp_text:
                score += 10
        
        if resume.personal_info.education:
            job_edu = job.get('education', '')
            if resume.personal_info.education in job_edu:
                score += 10
        
        score += job.get('hot_score', 0) * 0.1
        
        return min(round(score, 2), 100.0)

    def _get_match_level(self, score: float) -> str:
        if score >= 60:
            return "精准匹配"
        elif score >= 40:
            return "潜力匹配"
        elif score >= 20:
            return "跨界匹配"
        return "待提升"

    def _generate_reason(self, resume: ResumeParseResult, job: Dict, score: float) -> str:
        reasons = []
        
        resume_skills = [s.skill_name for s in resume.skills[:3]]
        for skill in resume_skills:
            if skill.lower() in (job.get('raw_jd', '') + job.get('title', '')).lower():
                reasons.append(f"具备{skill}技能")
        
        if job.get('experience') == '不限' or '应届' in job.get('experience', ''):
            reasons.append("符合经验要求")
        
        if resume.personal_info.education and resume.personal_info.education in job.get('education', ''):
            reasons.append("学历匹配")
        
        if not reasons:
            reasons.append("综合匹配度较高")
        
        return '，'.join(reasons)

    def get_job_by_id(self, job_id: int) -> Dict:
        for job in self.jobs:
            if job['id'] == job_id:
                return job
        return None