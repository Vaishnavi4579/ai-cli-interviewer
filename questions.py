from openai_client import get_ai_client

client_info = get_ai_client()

def generate_question():
    prompt = "Act as a technical interviewer and ask one interview question."

    if client_info is None:
        return "Tell me about yourself."

    try:
        response = client_info["client"].generate_content(prompt)
        return getattr(response, "text", "").strip() or "Tell me about yourself."
    except Exception:
        pass

    return "Tell me about yourself."
