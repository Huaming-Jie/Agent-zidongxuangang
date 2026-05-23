from typing import List
import re
from schemas.job import JobParseResult, JobSkillItem
from utils.nlp_utils import extract_education, extract_work_years, extract_keywords, clean_text
from utils.skill_dictionary import find_matching_skills, SKILL_DICTIONARY

class JDParserService:
    def __init__(self):
        self.required_indicators = ['熟练', '精通', '掌握', '必须', '必备', '扎实', '深入']
        self.optional_indicators = ['了解', '熟悉', '优先', '良好', '一定']
        self.soft_skill_keywords = ['沟通', '团队', '协作', '抗压', '学习', '责任心', '执行力']
        self.industry_keywords = {
            '互联网': ['互联网', '电商', '软件', '科技', '网络', '平台'],
            '智能制造': ['制造', '工业', '智能', '自动化', '设备', '机械'],
            '人工智能': ['AI', '人工智能', '机器学习', '深度学习', '算法'],
            '金融': ['金融', '银行', '证券', '投资', '基金']
        }
        self.job_type_keywords = {
            '开发': ['开发', '工程师', '编程', '代码', '后端', '前端'],
            '测试': ['测试', 'QA', '自动化', '质量'],
            '运维': ['运维', 'DevOps', '部署', '服务器'],
            '数据分析': ['数据', '分析', 'BI', '统计'],
            '产品': ['产品', 'PM', '设计', '需求']
        }

    def parse(self, raw_jd: str) -> JobParseResult:
        cleaned_jd = clean_text(raw_jd)
        
        education = extract_education(cleaned_jd)
        experience_required = self._extract_experience(cleaned_jd)
        major = self._extract_major(cleaned_jd)
        certificates = self._extract_certificates(cleaned_jd)
        skills = self._extract_skills(cleaned_jd)
        soft_skills = self._extract_soft_skills(cleaned_jd)
        industry = self._classify_industry(cleaned_jd)
        job_type = self._classify_job_type(cleaned_jd)
        salary_range = self._extract_salary(cleaned_jd)

        required_skills = [s for s in skills if s.is_required]
        optional_skills = [s for s in skills if not s.is_required]

        return JobParseResult(
            education=education,
            experience_required=experience_required,
            major=major,
            required_certificates=certificates,
            required_skills=required_skills,
            optional_skills=optional_skills,
            soft_skills=soft_skills,
            industry=industry,
            job_type=job_type,
            salary_range=salary_range
        )

    def _extract_experience(self, text: str) -> str:
        years = extract_work_years(text)
        if years:
            return f"{years}年"
        patterns = [r'(不限|应届|毕业生|entry|junior)', r'(\d+)-(\d+)年']
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    def _extract_major(self, text: str) -> str:
        major_keywords = ['计算机', '电子', '通信', '自动化', '软件', '数据', '信息']
        for keyword in major_keywords:
            if keyword in text:
                return keyword + '相关'
        return None

    def _extract_certificates(self, text: str) -> List[str]:
        certs = []
        for cert in SKILL_DICTIONARY.get('certifications', []):
            if cert in text:
                certs.append(cert)
        return certs

    def _extract_skills(self, text: str) -> List[JobSkillItem]:
        all_skills = find_matching_skills(text)
        job_skills = []
        
        for skill in all_skills:
            skill_name = skill['skill_name']
            is_required = any(indicator in text for indicator in self.required_indicators if indicator + skill_name in text or skill_name + indicator in text)
            importance = 1.0 if is_required else 0.7
            
            job_skills.append(JobSkillItem(
                skill_name=skill_name,
                is_required=is_required,
                importance=importance
            ))
        return job_skills

    def _extract_soft_skills(self, text: str) -> List[str]:
        found = []
        for keyword in self.soft_skill_keywords:
            if keyword in text:
                found.append(keyword)
        return found

    def _classify_industry(self, text: str) -> str:
        for industry, keywords in self.industry_keywords.items():
            if any(keyword in text for keyword in keywords):
                return industry
        return None

    def _classify_job_type(self, text: str) -> str:
        for job_type, keywords in self.job_type_keywords.items():
            if any(keyword in text for keyword in keywords):
                return job_type
        return None

    def _extract_salary(self, text: str) -> str:
        patterns = [r'(\d+)K?-(\d+)K?', r'(\d+)k?-(\d+)k?', r'薪资[:：]\s*([\u4e00-\u9fa50-9]+)']
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}-{match.group(2)}K"
        return None