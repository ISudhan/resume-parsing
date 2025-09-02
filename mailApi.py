from fastapi import FastAPI, Request
import re
from rapidfuzz import process

  
  # List of common valid domains (expandable)
valid_domains = [
    "gmail.com", "yahoo.com", "yahoo.co.in",
    "hotmail.com", "outlook.com", "rediffmail.com",
    "icloud.com", "protonmail.com", "aol.com"
]

def clean_start(text):
    # remove only leading special chars, NOT digits unless they’re followed by - or :
    return re.sub(r'^[\W_]+', '', text)


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

    # --------- RULES ---------
    if "-" in local:
        # Case 1: Local contains "-"
        local = local.split("-", 1)[1]   # take right side only

    # Always fuzzy match domain
    best_match = process.extractOne(domain, valid_domains)
    if best_match and best_match[1] > 70:
        domain = best_match[0]

    return f"{local}@{domain}"



def extract_emails_from_text(text):
    # Roughly find all email-like candidates (with optional number- or number:)
    candidates = re.findall(r"(?:[a-zA-Z0-9]+[-:])?[a-zA-Z0-9._%+-]+(?:\s?@|\sat\s|\(at\))[a-zA-Z0-9.-]+", text)
    cleaned = []
    for c in candidates:
        fixed = clean_and_correct_email(c)
        if fixed and fixed not in cleaned:
            cleaned.append(fixed)
    return cleaned


# Example usage
resume_text = """ 
"""
emails = extract_emails_from_text(resume_text)

print("Extracted Emails:")
for e in emails:
    print(e)



app = FastAPI()

@app.post("/data/")
async def get_json(request: Request):
    # Accept either a single JSON or a list of JSONs
    data_list = await request.json()

    # If a single JSON is sent, wrap it in a list
    if isinstance(data_list, dict):
        data_list = [data_list]

    results = []
    for item in data_list:
        resume_text = item.get("resumeText", "")
        emails = extract_emails_from_text(resume_text)
        results+=emails

    return {"received_data": results}



