import streamlit as st
import os
import sys

# --- Environment Setup ---
import shutil

# Make local ffmpeg available if it exists (for local dev)
# On Streamlit Cloud, it will be in the system PATH via packages.txt
cwd = os.getcwd()
ffmpeg_local = os.path.join(cwd, "ffmpeg.exe")
if os.path.exists(ffmpeg_local) and cwd not in os.environ.get("PATH", ""):
    os.environ["PATH"] = cwd + os.pathsep + os.environ.get("PATH", "")

# Verify ffmpeg availability
def check_ffmpeg():
    return shutil.which("ffmpeg") is not None

import json
import pandas as pd
import streamlit.components.v1 as components
from datetime import datetime
from dotenv import load_dotenv

load_dotenv() # Load local .env if it exists

# Import our modules
from pipeline.whisper_service import process_audio
from pipeline.audit_logic import extract_and_verify
from pipeline.sarvam_asr import speech_to_text
from pipeline.llm_audit import extract_and_verify_llm
from database import get_db, SurveyRecord

st.set_page_config(
    page_title="ZeeX AI Audio Auditor",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern UI
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif !important; }
.stApp { background: #07071a; color: #e2e8f0; min-height: 100vh; }
.stApp::before {
    content: ''; position: fixed; inset: 0;
    background: radial-gradient(ellipse 80% 50% at 20% 10%, rgba(139,92,246,0.18) 0%, transparent 60%),
                radial-gradient(ellipse 60% 40% at 80% 80%, rgba(59,130,246,0.15) 0%, transparent 60%);
    pointer-events: none; z-index: 0;
}
.hero-title {
    font-size: clamp(2rem, 5vw, 3.5rem); font-weight: 900; line-height: 1.1;
    background: linear-gradient(135deg, #a78bfa 0%, #60a5fa 40%, #f472b6 80%, #a78bfa 100%);
    background-size: 200% 200%; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: gradientShift 4s ease infinite; letter-spacing: -0.02em; text-align: center;
}
@keyframes gradientShift { 0% {background-position: 0% 50%;} 50% {background-position: 100% 50%;} 100% {background-position: 0% 50%;} }
.hero-sub { color: #94a3b8; font-size: 1.05rem; text-align: center; margin-top: 0.5rem; }
.glass-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 1.5rem; backdrop-filter: blur(16px); }
.score-match { color: #00c853; font-weight: bold; }
.score-mismatch { color: #ff4b4b; font-weight: bold; }
.score-missing { color: #facc15; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def show_confetti():
    components.html(
        """
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
        <script>
            var duration = 3 * 1000;
            var animationEnd = Date.now() + duration;
            var defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };
            function randomInRange(min, max) { return Math.random() * (max - min) + min; }
            var interval = setInterval(function() {
                var timeLeft = animationEnd - Date.now();
                if (timeLeft <= 0) { return clearInterval(interval); }
                var particleCount = 50 * (timeLeft / duration);
                confetti(Object.assign({}, defaults, { particleCount, origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 } }));
                confetti(Object.assign({}, defaults, { particleCount, origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 } }));
            }, 250);
        </script>
        """,
        height=0,
        width=0,
    )

st.markdown('<div class="hero-title">🎙️ AI Audio Survey Auditor</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Upload audio + Survey data to instantly verify authenticity via faster-whisper.</div>', unsafe_allow_html=True)

# Pre-flight checks
errors = []
if not check_ffmpeg():
    errors.append("❌ `ffmpeg` not found. Please ensure it is installed and in your PATH.")
from config.settings import OPENROUTER_API_KEY
if not OPENROUTER_API_KEY:
    errors.append("❌ `OPENROUTER_API_KEY` is not set. Please add it to your secrets or .env file.")

if errors:
    for err in errors:
        st.error(err)
    if not check_ffmpeg():
        st.info("💡 On Streamlit Cloud, ensure you have a `packages.txt` file with `ffmpeg` listed.")
    st.stop()

st.markdown("<br>", unsafe_allow_html=True)

tab_collect, tab_results, tab_history = st.tabs(["📝 Intake & Audit", "📊 Audit Results", "🗄️ History Database"])

if "current_audit" not in st.session_state:
    st.session_state["current_audit"] = None

# ---- INTAKE ----
with tab_collect:
    st.markdown("### 1. Survey Data Form")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            form_name = st.text_input("Full Name")
            form_age = st.text_input("Age")
            form_prof = st.text_input("Profession (e.g. Student, Business)")
        with col2:
            form_edu = st.text_input("Education Level (e.g. 10th, Graduate)")
            form_dist = st.text_input("District / Location")
            
    st.markdown("### 2. Audio Evidence")
    uploaded = st.file_uploader("Upload Survey Audio (.wav, .mp3, .m4a)", type=["wav", "mp3", "m4a"])
    
    if st.button("🚀 Run Full Audit", use_container_width=True, type="primary"):
        if not uploaded:
            st.error("Please upload an audio file.")
        else:
            with st.spinner("⚡ Processing audio via Whisper & auditing via OpenRouter LLM..."):
                os.makedirs("temp_dir", exist_ok=True)
                temp_path = os.path.join("temp_dir", uploaded.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded.read())
                
                try:
                    # 1. Process Audio with Whisper for accurate word timestamps
                    audio_data = process_audio(temp_path)
                    transcript = audio_data["transcript"]
                    segments_list = audio_data.get("segments", [])
                    
                    # 2. Extract & Verify with OpenRouter (pass segments for accurate timestamps)
                    form_data = {
                        "Name": form_name, "Age": form_age, "Profession": form_prof,
                        "Education": form_edu, "District": form_dist
                    }
                    audit_res = extract_and_verify_llm(form_data, transcript, segments_list)
                    
                    # Consolidate language detection
                    whisper_lang = audio_data.get("language", "Unknown")
                    llm_lang = audit_res.get("language", "Unknown")
                    
                    final_lang = whisper_lang
                    if final_lang.lower() == "unknown" and llm_lang.lower() != "unknown":
                        final_lang = llm_lang
                    
                    audit_res["detected_language"] = final_lang
                    
                    # 3. Save to DB
                    db = next(get_db())
                    record = SurveyRecord(
                        name=form_name, age=form_age, profession=form_prof,
                        education=form_edu, district=form_dist,
                        transcript=transcript,
                        result_json=json.dumps(audit_res),
                        verdict=audit_res.get("verdict", "Missing Data")
                    )
                    db.add(record)
                    db.commit()
                    db.refresh(record)
                    
                    st.session_state["current_audit"] = {
                        "transcript": transcript,
                        "words": [],
                        "audit": audit_res,
                        "audio_bytes": uploaded.getvalue(),
                        "audio_mime": uploaded.type,
                        "language": final_lang
                    }
                    st.success("Audit completed! Go to the 'Audit Results' tab.")
                    
                    if audit_res.get("verdict", "Missing Data") == "Match":
                        show_confetti()
                        
                except Exception as e:
                    st.error(f"Error during processing: {e}")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

# ---- RESULTS ----
with tab_results:
    if st.session_state["current_audit"] is None:
        st.info("Run an audit first to see results.")
    else:
        res = st.session_state["current_audit"]
        audit = res["audit"]
        verdict = audit.get("verdict", "Error")
        
        st.markdown(f"### Final Verdict: <span style='color:{'#00c853' if verdict=='Match' else '#ff4b4b' if verdict=='Mismatch' else '#facc15'}'>{verdict}</span>", unsafe_allow_html=True)
        
        # Display Language
        lang_source = audit.get("detected_language") or res.get("language") or "Unknown"
        lang = lang_source.upper()
        st.markdown(f"**Detected Language:** `{lang}`")
        
        st.markdown("### Scorecard Breakdown")
        cols = st.columns(5)
        details = audit["details"]
        
        for col, (k, v) in zip(cols, details.items()):
            status = v['status']
            color = "#00c853" if status == "Match" else "#ff4b4b" if status == "Mismatch" else "#facc15"
            with col:
                st.markdown(f"""
                <div class="glass-card" style="text-align:center; padding:1rem;">
                    <div style="font-size:0.9rem; color:#94a3b8;">{k}</div>
                    <div style="font-size:1.2rem; font-weight:bold; color:{color};">{status}</div>
                    <div style="font-size:0.8rem; color:#64748b; margin-top:0.4rem;">
                        {"⏱️ " + str(v['timestamp']) + "s" if v['timestamp'] else "Not Found"}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
        st.markdown("---")
        st.markdown("### Conversation Breakdown")
        
        # Build a custom HTML5 audio player with JS for precise timestamp playback
        if "audio_bytes" in res:
            import base64
            audio_b64 = base64.b64encode(res["audio_bytes"]).decode("utf-8")
            audio_mime = res.get("audio_mime", "audio/mp3")
            
            # Build conversation HTML with play buttons
            conversation = audit.get("conversation", [])
            convo_html = ""
            for i, msg in enumerate(conversation):
                speaker = msg.get("speaker", "Unknown")
                text = msg.get("text", "")
                timestamp = msg.get("timestamp", "")
                
                # Parse start-end
                start_sec = 0
                end_sec = 0
                if timestamp and "-" in str(timestamp):
                    try:
                        parts = str(timestamp).replace("s","").split("-")
                        start_sec = float(parts[0])
                        end_sec = float(parts[1])
                    except:
                        pass
                
                # Format display time
                def fmt_time(s):
                    m = int(s) // 60
                    sec = s - m * 60
                    return f"{m}:{sec:04.1f}"
                
                time_display = f"{fmt_time(start_sec)} → {fmt_time(end_sec)}" if timestamp else ""
                
                is_suryeior = speaker.lower() in ["suryeior", "agent"]
                speaker_label = "Suryeior" if is_suryeior else "Respondent"
                bg = "rgba(139,92,246,0.15)" if is_suryeior else "rgba(59,130,246,0.1)"
                avatar = "🤖" if is_suryeior else "🗣️"
                border_color = "rgba(139,92,246,0.3)" if is_suryeior else "rgba(59,130,246,0.2)"
                
                convo_html += f"""
                <div style="background:{bg}; border:1px solid {border_color}; border-radius:12px; padding:12px 16px; margin-bottom:10px;">
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                        <span style="font-size:1.3rem;">{avatar}</span>
                        <span style="font-weight:700; color:{'#a78bfa' if is_suryeior else '#60a5fa'};">{speaker_label}</span>
                        <span style="font-size:0.75rem; background:rgba(0,0,0,0.3); color:#94a3b8; padding:2px 8px; border-radius:6px; font-family:monospace;">⏱ {time_display}</span>
                    </div>
                    <div style="color:#e2e8f0; margin-left:36px; line-height:1.5;">{text}</div>
                    <div style="margin-left:36px; margin-top:8px;">
                        <button onclick="playSegment({start_sec}, {end_sec})" style="background:linear-gradient(135deg,#7c3aed,#3b82f6); color:white; border:none; padding:5px 14px; border-radius:8px; cursor:pointer; font-size:0.8rem; font-weight:600;">
                            ▶ Play {time_display}
                        </button>
                    </div>
                </div>
                """
            
            # Full HTML component with audio element + JS
            full_html = f"""
            <div style="margin-bottom:16px;">
                <audio id="auditAudioPlayer" controls style="width:100%; border-radius:8px;">
                    <source src="data:{audio_mime};base64,{audio_b64}" type="{audio_mime}">
                </audio>
            </div>
            {convo_html}
            <script>
                var stopTimer = null;
                function playSegment(startSec, endSec) {{
                    var audio = document.getElementById('auditAudioPlayer');
                    if (!audio) return;
                    if (stopTimer) clearTimeout(stopTimer);
                    
                    // Add 0.3s buffer at start and end for better context
                    var paddedStart = Math.max(0, startSec - 0.3);
                    var paddedEnd = endSec + 0.3;
                    
                    audio.currentTime = paddedStart;
                    audio.play();
                    
                    var duration = (paddedEnd - paddedStart) * 1000;
                    if (duration > 0) {{
                        stopTimer = setTimeout(function() {{
                            audio.pause();
                        }}, duration);
                    }}
                }}
            </script>
            """
            
            # Calculate height based on number of conversation items
            height = 120 + len(conversation) * 130
            components.html(full_html, height=height, scrolling=True)
        else:
            conversation = audit.get("conversation", [])
            if conversation:
                for i, msg in enumerate(conversation):
                    speaker = msg.get("speaker", "Unknown")
                    text = msg.get("text", "")
                    timestamp = msg.get("timestamp", "")
                    time_badge = f" `[{timestamp}]`" if timestamp else ""
                    if speaker.lower() in ["suryeior", "agent"]:
                        with st.chat_message("user", avatar="🤖"):
                            st.markdown(f"**Suryeior{time_badge}:** {text}")
                    else:
                        with st.chat_message("assistant", avatar="🗣️"):
                            st.markdown(f"**Respondent{time_badge}:** {text}")
            else:
                st.info("No speaker breakdown available.")

        st.markdown("---")
        st.markdown("### Raw Translated Transcript")
        st.markdown(f"""
        <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.1); border-radius:10px; padding:1.2rem; max-height:200px; overflow-y:auto; font-family:monospace; line-height:1.6;">
        {res['transcript']}
        </div>
        """, unsafe_allow_html=True)

# ---- HISTORY ----
with tab_history:
    st.markdown("### Audit History DB")
    
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🗑️ Clear Database"):
            db = next(get_db())
            db.query(SurveyRecord).delete()
            db.commit()
            st.success("Database cleared.")
            st.rerun()
            
    db = next(get_db())
    records = db.query(SurveyRecord).order_by(SurveyRecord.created_at.desc()).all()
    
    if not records:
        st.info("No records in database.")
    else:
        data = []
        for r in records:
                try:
                    res_j = json.loads(r.result_json)
                    # Try various possible keys for language
                    lang_source = res_j.get("detected_language") or res_j.get("language") or "UNKNOWN"
                    lang = str(lang_source).upper()
                except:
                    lang = "UNKNOWN"
                    
                data.append({
                    "ID": r.id,
                    "Date": r.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "Name": r.name,
                    "Language": lang,
                    "Verdict": r.verdict,
                })
        st.dataframe(pd.DataFrame(data), use_container_width=True)
        
        st.markdown("#### View/Delete specific record")
        cols2 = st.columns(2)
        with cols2[0]:
            view_id = st.number_input("View Record ID", min_value=1, step=1)
            if st.button("View Details"):
                r_to_view = db.query(SurveyRecord).filter(SurveyRecord.id == view_id).first()
                if r_to_view:
                    try:
                        audit_data = json.loads(r_to_view.result_json)
                        st.markdown(f"**Verdict:** {r_to_view.verdict}")
                        
                        st.markdown("**Conversation Breakdown**")
                        conversation = audit_data.get("conversation", [])
                        if conversation:
                            for msg in conversation:
                                speaker = msg.get("speaker", "Unknown")
                                text = msg.get("text", "")
                                timestamp = msg.get("timestamp", "")
                                time_badge = f" `[{timestamp}]`" if timestamp else ""
                                if speaker.lower() in ["suryeior", "agent"]:
                                    with st.chat_message("user", avatar="🤖"):
                                        st.markdown(f"**Suryeior{time_badge}:** {text}")
                                else:
                                    with st.chat_message("assistant", avatar="🗣️"):
                                        st.markdown(f"**Respondent{time_badge}:** {text}")
                        else:
                            st.info("No speaker breakdown available for this record.")
                    except:
                        st.error("Could not parse result JSON for this record.")
                else:
                    st.error("Record not found.")

        with cols2[1]:
            del_id = st.number_input("Delete Record ID", min_value=1, step=1)
            if st.button("Delete Record"):
                r_to_del = db.query(SurveyRecord).filter(SurveyRecord.id == del_id).first()
                if r_to_del:
                    db.delete(r_to_del)
                    db.commit()
                    st.success(f"Record {del_id} deleted.")
                    st.rerun()
                else:
                    st.error("Record not found.")
