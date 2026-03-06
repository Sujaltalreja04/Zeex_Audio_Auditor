import json
import os

import streamlit as st

st.set_page_config(page_title="ZeeX AI Audio Auditor", page_icon="🎙️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #e8e8f0; }
.metric-card {
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px; padding: 1.4rem 1.6rem; backdrop-filter: blur(12px);
    transition: transform 0.2s, box-shadow 0.2s;
}
.metric-card:hover { transform: translateY(-4px); box-shadow: 0 8px 32px rgba(0,0,0,0.4); }
.badge-high   { background:#ff4b4b22; border:1px solid #ff4b4b; color:#ff4b4b; }
.badge-medium { background:#ffa50022; border:1px solid #ffa500; color:#ffa500; }
.badge-low    { background:#00c85322; border:1px solid #00c853; color:#00c853; }
.badge-unknown{ background:#80808022; border:1px solid #808080; color:#aaaaaa; }
.risk-badge {
    display:inline-block; padding:0.3rem 1rem; border-radius:999px;
    font-weight:600; font-size:1rem; letter-spacing:0.05em;
}
.section-header {
    font-size:1.1rem; font-weight:700; color:#a78bfa;
    text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.6rem;
}
.transcript-box {
    background:rgba(0,0,0,0.35); border:1px solid rgba(167,139,250,0.3);
    border-radius:12px; padding:1.2rem 1.4rem; font-size:0.9rem;
    line-height:1.7; max-height:260px; overflow-y:auto; white-space:pre-wrap;
}
.tag-asked  { background:#00c85322; border:1px solid #00c853; color:#00c853; }
.tag-missed { background:#ff4b4b22; border:1px solid #ff4b4b; color:#ff4b4b; }
.tag { display:inline-block; margin:3px 4px; padding:0.2rem 0.75rem; border-radius:999px; font-size:0.82rem; font-weight:600; }
section[data-testid="stFileUploadDropzone"] {
    background:rgba(255,255,255,0.04); border:2px dashed rgba(167,139,250,0.5); border-radius:16px;
}
div[data-testid="stMetricValue"] { color: #e8e8f0 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding:2rem 0 1rem;">
    <h1 style="font-size:2.8rem; font-weight:700;
               background:linear-gradient(90deg,#a78bfa,#60a5fa);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
        🎙️ ZeeX AI Audio Auditor
    </h1>
    <p style="color:#9ca3af; font-size:1.05rem; margin-top:-0.5rem;">
        Upload a survey call recording and get an instant AI-powered audit report.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    def _get_secret(key):
        try:
            return st.secrets[key]
        except Exception:
            return os.getenv(key, "")

    sarvam_ok     = bool(_get_secret("SARVAM_API_KEY"))
    openrouter_ok = bool(_get_secret("OPENROUTER_API_KEY"))

    st.markdown(f"**Sarvam API Key:** {'✅ Set' if sarvam_ok else '❌ Missing'}")
    st.markdown(f"**OpenRouter API Key:** {'✅ Set' if openrouter_ok else '❌ Missing'}")
    if not sarvam_ok or not openrouter_ok:
        st.error("⚠️ API keys missing! Add them in Streamlit Cloud → Settings → Secrets.")
    st.divider()
    st.markdown("### 📋 Required Survey Topics")
    for t in ["age", "location", "voting", "government satisfaction"]:
        st.markdown(f"- `{t}`")

keys_missing = not sarvam_ok or not openrouter_ok

uploaded = st.file_uploader(
    "Drop your survey call audio here",
    type=["wav", "mp3"],
    label_visibility="visible",
    disabled=keys_missing,
)

if keys_missing:
    st.warning("🔑 Add your API keys in **Streamlit Cloud → App settings → Secrets** before uploading.")


if uploaded:
    # Preserve original extension so MIME detection works
    _, ext    = os.path.splitext(uploaded.name)
    TEMP_PATH = f"temp_audio{ext.lower()}"

    with open(TEMP_PATH, "wb") as f:
        f.write(uploaded.read())

    with st.spinner("🔍 Running AI pipeline — transcribing & analysing…"):
        try:
            from pipeline.audio_pipeline import run_audit
            result = run_audit(TEMP_PATH)
        except Exception as e:
            st.error(f"Pipeline error: {e}")
            if os.path.exists(TEMP_PATH):
                os.remove(TEMP_PATH)
            st.stop()

    transcript    = result.get("transcript", "")
    survey        = result.get("survey_compliance", {})
    fraud_risk    = result.get("fraud_risk", "unknown")
    agent_ratio   = result.get("agent_ratio", 0.0)
    llm           = result.get("llm_analysis", {})

    compliance_score = survey.get("compliance_score", 0)
    asked            = survey.get("asked", [])
    missed           = survey.get("missed", [])

    lang                = llm.get("language_detected", "—")
    sentiment           = llm.get("respondent_sentiment", "—")
    quality_score       = llm.get("call_quality_score", "—")
    summary             = llm.get("summary", llm.get("raw_response", "—"))
    is_authentic        = llm.get("is_authentic", "—")
    authenticity_reason = llm.get("authenticity_reason", "")

    st.success("✅ Audit complete!")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Survey Compliance", f"{compliance_score}%")
        st.progress(compliance_score / 100)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        badge_cls = f"badge-{fraud_risk}"
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<span class="section-header">Fraud Risk</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="risk-badge {badge_cls}">{fraud_risk.upper()}</span>', unsafe_allow_html=True)
        st.caption(f"Agent talk ratio: {int(agent_ratio * 100)}%")
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Call Quality Score", f"{quality_score} / 100")
        if isinstance(quality_score, (int, float)):
            st.progress(int(quality_score) / 100)
        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Language Detected", lang)
        st.metric("Respondent Sentiment", sentiment.capitalize() if sentiment != "—" else "—")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ── Authenticity verdict banner ───────────────────────────────────────────
    if is_authentic == "Authentic":
        st.success(f"✅  **Survey Authenticity: AUTHENTIC** — {authenticity_reason}")
    else:
        st.error(f"🚨  **Survey Authenticity: NOT AUTHENTIC** — {authenticity_reason}")


    left, right = st.columns([3, 2])

    with left:
        st.markdown('<p class="section-header">📝 Transcript</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="transcript-box">{transcript or "No transcript available."}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="section-header">🤖 AI Summary</p>', unsafe_allow_html=True)
        st.info(summary)

    with right:
        st.markdown('<p class="section-header">📋 Survey Question Coverage</p>', unsafe_allow_html=True)
        asked_tags  = "".join(f'<span class="tag tag-asked">✔ {q}</span>'  for q in asked)
        missed_tags = "".join(f'<span class="tag tag-missed">✘ {q}</span>' for q in missed)
        st.markdown(f'<div style="margin-bottom:0.5rem">{asked_tags}{missed_tags}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="section-header">📊 Raw Audit Report (JSON)</p>', unsafe_allow_html=True)
        with st.expander("View full JSON output", expanded=False):
            st.json(result)

    st.divider()
    st.download_button(
        label="⬇️ Download Audit Report (JSON)",
        data=json.dumps(result, indent=4, ensure_ascii=False),
        file_name="zeex_audit_report.json",
        mime="application/json",
    )

    if os.path.exists(TEMP_PATH):
        os.remove(TEMP_PATH)

else:
    st.markdown("""
    <div style="text-align:center; padding:4rem 2rem;
                background:rgba(255,255,255,0.03);
                border:2px dashed rgba(167,139,250,0.3);
                border-radius:20px; margin-top:1rem;">
        <p style="font-size:3rem; margin:0">🎧</p>
        <p style="color:#9ca3af; font-size:1.1rem; margin-top:0.5rem;">
            Upload a <strong>.wav</strong> or <strong>.mp3</strong> survey call to begin.
        </p>
    </div>
    """, unsafe_allow_html=True)
