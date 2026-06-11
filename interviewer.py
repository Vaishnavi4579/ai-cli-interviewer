from openai_client import ask_gpt
from resume_parser import extract_skills_from_resume


def generate_interview_question(
    resume_text,
    job_description="",
    prev_question=None,
    prev_answer=None,
    question_history=None,
    answer_history=None,
    use_previous_context=True,
):
    skills = extract_skills_from_resume(resume_text, max_skills=8)

    prompt = (
        "You are a professional interviewer conducting a live candidate interview. "
        "Do not explain your process or mention matched skills to the candidate. "
        "Keep the tone natural, conversational, and realistic.\n\n"
        "Resume:\n"
        f"{resume_text}\n"
    )

    if skills:
        prompt += "\nRelevant skills from the resume:\n"
        prompt += ", ".join(skills) + "\n"

    if job_description:
        prompt += f"\nJob Description:\n{job_description}\n"

    if use_previous_context and question_history and answer_history:
        prompt += "\nPrevious interview turns:\n"
        for q, a in zip(question_history, answer_history):
            prompt += f"Q: {q}\nA: {a}\n"

    if prev_question and prev_answer and use_previous_context:
        prompt += (
            "\nThe candidate just answered the previous question. "
            "Use that answer to ask the next question as a real interviewer would. "
            "Maintain the conversation flow and keep the question relevant to the role and the candidate's experience. "
            "Do not mention matched skills or job descriptions directly."
        )
    elif prev_question and prev_answer:
        prompt += (
            "\nThe candidate just answered the previous question. "
            "Do not use the previous answer to condition the next question. "
            "Instead, ask a new relevant question based on the resume and role."
        )
    else:
        prompt += (
            "\nThis is the first question in the interview. "
            "Start with a realistic opening interviewer prompt such as 'Tell me about yourself' or 'Walk me through your background.' "
            "Then ask one professional interview question that is relevant to the candidate and the role."
        )

    prompt += "\n\nAsk only one question."
    response = ask_gpt(prompt)
    return response.strip()


generate_question = generate_interview_question