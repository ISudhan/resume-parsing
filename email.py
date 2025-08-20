# Ensure rapidfuzz is installed before running this script.
# You can install it via: pip install rapidfuzz
import re
from rapidfuzz import process

# List of valid domains we support
valid_domains = [
    "gmail.com", "yahoo.com", "yahoo.co.in",
    "hotmail.com", "outlook.com", "rediffmail.com",
    "icloud.com", "protonmail.com", "aol.com"
]

def clean_and_correct_email(raw_email):
    # 1. Remove unwanted chars and normalize
    email = raw_email.lower().strip()
    email = email.replace(" ", "").replace("..", ".").replace(",,,", ",").replace(",,", ",")
    email = re.sub(r'[^a-z0-9@._-]', '', email)

    # 2. Fix "at" → "@" and "dot" → "."
    email = email.replace(" at ", "@").replace(" dot ", ".")
    email = email.replace("(at)", "@").replace("(dot)", ".")
    email = email.replace("at", "@").replace("dot", ".")

    # 3. Extract parts
    if "@" not in email:
        return None  # invalid if no @ at all
    local, _, domain = email.partition("@")

    # 4. Auto-correct domain using fuzzy matching
    best_match = process.extractOne(domain, valid_domains)
    if best_match and best_match[1] > 70:  # similarity > 70%
        domain = best_match[0]

    # 5. Return clean email
    return f"{local}@{domain}"


# 🔹 Test cases
emails = [
    "uj.m  @ gml . com",
    "keerthi_suresh 123 @yaho .co . in",
    "vijay.. kumar@@hotma..com",
    "sudha r2001 @ outlok. com",
    "pravinmec@ gmail. com,",
    "deepa123 at rediffmail dot com",
    "arun---raj1999@@@gail.con",   # typo domain
    "xyz_user@hotmial.cm",          # typo domain
    "keerthi@oulok.co",            # typo domain
    "deepa@@yahho.com"              # typo domain
]

for e in emails:
    print(clean_and_correct_email(e))
