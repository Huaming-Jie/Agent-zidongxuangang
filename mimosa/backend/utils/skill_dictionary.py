import json
import os

SKILL_DICTIONARY = {
    "programming_languages": [
        "Python", "Java", "C++", "C", "C#", "JavaScript", "TypeScript",
        "Go", "Rust", "Swift", "Kotlin", "PHP", "Ruby", "Perl", "Shell",
        "SQL", "HTML", "CSS", "Vue", "React", "Angular", "Node.js"
    ],
    "frameworks": [
        "Spring Boot", "Django", "Flask", "FastAPI", "Express",
        "Vue.js", "React Native", "TensorFlow", "PyTorch", "Scikit-learn",
        "OpenCV", "Pandas", "NumPy", "Matplotlib", "Docker", "Kubernetes"
    ],
    "databases": [
        "MySQL", "PostgreSQL", "SQLite", "Oracle", "SQL Server",
        "MongoDB", "Redis", "Elasticsearch", "Cassandra", "HBase"
    ],
    "tools": [
        "Git", "SVN", "Jenkins", "GitLab CI", "Docker", "Kubernetes",
        "Jira", "Confluence", "VS Code", "IntelliJ", "Postman", "Swagger"
    ],
    "certifications": [
        "CET-4", "CET-6", "TOEFL", "IELTS", "PMP", "AWS", "Azure",
        "Oracle", "CCNA", "CFA", "CPA", "软考", "HCIA", "HCIP", "HCIE"
    ],
    "embedded": [
        "STM32", "Arduino", "Raspberry Pi", "ESP32", "FPGA",
        "RTOS", "Linux", "FreeRTOS", "CAN", "I2C", "SPI", "UART"
    ],
    "soft_skills": [
        "沟通能力", "团队协作", "抗压能力", "学习能力", "创新能力",
        "项目管理", "责任心", "执行力", "逻辑思维", "英语能力"
    ]
}

def load_skill_dictionary(file_path=None):
    if file_path and os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return SKILL_DICTIONARY

def find_matching_skills(text, threshold=0.8):
    skills_found = []
    text_lower = text.lower()
    
    for category, skills in SKILL_DICTIONARY.items():
        for skill in skills:
            if skill.lower() in text_lower:
                skills_found.append({
                    "skill_name": skill,
                    "category": category,
                    "proficiency": "熟练"
                })
    return skills_found

def get_skill_category(skill_name):
    for category, skills in SKILL_DICTIONARY.items():
        if skill_name in skills:
            return category
    return "other"