import json
import os
import streamlit as st

st.set_page_config(
    page_title="ZeeX AI Audio Auditor",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Premium CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
}

/* ── Background ── */
.stApp {
    background: #07071a;
    color: #e2e8f0;
    min-height: 100vh;
}

/* Animated star-field gradient */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 50% at 20% 10%, rgba(139,92,246,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(59,130,246,0.15) 0%, transparent 60%),
        radial-gradient(ellipse 40% 30% at 60% 30%, rgba(236,72,153,0.10) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem !important; position: relative; z-index: 1; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(15, 15, 40, 0.95) !important;
    border-right: 1px solid rgba(139,92,246,0.2) !important;
    backdrop-filter: blur(20px);
}
[data-testid="stSidebar"] .block-container { padding: 2rem 1.5rem !important; }

/* ── Animated header title ── */
.hero-title {
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 900;
    line-height: 1.1;
    background: linear-gradient(135deg, #a78bfa 0%, #60a5fa 40%, #f472b6 80%, #a78bfa 100%);
    background-size: 200% 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradientShift 4s ease infinite;
    letter-spacing: -0.02em;
}
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.hero-sub {
    color: #94a3b8;
    font-size: 1.05rem;
    font-weight: 400;
    margin-top: 0.6rem;
    letter-spacing: 0.01em;
}

/* ── Glowing divider ── */
.glow-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(139,92,246,0.6), rgba(96,165,250,0.6), transparent);
    margin: 1.5rem 0;
    border: none;
}

/* ── Glass metric cards ── */
.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 1.4rem 1.6rem;
    backdrop-filter: blur(16px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
.glass-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
}
.glass-card:hover {
    transform: translateY(-4px);
    border-color: rgba(139,92,246,0.35);
    box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 0 1px rgba(139,92,246,0.1);
}

.card-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #64748b;
    margin-bottom: 0.5rem;
}
.card-value {
    font-size: 1.9rem;
    font-weight: 800;
    color: #f1f5f9;
    line-height: 1;
}
.card-sub {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 0.4rem;
}

/* ── Progress bar ── */
.prog-track {
    height: 6px;
    background: rgba(255,255,255,0.06);
    border-radius: 99px;
    margin-top: 0.8rem;
    overflow: hidden;
}
.prog-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 1s ease;
}

/* ── Risk badge ── */
.risk-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 1rem;
    border-radius: 99px;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* ── Authenticity banner ── */
