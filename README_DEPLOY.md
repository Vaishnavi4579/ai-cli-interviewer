Deploying AI CLI Interviewer to Render

This document describes how to deploy the updated AI CLI Interviewer (voice-only flow, auto-advance, and Infrabeat branding) to Render.com.

Prerequisites
- Git remote (e.g. GitHub) with push access.
- Render account and access to the target service (or permission to create a new Web Service).
- Your Infrabeat logo PNG file ready to place at `static/Avatar/infrabeat_logo.png`.
- Model API keys (if required) such as `GROQ_API_KEY`.

1) Replace logo (locally)
- Copy your real logo PNG over the placeholder used in the repo:
  - Path: `static/Avatar/infrabeat_logo.png`

2) Create a branch and commit your changes
- Recommended: create a new branch, commit changes, and open a PR.

Bash/macOS/Linux:
```bash
git checkout -b infra/voice-interview
git add -A
git commit -m "Voice-only interview flow, auto-submit answers, Infrabeat branding"
git push origin infra/voice-interview
```

PowerShell (Windows):
```powershell
git checkout -b infra/voice-interview
git add -A
git commit -m "Voice-only interview flow, auto-submit answers, Infrabeat branding"
git push origin infra/voice-interview
```

3) Merge the branch to the main branch on GitHub (create PR and merge) or push directly to `main` if you prefer.

4) Configure Render service
- Navigate to your Render dashboard and open the web service for `ai-cli-interviewer` (or create a new Web Service pointing to your repo and branch).
- Confirm `Procfile` exists at repo root with `web: gunicorn web_app:app` (this repo has it).
- Build Command (optional): `pip install -r requirements.txt` (Render typically does this automatically).
- Environment Variables (in Render dashboard -> Environment):
  - `FLASK_DEBUG = 0`  # disable debug/reloader in production
  - `MAX_QUESTIONS = 20`  # safety cap (optional)
  - `GROQ_API_KEY = <your-key>` (if using groq)
  - `JOB_DESCRIPTION` / `JOB_DESCRIPTION_FILE` (optional)
  - `USE_PREVIOUS_CONTEXT = true` (optional)

5) Deploy
- In Render, click "Manual Deploy" or wait for auto-deploy after push.
- Monitor the Deploy logs for build errors; fix missing packages by updating `requirements.txt` if necessary.

6) Verify runtime behavior
- Open the Render URL (e.g., `https://ai-cli-interviewer.onrender.com`).
- Use Chrome or Edge for SpeechRecognition support. Allow microphone access.
- Start a session (upload or paste resume). The interviewer should auto-speak, listen for your spoken answer, transcribe and auto-submit, then ask a follow-up question based on the answer.

Troubleshooting
- Build fails with missing packages: add packages to `requirements.txt` and re-deploy.
- Logo not visible: ensure `static/Avatar/infrabeat_logo.png` was committed and deployed.
- TTS or SpeechRecognition not working locally but OK on Render: ensure you use Chrome/Edge (not all browsers support SpeechRecognition), and that the site is served over HTTPS (Render is HTTPS by default).
- Model/API errors: check server logs for stack traces; ensure API keys are set in Render environment.

Helpful commands (local)
- Run app locally (simulate production):
```powershell
$env:FLASK_DEBUG = "0"  # PowerShell
python web_app.py
# or
gunicorn web_app:app
```

- Install dependencies:
```bash
pip install -r requirements.txt
```

If you want me to prepare a branch and commit in the repository here (I can create the branch and commit locally), tell me and I'll create it and print the exact `git push` command you should run to push it to your remote.

If you prefer, I can also create a small `deploy.sh` or `deploy.ps1` script to automate the push + Render redeploy (manual trigger required on Render unless you enable auto-deploy).

-- End of guide
