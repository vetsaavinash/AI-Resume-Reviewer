import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Get Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found. "
        "Add it to your .env file locally and Render environment variables."
    )

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Your currently available Groq model
MODEL_NAME = "openai/gpt-oss-20b"


def extract_json(text):
    """
    Extract valid JSON from AI response safely.
    """

    if not text:
        raise ValueError("AI returned an empty response.")

    text = text.strip()

    # Remove markdown code blocks if present
    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    # First try direct JSON parsing
    try:
        return json.loads(text)

    except json.JSONDecodeError:
        pass

    # Try extracting JSON object boundaries
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        possible_json = text[start:end + 1]

        try:
            return json.loads(possible_json)

        except json.JSONDecodeError as e:
            print("\nJD MATCH JSON ERROR:")
            print(e)
            print("\nRAW AI RESPONSE:")
            print(text)

            raise ValueError(
                "Groq returned invalid JSON for JD matching."
            )

    print("\nJD MATCH RAW RESPONSE:")
    print(text)

    raise ValueError(
        "Could not find valid JSON in the Groq response."
    )


def compare_resume_jd(resume_text, job_description):

    prompt = f"""
You are a professional ATS resume and job-description matching system.

Compare the candidate's resume ONLY with the provided job description.

IMPORTANT RULES:

1. Use only information present in the resume and job description.

2. Do not invent skills, experience, projects, qualifications, or achievements.

3. Do not assume that a skill is present unless the resume provides evidence for it.

4. A skill demonstrated inside a project or internship should be considered a matching skill even if it is not listed separately in the resume's skills section.

5. Missing skills must come ONLY from requirements mentioned in the job description.

6. Do not add generic skills that are not required by the job description.

7. Do not penalize the candidate for unrelated skills that are absent.

8. Consider the overall relevance of:
   - technical skills
   - projects
   - internships/experience
   - education
   - certifications
   - other relevant qualifications

9. The match percentage should represent how well the resume matches the specific job description.

10. Do not automatically give a high score simply because several technologies match.

11. If an important required skill from the JD is missing from the resume, mention it under missing_skills.

12. If the resume contains a skill but the JD does not require it, do not count it as a missing or matching JD skill.

13. Keep the analysis concise and professional.

14. Suggestions must focus on improving the resume for THIS job, not generic career advice.

15. Recruiter decision should be realistic for an entry-level recruitment scenario.

Return ONLY valid JSON.

Do not use Markdown.
Do not use code fences.
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

    try:

        print("\nMATCHING RESUME WITH JOB DESCRIPTION...")

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise resume and job description "
                        "matching engine. Always follow the requested "
                        "JSON structure exactly."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_completion_tokens=2500
        )

        text = response.choices[0].message.content

        print("\n" + "=" * 60)
        print("JD MATCH RAW RESPONSE:")
        print(text)
        print("=" * 60)

        result = extract_json(text)

        # Ensure match percentage is valid
        try:
            match_percentage = int(
                float(result.get("match_percentage", 0))
            )
        except (ValueError, TypeError):
            match_percentage = 0

        result["match_percentage"] = max(
            0,
            min(100, match_percentage)
        )

        # Ensure all list fields are lists
        list_fields = [
            "matching_skills",
            "missing_skills",
            "strengths",
            "weaknesses",
            "suggestions"
        ]

        for field in list_fields:
            if field not in result or not isinstance(result[field], list):
                result[field] = []

        # Ensure recruiter decision exists
        if not result.get("recruiter_decision"):
            result["recruiter_decision"] = (
                "No recruiter decision was generated."
            )

        return result

    except Exception as e:

        print("\n" + "=" * 60)
        print("JD MATCH ERROR")
        print(type(e).__name__)
        print(repr(e))
        print("=" * 60)

        raise ValueError(
            f"JD matching failed: {str(e)}"
        )