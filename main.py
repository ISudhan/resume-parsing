import re
from fastapi import FastAPI
from pydantic import BaseModel

# Allowed country codes
VALID_CODES = ['234', '971', '968', '965', '977', '852', '963', '356',
               '212', '81', '91', '44', '49', '61', '66', '34', '60',
               '62', '86', '48', '57', '7', '9', '1']

# ===========================
# Extraction Function
# ===========================
def extract_clean_phone_numbers(text, default_code="+91"):
    """
    Extracts and cleans phone numbers from text with these rules:
    1. Detects numbers with +country_code
    2. Detects plain 11/12 digit numbers like 911234567890 -> split country + last 10 digits
    3. Detects numbers without + but starting with valid country codes
    4. Only accepts country codes from VALID_CODES list
    """
    result = []
    seen = set()

    # 1️⃣ Detect numbers with +country_code
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

    # 2️⃣ Detect plain numbers (10–12 digits)
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


# ===========================
# FastAPI App
# ===========================
app = FastAPI()

class TextInput(BaseModel):
    text: str

@app.post("/extract_numbers")
def extract_numbers(input: TextInput):
    numbers = extract_clean_phone_numbers(input.text)
    return {"extracted_numbers": numbers}
