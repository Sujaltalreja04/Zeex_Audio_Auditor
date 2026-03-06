def detect_fraud(transcript: str) -> str:
    """
    Detects potential fraud based on agent-to-respondent talk ratio.

    The heuristic counts lines attributed to "agent" vs "respondent"
    in the transcript. A very high agent ratio suggests the agent may
    be doing the talking for the respondent (fraudulent behaviour).

    Args:
        transcript: Full call transcript as a string.

    Returns:
        Risk level string: "high", "medium", "low", or "unknown".
    """
    lines = transcript.split("\n")

    agent_lines = [line for line in lines if "agent" in line.lower()]
    respondent_lines = [line for line in lines if "respondent" in line.lower()]

    total = len(agent_lines) + len(respondent_lines)

    if total == 0:
        return "unknown"

    agent_ratio = len(agent_lines) / total

    if agent_ratio > 0.8:
        return "high"

    if agent_ratio > 0.6:
        return "medium"

    return "low"


def get_agent_ratio(transcript: str) -> float:
    """
    Returns the agent talk ratio as a float between 0 and 1.

    Useful for displaying the raw statistic in the dashboard.
    """
    lines = transcript.split("\n")
    agent_lines = [line for line in lines if "agent" in line.lower()]
    respondent_lines = [line for line in lines if "respondent" in line.lower()]
    total = len(agent_lines) + len(respondent_lines)

    if total == 0:
        return 0.0

    return round(len(agent_lines) / total, 2)
