from schemas.resume import ResumeParseResult
from schemas.job import JobParseResult
from typing import List, Dict

class ResumeOptimizerService:
    def __init__(self):
        self.action_verbs = ['负责', '主导', '优化', '设计', '开发', '实现', '参与', '协调', '推进', '完成']
        self.achievement_prefixes = ['提升', '降低', '节省', '增加', '优化', '改进']

    def optimize(self, resume: ResumeParseResult, job: JobParseResult) -> dict:
        suggestions = []
        optimized_projects = []
        missing_skills = []

        required_skills = {s.skill_name for s in job.required_skills}
        resume_skills = {s.skill_name for s in resume.skills}
        missing_required = required_skills - resume_skills
        
        for skill in missing_required:
            missing_skills.append(skill)
            suggestions.append(f"建议补充技能：{skill}")

        summary = self._generate_summary(resume, job)
        
        for project in resume.projects:
            optimized_project = self._optimize_project(project, job)
            optimized_projects.append(optimized_project)
            if not project.achievements:
                suggestions.append(f"项目「{project.project_name}」建议补充量化成果")

        optimized_resume = self._generate_optimized_resume(resume, job, summary, optimized_projects)
        cover_letter = self._generate_cover_letter(resume, job)
        interview_questions = self._generate_interview_questions(job)

        return {
            'optimized_resume': optimized_resume,
            'cover_letter': cover_letter,
            'interview_questions': interview_questions,
            'suggestions': suggestions,
            'missing_skills': list(missing_required),
            'optimization_report': self._generate_report(resume, job, suggestions)
        }

    def _generate_summary(self, resume: ResumeParseResult, job: JobParseResult) -> str:
        key_skills = [s.skill_name for s in job.required_skills[:3]]
        experiences = [p.project_name for p in resume.projects[:2]]
        
        summary_parts = []
        if key_skills:
            summary_parts.append(f"熟练掌握{', '.join(key_skills)}等核心技能")
        if experiences:
            summary_parts.append(f"拥有{', '.join(experiences)}等项目经验")
        if resume.personal_info.education:
            summary_parts.append(f"{resume.personal_info.education}学历")
        
        return '，'.join(summary_parts) + "，具备良好的团队协作能力和学习能力。"

    def _optimize_project(self, project, job):
        optimized = project.dict()
        
        job_keywords = [s.skill_name for s in job.required_skills + job.optional_skills]
        
        if project.responsibilities:
            new_resp = project.responsibilities
            for verb in self.action_verbs:
                if verb not in new_resp[:4]:
                    new_resp = verb + new_resp
                    break
            for keyword in job_keywords:
                if keyword not in new_resp:
                    new_resp += f"，熟悉{keyword}"
            optimized['responsibilities'] = new_resp
        
        if not project.achievements:
            optimized['suggested_achievements'] = "建议补充量化成果，如：提升效率XX%，节省时间XX小时"
        
        return optimized

    def _generate_optimized_resume(self, resume: ResumeParseResult, job: JobParseResult, summary: str, optimized_projects: List) -> str:
        lines = []
        lines.append("【个人信息】")
        if resume.personal_info.name:
            lines.append(f"姓名：{resume.personal_info.name}")
        if resume.personal_info.education:
            lines.append(f"学历：{resume.personal_info.education}")
        if resume.personal_info.major:
            lines.append(f"专业：{resume.personal_info.major}")
        if resume.personal_info.phone:
            lines.append(f"电话：{resume.personal_info.phone}")
        if resume.personal_info.email:
            lines.append(f"邮箱：{resume.personal_info.email}")
        
        lines.append("\n【专业技能】")
        for skill in resume.skills:
            lines.append(f"- {skill.skill_name}（{skill.proficiency or '熟练'}）")
        
        lines.append("\n【项目经验】")
        for project in optimized_projects:
            lines.append(f"\n项目名称：{project['project_name']}")
            if project.get('start_date') and project.get('end_date'):
                lines.append(f"项目时间：{project['start_date']} - {project['end_date']}")
            if project.get('responsibilities'):
                lines.append(f"职责描述：{project['responsibilities']}")
            if project.get('tech_stack'):
                lines.append(f"技术栈：{', '.join(project['tech_stack'])}")
            if project.get('achievements'):
                lines.append(f"项目成果：{project['achievements']}")
        
        lines.append("\n【工作经验】")
        for exp in resume.work_experience:
            if exp.company:
                lines.append(f"\n公司名称：{exp.company}")
            if exp.position:
                lines.append(f"职位：{exp.position}")
            if exp.start_date and exp.end_date:
                lines.append(f"工作时间：{exp.start_date} - {exp.end_date}")
            if exp.responsibilities:
                lines.append(f"工作职责：{exp.responsibilities}")
        
        return '\n'.join(lines)

    def _generate_cover_letter(self, resume: ResumeParseResult, job: JobParseResult) -> str:
        lines = []
        lines.append("尊敬的招聘负责人：")
        lines.append(f"\n您好！我从招聘信息中了解到贵公司正在招聘{job.industry or ''}{job.job_type or ''}岗位，非常感兴趣。")
        lines.append(f"\n我是{resume.personal_info.education or ''}{resume.personal_info.major or ''}专业毕业生，")
        lines.append(f"具备{', '.join([s.skill_name for s in resume.skills[:3]])}等技能，")
        lines.append(f"拥有{len(resume.projects)}个相关项目经验。")
        lines.append("\n我对贵公司的业务方向非常认同，相信我的专业背景和工作态度能够胜任该岗位。")
        lines.append("期待有机会加入贵公司，为团队贡献价值。")
        lines.append("\n此致")
        lines.append("敬礼")
        return '\n'.join(lines)

    def _generate_interview_questions(self, job: JobParseResult) -> List[str]:
        questions = []
        
        if job.required_skills:
            for skill in job.required_skills[:2]:
                questions.append(f"请介绍一下您在{skill.skill_name}方面的经验？")
        
        questions.append("请描述一个您负责的最有挑战性的项目？")
        questions.append("您为什么选择我们公司？")
        questions.append("您的职业规划是什么？")
        questions.append("您的优点和缺点是什么？")
        
        return questions

    def _generate_report(self, resume: ResumeParseResult, job: JobParseResult, suggestions: List[str]) -> Dict:
        return {
            'total_optimizations': len(suggestions),
            'missing_skills_count': len([s for s in suggestions if '补充技能' in s]),
            'suggestions': suggestions,
            'original_projects_count': len(resume.projects),
            'optimized_projects_count': len([p for p in resume.projects if p.achievements])
        }