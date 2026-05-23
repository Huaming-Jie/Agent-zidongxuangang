import os

_pdf_available = False
_docx_available = False

try:
    import pdfplumber
    _pdf_available = True
except ImportError:
    pass

try:
    from docx import Document
    _docx_available = True
except ImportError:
    pass

def parse_pdf(file_path):
    if not _pdf_available:
        return _fallback_text(file_path)
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception:
        return _fallback_text(file_path)

def parse_docx(file_path):
    if not _docx_available:
        return _fallback_text(file_path)
    try:
        text = ""
        doc = Document(file_path)
        for para in doc.paragraphs:
            if para.text:
                text += para.text + "\n"
        return text.strip()
    except Exception:
        return _fallback_text(file_path)

def parse_txt(file_path):
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.read().strip()
        except (UnicodeDecodeError, UnicodeError):
            continue
    return ""

def _fallback_text(file_path):
    if file_path.lower().endswith('.txt'):
        return parse_txt(file_path)
    return ""

def parse_file(file_path):
    if not os.path.exists(file_path):
        return ""

    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return parse_pdf(file_path)
    elif ext in ('.docx', '.doc'):
        return parse_docx(file_path)
    elif ext == '.txt':
        return parse_txt(file_path)
    else:
        return _fallback_text(file_path)
