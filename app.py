import os
import json
from flask import Flask, render_template, request
from utils.pdf_reader import extract_text
from utils.ai import analyze_resume
from utils.jd_match import compare_resume_jd
from utils.resume_structurer import structure_resume
from utils.ats import validate_resume

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create upload folder if it does not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/resume-analyzer", methods=["GET", "POST"])
def resume_analyzer():
    if request.method == "POST":
        resume = request.files["resume"]

        if resume.filename != "":
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], resume.filename)
            resume.save(file_path)
            text = extract_text(file_path)

            # 1. Structure the extracted text
            structured_resume = structure_resume(text)
            print(json.dumps(structured_resume, indent=4))

            # 2. Validate against ATS checks
            ats_result = validate_resume(structured_resume)
            print("\nATS VALIDATION:")
            print(ats_result)

            # 3. Perform final AI analysis
            result = analyze_resume(
                structured_resume,
                ats_result
            )
            print("\nFINAL AI ANALYSIS:")
            print(json.dumps(result, indent=4))

            return render_template("result.html", result=result)

    return render_template("resume_analyzer.html")


@app.route("/jd-match", methods=["GET", "POST"])
def jd_match():
    if request.method == "POST":
        resume = request.files["resume"]
        job_description = request.form["job_description"]

        if resume.filename != "":
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], resume.filename)
            resume.save(file_path)
            resume_text = extract_text(file_path)

            result = compare_resume_jd(
                resume_text,
                job_description
            )

            return render_template(
                "jd_result.html",
                result=result
            )

    return render_template("jd_match.html")


if __name__ == "__main__":
    app.run(debug=True)