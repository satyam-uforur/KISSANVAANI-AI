import streamlit as st
import requests
import tempfile
import os
from streamlit_mic_recorder import mic_recorder

# === Backend URL ===
BACKEND_URL = "http://localhost:8000/ask"

st.set_page_config(page_title="🎙️ Hinglish Voice QA", layout="centered")
st.title("🎙️ Hinglish Voice Q&A Assistant")

tab1, tab2 = st.tabs(["🎧 Record Voice", "📂 Upload Audio"])


def process_audio(file_path):
    """Send audio to FastAPI backend and handle both text + audio response."""
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "audio/opus")}
        response = requests.post(BACKEND_URL, files=files)

    if response.status_code != 200:
        st.error("❌ API request failed.")
        st.text(response.text)
        return

    data = response.json()
    st.subheader("🧠 Hinglish Text")
    st.write(data.get("query_text", "❌ No text received."))

    # Show answers
    answers = data.get("answers", [])
    if isinstance(answers, list) and len(answers) > 0:
        st.subheader("🔍 Top Answers")
        for i, ans in enumerate(answers, 1):
            st.markdown(f"**{i}.** {ans}")
    else:
        st.warning("⚠️ No valid answers returned.")

   

    # ✅ Static local example audio
    local_audio_path = os.path.join(os.getcwd(), "answer_1.mp3")
    local_audio_path1 = os.path.join(os.getcwd(), "answer_2.mp3")
    local_audio_path2 = os.path.join(os.getcwd(), "answer_3.mp3")
    if os.path.exists(local_audio_path):
        st.subheader("🎧Audio of answers")
        st.audio(local_audio_path, format="audio/mp3")
        st.audio(local_audio_path1, format="audio/mp3")
        st.audio(local_audio_path2, format="audio/mp3")
    else:
        st.warning("⚠️ 'answer.mp3' not found in working directory.")


# === 🎤 Record directly from browser ===
with tab1:
    st.write("🎙️ Click record, ask your question, then stop.")
    audio_data = mic_recorder(
        start_prompt="🎙️ Start Recording",
        stop_prompt="🛑 Stop Recording",
        use_container_width=True,
        just_once=False,
        key="mic"
    )

    if audio_data and "bytes" in audio_data:
        st.success("✅ Audio recorded successfully!")

        # Save recording
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(audio_data["bytes"])
            file_path = tmp.name

        st.audio(file_path, format="audio/webm")

        if st.button("🚀 Ask My Question"):
            process_audio(file_path)


# === 📂 Upload pre-recorded audio ===
with tab2:
    file = st.file_uploader(
        "📂 Upload your question audio (WAV, OPUS, WEBM, MP3)",
        type=["wav", "opus", "webm", "mp3"]
    )
    if file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.name.split('.')[-1]}") as tmp:
            tmp.write(file.read())
            file_path = tmp.name

        st.audio(file_path)

        if st.button("🚀 Ask My Question", key="upload_btn"):
            process_audio(file_path)
