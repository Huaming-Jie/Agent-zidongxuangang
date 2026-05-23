import re
import string

_word_tokenize = None
_stopwords_set = None

try:
    import nltk
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)

    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)

    from nltk.tokenize import word_tokenize as _nltk_word_tokenize
    from nltk.corpus import stopwords as _nltk_stopwords
    _word_tokenize = _nltk_word_tokenize
    _stopwords_set = set(_nltk_stopwords.words('chinese')) if 'chinese' in _nltk_stopwords.fileids() else set()
except Exception as e:
    pass

def extract_education(text):
    education_patterns = [
        r'(博士|博士后)',
        r'(硕士|研究生)',
        r'(学士|本科)',
        r'(大专|高职)',
        r'(中专|高中)'
    ]
    for pattern in education_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None

def extract_work_years(text):
    patterns = [
        r'(\d+)年以上?经验',
        r'(\d+)年工作经验',
        r'(\d+)年以上工作',
        r'(\d+)-(\d+)年经验'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            if len(match.groups()) == 2:
                return int(match.group(1))
            return int(match.group(1))
    return None

def extract_achievements(text):
    achievement_patterns = [
        r'(提升|提高|增加|增长|节省|减少|缩短|优化)(\d+[\.]?\d*)(%|倍|万元|万|元|小时|天|分钟)',
        r'(\d+[\.]?\d*)(%|倍|万元|万|元|小时|天|分钟)(提升|提高|增加|增长|节省|减少|缩短|优化)'
    ]
    achievements = []
    for pattern in achievement_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            achievements.append(''.join(match))
    return achievements

def extract_projects(text):
    project_patterns = [
        r'(项目|课题|研发|开发|设计)\s*[:：]\s*([\u4e00-\u9fa5a-zA-Z0-9_]+)',
        r'([\u4e00-\u9fa5a-zA-Z0-9_]+)\s*(项目|系统|平台|模块)'
    ]
    projects = []
    for pattern in project_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            project_name = match[-1] if match[0] in ['项目', '课题', '研发', '开发', '设计'] else match[0]
            projects.append(project_name)
    return list(set(projects))

def extract_keywords(text, keywords_list):
    found = []
    text_lower = text.lower()
    for keyword in keywords_list:
        if keyword.lower() in text_lower:
            found.append(keyword)
    return found

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s，。！？、；：（）【】《》]', '', text)
    return text.strip()

def tokenize_chinese(text):
    if _word_tokenize is None:
        tokens = list(text)
    else:
        tokens = _word_tokenize(text)
    stop_words = _stopwords_set if _stopwords_set else set()
    tokens = [t for t in tokens if t not in stop_words and t not in string.punctuation and t.strip()]
    return tokens

def calculate_keyword_density(text, keywords):
    if not text or not keywords:
        return 0.0
    text_lower = text.lower()
    total_length = len(text_lower)
    if total_length == 0:
        return 0.0
    keyword_count = sum(text_lower.count(k.lower()) for k in keywords)
    return (keyword_count * len(max(keywords, key=len))) / total_length