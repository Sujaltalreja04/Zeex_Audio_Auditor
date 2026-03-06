import json
import os

from pipeline.sarvam_asr import speech_to_text
from pipeline.llm_analyzer import analyze_transcript
from pipeline.survey_checker import check_questions
from pipeline.fraud_detector import detect_fraud, get_agent_ratio


def run_audit(audio_path: str) -> dict:
    """
    Runs the full ZeeX AI audio audit pipeline on a given audio file.

    Steps:
        1. Transcribe audio via Sarvam ASR
        2. Check survey compliance
        3. Detect fraud risk via talk ratio
        4. Analyze transcript quality via LLM

    Args:
        audio_path: Path to the audio file to audit.

    Returns:
        Dictionary containing transcript, survey_compliance,
        fraud_risk, agent_ratio, and llm_analysis.
    """
    # Step 1: Transcribe
    transcript = speech_to_text(audio_path)

    # Step 2: Survey compliance
    survey_report = check_questions(transcript)

    # Step 3: Fraud detection
    fraud_risk = detect_fraud(transcript)
    agent_ratio = get_agent_ratio(transcript)

    # Step 4: LLM quality analysis
    llm_report = analyze_transcript(transcript)

    result = {
        "transcript": transcript,
        "survey_compliance": survey_report,
        "fraud_risk": fraud_risk,
        "agent_ratio": agent_ratio,
        "llm_analysis": llm_report
    }

    # Persist output
    os.makedirs("reports", exist_ok=True)
    with open("reports/output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    return result
