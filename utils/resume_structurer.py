import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


def structure_resume(resume_text):

    prompt = f"""
You are NOT an ATS.

You are a Resume Structuring Engine.

Your job is ONLY to organize the resume.

Do NOT analyze.

Do NOT score.

Do NOT suggest improvements.

Extract the information into this JSON format.

Return ONLY valid JSON.

{{
    "personal": {{
        "name":"",
        "email":"",
        "phone":"",
        "location":"",
        "linkedin":"",
        "github":"",
        "leetcode":"",
        "hackerrank":""
    }},

    "summary":"",

    "education":[],

    "skills":{{
        "programming":[],
        "frameworks":[],
        "tools":[],
        "databases":[],
        "other":[]
    }},

    "projects":[],

    "experience":[],

    "certifications":[],

    "achievements":[],

    "languages":[]
}}

Resume:

{resume_text}
"""

    response = model.generate_content(prompt)

    text = response.text.strip()

    text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)