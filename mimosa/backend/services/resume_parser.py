from typing import List
from schemas.resume import ResumeParseResult, PersonalInfo, SkillItem, ProjectItem, WorkExperience
from utils.nlp_utils import extract_education, extract_work_years, extract_projects, extract_achievements, clean_text
from utils.skill_dictionary import find_matching_skills
import re

class ResumeParserService:
    def __init__(self):
        self.education_keywords = ['博士', '硕士', '研究生', '学士', '本科', '大专', '高职', '中专', '高中']
        self.city_keywords = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '西安', '南京', '苏州', '重庆']
        self.email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        self.phone_pattern = r'1[3-9]\d{9}'

    def parse(self, raw_content: str) -> ResumeParseResult:
        cleaned_content = clean_text(raw_content)
        
        personal_info = self._extract_personal_info(cleaned_content)
        skills = self._extract_skills(cleaned_content)
        projects = self._extract_projects(cleaned_content)
        work_experience = self._extract_work_experience(cleaned_content)

        return ResumeParseResult(
            personal_info=personal_info,
            skills=skills,
            projects=projects,
            work_experience=work_experience,
            raw_content=raw_content
        )

    def _extract_personal_info(self, text: str) -> PersonalInfo:
        education = extract_education(text)
        work_years = extract_work_years(text)
        
        email_match = re.search(self.email_pattern, text)
        phone_match = re.search(self.phone_pattern, text)
        
        target_city = None
        for city in self.city_keywords:
            if city in text:
                target_city = city
                break
        
        school = self._extract_school(text)
        major = self._extract_major(text)
        name = self._extract_name(text)

        return PersonalInfo(
            name=name,
            education=education,
            major=major,
            school=school,
            work_years=work_years,
            target_city=target_city,
            email=email_match.group() if email_match else None,
            phone=phone_match.group() if phone_match else None
        )

    def _extract_name(self, text: str) -> str:
        name_patterns = [
            r'(姓名[:：]\s*([\u4e00-\u9fa5]{2,4}))',
            r'^([\u4e00-\u9fa5]{2,4})\s',
            r'([\u4e00-\u9fa5]{2,4})\s*(求职|简历)'
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(2) if len(match.groups()) == 2 else match.group(1)
        return None

    def _extract_school(self, text: str) -> str:
        school_patterns = [
            r'(北京大学|清华大学|复旦大学|上海交通大学|浙江大学|南京大学|中国人民大学|武汉大学|华中科技大学)',
            r'([\u4e00-\u9fa5]+大学|[\u4e00-\u9fa5]+学院)'
        ]
        for pattern in school_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    def _extract_major(self, text: str) -> str:
        major_patterns = [
            r'(计算机科学|软件工程|电子信息|通信工程|自动化|数据科学|人工智能|机械工程)',
            r'(专业[:：]\s*([\u4e00-\u9fa5]+))'
        ]
        for pattern in major_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1) if len(match.groups()) == 1 else match.group(2)
        return None

    def _extract_skills(self, text: str) -> List[SkillItem]:
        skills_found = find_matching_skills(text)
        return [SkillItem(**skill) for skill in skills_found]

    def _extract_projects(self, text: str) -> List[ProjectItem]:
        project_names = extract_projects(text)
        achievements = extract_achievements(text)
        
        projects = []
        for name in project_names[:5]:
            projects.append(ProjectItem(
                project_name=name,
                achievements='; '.join(achievements) if achievements else None
            ))
        return projects

    def _extract_work_experience(self, text: str) -> List[WorkExperience]:
        experience_patterns = [
            r'([\u4e00-\u9fa5a-zA-Z0-9_]+)\s*(公司|集团|科技|有限|股份)\s*[（(]?[\u4e00-\u9fa5]*[）)]?',
            r'(任职|担任|负责)\s*([\u4e00-\u9fa5a-zA-Z]+(工程师|经理|专员|助理))'
        ]
        
        companies = []
        positions = []
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if '公司' in match[0] or '集团' in match[0]:
                    companies.append(match[0])
                elif '工程师' in match[-1] or '经理' in match[-1]:
                    positions.append(match[-1])
        
        return [WorkExperience(company=companies[0] if companies else None, position=positions[0] if positions else None)]