.auth-banner {
    border-radius: 18px;
    padding: 1.4rem 1.8rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    margin: 1.2rem 0;
    border: 1.5px solid;
    position: relative;
    overflow: hidden;
}
.auth-banner::before {
    content: '';
    position: absolute;
    inset: 0;
    opacity: 0.06;
    background: linear-gradient(135deg, currentColor, transparent);
}
.auth-icon  { font-size: 2.2rem; line-height: 1; flex-shrink: 0; }
.auth-label-sm { font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; color: #64748b; }
.auth-label-lg { font-size: 1.5rem; font-weight: 800; line-height: 1.2; }
.auth-reason   { font-size: 0.85rem; color: #94a3b8; margin-top: 0.25rem; }

/* ── Section header ── */
.section-hdr {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #7c3aed;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* ── Transcript box ── */
.transcript-scroll {
    background: rgba(0,0,0,0.4);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    font-size: 0.88rem;
    line-height: 1.75;
    max-height: 260px;
    overflow-y: auto;
    white-space: pre-wrap;
    color: #cbd5e1;
    font-family: 'Inter', monospace;
}
.transcript-scroll::-webkit-scrollbar { width: 4px; }
.transcript-scroll::-webkit-scrollbar-track { background: transparent; }
.transcript-scroll::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.4); border-radius: 99px; }

/* ── Compliance tags ── */
.tag {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.3rem 0.85rem;
    border-radius: 99px;
    font-size: 0.78rem;
    font-weight: 600;
    margin: 3px 4px;
    border: 1px solid;
}
.tag-yes { background: rgba(0,200,83,0.1);  border-color: #00c853; color: #00c853; }
.tag-no  { background: rgba(255,75,75,0.1); border-color: #ff4b4b; color: #ff4b4b; }

/* ── Upload dropzone ── */
section[data-testid="stFileUploadDropzone"] {
    background: rgba(139,92,246,0.05) !important;
    border: 2px dashed rgba(139,92,246,0.4) !important;
    border-radius: 18px !important;
    transition: all 0.2s ease;
}
section[data-testid="stFileUploadDropzone"]:hover {
    border-color: rgba(139,92,246,0.8) !important;
    background: rgba(139,92,246,0.08) !important;
}

/* ── Success/error overrides ── */
div[data-testid="stMetricValue"] { color: #f1f5f9 !important; }
[data-testid="stAlert"] { border-radius: 14px !important; }

/* ── Download button ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #7c3aed, #3b82f6) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.7rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.4) !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(124,58,237,0.6) !important;
}

/* ── Spinner ── */
.stSpinner { color: #a78bfa !important; }

/* ── Sidebar items ── */
.sidebar-status {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 0.6rem 0.9rem;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: read secret ───────────────────────────────────────────────────────
def _get_secret(key: str) -> str:
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, "")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <p style="font-size:1.1rem; font-weight:800; color:#a78bfa; margin:0;">🎙️ ZeeX Auditor</p>
        <p style="font-size:0.78rem; color:#475569; margin:0.2rem 0 0;">AI-powered call audit platform</p>
    </div>
    """, unsafe_allow_html=True)

    sarvam_ok     = bool(_get_secret("SARVAM_API_KEY"))
    openrouter_ok = bool(_get_secret("OPENROUTER_API_KEY"))

    st.markdown(f"""
    <div class="sidebar-status">
        <span style="color:#94a3b8;">Sarvam ASR</span>
        <span>{"✅" if sarvam_ok else "❌"}</span>
    </div>
    <div class="sidebar-status">
        <span style="color:#94a3b8;">OpenRouter LLM</span>
        <span>{"✅" if openrouter_ok else "❌"}</span>
    </div>
    """, unsafe_allow_html=True)

    if not sarvam_ok or not openrouter_ok:
        st.error("API keys missing. Add them in **Streamlit Cloud → Settings → Secrets**.")

    st.markdown('<hr class="glow-divider">', unsafe_allow_html=True)
    st.markdown("""
    <p style="font-size:0.72rem; font-weight:700; text-transform:uppercase;
              letter-spacing:0.12em; color:#7c3aed; margin-bottom:0.6rem;">
        📋 Required Topics
    </p>
    """, unsafe_allow_html=True)

    for topic in ["Age", "Location", "Voting", "Government Satisfaction"]:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.35rem;
                    font-size:0.83rem; color:#94a3b8;">
            <span style="color:#7c3aed;">▸</span> {topic}
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="glow-divider">', unsafe_allow_html=True)
    st.markdown("""
    <p style="font-size:0.75rem; color:#334155; text-align:center;">
        Powered by Sarvam AI + OpenRouter
    </p>
    """, unsafe_allow_html=True)


# ── Hero header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 2.5rem 0 1.5rem;">
    <p class="hero-title">🎙️ ZeeX AI Audio Auditor</p>
    <p class="hero-sub">
        Upload a survey call recording · Get instant transcription, fraud detection & authenticity verdict
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

# ── Upload ────────────────────────────────────────────────────────────────────
keys_missing = not sarvam_ok or not openrouter_ok

uploaded = st.file_uploader(
    "Drop your survey call audio here (.wav or .mp3)",
    type=["wav", "mp3"],
    label_visibility="visible",
    disabled=keys_missing,
)

if keys_missing:
    st.markdown("""
    <div style="text-align:center; margin-top:0.8rem; padding:1rem;
                background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.3);
                border-radius:14px; color:#fca5a5; font-size:0.9rem;">
        🔑 Add API keys in <strong>Streamlit Cloud → App settings → Secrets</strong> to enable uploads.
    </div>
    """, unsafe_allow_html=True)

elif not uploaded:
    st.markdown("""
    <div style="text-align:center; padding:4rem 2rem; margin-top:1rem;
                background:rgba(139,92,246,0.04);
                border:2px dashed rgba(139,92,246,0.2);
                border-radius:24px;">
        <div style="font-size:3.5rem; margin-bottom:1rem;">🎧</div>
        <p style="font-size:1.1rem; font-weight:600; color:#e2e8f0; margin-bottom:0.4rem;">
            Ready to audit your survey call
        </p>
        <p style="color:#64748b; font-size:0.9rem;">
            Supports <strong>.wav</strong> and <strong>.mp3</strong> · Up to 200MB
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── Processing ────────────────────────────────────────────────────────────────
if uploaded:
    _, ext    = os.path.splitext(uploaded.name)
    TEMP_PATH = f"temp_audio{ext.lower()}"

    with open(TEMP_PATH, "wb") as f:
        f.write(uploaded.read())

    with st.spinner("⚡ Analysing call — transcribing, detecting fraud & running LLM…"):
        try:
            from pipeline.audio_pipeline import run_audit
            result = run_audit(TEMP_PATH)
        except Exception as e:
            st.error(f"Pipeline error: {e}")
            if os.path.exists(TEMP_PATH):
                os.remove(TEMP_PATH)
            st.stop()

    if os.path.exists(TEMP_PATH):
        os.remove(TEMP_PATH)

    transcript    = result.get("transcript", "")
    survey        = result.get("survey_compliance", {})
    fraud_risk    = result.get("fraud_risk", "unknown")
    agent_ratio   = result.get("agent_ratio", 0.0)
    llm           = result.get("llm_analysis", {})

    compliance    = survey.get("compliance_score", 0)
    asked         = survey.get("asked", [])
    missed        = survey.get("missed", [])

    lang          = llm.get("language_detected", "—")
    sentiment     = llm.get("respondent_sentiment", "—").capitalize()
    quality       = llm.get("call_quality_score", 0)
    summary       = llm.get("summary", llm.get("raw_response", "—"))
    is_authentic  = llm.get("is_authentic", "—")
    auth_reason   = llm.get("authenticity_reason", "")

    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

    # ── KPI cards ─────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)

    # Compliance card
    comp_color = "#00c853" if compliance >= 75 else "#ffa500" if compliance >= 50 else "#ff4b4b"
    with c1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-label">📋 Survey Compliance</div>
            <div class="card-value" style="color:{comp_color};">{compliance}%</div>
            <div class="prog-track">
                <div class="prog-fill" style="width:{compliance}%;
                     background:linear-gradient(90deg,{comp_color}88,{comp_color});"></div>
            </div>
            <div class="card-sub">{len(asked)} of {len(asked)+len(missed)} topics covered</div>
        </div>
        """, unsafe_allow_html=True)

    # Fraud risk card
    risk_cfg = {
        "high":    ("#ff4b4b", "🔴", "rgba(255,75,75,0.15)"),
        "medium":  ("#ffa500", "🟡", "rgba(255,165,0,0.15)"),
        "low":     ("#00c853", "🟢", "rgba(0,200,83,0.15)"),
        "unknown": ("#808080", "⚪", "rgba(128,128,128,0.15)"),
    }
    r_col, r_icon, r_bg = risk_cfg.get(fraud_risk, risk_cfg["unknown"])
    with c2:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-label">🕵️ Fraud Risk</div>
            <div style="display:flex; align-items:center; gap:0.6rem; margin-top:0.2rem;">
                <span class="risk-pill" style="background:{r_bg}; border:1px solid {r_col}; color:{r_col};">
                    {r_icon} {fraud_risk.upper()}
                </span>
            </div>
            <div class="prog-track">
                <div class="prog-fill" style="width:{int(agent_ratio*100)}%;
                     background:linear-gradient(90deg,{r_col}88,{r_col});"></div>
            </div>
            <div class="card-sub">Agent talk ratio: {int(agent_ratio*100)}%</div>
        </div>
        """, unsafe_allow_html=True)

    # Quality score card
    q_color = "#00c853" if quality >= 75 else "#ffa500" if quality >= 50 else "#ff4b4b"
    with c3:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-label">⭐ Call Quality</div>
            <div class="card-value" style="color:{q_color};">{quality}<span style="font-size:1rem;color:#64748b;">/100</span></div>
            <div class="prog-track">
                <div class="prog-fill" style="width:{quality}%;
                     background:linear-gradient(90deg,{q_color}88,{q_color});"></div>
            </div>
            <div class="card-sub">LLM quality assessment</div>
        </div>
        """, unsafe_allow_html=True)

    # Language & sentiment card
    sent_emoji = {"positive": "😊", "neutral": "😐", "negative": "😟"}.get(sentiment.lower(), "💬")
    with c4:
        st.markdown(f"""
        <div class="glass-card">
            <div class="card-label">🌐 Language & Sentiment</div>
            <div class="card-value" style="font-size:1.3rem; margin-top:0.1rem;">{lang}</div>
            <div style="margin-top:0.6rem; display:flex; align-items:center; gap:0.4rem;">
                <span style="font-size:1.2rem;">{sent_emoji}</span>
                <span style="font-size:0.9rem; color:#94a3b8;">{sentiment}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Authenticity banner ───────────────────────────────────────────────────
    if is_authentic == "Authentic":
        a_col, a_bg, a_icon, a_label = "#00c853", "rgba(0,200,83,0.08)", "✅", "AUTHENTIC"
    else:
        a_col, a_bg, a_icon, a_label = "#ff4b4b", "rgba(255,75,75,0.08)", "🚨", "NOT AUTHENTIC"

    st.markdown(f"""
    <div class="auth-banner" style="background:{a_bg}; border-color:{a_col}; color:{a_col};">
        <span class="auth-icon">{a_icon}</span>
        <div>
            <div class="auth-label-sm">Survey Authenticity Verdict</div>
            <div class="auth-label-lg" style="color:{a_col};">{a_label}</div>
            <div class="auth-reason">{auth_reason}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

    # ── Detail section ────────────────────────────────────────────────────────
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown('<div class="section-hdr">📝 Transcript</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="transcript-scroll">{transcript or "No transcript available."}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-hdr">🤖 AI Summary</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:rgba(139,92,246,0.07); border:1px solid rgba(139,92,246,0.2);
                    border-radius:14px; padding:1.1rem 1.3rem; font-size:0.9rem;
                    line-height:1.7; color:#cbd5e1;">
            {summary}
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-hdr">📋 Survey Question Coverage</div>', unsafe_allow_html=True)
        tags_html = ""
        from pipeline.survey_checker import REQUIRED_QUESTIONS
        for q in REQUIRED_QUESTIONS:
            if q in asked:
                tags_html += f'<span class="tag tag-yes">✔ {q.title()}</span>'
            else:
                tags_html += f'<span class="tag tag-no">✘ {q.title()}</span>'
        st.markdown(f'<div style="line-height:2.2;">{tags_html}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-hdr">📊 Raw Audit Data</div>', unsafe_allow_html=True)
        with st.expander("View full JSON", expanded=False):
            st.json(result)

    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

    # ── Download ──────────────────────────────────────────────────────────────
    col_dl, _ = st.columns([1, 3])
    with col_dl:
        st.download_button(
            label="⬇️ Download Audit Report",
            data=json.dumps(result, indent=4, ensure_ascii=False),
            file_name="zeex_audit_report.json",
            mime="application/json",
            use_container_width=True,
        )
