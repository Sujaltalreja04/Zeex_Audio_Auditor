# 🎙️ ZeeX AI Audio Auditor

An AI-powered survey call audit tool that transcribes audio, checks survey compliance, detects potential fraud, and generates a quality report using LLMs.

---

## 🗂️ Project Structure

```
zeex-ai-audio-audit/
├── app.py                     # Streamlit dashboard
├── pipeline/
│   ├── audio_pipeline.py      # Orchestrates the full pipeline
│   ├── sarvam_asr.py          # Sarvam AI Speech-to-Text
│   ├── llm_analyzer.py        # OpenRouter LLM analysis
│   ├── fraud_detector.py      # Talk-ratio fraud detection
│   └── survey_checker.py      # Survey question verification
├── prompts/
│   └── audit_prompt.txt       # LLM prompt template
├── config/
│   └── settings.py            # API key configuration
├── sample_audio/              # Place test .wav / .mp3 files here
├── reports/
│   └── output.json            # Last audit output (auto-generated)
├── .env.example               # API key template
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API keys

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

```env
SARVAM_API_KEY=your_sarvam_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

> Get your **Sarvam AI** key at [sarvam.ai](https://sarvam.ai)  
> Get your **OpenRouter** key at [openrouter.ai](https://openrouter.ai)

### 3. Load environment variables

Streamlit will pick up `.env` automatically if you use `python-dotenv`. Alternatively:

```powershell
# Windows PowerShell
$env:SARVAM_API_KEY="your_key"
$env:OPENROUTER_API_KEY="your_key"
```

---

## 🚀 Run the Dashboard

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📊 What the Audit Produces

| Field                  | Description                                           |
|------------------------|-------------------------------------------------------|
| **Transcript**         | Full speech-to-text transcription via Sarvam AI       |
| **Survey Compliance**  | % of required questions asked (age, location, voting, govt. satisfaction) |
| **Fraud Risk**         | `low` / `medium` / `high` based on agent talk ratio   |
| **Agent Talk Ratio**   | % of lines attributed to the agent                    |
| **Language Detected**  | Primary language in the call                          |
| **Respondent Sentiment** | `positive` / `neutral` / `negative`                |
| **Call Quality Score** | 0–100 score from the LLM                             |
| **AI Summary**         | One-paragraph call summary                            |

---

## 🔧 LLM Model

Default: `meta-llama/llama-3.2-11b-vision-instruct` via OpenRouter.  
Change in `config/settings.py`:

```python
OPENROUTER_MODEL = "meta-llama/llama-3.2-11b-vision-instruct"
```

---

## 🗺️ Roadmap (Advanced Features)

- [ ] Speaker Diarization (who spoke when)
- [ ] Emotion Detection from Voice
- [ ] Vector database search for similar calls
- [ ] Real-time call auditing via microphone stream
- [ ] Batch processing of multiple call recordings
