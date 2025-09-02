from fastapi import FastAPI, Request
import pandas as pd

app = FastAPI()

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

    results = []
    for item in data_list:
        resume_text = item.get("resumeText", "")
        skills = skill_extract(resume_text)
        results.append({

            
            "skills": skills
        })

    return {"parsed_data": results}
