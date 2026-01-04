# 🌾 KissanVaani AI – Hindi / Hinglish Voice Farming Assistant

KissanVaani AI is an end‑to‑end **voice-based Question Answering system for Indian farmers**, supporting **Hindi + Hinglish**.  
Ask your farming questions by voice, get **Hinglish transcription**, **retrieved answers from Pinecone**, and **bilingual (English + Hindi) audio replies**.

Built with:

- 🎧 **OpenAI Whisper (local)** – Speech‑to‑Text  
- 🧠 **SentenceTransformers + Pinecone** – Semantic search  
- 🖥 **FastAPI** – Backend API  
- 🌐 **Streamlit** – Modern web UI  
- 🔊 **gTTS + googletrans** – Text‑to‑Speech in English and Hindi  


---

## 🚀 Features

- 🎙 **Voice Input**
  - Record from mic (browser) or upload audio (`.wav`, `.mp3`, `.webm`, `.opus`).
- 🧠 **Speech‑to‑Text with Whisper**
  - Uses Whisper **medium** model.
  - Forces transcription into **Roman script (“Hinglish”)** for easier downstream processing.
- 🔍 **Semantic Retrieval with Pinecone**
  - Converts text to embeddings (MiniLM).
  - Queries Pinecone index (`kissanai`) for top farming answers.
  - Supports simple **query expansion** (e.g., `seb` → `apple`).
- 💬 **Bilingual Answers**
  - Retrieves answer text (English).
  - Automatically translates to **Hindi** using `googletrans`.
- 🔊 **Audio Responses**
  - Generates **English + Hindi TTS** using `gTTS`.
  - Frontend plays the generated MP3 files directly.
- 🌐 **Modern UI**
  - Clean Streamlit app with **day / night theme**.
  - UI language: English / Hindi / Hinglish.
  - Hero section with dynamic greeting for farmers (IST time‑based).

---

## 🧱 Tech Stack

- **Backend**
  - FastAPI
  - Whisper (`medium` model)
  - SentenceTransformers (`all-MiniLM-L6-v2`)
  - Pinecone Vector Database
  - googletrans (EN → HI translation)
  - gTTS (Text → MP3)
  - indic‑transliteration (Hindi ↔ Hinglish normalization)

- **Frontend**
  - Streamlit
  - `streamlit-mic-recorder` for in‑browser audio recording

- **Infra / Tools**
  - FFmpeg (audio processing)
  - Python 3.9+  
  - (Optional) CUDA GPU for faster Whisper inference

---

## ⚙️ Installation Guide
###### must needed
### 1️⃣ Install FFmpeg
Required for audio conversion and processing.

#### 🪟 Windows
Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)  
Extract and add the `bin` path to **System Environment Variables**.

Verify:
```bash
ffmpeg -version
````

#### 🐧 Linux / 🍎 macOS

```bash
sudo apt install ffmpeg
# or
brew install ffmpeg
```

---

### 2️⃣ Create and Activate Virtual Environment

```bash
# Create venv
python -m venv kissanqa

# Activate
# Windows:
kissanqa\Scripts\activate

# macOS/Linux:
source kissanqa/bin/activate
```

---

### 3️⃣ Install Dependencies

Make sure pip is up to date:

```bash
pip install --upgrade pip
```

Then install all requirements:

```bash
pip install -r requirements.txt
```

If you don’t have one, create `requirements.txt`:

```txt
fastapi
uvicorn
git+https://github.com/openai/whisper.git
streamlit                     
streamlit-audiorecorder       
streamlit-javascript          
streamlit_mic_recorder 
soundfile
pydub
indic-transliteration
sentence-transformers
pinecone
gtts
python-dotenv
python-multipart
requests
```

---
#### NOTE GENERATE YOUR OWN VECTOR 
here is notebook = https://colab.research.google.com/drive/14nSt-UaBG3tcCwqdQHwijH0n96WF55-7?usp=sharing
### 4️⃣ Setup Pinecone (Vector Database)

1. Create an account → [https://www.pinecone.io/](https://www.pinecone.io/)
2. Create an index (for example `qa-index`)
3. Copy your **API key**

Then create a `.env` file:

```bash
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=qa-index
```

You’ll load it in Python using `dotenv`.



### 5️⃣ Install Whisper (Speech-to-Text)

Install directly from GitHub:

```bash
pip install git+https://github.com/openai/whisper.git
```

Load it in your backend:

```python
import whisper
model = whisper.load_model("base")
```



### 6️⃣ Run Backend (FastAPI)

Start your backend service:

```bash
uvicorn main:app --reload
```

The backend runs at → `http://localhost:8000`



### 7️⃣ Run Frontend (Streamlit)

Launch your UI:

```bash
streamlit run app.py
```

Open in your browser: → `http://localhost:8501`


## 🧩 Project Structure

```
📂 project_root/
 ┣ 📁 whisper_model/
 ┣ 📁 vosk-model-small-hi-0.22/
 ┣ 📄 main.py              ← FastAPI backend
 ┣ 📄 app.py               ← Streamlit frontend
 ┣ 📄 utils.py             ← Whisper + TTS utilities
 ┣ 📄 .env                 ← Pinecone config
 ┣ 📄 requirements.txt
 ┣ 📄 README.md
```


## 🧠 Example Workflow

1. 🎙️ Record or upload your voice question
2. 🧠 Whisper converts Hindi/Hinglish speech → text
3. 🔍 Pinecone retrieves the most relevant answers
4. 💬 Answer is displayed + converted to speech
5. 🔊 Audio response plays automatically



## 🪄 Example Commands

```bash
# 1. Activate environment
kissanqa\Scripts\activate

# 2. Run backend
uvicorn main:app --reload

# 3. Run frontend
streamlit run app.py
```


## 💡 Notes

* Use 16 kHz mono audio for best results.
* You can switch Pinecone with FAISS or Chroma if you prefer.
* The backend auto-generates responses and Hindi speech (via gTTS).


## 🧾 Example Output

```bash
🎙️ Recording question...
🧠 "Kisan ke liye AI kya fayda karta hai?"
🔍 Searching vector database...
✅ Answer: "AI helps farmers with weather prediction and crop yield optimization."
🔊 Playing Hindi voice response...
```



👨‍💻 Authors
**Satyam Tiwari**
& **Ayush Kale**

✨ KissanVaani AI is built with a focus on Indian farmers,
bringing LLMs + Retrieval + Voice together for practical, local‑language support.

🚀 Made with ❤️ for Hindi + Hinglish learners and developers.


