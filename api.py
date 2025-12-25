from fastapi import FastAPI, Request
import re
from rapidfuzz import process
import pandas as pd

app = FastAPI()

# List of common valid domains (expandable)
valid_domains = [
    "gmail.com", "yahoo.com", "yahoo.co.in",
    "hotmail.com", "outlook.com", "rediffmail.com",
    "icloud.com", "protonmail.com", "aol.com"
]

def clean_and_correct_email(raw_email):
    if not raw_email:
        return None

    # Normalize
    email = raw_email.lower()
    email = email.replace(" ", "").replace("\n", "").replace("\r", "")
    email = email.replace("..", ".").replace(",,,", ",").replace(",,", ",")

    # Replace text patterns
    email = email.replace(" at ", "@").replace(" dot ", ".")
    email = email.replace("(at)", "@").replace("(dot)", ".")
    email = email.replace("[at]", "@").replace("[dot]", ".")
    email = email.replace("at", "@").replace("dot", ".")

    # Remove unwanted chars except @, ., -, _
    email = re.sub(r'[^a-z0-9@._-]', '', email)

    # Fix multiple @
    if email.count("@") > 1:
        parts = email.split("@")
        email = parts[0] + "@" + parts[-1]

    # Split into local + domain
    if "@" not in email:
        return None
    local, _, domain = email.partition("@")
    if not local or not domain:
        return None

    # Reject if domain does not contain a dot
    if "." not in domain:
        return None

    # Auto-correct domain using fuzzy match
    best_match = process.extractOne(domain, valid_domains)
    if best_match and best_match[1] > 70:
        domain = best_match[0]

    return f"{local}@{domain}"


def extract_emails_from_text(text):
    # Roughly find all email-like candidates
    candidates = re.findall(r"[a-zA-Z0-9._%+-]+(?:\s?@|\sat\s|\(at\))[a-zA-Z0-9.-]+", text)
    cleaned = []
    for c in candidates:
        fixed = clean_and_correct_email(c)
        if fixed and fixed not in cleaned:
            cleaned.append(fixed)
    return cleaned


def skill_extract(resume_text):
    import pandas as pd

    # Read the unique skills file
    skills_df = pd.read_excel("skills.xlsx")

    # Ensure lowercase and drop NaN
    skills = skills_df["skill"].dropna().str.lower().tolist()

    # Normalize input text
    input_text_lower = resume_text.lower()

    # Extract matching skills
    skills_list = [skill for skill in skills if skill in input_text_lower]

    return skills_list





@app.post("/data/")
async def get_json(request: Request):
    data_list = await request.json()

    # If a single JSON is sent, wrap it in a list
    if isinstance(data_list, dict):
        data_list = [data_list]

    results = []
    for item in data_list:
        resume_text = item.get("resumeText", "")
        skills = skill_extract(resume_text)
        emails = extract_emails_from_text(resume_text)
        results.append({
            "emails": emails,
            "skills": skills
        })

    return {"parsed_data": results}
