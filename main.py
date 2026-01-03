from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import whisper
import torch
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from utils import text_to_speech

# # ---------------- CONFIG ----------------
# PINECONE_API_KEY = "pcsk_2kwhSX_ESPq3M4GKASr55VgLmjwS9YcH4LA4LB9NwQuGWqRtEikzEUcynKBqs9eQdaDT1P"
# INDEX_NAME = "kissanai"

# # ---------------- DEVICE ----------------
# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"✅ Using device: {device}")

# # ---------------- LOAD MODELS ----------------

# # 1️⃣ Whisper (Speech → Hinglish Text)
# print("✅ Loading Whisper model...")
# stt_model = whisper.load_model("medium", device=device)
# print("✅ Whisper loaded")

# # 2️⃣ MiniLM (Text → Vector)
# print("✅ Loading MiniLM embedding model...")
# embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# print("✅ MiniLM loaded")

# # ---------------- PINECONE ----------------
# pc = Pinecone(api_key=PINECONE_API_KEY)
# index = pc.Index(INDEX_NAME)
# print(f"✅ Connected to Pinecone index: {INDEX_NAME}")

# # ---------------- FASTAPI APP ----------------
# app = FastAPI(title="KissanVaani Voice QA API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ---------------- ROUTES ----------------

# @app.post("/ask")
# async def ask_question(file: UploadFile):
#     """
#     1. Audio upload
#     2. Whisper → Hinglish text (Roman)
#     3. MiniLM → Embedding
#     4. Pinecone search
#     5. Answer + TTS
#     """

#     # 1️⃣ Save temp audio
#     ext = file.filename.split(".")[-1]
#     with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
#         tmp.write(await file.read())
#         audio_path = tmp.name

#     # 2️⃣ Speech → Text (HINGLISH FIX 🔥)
#     try:
#         result = stt_model.transcribe(
#             audio_path,
#             language="en",        # 🔥 FORCE ROMAN OUTPUT
#             task="transcribe",
#             fp16=torch.cuda.is_available()
#         )
#         query_text = result["text"].strip()
#         print("🎤 Transcribed (Hinglish):", query_text)
#     except Exception as e:
#         return {"error": f"Whisper failed: {str(e)}"}
#     finally:
#         os.remove(audio_path)

#     if not query_text:
#         return {"error": "No speech detected"}

#     # 3️⃣ Text → Vector
#     query_vector = embed_model.encode(query_text).tolist()

#     # 4️⃣ Pinecone Search
#     try:
#         search_result = index.query(
#             vector=query_vector,
#             top_k=3,
#             include_metadata=True
#         )
#     except Exception as e:
#         return {"error": "Pinecone query failed"}

#     # 5️⃣ Extract Answers
#     answers = []
#     for match in search_result.matches:
#         ans = (
#             match.metadata.get("answer")
#             or match.metadata.get("text")
#             or "Koi jawab nahi mila"
#         )
#         answers.append(ans)

#     if not answers:
#         answers = ["Maaf kijiye, mujhe iska jawab nahi mila"]

#     # 6️⃣ Text → Speech
#     tts_files = []
#     for i, ans in enumerate(answers):
#         filename = f"answer_{i+1}.mp3"
#         text_to_speech(ans, filename)
#         tts_files.append(filename)

#     # 7️⃣ Response
#     return {
#         "query_text": query_text,
#         "answers": answers,
#         "tts_audio_files": tts_files,
#     }

# @app.get("/")
# def root():
#     return {
#         "status": "ok",
#         "message": "KissanVaani API running (Whisper Hinglish + Pinecone)"
#     }



from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import tempfile, os, torch, whisper
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from googletrans import Translator
from gtts import gTTS

# ================= CONFIG =================
# ---------------- CONFIG ----------------
PINECONE_API_KEY = "pcsk_2kwhSX_ESPq3M4GKASr55VgLmjwS9YcH4LA4LB9NwQuGWqRtEikzEUcynKBqs9eQdaDT1P"
INDEX_NAME = "kissanai"

# ================= INIT =================
device = "cuda" if torch.cuda.is_available() else "cpu"
stt_model = whisper.load_model("medium", device=device)
embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
translator = Translator()

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# ================= APP =================
app = FastAPI(title="KissanVaani API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= HELPERS =================

def hindi_to_hinglish(text: str):
    try:
        return transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS).lower()
    except:
        return text.lower()

def build_queries(hinglish):
    crop_map = {"seb": "apple"}
    queries = [hinglish]
    for hi, en in crop_map.items():
        if hi in hinglish:
            queries += [
                f"how to grow {en}",
                f"how to harvest {en}",
                f"{en} farming method"
            ]
    return list(set(queries))

def to_hindi(text):
    try:
        return translator.translate(text, dest="hi").text
    except:
        return text

def tts(text, filename, lang):
    gTTS(text=text, lang=lang).save(filename)

# ================= ROUTE =================

@app.post("/ask")
async def ask(file: UploadFile):
    # ---- save audio ----
    ext = file.filename.split(".")[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(await file.read())
        audio_path = tmp.name

    # ---- STT ----
    result = stt_model.transcribe(
        audio_path,
        language="en",
        task="transcribe",
        fp16=torch.cuda.is_available()
    )
    os.remove(audio_path)

    spoken_text = result["text"].strip()
    if not spoken_text:
        return {"error": "No speech detected"}

    hinglish_text = hindi_to_hinglish(spoken_text)
    queries = build_queries(hinglish_text)

    # ---- Pinecone search ----
    matches = []
    for q in queries:
        vec = embed_model.encode(q).tolist()
        res = index.query(vector=vec, top_k=3, include_metadata=True)
        matches.extend(res.matches)

    # ---- rank ----
    uniq = {}
    for m in matches:
        if m.id not in uniq or m.score > uniq[m.id].score:
            uniq[m.id] = m

    top = sorted(uniq.values(), key=lambda x: x.score, reverse=True)[:3]

    # ---- build bilingual answers ----
    final_answers = []
    for i, m in enumerate(top, 1):
        en = m.metadata.get("answer") or m.metadata.get("text") or "No answer"
        hi = to_hindi(en)

        en_audio = f"answer_{i}_en.mp3"
        hi_audio = f"answer_{i}_hi.mp3"

        tts(en, en_audio, "en")
        tts(hi, hi_audio, "hi")

        final_answers.append({
            "english": en,
            "hindi": hi,
            "audio_en": en_audio,
            "audio_hi": hi_audio
        })

    return {
        "hinglish_text": hinglish_text,
        "search_queries": queries,
        "answers": final_answers
    }

@app.get("/")
def root():
    return {"status": "ok"}
