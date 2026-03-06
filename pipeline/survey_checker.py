REQUIRED_QUESTIONS = [
    "age",
    "location",
    "voting",
    "government satisfaction"
]


def check_questions(transcript: str) -> dict:
    """
    Checks whether required survey questions were covered in the transcript.

    Args:
        transcript: Full call transcript as a string.

    Returns:
        Dictionary with asked questions, missed questions, and compliance score.
    """
    transcript_lower = transcript.lower()

    asked = []
    missed = []

    for question in REQUIRED_QUESTIONS:
        if question in transcript_lower:
            asked.append(question)
        else:
            missed.append(question)

    compliance_score = int((len(asked) / len(REQUIRED_QUESTIONS)) * 100)

    return {
        "asked": asked,
        "missed": missed,
        "compliance_score": compliance_score
    }
