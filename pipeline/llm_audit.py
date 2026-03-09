import json
import requests
from config.settings import OPENROUTER_API_KEY, OPENROUTER_MODEL

def extract_and_verify_llm(form_data: dict, transcript: str, segments: list = None) -> dict:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set.")

    # Build indexed segment list for the LLM
    indexed_lines = ""
    if segments:
        for i, seg in enumerate(segments):
            indexed_lines += f"[{i}] {seg['text']}\n"
    else:
        indexed_lines = transcript

    num_segments = len(segments) if segments else 0

    prompt = f"""You are an AI survey call auditor. Read the translated transcript and verify the form data provided.
Evaluate if each form field is a 'Match', 'Mismatch', or 'Missing' based ONLY on what is spoken in the transcript.

Form Data Context:
Name: {form_data.get('Name', '')}
Age: {form_data.get('Age', '')}
Profession: {form_data.get('Profession', '')}
Education: {form_data.get('Education', '')}
District: {form_data.get('District', '')}

Rules:
- Match: Transcript provides evidence supporting the form data (fuzzily matching meaning is fine).
- Mismatch: Transcript explicitly contradicts the form data.
- Missing: The topic was not mentioned in the transcript.

Speaker Labeling Instructions:
The transcript below has {num_segments} indexed lines [0] through [{num_segments - 1}].
You MUST label EVERY SINGLE line with a speaker. Do NOT skip any line.
For EACH index from 0 to {num_segments - 1}, include an entry in the 'conversation' array.
Classify speaker as 'Suryeior' (person asking questions/conducting survey) or 'Respondent' (person answering).

Return ONLY a raw JSON object. Do NOT wrap in markdown fences.
{{
  "verdict": "Match",
  "language": "<identify the original spoken language, e.g. Hindi, English, Marathi>",
  "details": {{
      "Name": {{"status": "Match|Mismatch|Missing", "timestamp": "N/A", "spoken": "<what they actually said>"}},
      "Age": {{"status": "Match|Mismatch|Missing", "timestamp": "N/A", "spoken": "<what they actually said>"}},
      "Profession": {{"status": "Match|Mismatch|Missing", "timestamp": "N/A", "spoken": "<what they actually said>"}},
      "Education": {{"status": "Match|Mismatch|Missing", "timestamp": "N/A", "spoken": "<what they actually said>"}},
      "District": {{"status": "Match|Mismatch|Missing", "timestamp": "N/A", "spoken": "<what they actually said>"}}
  }},
  "conversation": [
      {{"segment_index": 0, "speaker": "Suryeior"}},
      {{"segment_index": 1, "speaker": "Respondent"}}
  ]
}}

Indexed Transcript Lines:
{indexed_lines}
"""

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
        raise RuntimeError(f"OpenRouter Error {response.status_code}")

    raw = response.json()["choices"][0]["message"]["content"]
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        data = json.loads(raw)
        
        # Post-process: merge real Whisper timestamps into conversation
        if segments:
            # Build a map of segment_index -> speaker from LLM response
            speaker_map = {}
            if "conversation" in data:
                for item in data["conversation"]:
                    idx = item.get("segment_index")
                    if idx is not None:
                        speaker_map[idx] = item.get("speaker", "Unknown")
            
            # Build enriched conversation from ALL segments (never skip any)
            enriched_convo = []
            for i, seg in enumerate(segments):
                speaker = speaker_map.get(i, "Unknown")
                # If LLM didn't label it, try to guess based on content
                if speaker == "Unknown":
                    text_lower = seg["text"].lower()
                    if "?" in seg["text"] or any(w in text_lower for w in ["what", "how", "where", "which", "your name", "your age", "tell me", "do you"]):
                        speaker = "Suryeior"
                    else:
                        speaker = "Respondent"
                
                enriched_convo.append({
                    "speaker": speaker,
                    "text": seg["text"],
                    "timestamp": f"{seg['start']}-{seg['end']}"
                })
            
            data["conversation"] = enriched_convo
        
        return data
    except:
        # Even on parse error, build conversation from segments if available
        convo = []
        if segments:
            for i, seg in enumerate(segments):
                text_lower = seg["text"].lower()
                if "?" in seg["text"] or any(w in text_lower for w in ["what", "how", "where", "which", "your name", "tell me"]):
                    speaker = "Suryeior"
                else:
                    speaker = "Respondent"
                convo.append({
                    "speaker": speaker,
                    "text": seg["text"],
                    "timestamp": f"{seg['start']}-{seg['end']}"
                })
        
        return {
            "verdict": "Error",
            "details": {
                k: {"status": "Missing", "timestamp": "N/A", "spoken": "Error parsing LLM response"} 
                 for k in form_data.keys()
            },
            "conversation": convo
        }
