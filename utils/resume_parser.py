import re

SECTION_HEADERS = {
    "SUMMARY": "summary",
    "PROFILE": "summary",
    "OBJECTIVE": "summary",

    "EDUCATION": "education",

    "TECHNICAL SKILLS": "skills",
    "SKILLS": "skills",
    "CORE SKILLS": "skills",

    "PROJECTS": "projects",
    "ACADEMIC PROJECTS": "projects",

    "INTERNSHIPS": "experience",
    "EXPERIENCE": "experience",
    "WORK EXPERIENCE": "experience",

    "CERTIFICATIONS": "certifications",

    "ACHIEVEMENTS": "achievements",

    "LANGUAGES": "languages"
}


def parse_resume(text):

    text = text.replace("\r", "")

    lines = []

    for line in text.split("\n"):
        line = line.strip()

        if line:
            lines.append(line)

    sections = {
        "header": ""
    }

    current = "header"

    for line in lines:

        clean = re.sub(r'[:\-]', '', line).strip().upper()

        if clean in SECTION_HEADERS:

            current = SECTION_HEADERS[clean]

            if current not in sections:
                sections[current] = ""

            continue

        sections.setdefault(current, "")

        sections[current] += line + "\n"

    return sections