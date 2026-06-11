# AI CLI Interviewer Project Explanation

## Overview

This project is a command-line AI interview simulator built in Python. It uses a resume PDF file to generate interview questions, prompts the user for spoken answers with microphone support, evaluates those answers, and optionally displays a webcam feed during the interview.

The application is designed to work with Gemini via Google Generative AI, but it includes fallback behavior when the Gemini API is unavailable or when audio input fails.

## Main Purpose

The goal is to create a simple interactive interviewer that:
- extracts resume text from a PDF,
- generates interview questions based on that resume,
- speaks questions aloud using text-to-speech,
- accepts spoken answers or typed input,
- evaluates answers with AI or a local fallback,
- displays a final interview report.

## Key Files and Responsibilities

### `main.py`

This is the primary entry point and orchestrator for the interview flow.

Responsibilities:
- load the candidate resume text,
- start the camera thread,
- speak a greeting,
- loop through multiple questions,
- generate a question using `interviewer.py`,
- announce the question via `speaker.py`,
- collect the answer via `voice.py`,
- evaluate the answer with `evaluator.py`,
- store interview data,
- print a final report.

Important details:
- A default resume path of `resume.pdf` is offered.
- If resume loading fails, a built-in fallback summary is used.
- The camera runs in a daemon thread so the interview continues even if the webcam window is open.
- Each question is spoken and then the program listens for the user's voice response.

### `openai_client.py`

This module is responsible for loading environment variables and configuring the Gemini AI client.

Responsibilities:
- load `.env` file values into the environment,
- read `GOOGLE_API_KEY` and optionally `GOOGLE_GEMINI_MODEL`,
- initialize the Gemini client via `google.generativeai`,
- select a compatible model for `generateContent`,
- return a dictionary containing provider, client, and model.

Important details:
- If `.env` is missing or the key is absent, AI features fall back to local logic.
- If an environment model is set but invalid for content generation, the module falls back to a default Gemini model.
- Errors result in `None`, which other modules interpret as "no API available." 

### `interviewer.py`

This module generates interview questions from resume text.

Responsibilities:
- detect whether the Gemini client is available,
- form a prompt with the resume text,
- call `generate_content` on the Gemini client,
- return the generated question.

Fallback behavior:
- if the Gemini client is not configured or fails, it returns a safe fallback question: `"Tell me about yourself."`

### `evaluator.py`

This module evaluates the candidate's answer.

Responsibilities:
- build an evaluation prompt with the question and answer,
- call Gemini `generate_content` to rate the response,
- return the model's text output.

Fallback behavior:
- if Gemini is unavailable or fails, it returns a hardcoded local evaluation with score, strengths, weaknesses, and a sample correct answer.

### `voice.py`

This module handles spoken answer input.

Responsibilities:
- use `speech_recognition` to access the default system microphone,
- prompt the user to speak,
- calibrate ambient noise,
- listen with a timeout and phrase limit,
- convert speech to text with Google speech recognition.

Fallback behavior:
- if audio input fails, it falls back to typed answer input.
- if recognition fails or the service is unavailable, the user is prompted to type their answer.

### `resume_parser.py`

This module extracts text from a resume PDF.

Responsibilities:
- validate that the PDF exists,
- open the file with `PyPDF2.PdfReader`,
- extract text from every page,
- return the concatenated resume text.

Important details:
- if the file is missing, a `FileNotFoundError` is raised and handled in `main.py`.
- the text returned is stripped and may be empty if PDF extraction yields no text.

### `camera.py`

This module opens the computer webcam feed during the interview.

Responsibilities:
- initialize the default camera with OpenCV,
- display a live video window,
- allow the user to close the camera by pressing `Q`.

Important details:
- if the camera cannot be opened, it prints a message and exits gracefully.
- the camera loop runs until the user chooses to close it.

### `speaker.py`

This module performs text-to-speech narration.

Responsibilities:
- use native Windows SAPI via `win32com.client` when available,
- fall back to `pyttsx3` if SAPI is unavailable or fails,
- print text instead when TTS is unavailable.

Important details:
- the module attempts to speak every generated question and the opening greeting.
- if both speech methods fail, the text is still displayed in the console.

## Execution Flow

1. Start `main.py`.
2. The user is asked for a resume PDF path.
3. `main.py` loads resume text or uses fallback text.
4. The application greets the user and speaks a welcome message.
5. A camera thread starts to display the webcam.
6. For each interview question:
   - `interviewer.py` generates a question from resume text,
   - `main.py` prints and speaks the question,
   - `voice.py` listens for an answer or asks the user to type if audio fails,
   - `evaluator.py` evaluates the answer and returns feedback.
7. After questions complete, `main.py` prints a final interview report.

## Dependencies

The project depends on the following Python packages:
- `pyttsx3` for text-to-speech,
- `speech_recognition` for microphone input,
- `PyPDF2` for PDF text extraction,
- `opencv-python` for webcam display,
- `google-generativeai` for Gemini AI interaction,
- `pywin32` or `pypiwin32` for native Windows SAPI access.

## Environment Setup

The project expects a `.env` file at the repository root containing:

```text
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_GEMINI_MODEL=models/gemini-2.5-flash
```

Notes:
- `GOOGLE_API_KEY` is required for Gemini API access.
- `GOOGLE_GEMINI_MODEL` is optional and only used if the model supports `generateContent`.

## Error Handling and Fallbacks

This project is resilient to missing hardware or API access.

- Missing or unreadable resume PDF uses a default summary.
- Missing Gemini key or model issues use fallback question/evaluation text.
- Audio input errors fall back to typed answers.
- Camera failure prints a warning and does not block the interview.
- Text-to-speech errors fall back to a second TTS engine or plain text output.

## Practical Use

This tool can be used as a prototype interview practice assistant. It simulates an AI interviewer by:
- generating questions from real resume content,
- speaking questions aloud,
- accepting spoken input,
- evaluating answers with AI-generated feedback.

It is especially useful for developers or interviewees who want a quick CLI-based interview experience without a full graphical user interface.

## Project Strengths

- simple architecture with clear module boundaries,
- robust fallback paths for offline or unavailable services,
- actual resume-based question generation,
- voice-based interaction for a more natural interview feel,
- easy customization by changing the prompt templates or adding more question rounds.

## Potential Improvements

Future enhancements could include:
- richer multi-turn dialogue instead of a single question-answer loop,
- better error handling and user prompts for webcam and microphone permission issues,
- support for more than one resume file format,
- improved AI prompt engineering for more realistic interview questions,
- a logging or scoring system for longitudinal practice sessions.
