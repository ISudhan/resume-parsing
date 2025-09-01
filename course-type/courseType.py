from fastapi import FastAPI, Request
import re

COURSE_PATTERNS = {
    # ================= Undergraduate =================
    "BA": [r"\bB\.?\s?A\b", r"\bBachelor(?:'s)?\s+of\s+Arts\b"],
    "B.Sc": [r"\bB\.?\s?Sc\b", r"\bBachelor(?:'s)?\s+of\s+Science\b", r"\bBS\b"],
    "B.Com": [r"\bB\.?\s?Com\b", r"\bBachelor(?:'s)?\s+of\s+Commerce\b"],
    "BBA": [r"\bBBA\b", r"\bBachelor(?:'s)?\s+of\s+Business\s+Administration\b"],
    "BCA": [r"\bBCA\b", r"\bBachelor(?:'s)?\s+of\s+Computer\s+Applications\b"],
    "B.Tech": [r"\bB\.?\s?Tech\b", r"\bBachelor(?:'s)?\s+of\s+Technology\b"],
    "BE": [r"\bB\.?\s?E\b", r"\bBachelor(?:'s)?\s+of\s+Engineering\b"],
    "MBBS": [r"\bMBBS\b", r"\bBachelor(?:'s)?\s+of\s+Medicine\b"],
    "B.Ed": [r"\bB\.?\s?Ed\b", r"\bBachelor(?:'s)?\s+of\s+Education\b"],
    "LLB": [r"\bLLB\b", r"\bBachelor(?:'s)?\s+of\s+Law\b"],
    "BFA": [r"\bBFA\b", r"\bBachelor(?:'s)?\s+of\s+Fine\s+Arts\b"],
    "B.Arch": [r"\bB\.?\s?Arch\b", r"\bBachelor(?:'s)?\s+of\s+Architecture\b"],
    "B.Pharm": [r"\bB\.?\s?Pharm\b", r"\bBachelor(?:'s)?\s+of\s+Pharmacy\b"],
    "BDS": [r"\bBDS\b", r"\bBachelor(?:'s)?\s+of\s+Dental\s+Surgery\b"],
    "BSW": [r"\bBSW\b", r"\bBachelor(?:'s)?\s+of\s+Social\s+Work\b"],
    "BVoc": [r"\bBVoc\b", r"\bBachelor(?:'s)?\s+of\s+Vocation\b"],
    "BHM": [r"\bBHM\b", r"\bBachelor(?:'s)?\s+of\s+Hotel\s+Management\b"],

    # ================= Postgraduate =================
    "MA": [r"\bM\.?\s?A\b", r"\bMaster(?:'s)?\s+of\s+Arts\b"],
    "M.Sc": [r"\bM\.?\s?Sc\b", r"\bMaster(?:'s)?\s+of\s+Science\b", r"\bMS\b"],
    "M.Com": [r"\bM\.?\s?Com\b", r"\bMaster(?:'s)?\s+of\s+Commerce\b"],
    "MBA": [r"\bMBA\b", r"\bMaster(?:'s)?\s+of\s+Business\s+Administration\b", r"\bPGDM\b"],
    "MCA": [r"\bMCA\b", r"\bMaster(?:'s)?\s+of\s+Computer\s+Applications\b"],
    "M.Tech": [r"\bM\.?\s?Tech\b", r"\bMaster(?:'s)?\s+of\s+Technology\b"],
    "ME": [r"\bM\.?\s?E\b", r"\bMaster(?:'s)?\s+of\s+Engineering\b"],
    "M.Ed": [r"\bM\.?\s?Ed\b", r"\bMaster(?:'s)?\s+of\s+Education\b"],
    "LLM": [r"\bLLM\b", r"\bMaster(?:'s)?\s+of\s+Law\b"],
    "MFA": [r"\bMFA\b", r"\bMaster(?:'s)?\s+of\s+Fine\s+Arts\b"],
    "M.Arch": [r"\bM\.?\s?Arch\b", r"\bMaster(?:'s)?\s+of\s+Architecture\b"],
    "M.Pharm": [r"\bM\.?\s?Pharm\b", r"\bMaster(?:'s)?\s+of\s+Pharmacy\b"],
    "MD": [r"\bMD\b", r"\bDoctor(?:'s)?\s+of\s+Medicine\b"],
    "MS (Medical)": [r"\bMS\b", r"\bMaster(?:'s)?\s+of\s+Surgery\b"],
    "MDS": [r"\bMDS\b", r"\bMaster(?:'s)?\s+of\s+Dental\s+Surgery\b"],
    "M.Phil": [r"\bM\.?\s?Phil\b", r"\bMaster(?:'s)?\s+of\s+Philosophy\b"],

    # ================= Doctoral =================
    "PhD": [r"\bPh\.?\s?D\b", r"\bDoctor(?:'s)?\s+of\s+Philosophy\b", r"\bDPhil\b"],
    "D.Sc": [r"\bD\.?\s?Sc\b", r"\bDoctor\s+of\s+Science\b"],
    "DM": [r"\bDM\b", r"\bDoctorate\s+of\s+Medicine\b"],
    "MCh": [r"\bMCh\b", r"\bMagister\s+Chirurgiae\b"],
    "Postdoctoral": [r"\bPostdoctoral\b", r"\bPost\s+Doc\b"],

    # ================= Diplomas & Vocational =================
    "Diploma": [r"\bDiploma\b", r"\bAdvanced\s+Diploma\b", r"\bPG\s+Diploma\b", r"\bPost\s+Graduate\s+Diploma\b"],
    "Polytechnic": [r"\bPolytechnic\b"],
    "ITI": [r"\bITI\b", r"\bIndustrial\s+Training\s+Institute\b"],
}

def extract_course_types(text, unique=True):
    found = []
    for course, patterns in COURSE_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                found.append(course)
                break 
    return list(dict.fromkeys(found)) if unique else found



sample_text = """

"""

print("CourseType: ",extract_course_types(sample_text))


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
        sample_text = item.get("sample_text", "")
        course = extract_course_types(sample_text)
        results+=course

    return {"received_data": results}


