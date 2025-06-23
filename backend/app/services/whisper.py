import logging
import requests
import time
from app.config import Config

def transcribe_audio(file_path: str, language: str = "en") -> str:
    max_retries = 3
    backoff = 2
    for attempt in range(max_retries):
        try:
            logging.info(f"Sending transcription request to {Config.WHISPER_API_URL}")
            with open(file_path, "rb") as audio_file:
                response = requests.post(
                    Config.WHISPER_API_URL,
                    headers={"Authorization": f"Bearer {Config.WHISPER_API_KEY}"},
                    files={"file": audio_file},
                    data={"model": "whisper-large-v3", "language": language},
                )
                logging.info(f"API Response Status: {response.status_code}")
                logging.info(f"API Response Body: {response.text}")
                response.raise_for_status()
                return response.json().get("text", "")
        except requests.exceptions.RequestException as e:
            logging.warning(f"Whisper API request failed (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(backoff ** attempt)
            else:
                raise
