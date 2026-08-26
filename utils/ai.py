import os
import json
from datetime import date

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-2.5-flash")


def analyze_resume(resume, ats_validation):

    current_date = date.today().isoformat()

    prompt = f"""
You are a professional ATS resume evaluator and technical recruiter.

Analyze the resume using ONLY the provided structured resume data.

CURRENT DATE: {current_date}

IMPORTANT RULES:

1. Never invent skills, experience, companies, projects, achievements,
   certifications, responsibilities, or dates.

2. Determine the candidate's career direction from actual evidence in:
   skills, projects, internships, experience, certifications and achievements.
   Do not judge career direction only from the degree.

3. DATE RULES:
   - Use the current date above.
   - If an activity ended before today, it is completed.
   - If it includes today, it is ongoing.
   - If it starts after today, it is upcoming.
   - Do not call completed activities future activities.
   - If a date is unclear, say it is unclear instead of guessing.

4. EXPERIENCE RULES:
   - An internship is not automatically full-time professional employment.
   - If internships exist but no professional employment exists, clearly say:
     "No full-time professional work experience is listed. The resume includes internship experience."
   - If there is no experience or internship information at all, say:
     "No professional experience is listed on the resume."
   - Never invent responsibilities for internships.

5. SKILLS RULES:
   - Do not assume skills based on degree.
   - Do not list a skill as missing if it appears in skills, projects,
     experience, certifications, or achievements.
   - Only mention missing skills that are genuinely relevant to the
     candidate's demonstrated career direction.
   - Maximum 5 missing keywords.

6. ATS RULES:
   - Python ATS validation is only a structural check.
   - Do not automatically give 100 because sections exist.
   - Give a realistic ATS score based on clarity, structure, content,
     keywords, consistency and readability.

7. SUGGESTIONS:
   - Give specific suggestions for this resume.
   - Do not give generic advice.
   - Do not recommend unrelated technologies.
   - Do not recommend changing valid dates.
   - Keep suggestions practical and concise.

8. PROFILE LINKS:
   - If LinkedIn, GitHub, LeetCode or HackerRank is mentioned but no URL
     is extracted, do not claim the candidate does not have the profile.
   - Say the profile is mentioned but the URL was not extracted if relevant.

Return ONLY valid JSON.

Use this exact structure:

{{
    "candidate_profile": "",
    "ats_score": 0,
    "professional_summary": "",
    "strengths": [],
    "weaknesses": [],
    "skills_analysis": "",
    "experience_analysis": "",
    "education_analysis": "",
    "ats_analysis": "",
    "missing_keywords": [],
    "suggestions": [],
    "recruiter_opinion": ""
}}

OUTPUT LENGTH:
- candidate_profile: maximum 2 sentences
- professional_summary: maximum 4 sentences
- strengths: maximum 5 points
- weaknesses: maximum 5 points
- skills_analysis: maximum 5 sentences
- experience_analysis: maximum 5 sentences
- education_analysis: maximum 4 sentences
- ats_analysis: maximum 5 sentences
- missing_keywords: maximum 5 items
- suggestions: maximum 5 items
- recruiter_opinion: maximum 4 sentences

ATS VALIDATION:
{json.dumps(ats_validation, ensure_ascii=False)}

STRUCTURED RESUME:
{json.dumps(resume, ensure_ascii=False)}
"""

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=1800
            )
        )

        if not response or not response.text:
            raise ValueError("Empty response from Gemini")

        text = response.text.strip()

        print("\nGEMINI RAW RESPONSE:")
        print(text[:500])
        print()

        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

        result = json.loads(text)

        default_result = {
            "candidate_profile": "",
            "ats_score": 0,
            "professional_summary": "",
            "strengths": [],
            "weaknesses": [],
            "skills_analysis": "",
            "experience_analysis": "",
            "education_analysis": "",
            "ats_analysis": "",
            "missing_keywords": [],
            "suggestions": [],
            "recruiter_opinion": ""
        }

        for key, value in default_result.items():
            if key not in result:
                result[key] = value

        try:
            result["ats_score"] = int(result["ats_score"])
            result["ats_score"] = max(0, min(100, result["ats_score"]))
        except Exception:
            result["ats_score"] = 0

        return result

    except json.JSONDecodeError as e:
        print("\nJSON ERROR:", repr(e))
        print("Response received but was not valid JSON.")

        return {
            "candidate_profile": "",
            "ats_score": 0,
            "professional_summary": "The AI returned an invalid response. Please try again.",
            "strengths": [],
            "weaknesses": [],
            "skills_analysis": "",
            "experience_analysis": "",
            "education_analysis": "",
            "ats_analysis": "",
            "missing_keywords": [],
            "suggestions": [],
            "recruiter_opinion": ""
        }

    except Exception as e:
        print("\n" + "=" * 60)
        print("GEMINI ERROR TYPE:", type(e).__name__)
        print("GEMINI ERROR:", repr(e))
        print("=" * 60 + "\n")

        return {
            "candidate_profile": "",
            "ats_score": 0,
            "professional_summary": "AI analysis is temporarily unavailable. Please try again.",
            "strengths": [],
            "weaknesses": [],
            "skills_analysis": "",
            "experience_analysis": "",
            "education_analysis": "",
            "ats_analysis": "",
            "missing_keywords": [],
            "suggestions": [],
            "recruiter_opinion": ""
        }