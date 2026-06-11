from evaluator import evaluate
from interviewer import generate_interview_question

from resume_parser import extract_resume_text

import threading
import time
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_RESUME_TEXT = (
    "Candidate resume summary:\n"
    "Experienced professional with strong communication skills, technical knowledge, and interview problem-solving ability."
)

KNOWN_RESUME_FILES = ["resume.pdf", "resume.docx", "sample resume.pdf", "sample resume.docx", "sample_resume.pdf", "sample_resume.docx"]


def load_resume_text():
    default_file = "resume.pdf"
    resume_path = input(f"Enter resume path (PDF or DOCX, default {default_file}): ").strip() or default_file

    files_to_try = [resume_path] + [f for f in KNOWN_RESUME_FILES if f != resume_path]
    for path in files_to_try:
        try:
            resume_text = extract_resume_text(path)
            if resume_text:
                print(f"📄 Resume loaded successfully from: {path}")
                return resume_text
            print(f"⚠️ Resume parsed but contained no text: {path}")
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"⚠️ Error reading resume {path}: {e}")
            continue

    print("⚠️ No resume file loaded. Using fallback resume summary.")
    return DEFAULT_RESUME_TEXT


def load_job_description():
    print("\nEnter the job description or required skills for this role.")
    return input("Job description: ").strip()


def speak(text):
    """Fallback text output for interview prompts."""
    print(f"🔊 [speak] {text}")


def start_camera():
    """Placeholder camera thread. Replace with actual camera logic if needed."""
    print("📷 Camera thread started (placeholder).")
    while True:
        time.sleep(5)


def listen_answer():
    """Read the candidate's response from standard input."""
    return input("📝 Your answer: ")


def run_interview():
    resume_text = load_resume_text()
    job_description = load_job_description()
    use_previous_context = os.getenv("USE_PREVIOUS_CONTEXT", "true").strip().lower() in {"1", "true", "yes"}

    intro = "Hello, I am your AI interviewer. Let's begin."
    print(intro)
    speak(intro)

    camera_thread = threading.Thread(target=start_camera, daemon=True)
    camera_thread.start()

    time.sleep(2)

    interview_data = []

    question_history = []
    answer_history = []
    prev_question = None
    prev_answer = None

    for i in range(3):
        question = generate_interview_question(
            resume_text,
            job_description,
            prev_question=prev_question,
            prev_answer=prev_answer,
            question_history=question_history,
            answer_history=answer_history,
            use_previous_context=use_previous_context,
        )
        spoken_question = f"Question {i + 1}. {question}. Please answer now."

        print("\n🧠 AI Interviewer:", question)
        speak(spoken_question)

        answer = listen_answer()
        print("🗣 Your Answer:", answer)

        result = evaluate(question, answer)
        interview_data.append({
            "question": question,
            "answer": answer,
            "evaluation": result,
        })

        question_history.append(question)
        answer_history.append(answer)
        prev_question = question
        prev_answer = answer

    print("\n✅ Interview Completed")
    print("\n📄 Interview Report")
    for index, item in enumerate(interview_data, start=1):
        print(f"\nQuestion {index}: {item['question']}")
        print(f"Answer {index}: {item['answer']}")
        print(f"Evaluation {index}:\n{item['evaluation']}")


if __name__ == "__main__":
    run_interview()