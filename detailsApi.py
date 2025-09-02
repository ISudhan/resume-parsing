from fastapi import FastAPI, Request
import pandas as pd
from pydantic import BaseModel
import re

app = FastAPI()
VALID_CODES = ['234', '971', '968', '965', '977', '852', '963', '356',
               '212', '81', '91', '44', '49', '61', '66', '34', '60',
               '62', '86', '48', '57', '7', '9', '1']


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




def extract_clean_phone_numbers(text, default_code="+91"):
    result = []
    seen = set()

    pattern_plus = r'(\+\d{1,3})[\s\-()]*([\d\s\-()]{6,14})'
    matches_plus = re.findall(pattern_plus, text)
    for code, number in matches_plus:
        clean_number = re.sub(r'\D', '', number)
        code_digits = code.replace("+", "")
        if code_digits in VALID_CODES and len(clean_number) == 10:
            key = f"{code}{clean_number}"
            if key not in seen:
                seen.add(key)
                result.append({"country_code": code, "number": clean_number})

    pattern_plain = r'\b\d{10,12}\b'
    matches_plain = re.findall(pattern_plain, text)
    for num in matches_plain:
        clean_number = re.sub(r'\D', '', num)

        if len(clean_number) == 10:
            code = default_code
            local = clean_number
        elif len(clean_number) in [11, 12]:
            for code_len in range(1, 4):  # try 1–3 digit codes
                country_part = clean_number[:code_len]
                local = clean_number[-10:]
                if country_part in VALID_CODES and len(local) == 10:
                    code = f"+{country_part}"
                    break
            else:
                continue
        else:
            continue

        key = f"{code}{local}"
        if key not in seen:
            seen.add(key)
            result.append({"country_code": code, "number": local})

    return result

def skill_extract(resume_text):
    # Read the unique skills file
    skills_df = pd.read_excel("skills.xlsx")

    # Ensure lowercase and drop NaN
    skills = skills_df["skill"].dropna().str.lower().tolist()

    # Normalize input text
    input_text_lower = resume_text.lower()

    # Extract matching skills
    skills_list = [skill for skill in skills if skill in input_text_lower]

    return skills_list





@app.post("/details/")
async def get_json(request: Request):
    data_list = await request.json()

    # If a single JSON is sent, wrap it in a list
    if isinstance(data_list, dict):
        data_list = [data_list]

    results = dict()
    for item in data_list:
        resume_text = item.get("resumeText", "")
        name = extract_name_from_resume(resume_text)
        skills = skill_extract(resume_text)
        numbers = extract_clean_phone_numbers(resume_text)
        results["name"] = name
        results["skills"] = skills
        results["numbers"] = numbers

    return results
