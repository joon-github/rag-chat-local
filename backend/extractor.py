from pathlib import Path
import fitz  # PyMuPDF
import docx

def extract_text_from_file(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    
    try:
        if ext == ".pdf":
            return extract_from_pdf(file_path)
        elif ext == ".txt":
            return extract_from_txt(file_path)
        elif ext == ".docx":
            return extract_from_docx(file_path)
        else:
            return ""
    except Exception as e:
        print(f"❌ 텍스트 추출 실패: {file_path}, 에러: {e}")
        return ""

def extract_from_pdf(path):
    text = ""
    doc = fitz.open(path)
    for page in doc:
        text += page.get_text()
    return text

def extract_from_txt(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def extract_from_docx(path):
    doc = docx.Document(path)
    return "\n".join([p.text for p in doc.paragraphs])