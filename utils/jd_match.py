import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


def compare_resume_jd(resume_text, job_description):

    prompt = f"""
You are a professional ATS resume and job-description matching system.

Compare the candidate's resume ONLY with the provided job description.

IMPORTANT RULES:

1. Use only information present in the resume and job description.

2. Do not invent skills, experience, projects, qualifications, or
   achievements.

3. Do not assume that a skill is present unless the resume provides
   evidence for it.

4. A skill demonstrated inside a project or internship should be
   considered a matching skill even if it is not listed separately in
   the resume's skills section.

5. Missing skills must come ONLY from requirements mentioned in the
   job description.

6. Do not add generic skills that are not required by the job
   description.

7. Do not penalize the candidate for unrelated skills that are absent.

8. Consider the overall relevance of:
   - technical skills
   - projects
   - internships/experience
   - education
   - certifications
   - other relevant qualifications

9. The match percentage should represent how well the resume matches
   the specific job description.

10. Do not automatically give a high score simply because several
    technologies match.

11. If an important required skill from the JD is missing from the
    resume, mention it under missing_skills.

12. If the resume contains a skill but the JD does not require it,
    do not count it as a missing or matching JD skill.

13. Keep the analysis concise and professional.

14. Suggestions must focus on improving the resume for THIS job,
    not generic career advice.

15. Recruiter decision should be realistic for an entry-level
    recruitment scenario.

Return ONLY valid JSON.

Do not use Markdown.
Do not use ```json.
Do not add explanations outside the JSON.

Return exactly this structure:

{{
    "match_percentage": 0,
    "matching_skills": [],
    "missing_skills": [],
    "strengths": [],
    "weaknesses": [],
    "suggestions": [],
    "recruiter_decision": ""
}}

Resume:
----------------
{resume_text}

Job Description:
----------------
{job_description}
"""

    response = model.generate_content(prompt)

    text = response.text.strip()

    # Remove Markdown code fences if Gemini adds them
    if text.startswith("```json"):
        text = text[7:]

    if text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    result = json.loads(text)

    # Keep match percentage within valid range
    result["match_percentage"] = max(
        0,
        min(100, int(result.get("match_percentage", 0)))
    )

    return result