import os
import streamlit as st


def _get_secret(key: str) -> str:
    """
    Read a secret from Streamlit secrets (works on Streamlit Cloud)
    with a fallback to environment variables (works locally with .env).
    """
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.getenv(key, "")


SARVAM_API_KEY     = _get_secret("SARVAM_API_KEY")
OPENROUTER_API_KEY = _get_secret("OPENROUTER_API_KEY")
OPENROUTER_MODEL   = "nvidia/nemotron-3-nano-30b-a3b:free"
