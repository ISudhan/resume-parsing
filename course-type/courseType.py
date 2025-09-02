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


SUBJECT_PATTERNS = {
    # ================= Engineering & Technology =================
    "Computer Science Engineering": [r"\bcomputer\s+science\s+engineering\b", r"\bcse\b"],
    "Computer Science and Design Engineering": [r"\bcomputer\s+science\s+and\s+design\s+engineering\b", r"\bcsd\b", r"\bcs\s*&?\s*design\b", r"\bcs\s+design\s+engg\b"],
    "Information Technology": [r"\binformation\s+technology\b", r"\bit\b"],
    "Electronics and Communication Engineering": [r"\belectronics\s+and\s+communication\s+engineering\b", r"\bece\b"],
    "Electrical Engineering": [r"\belectrical\s+engineering\b", r"\bee\b"],
    "Mechanical Engineering": [r"\bmechanical\s+engineering\b", r"\bmech\b"],
    "Mechatronics Engineering": [r"\bmechatronics\s+engineering\b", r"\bmts\b"],
    "Electronics and Instrumentation Engineering": [r"\belectronics\s+and\s+instrumentation\s+engineering\b", r"\beie\b"],
    "Civil Engineering": [r"\bcivil\s+engineering\b", r"\bcivil\b"],
    "Automobile Engineering": [r"\bautomobile\s+engineering\b", r"\bautomobile\b"],
    "Aeronautical Engineering": [r"\baeronautical\s+engineering\b", r"\baero\b"],
    "Artificial Intelligence and Machine Learning": [r"\bartificial\s+intelligence\s+and\s+machine\s+learning\b", r"\bai/ml\b"],
    "Artificial Intelligence and Data Science": [r"\bartificial\s+intelligence\s+and\s+data\s+science\b", r"\bai/ds\b"],
    "Data Science": [r"\bdata\s+science\b"],
    "Robotics": [r"\brobotics\b"],
    "Biotechnology Engineering": [r"\bbiotechnology\s+engineering\b", r"\bbiotech\s+engg\b"],
    "Genetic Engineering": [r"\bgenetic\s+engineering\b"],
    "Biomedical Engineering": [r"\biomedical\s+engineering\b"],
    "Food Technology": [r"\bfood\s+technology\b", r"\bfood\s+engg\b"],
    "Ceramic Engineering": [r"\bceramic\s+engineering\b"],
    "Metallurgical Engineering": [r"\bmetallurgical\s+engineering\b", r"\bmetallurgy\b"],
    "Naval Architecture": [r"\bnaval\s+architecture\b"],
    "Ocean Engineering": [r"\bocean\s+engineering\b"],
    "Instrumentation Engineering": [r"\binstrumentation\s+engineering\b"],
    "Control Engineering": [r"\bcontrol\s+engineering\b"],
    "Industrial Engineering": [r"\bindustrial\s+engineering\b"],
    "Production Engineering": [r"\bproduction\s+engineering\b"],
    "Manufacturing Engineering": [r"\bmanufacturing\s+engineering\b"],
    "Textile Technology": [r"\btextile\s+technology\b"],
    "Leather Technology": [r"\bleather\s+technology\b"],
    "Rubber Technology": [r"\brubber\s+technology\b"],
    "Polymer Engineering": [r"\bpolymer\s+engineering\b"],
    "Environmental Engineering": [r"\benvironmental\s+engineering\b"],
    "Energy Engineering": [r"\benergy\s+engineering\b"],
    "Power Engineering": [r"\bpower\s+engineering\b"],
    "Safety Engineering": [r"\bsafety\s+engineering\b"],
    "Structural Engineering": [r"\bstructural\s+engineering\b"],
    "Transport Engineering": [r"\btransport\s+engineering\b"],
    "Geoinformatics Engineering": [r"\bgeoinformatics\s+engineering\b"],
    "Mining Machinery": [r"\bmining\s+machinery\b"],
    "Petrochemical Engineering": [r"\bpetrochemical\s+engineering\b"],
    "Plastic Engineering": [r"\bplastic\s+engineering\b"],
    "Thermal Engineering": [r"\bthermal\s+engineering\b"],
    "Welding Technology": [r"\bwelding\s+technology\b"],

    # ================= Science =================
    "Physics": [r"\bphysics\b"],
    "Chemistry": [r"\bchemistry\b"],
    "Mathematics": [r"\bmathematics\b", r"\bmaths?\b"],
    "Statistics": [r"\bstatistics\b"],
    "Biology": [r"\bbiology\b"],
    "Zoology": [r"\bzoology\b"],
    "Botany": [r"\bbotany\b"],

    # ================= Arts & Humanities =================
    "English": [r"\benglish\b"],
    "History": [r"\bhistory\b"],
    "Political Science": [r"\bpolitical\s+science\b"],
    "Psychology": [r"\bpsychology\b"],
    "Sociology": [r"\bsociology\b"],
    "Philosophy": [r"\bphilosophy\b"],

    # ================= Commerce & Management =================
    "Finance": [r"\bfinance\b"],
    "Accounting": [r"\baccounting\b", r"\baccounts?\b"],
    "Economics": [r"\beconomics\b"],
    "Business Administration": [r"\bbusiness\s+administration\b", r"\bmba\b"],
    "Human Resources": [r"\bhuman\s+resources\b", r"\bhr\b"],
    "Marketing": [r"\bmarketing\b"],

    # ================= Law, Medicine & Others =================
    "Law": [r"\blaw\b", r"\bl\.?l\.?b\b", r"\bllb\b"],
    "Nursing": [r"\bnursing\b", r"\bbsc\s+nursing\b"],
    "Pharmacy": [r"\bpharmacy\b", r"\bbpharm\b", r"\bmpharm\b"],
    "Medicine": [r"\bmedicine\b", r"\bmbbs\b"],
    "Dentistry": [r"\bdentistry\b", r"\bbds\b", r"\bmds\b"],
    "Physiotherapy": [r"\bphysiotherapy\b", r"\bpt\b", r"\bbpt\b"],
    "Ayurveda": [r"\bayurveda\b", r"\bbams\b"],
    "Homeopathy": [r"\bhomeopathy\b", r"\bbhms\b"],
    "Unani Medicine": [r"\bunani\b", r"\bbums\b"],
    "Veterinary Science": [r"\bveterinary\s+science\b", r"\bbvsc\b"],
    "Hotel Management": [r"\bhotel\s+management\b", r"\bbhm\b"],
    "Tourism": [r"\btourism\b"],
    "Fine Arts": [r"\bfine\s+arts\b", r"\bbfa\b"],
    "Performing Arts": [r"\bperforming\s+arts\b"],
    "Music": [r"\bmusic\b"],
    "Design": [r"\bdesign\b", r"\bbdes\b", r"\bmdes\b"],
    "Fashion Technology": [r"\bfashion\s+technology\b"],
    "Journalism": [r"\bjournalism\b", r"\bbjmc\b"],
    "Mass Communication": [r"\bmass\s+communication\b"],
    "Education": [r"\beducation\b", r"\bb\.?ed\b"],
    "Library Science": [r"\blibrary\s+science\b"],
    "Social Work": [r"\bsocial\s+work\b", r"\bmsw\b"],
    "Public Administration": [r"\bpublic\s+administration\b"],
}



def detect_degree_with_subject(text: str, window_size: int = 50):
    results = []
    for degree, d_patterns in COURSE_PATTERNS.items():
        for d_pattern in d_patterns:
            for d_match in re.finditer(d_pattern, text, re.IGNORECASE):

                start = max(0, d_match.start() - window_size)
                end = min(len(text), d_match.end() + window_size)
                snippet = text[start:end]

                found_subject = None
                for subject, s_patterns in SUBJECT_PATTERNS.items():
                    for s_pattern in s_patterns:
                        if re.search(s_pattern, snippet, re.IGNORECASE):
                            found_subject = subject
                            break
                    if found_subject:
                        break

                results.append({
                    "degree": degree,
                    "course": found_subject
                })
    return results


resume_text = """ 
"""

print(detect_degree_with_subject(resume_text))

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
        sample_text = item.get("resumeText", "")
        course = detect_degree_with_subject(sample_text)
        results+=course

    return {"received_data": results}
