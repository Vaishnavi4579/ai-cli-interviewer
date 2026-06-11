import os
from dotenv import load_dotenv

load_dotenv()

# Try to use the groq client if available; otherwise provide a lightweight
# mock fallback so the app can run without installing the provider SDK.
try:
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def ask_gpt(prompt):
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

except Exception:
    def ask_gpt(prompt):
        # Fallback behavior: return a simple mock question so the app remains usable
        # without the Groq SDK. This helps development and testing.
        print("[openai_client] WARNING: groq client not available — returning mock response.")
        return (
            "MOCK QUESTION: Based on the provided resume and job description, "
            "please describe a recent project where you implemented SAP Analytics Cloud solutions and the key challenges you solved."
        )