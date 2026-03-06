import os
import requests
from config.settings import SARVAM_API_KEY


def speech_to_text(audio_path: str) -> str:
    url = "https://api.sarvam.ai/speech-to-text"

    ext = os.path.splitext(audio_path)[1].lower()
    mime_map = {
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".mp4": "audio/mp4",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac",
        ".aac":  "audio/aac",
        ".webm": "audio/webm",
        ".amr":  "audio/amr",
    }
    mime = mime_map.get(ext, "audio/wav")

    with open(audio_path, "rb") as f:
        response = requests.post(
            url,
            headers={"api-subscription-key": SARVAM_API_KEY},
            files={"file": (os.path.basename(audio_path), f, mime)},
        )

    if not response.ok:
        raise RuntimeError(f"Sarvam {response.status_code}: {response.text}")

    return response.json().get("transcript", "")
