from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Union
import re
from rapidfuzz import process
import spacy

# ---------------- Load spaCy ----------------
nlp = spacy.load("en_core_web_sm")

# ---------------- Email Extraction ----------------
valid_domains = [
    "gmail.com", "yahoo.com", "yahoo.co.in",
    "hotmail.com", "outlook.com", "rediffmail.com",
    "icloud.com", "protonmail.com", "aol.com"
]

def clean_and_correct_email(raw_email):
    if not raw_email:
        return None
    email = raw_email.lower()
    email = email.replace(" ", "").replace("\n", "").replace("\r", "")
    email = email.replace("..", ".").replace(",,,", ",").replace(",,", ",")
    email = email.replace(" at ", "@").replace(" dot ", ".")
    email = email.replace("(at)", "@").replace("(dot)", ".")
    email = email.replace("[at]", "@").replace("[dot]", ".")
    email = email.replace("at", "@").replace("dot", ".")
    email = re.sub(r'[^a-z0-9@._-]', '', email)

    if email.count("@") > 1:
        parts = email.split("@")
        email = parts[0] + "@" + parts[-1]

    if "@" not in email:
        return None
    local, _, domain = email.partition("@")
    if not local or not domain:
        return None
    if "." not in domain:
        return None

    best_match = process.extractOne(domain, valid_domains)
    if best_match and best_match[1] > 70:
        domain = best_match[0]
    return f"{local}@{domain}"

def extract_emails_from_text(text):
    candidates = re.findall(r"[a-zA-Z0-9._%+-]+(?:\s?@|\sat\s|\(at\))[a-zA-Z0-9.-]+", text)
    cleaned = []
    for c in candidates:
        fixed = clean_and_correct_email(c)
        if fixed and fixed not in cleaned:
            cleaned.append(fixed)
    return cleaned

# ---------------- Name Extraction ----------------
LINE_BLOCKLIST = {
    "resume", "curriculum vitae", "cv", "objective", "profile", "summary",
    "job objective", "education", "skills", "experience", "declaration",
    "personal details", "contact", "address", "about me"
}
RELATIVE_WORDS = {"father", "mother", "guardian", "parent", "husband", "wife", "spouse", "son", "daughter"}
ORG_WORDS = {
    "pvt", "ltd", "private", "limited", "inc", "llc", "solutions", "consulting",
    "technologies", "technology", "systems", "info", "services", "institute",
    "university", "college", "school", "department"
}
DEGREE_WORDS = {
    "btech", "b.tech", "b tech", "mtech", "m.tech", "m tech",
    "bsc", "b.sc", "m.sc", "msc", "be", "b.e", "me", "m.e",
    "mba", "ms", "phd", "mca", "bca", "ba", "ma",
    "engineering", "engineer", "technology", "tech",
    "science", "sciences", "commerce", "arts", "management",
    "computer", "electronics", "communication", "electrical", "mechanical", "civil", "it", "ece", "cse"
}

def _norm_token(tok: str) -> str:
    return re.sub(r"[^a-z]", "", tok.lower())

def _left_chunk(line: str) -> str:
    parts = re.split(r"[–—\-|:/••]+", line)
    return parts[0].strip() if parts else line.strip()

def _bad_line(line: str) -> bool:
    l = line.lower()
    if any(p in l for p in LINE_BLOCKLIST):
        return True
    if any(r in l for r in RELATIVE_WORDS):
        return True
    if "@" in l or "www" in l:
        return True
    if sum(ch.isdigit() for ch in l) >= 2:
        return True
    return False

def _is_name_token(tok: str) -> bool:
    if re.fullmatch(r"[A-Z][a-z]+", tok):
        return True
    if re.fullmatch(r"[A-Z]\.?", tok):
        return True
    return False

def _contains_bad_words(tokens) -> bool:
    for t in tokens:
        nt = _norm_token(t)
        if nt in DEGREE_WORDS or nt in ORG_WORDS:
            return True
    return False

def _is_valid_name_line(line: str) -> bool:
    if _bad_line(line):
        return False
    chunk = _left_chunk(line)
    chunk = re.sub(r"\s*\.\s*", " ", chunk).strip()
    if not (2 <= len(chunk) <= 40):
        return False
    tokens = chunk.split()
    if not (2 <= len(tokens) <= 4):
        return False
    if _contains_bad_words(tokens):
        return False
    if not all(_is_name_token(t) for t in tokens):
        return False
    if max(len(t.replace(".", "")) for t in tokens) < 3:
        return False
    return True

def extract_name_from_resume(resume_text: str) -> str:
    lines = [ln.strip() for ln in resume_text.splitlines() if ln.strip()][:10]
    if not lines:
        return ""
    for ln in lines:
        if _bad_line(ln):
            continue
        m = re.search(r"\bname\s*[:\-]\s*(.+)$", ln, flags=re.IGNORECASE)
        if m:
            cand = _left_chunk(m.group(1).strip())
            cand = re.sub(r"\s*\.\s*", " ", cand).strip()
            if _is_valid_name_line(cand):
                return cand
    for ln in lines:
        if _is_valid_name_line(ln):
            return _left_chunk(re.sub(r"\s*\.\s*", " ", ln).strip())
    for ln in lines:
        if _bad_line(ln):
            continue
        doc = nlp(ln)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                cand = _left_chunk(re.sub(r"\s*\.\s*", " ", ent.text.strip()))
                if _is_valid_name_line(cand):
                    return cand
    return ""

# ---------------- FastAPI ----------------
app = FastAPI()

# ✅ Input schema
class ResumeItem(BaseModel):
    resumeText: str

@app.post("/data/")
async def get_json(data_list: Union[List[ResumeItem], ResumeItem]):
    # Normalize to list
    if isinstance(data_list, ResumeItem):
        data_list = [data_list]

    results = []
    for item in data_list:
        resume_text = item.resumeText
        emails = extract_emails_from_text(resume_text)
        name = extract_name_from_resume(resume_text)
        results.append({"name": name, "emails": emails})

    return {"results": results}
