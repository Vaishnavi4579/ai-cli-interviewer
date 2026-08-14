import os
from flask import Flask, render_template, request, jsonify, session, url_for
from resume_parser import extract_resume_text
from interviewer import generate_interview_question
from evaluator import evaluate_answer
from avatar import generate_avatar_video
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Total number of interview questions per session (configurable via env)
# Optional safety cap on number of questions to avoid runaway sessions (not shown to user)
MAX_QUESTIONS = int(os.getenv("MAX_QUESTIONS", "20"))

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def load_job_description():
    job_description = os.getenv("JOB_DESCRIPTION", "").strip()
    if job_description:
        return job_description

    job_description_file = os.getenv("JOB_DESCRIPTION_FILE")
    if job_description_file and os.path.exists(job_description_file):
        with open(job_description_file, "r", encoding="utf-8") as f:
            return f.read().strip()

    return ""


def load_use_previous_context():
    return os.getenv("USE_PREVIOUS_CONTEXT", "true").strip().lower() in {"1", "true", "yes"}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/interview", methods=["POST"])
def interview():
    file = request.files.get("resume")
    # Support either an uploaded file (PDF/DOCX) or pasted resume text
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        resume_text = extract_resume_text(filepath)
    else:
        # Check for pasted resume text in the form
        pasted = request.form.get("resume_text", "").strip()
        if not pasted:
            return "No file uploaded or resume text provided", 400
        resume_text = pasted
    job_description = load_job_description()
    use_previous_context = load_use_previous_context()

    session["resume_text"] = resume_text
    session["job_description"] = job_description
    session["use_previous_context"] = use_previous_context

    question = generate_interview_question(
        resume_text,
        job_description,
        use_previous_context=use_previous_context,
    )
    session["question_history"] = [question]
    session["answer_history"] = []
    session["last_question"] = question
    video_path = generate_avatar_video(question)

    if video_path and not video_path.startswith("http"):
        video_path = url_for("static", filename=video_path)

    return render_template(
        "interview.html",
        question=question,
        video_path=video_path,
        session_id="default",
        job_description=job_description,
    )


@app.route("/answer/<session_id>", methods=["POST"])
def answer(session_id):
    data = request.get_json()
    # Accept empty answers to support auto-advance (skip) from the frontend
    user_answer = data.get("answer", "")

    resume_text = session.get("resume_text", "")
    job_description = session.get("job_description", "") or load_job_description()
    use_previous_context = session.get("use_previous_context", load_use_previous_context())
    question_history = session.get("question_history", [])
    answer_history = session.get("answer_history", [])
    last_question = session.get("last_question", "")

    if last_question:
        answer_history.append(user_answer)
        session["answer_history"] = answer_history

    # mark completion when we've reached the safety cap
    if len(answer_history) >= MAX_QUESTIONS:
        return jsonify({
            "question": "",
            "video_path": "",
            "done": True,
            "redirect": url_for("result")
        })

    next_question = generate_interview_question(
        resume_text,
        job_description,
        prev_question=last_question,
        prev_answer=user_answer,
        question_history=question_history,
        answer_history=answer_history,
        use_previous_context=use_previous_context,
    )

    question_history.append(next_question)
    session["question_history"] = question_history
    session["last_question"] = next_question
    video_path = generate_avatar_video(next_question)

    if video_path and not video_path.startswith("http"):
        video_path = url_for("static", filename=video_path)

    return jsonify({
        "question": next_question,
        "video_path": video_path,
        "done": False
    })


@app.route("/result")
def result():
    question_history = session.get("question_history", [])
    answer_history = session.get("answer_history", [])
    items = []

    for question, answer in zip(question_history, answer_history):
        evaluation = evaluate_answer(question, answer)
        items.append({
            "question": question,
            "answer": answer,
            "evaluation": evaluation,
        })

    return render_template("result.html", items=items)


if __name__ == "__main__":
    # Allow toggling debug/reloader via FLASK_DEBUG env var to avoid
    # continuous restarts when files are edited programmatically.
    debug_env = os.getenv("FLASK_DEBUG", "1").strip().lower()
    debug = debug_env in {"1", "true", "yes"}
    app.run(debug=debug, use_reloader=debug)