import os
import json
import tempfile
import subprocess
import whisper
from gtts import gTTS
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate


# --- Load Whisper Hindi Model ---
MODEL_PATH = os.path.join(os.getcwd(), "whisper_model")

if not os.path.exists(MODEL_PATH):
    os.makedirs(MODEL_PATH, exist_ok=True)

print("✅ Loading Whisper model...")
whisper_model = whisper.load_model("base", download_root=MODEL_PATH)
print("✅ Model loaded successfully!")


# --- Convert Any Audio (opus/webm/mp3/wav) → WAV Mono 16 kHz ---
def convert_to_wav_mono(audio_path: str) -> str:
    """Converts any audio format (opus, webm, mp3, wav, etc.) to WAV mono PCM 16 kHz."""
    try:
        tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        command = [
            "ffmpeg", "-y", "-i", audio_path,
            "-ac", "1", "-ar", "16000", "-f", "wav", tmp_wav
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return tmp_wav
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"❌ ffmpeg failed to convert {audio_path}: {e.stderr.decode('utf-8', errors='ignore')}")


# --- Speech → Text (Hindi → Hinglish) ---
def transcribe_hinglish(audio_path: str) -> str:
    """Transcribe an audio file to text in Hinglish (Romanized Hindi)."""
    wav_path = convert_to_wav_mono(audio_path)

    print(f"🎧 Transcribing '{audio_path}' ...")
    result = whisper_model.transcribe(wav_path, language="hi")
    os.remove(wav_path)

    text_result = result.get("text", "").strip()

    if not text_result:
        return ""

    # ✅ Convert Hindi (Devanagari) → Hinglish (ITRANS)
    try:
        hinglish_text = transliterate(text_result, sanscript.DEVANAGARI, sanscript.ITRANS)
        return hinglish_text
    except Exception as e:
        print(f"⚠️ Transliteration error: {e}")
        return text_result  # fallback


# --- Text → Speech (Hindi) ---
def text_to_speech(text, filename="output.mp3"):
    """Convert Hindi text to speech and save as MP3."""
    if not text.strip():
        print("❌ Error in TTS: No text to speak")
        return None

    try:
        tts = gTTS(text=text, lang="hi")
        tts.save(filename)
        print(f"✅ Speech saved: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error in TTS: {e}")
        return None
