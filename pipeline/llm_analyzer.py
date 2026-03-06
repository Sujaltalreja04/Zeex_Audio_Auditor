import json
import requests
from config.settings import OPENROUTER_API_KEY, OPENROUTER_MODEL


def analyze_transcript(transcript: str) -> dict:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set. Check your .env file.")

    prompt = f"""You are an AI survey call auditor. Analyze the transcript below and return ONLY a raw JSON object.

Required fields:
{{
  "language_detected": "<primary language>",
  "respondent_sentiment": "<positive or neutral or negative>",
  "call_quality_score": <integer 0-100>,
  "summary": "<one paragraph summary>",
  "is_authentic": "<write exactly one of: Authentic, Not Authentic>",
  "authenticity_reason": "<one sentence reason>"
}}

How to decide is_authentic:
- Write "Authentic" if the respondent speaks naturally and freely with no coaching.
- Write "Not Authentic" if the agent seems to answer for the respondent, the conversation is scripted, or there are signs of fraud.

Transcript:
{transcript}

IMPORTANT: Return ONLY the JSON object. No markdown, no code fences, no extra text."""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
        },
    )

    if not response.ok:
        raise RuntimeError(f"OpenRouter {response.status_code}: {response.text}")

    raw = response.json()["choices"][0]["message"]["content"] or ""
    raw = raw.strip()

    # Strip markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        return {"raw_response": raw}

    # Normalize is_authentic to exactly "Authentic" or "Not Authentic"
    raw_auth = str(result.get("is_authentic", "")).strip().lower()
    if "not" in raw_auth or "fake" in raw_auth or "fabricat" in raw_auth or "suspicious" in raw_auth:
        result["is_authentic"] = "Not Authentic"
    elif "authentic" in raw_auth or "genuine" in raw_auth or "real" in raw_auth:
        result["is_authentic"] = "Authentic"
    else:
        result["is_authentic"] = "Not Authentic"  # default to safer assumption

    return result
