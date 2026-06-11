import os
import re

# Optional heavy dependencies — import if available, otherwise fall back.
try:
    import PyPDF2
    _pdf_available = True
except Exception:
    _pdf_available = False

try:
    from docx import Document
    _docx_available = True
except Exception:
    _docx_available = False


def extract_pdf_text(pdf_path):
    if not _pdf_available:
        raise ImportError("PyPDF2 is required to read PDF resumes. Install with 'pip install PyPDF2' or provide a .txt resume.")

    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text


def extract_docx_text(docx_path):
    if not _docx_available:
        raise ImportError("python-docx is required to load .docx resume files")

    document = Document(docx_path)
    lines = [para.text for para in document.paragraphs if para.text]
    return "\n".join(lines)


def extract_resume_text(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Resume file not found: {file_path}")

    extension = os.path.splitext(file_path)[1].lower()
    if extension == ".pdf":
        text = extract_pdf_text(file_path)
    elif extension == ".docx":
        text = extract_docx_text(file_path)
    elif extension == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        raise ValueError("Unsupported resume format. Use PDF, DOCX, or plain TXT files.")

    return text.strip() or ""


def extract_skills_from_resume(resume_text, max_skills=10):
    """Very small heuristic extractor: looks for a 'Skills' section or
    extracts frequent capitalized/technical tokens as candidate skills.

    This is intentionally lightweight (no external NLP deps).
    """
    if not resume_text:
        return []

    text = resume_text

    # Try to find an explicit Skills section
    lowered = text.lower()
    markers = ["skills", "technical skills", "skill set", "technologies"]
    for m in markers:
        idx = lowered.find(m)
        if idx != -1:
            # take next ~300 chars after marker and split by common separators
            snippet = text[idx:idx+400]
            parts = [p.strip() for p in re.split(r'[\n,;•\-:]', snippet) if p.strip()]
            # return the first reasonable-looking tokens
            candidates = []
            for part in parts[1:]:
                # ignore very long lines
                if len(part) > 120:
                    continue
                # break by slashes or pipes
                for token in re.split(r"[\/|]", part):
                    t = token.strip()
                    if 1 < len(t) <= 60:
                        candidates.append(t)
                if len(candidates) >= max_skills:
                    break
            return candidates[:max_skills]

    # Fallback: pick frequent capitalized words and common tech tokens
    words = re.findall(r"[A-Za-z0-9+#\.\-]{2,}", text)
    freq = {}
    stop = set(["the","and","with","for","in","on","to","of","a","an","is","are","by","as","that"]) 
    for w in words:
        lw = w.lower()
        if lw in stop:
            continue
        # prefer tokens that look like technology identifiers (contain +, #, ., or capital letters)
        score = 0
        if re.search(r"[A-Z]", w):
            score += 1
        if re.search(r"[+#]", w):
            score += 1
        freq[w] = freq.get(w, 0) + 1 + score

    sorted_items = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
    skills = [k for k, _ in sorted_items if len(k) > 1][:max_skills]
    return skills
   