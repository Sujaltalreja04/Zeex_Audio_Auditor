import os
from faster_whisper import WhisperModel

# More comprehensive map for language codes if needed, 
# although WhisperModel.transcribe already returns info with language names/codes.
LANG_MAP = {
    "en": "English", "hi": "Hindi", "mr": "Marathi", "ta": "Tamil", 
    "te": "Telugu", "kn": "Kannada", "ml": "Malayalam", "gu": "Gujarati",
    "pa": "Punjabi", "bn": "Bengali", "as": "Assamese", "or": "Odia"
}

def process_audio(audio_path):
    # Load Faster-Whisper model - base is lightweight
    # Use CPU by default, int8 for speed
    model = WhisperModel("base", device="cpu", compute_type="int8")

    # Transcribe and translate to English with word-level timestamps
    # faster-whisper returns an iterator for segments and an info object
    segments_gen, info = model.transcribe(
        audio_path, 
        task="translate", 
        word_timestamps=True,
        beam_size=5
    )
    
    # Log the detected language info to console
    print(f"--- WHISPER DEBUG: Detected language: {info.language} with probability {info.language_probability:.4f}")
    
    segments_list = list(segments_gen) # Exhaust the generator
    
    transcript = ""
    words_data = []
    segments_data = []
    
    for segment in segments_list:
        segment_text = segment.text.strip()
        start = round(segment.start, 1)
        end = round(segment.end, 1)
        
        transcript += f"[{start}s - {end}s] {segment_text}\n"
        
        segments_data.append({
            "start": start,
            "end": end,
            "text": segment_text
        })
        
        # Extract word-level timestamps
        if segment.words:
            for word_info in segment.words:
                words_data.append({
                    "word": word_info.word.strip(),
                    "start": round(word_info.start, 2),
                    "end": round(word_info.end, 2)
                })

    # Get the language. info.language is the code (e.g. 'hi')
    lang_code = info.language
    
    # Try to get the language name. 
    # faster-whisper doesn't have a direct code-to-name dict like openai-whisper usually does 
    # in some installations, but info.language is usually correct.
    full_language = LANG_MAP.get(lang_code, lang_code.upper() if lang_code else "Unknown").title()

    return {
        "transcript": transcript.strip(),
        "words": words_data,
        "segments": segments_data,
        "language": full_language
    }

