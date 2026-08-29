import os
import json
from groq import Groq
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()


# Get Groq API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")


# Initialize Groq client
client = Groq(api_key=api_key)


def structure_resume(resume_text):

    prompt = f"""
You are NOT an ATS.

You are a Resume Structuring Engine.

Your job is ONLY to organize the resume.

Do NOT analyze.

Do NOT score.

Do NOT suggest improvements.

Extract the information into the exact JSON structure below.

IMPORTANT RULES:

1. Return ONLY valid JSON.
2. Do NOT use Markdown.
3. Do NOT use ```json or ``` code fences.
4. Do NOT add explanations before or after JSON.
5. Every key shown below must be present.
6. If information is not available, use an empty string "" or empty array [].
7. Preserve information from the resume accurately.
8. Do not invent information.
9. Ensure all JSON strings are properly closed.
10. Ensure the JSON object is complete before responding.

JSON STRUCTURE:

{{
    "personal": {{
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "linkedin": "",
        "github": "",
        "leetcode": "",
        "hackerrank": ""
    }},
    "summary": "",
    "education": [],
    "skills": {{
        "programming": [],
        "frameworks": [],
        "tools": [],
        "databases": [],
        "other": []
    }},
    "projects": [],
    "experience": [],
    "certifications": [],
    "achievements": [],
    "languages": []
}}

Resume:

{resume_text}
"""

    try:

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise resume information extraction engine. "
                        "Your output must always be valid JSON only."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.1,

            max_completion_tokens=4000,

            response_format={
                "type": "json_object"
            }
        )

        text = response.choices[0].message.content.strip()

        print("\n" + "=" * 60)
        print("STRUCTURER RESPONSE:")
        print(text)
        print("=" * 60 + "\n")

        result = json.loads(text)

        return result

    except json.JSONDecodeError as e:

        print("\n" + "=" * 60)
        print("STRUCTURER JSON ERROR:")
        print(repr(e))
        print("\nRAW RESPONSE:")
        print(text if "text" in locals() else "No response received")
        print("=" * 60 + "\n")

        raise ValueError(
            "Resume structuring failed because the AI returned invalid JSON."
        )

    except Exception as e:

        print("\n" + "=" * 60)
        print("STRUCTURER ERROR:")
        print(type(e).__name__)
        print(repr(e))
        print("=" * 60 + "\n")

        raise