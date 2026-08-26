def validate_resume(resume):

    checks = {}
    suggestions = []

    personal = resume.get("personal", {})

    # Contact details
    checks["email"] = bool(personal.get("email"))
    checks["phone"] = bool(personal.get("phone"))

    # Important sections
    checks["summary"] = bool(resume.get("summary"))
    checks["education"] = len(resume.get("education", [])) > 0
    checks["skills"] = any(
        resume.get("skills", {}).values()
    )
    checks["projects"] = len(resume.get("projects", [])) > 0
    checks["experience"] = len(resume.get("experience", [])) > 0

    # Suggestions
    if not checks["email"]:
        suggestions.append("Add a professional email address.")

    if not checks["phone"]:
        suggestions.append("Add a contact phone number.")

    if not checks["summary"]:
        suggestions.append("Add a concise professional summary.")

    if not checks["education"]:
        suggestions.append("Add your education details.")

    if not checks["skills"]:
        suggestions.append("Add relevant technical skills.")

    if not checks["projects"]:
        suggestions.append("Add relevant projects with technologies used.")

    # Calculate basic ATS score
    total = len(checks)
    passed = sum(checks.values())

    score = round((passed / total) * 100)

    return {
        "score": score,
        "checks": checks,
        "suggestions": suggestions
    }