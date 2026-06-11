from openai_client import ask_gpt


def evaluate_answer(question, answer):
    prompt = f"""
You are a professional HR interviewer evaluating a candidate's answer.

Question: {question}

Candidate's Answer: {answer}

Please evaluate the answer and provide:
1. Score out of 10
2. Strengths of the answer
3. Areas for improvement
4. Overall feedback

Be professional and constructive.
"""
    response = ask_gpt(prompt)
    return response