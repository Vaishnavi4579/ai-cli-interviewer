import os
import uuid
import requests
import time
from dotenv import load_dotenv

load_dotenv()

DID_API_KEY = os.getenv("DID_API_KEY")
DID_IMAGE_URL = os.getenv("DID_IMAGE_URL")
VIDEO_FOLDER = "static/generated_videos"

os.makedirs(VIDEO_FOLDER, exist_ok=True)


def _build_did_auth_header(api_key):
    if not api_key:
        return None

    api_key = api_key.strip()
    if api_key.lower().startswith("bearer ") or api_key.lower().startswith("basic "):
        return api_key
    return f"Bearer {api_key}"


def generate_did_video(text):
    try:
        print("Generating D-ID video...")

        auth_header = _build_did_auth_header(DID_API_KEY)
        if not auth_header:
            print("D-ID API key is missing or invalid.")
            return None

        url = "https://api.d-id.com/talks"
        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "source_url": DID_IMAGE_URL,
            "script": {
                "type": "text",
                "input": text,
                "provider": {
                    "type": "microsoft",
                    "voice_id": "en-US-GuyNeural"
                }
            },
            "config": {
                "fluent": True,
                "pad_audio": 0.0
            }
        }

        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        print("D-ID create response:", response_data)

        if response.status_code == 401:
            print("D-ID unauthorized. Check DID_API_KEY and permissions.")
            return None

        talk_id = response_data.get("id")
        if not talk_id:
            print("D-ID failed:", response_data)
            return None

        # Poll until video is ready
        print(f"Waiting for video (id: {talk_id})...")
        for attempt in range(20):
            time.sleep(3)
            poll = requests.get(
                f"https://api.d-id.com/talks/{talk_id}",
                headers=headers
            )
            poll_data = poll.json()
            status = poll_data.get("status")
            print(f"Attempt {attempt + 1}: status = {status}")

            if status == "done":
                video_url = poll_data.get("result_url")
                print(f"Video ready: {video_url}")
                return download_video(video_url)

            elif status == "error":
                print("D-ID error:", poll_data)
                return None

        print("D-ID timed out")
        return None

    except Exception as e:
        print(f"D-ID exception: {e}")
        return None


def download_video(video_url):
    try:
        video_filename = f"{uuid.uuid4()}.mp4"
        saved_path = os.path.join(VIDEO_FOLDER, video_filename)

        response = requests.get(video_url, stream=True)
        with open(saved_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Video saved: {saved_path}")
        return f"generated_videos/{video_filename}"

    except Exception as e:
        print(f"Video download error: {e}")
        return None


def generate_avatar_video(text):
    if DID_API_KEY and DID_IMAGE_URL:
        video_path = generate_did_video(text)
        if video_path:
            return video_path
    print("D-ID unavailable, using static avatar")
    return "images/interviewer.png"