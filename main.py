from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import tempfile, os
from utils import transcribe_hinglish, text_to_speech
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer


# ---------------- CONFIG ----------------
PINECONE_API_KEY = "pcsk_2kwhSX_ESPq3M4GKASr55VgLmjwS9YcH4LA4LB9NwQuGWqRtEikzEUcynKBqs9eQdaDT1P"
INDEX_NAME = "kissanai"

# ---------------- INIT MODELS ----------------
print("✅ Loading MiniLM model for embeddings...")
embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("✅ Embedding model loaded successfully!")

# ---------------- INIT PINECONE ----------------
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)
print(f"✅ Connected to Pinecone index: {INDEX_NAME}")

# ---------------- FASTAPI APP ----------------
app = FastAPI(title="Hinglish Voice QA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


# ---------------- ROUTES ----------------
@app.post("/ask")
async def ask_question(file: UploadFile):
    """
    1. Takes audio input (.wav or .opus)
    2. Transcribes to Hinglish text using Vosk (inside utils)
    3. Converts query to embedding with MiniLM
    4. Queries Pinecone top 3 answers
    5. Converts each answer to speech
    6. Returns text + answers + audio file names
    """

    # 1️⃣ Save uploaded audio temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # 2️⃣ Speech → Text
    text = transcribe_hinglish(tmp_path)
    print(f"🎤 Transcribed: {text}")

    if not text.strip():
        return {"error": "No speech detected or empty transcription."}

    # 3️⃣ Convert query → embedding
    query_embedding = embed_model.encode(text).tolist()

    # 4️⃣ Query Pinecone top 3 matches
    try:
        result = index.query(vector=query_embedding, top_k=3, include_metadata=True)
    except Exception as e:
        print(f"❌ Pinecone query failed: {e}")
        return {"error": "Pinecone query failed."}

    # 5️⃣ Extract answers
    answers = []
    for match in result.matches:
        ans = match.metadata.get("answer") or match.metadata.get("text") or "(no answer)"
        answers.append(ans)

    if not answers:
        answers = ["No relevant answer found."]

    # 6️⃣ Convert each answer → speech
    tts_files = []
    for i, ans in enumerate(answers):
        filename = f"answer_{i+1}.mp3"
        try:
            text_to_speech(ans, filename)
            tts_files.append(filename)
        except Exception as e:
            print(f"❌ Error in TTS for answer {i+1}: {e}")

    # 7️⃣ Return response
    return {
        "query_text": text,
        "answers": answers,
        "tts_audio_files": tts_files,
    }


@app.get("/")
def root():
    return {"status": "ok", "message": "Hinglish Voice QA API with MiniLM + Pinecone active!"}
