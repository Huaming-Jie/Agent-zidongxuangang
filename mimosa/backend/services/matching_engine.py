from schemas.resume import ResumeParseResult
from schemas.job import JobParseResult, MatchScoreDetail
from utils.nlp_utils import calculate_keyword_density

class MatchingEngine:
    def __init__(self):
        self.weights = {
            'skill': 0.4,
            'project': 0.25,
            'education': 0.15,
            'industry': 0.10,
            'keyword': 0.10
        }

    def calculate_match(self, resume: ResumeParseResult, job: JobParseResult) -> dict:
        scores = MatchScoreDetail()
        
        scores.skill_score = self._calculate_skill_score(resume, job)
        scores.project_score = self._calculate_project_score(resume, job)
        scores.education_score = self._calculate_education_score(resume, job)
        scores.industry_score = self._calculate_industry_score(resume, job)
        scores.keyword_score = self._calculate_keyword_score(resume, job)

        total_score = (
            scores.skill_score * self.weights['skill'] +
            scores.project_score * self.weights['project'] +
            scores.education_score * self.weights['education'] +
            scores.industry_score * self.weights['industry'] +
            scores.keyword_score * self.weights['keyword']
        )

        match_details = self._generate_match_details(resume, job, scores)

        return {
            'total_score': round(total_score * 100, 2),
            'score_detail': scores,
            'match_details': match_details
        }

    def _calculate_skill_score(self, resume: ResumeParseResult, job: JobParseResult) -> float:
        resume_skills = {s.skill_name.lower() for s in resume.skills}
        required_skills = {s.skill_name.lower() for s in job.required_skills}
        optional_skills = {s.skill_name.lower() for s in job.optional_skills}

        if not required_skills:
            return 0.5

        required_match = len(resume_skills & required_skills) / len(required_skills)
        optional_match = len(resume_skills & optional_skills) / max(len(optional_skills), 1)

        return (required_match * 0.7 + optional_match * 0.3)

    def _calculate_project_score(self, resume: ResumeParseResult, job: JobParseResult) -> float:
        if not resume.projects:
            return 0.3

        job_tech_stack = {s.skill_name.lower() for s in job.required_skills + job.optional_skills}
        project_score = 0.0
        count = 0

        for project in resume.projects:
            project_tech = set()
            if project.tech_stack:
                project_tech = {t.lower() for t in project.tech_stack}
            else:
                project_text = f"{project.project_name} {project.responsibilities} {project.achievements}"
                project_tech = {word.lower() for word in project_text.split() if word.lower() in job_tech_stack}
            
            if project_tech:
                overlap = len(project_tech & job_tech_stack) / max(len(job_tech_stack), 1)
                project_score += overlap
                count += 1

        return project_score / max(count, 1) if count > 0 else 0.3

    def _calculate_education_score(self, resume: ResumeParseResult, job: JobParseResult) -> float:
        education_levels = {'高中': 1, '中专': 1, '大专': 2, '本科': 3, '学士': 3, '硕士': 4, '研究生': 4, '博士': 5}
        
        resume_edu = education_levels.get(resume.personal_info.education, 2)
        job_edu = education_levels.get(job.education, 3)

        if resume_edu >= job_edu:
            return 1.0
        elif resume_edu == job_edu - 1:
            return 0.5
        else:
            return 0.2

    def _calculate_industry_score(self, resume: ResumeParseResult, job: JobParseResult) -> float:
        if not job.industry:
            return 0.8

        resume_industry = self._infer_resume_industry(resume)
        if resume_industry == job.industry:
            return 1.0
        return 0.5

    def _infer_resume_industry(self, resume: ResumeParseResult) -> str:
        industry_keywords = {
            '互联网': ['Python', 'Java', '前端', '后端', '数据', '算法'],
            '智能制造': ['STM32', '嵌入式', '自动化', '工业', '设备'],
            '人工智能': ['AI', '机器学习', '深度学习', 'TensorFlow', 'PyTorch']
        }
        
        resume_text = ' '.join([s.skill_name for s in resume.skills] + 
                               [p.project_name for p in resume.projects])
        
        for industry, keywords in industry_keywords.items():
            if any(keyword in resume_text for keyword in keywords):
                return industry
        return None

    def _calculate_keyword_score(self, resume: ResumeParseResult, job: JobParseResult) -> float:
        all_job_keywords = [s.skill_name for s in job.required_skills + job.optional_skills]
        resume_text = ' '.join([s.skill_name for s in resume.skills] + 
                               [p.project_name for p in resume.projects] +
                               [p.responsibilities for p in resume.projects if p.responsibilities] +
                               [we.responsibilities for we in resume.work_experience if we.responsibilities])
        
        if not all_job_keywords or not resume_text:
            return 0.5

        density = calculate_keyword_density(resume_text, all_job_keywords)
        return min(density * 10, 1.0)

    def _generate_match_details(self, resume: ResumeParseResult, job: JobParseResult, scores: MatchScoreDetail) -> dict:
        resume_skills = {s.skill_name for s in resume.skills}
        required_skills = {s.skill_name for s in job.required_skills}
        optional_skills = {s.skill_name for s in job.optional_skills}

        missing_required = required_skills - resume_skills
        matched_optional = optional_skills & resume_skills

        return {
            'missing_required_skills': list(missing_required),
            'matched_optional_skills': list(matched_optional),
            'education_match': resume.personal_info.education == job.education,
            'industry_match': self._infer_resume_industry(resume) == job.industry,
            'score_breakdown': {
                '技能匹配': f"{scores.skill_score * 100:.1f}%",
                '项目经验': f"{scores.project_score * 100:.1f}%",
                '学历年限': f"{scores.education_score * 100:.1f}%",
                '行业匹配': f"{scores.industry_score * 100:.1f}%",
                '关键词密度': f"{scores.keyword_score * 100:.1f}%"
            }
        }