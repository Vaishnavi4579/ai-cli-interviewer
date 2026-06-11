import argparse
import os
from resume_parser import extract_resume_text, extract_skills_from_resume
from interviewer import generate_interview_question
from openai_client import ask_gpt


def build_prompt(resume_text, job_description):
    skills = extract_skills_from_resume(resume_text, max_skills=8)
    prompt = f"""
You are a professional HR interviewer.

Resume:
{resume_text}
"""
    if skills:
        prompt += """

Matched Skills:
"""
        prompt += ", ".join(skills)
    if job_description:
        prompt += f"""

Job Description:
{job_description}
"""
    prompt += """
Based on the candidate's resume and the job description, identify the matching skills and ask one professional interview question that is relevant to the role.
"""
    return prompt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume', required=True, help='Path to resume (pdf or docx)')
    parser.add_argument('--jd', required=False, help='Path to job description text file')
    parser.add_argument('--jd-text', required=False, help='Job description text (overrides --jd)')
    parser.add_argument('--call-model', action='store_true', help='Call the configured model instead of printing prompt')
    args = parser.parse_args()

    resume_text = extract_resume_text(args.resume)
    job_description = ''
    if args.jd_text:
        job_description = args.jd_text
    elif args.jd:
        if os.path.exists(args.jd):
            with open(args.jd, 'r', encoding='utf-8') as f:
                job_description = f.read()

    prompt = build_prompt(resume_text, job_description)

    if args.call_model:
        try:
            print('Calling model...')
            response = ask_gpt(prompt)
            print('\n=== Model Response ===\n')
            print(response)
        except Exception as e:
            print('Model call failed:', e)
            print('\n=== Prompt ===\n')
            print(prompt)
    else:
        print('\n=== Prompt ===\n')
        print(prompt)
