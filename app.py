
import streamlit as st
import requests
import tempfile
import os
from streamlit_mic_recorder import mic_recorder
from datetime import datetime, timezone, timedelta

# =============== CONFIG ===============
BACKEND_URL = "http://localhost:8000/ask"
st.set_page_config(page_title="KissanVaani AI", layout="wide", page_icon="🌾")

IST = timezone(timedelta(hours=5, minutes=30))

# ---------- LANGUAGE STRINGS ----------
LANG = {
    "en": {
        "title": "KissanVaani AI - Voice Farming Assistant",
        "subtitle": "Ask any farming question using your voice. Get answers in English & Hindi with audio.",
        "record_tab": "🎙️ Record",
        "upload_tab": "📂 Upload",
        "hero_greet_morning": "Good Morning Farmer!",
        "hero_greet_noon": "Good Afternoon Farmer!",
        "hero_greet_evening": "Good Evening Farmer!",
        "hero_greet_night": "Ready for late night farm planning?",
        "rec_card_title": "🎙️ Ask with your Mic",
        "rec_card_text": "Press start, speak your farming question, then stop and let AI answer.",
        "upl_card_title": "📂 Upload recorded audio",
        "upl_card_text": "Upload WAV / MP3 / WEBM / OPUS and get AI farming answers.",
        "btn_get_answer": "🚀 Ask AI",
        "heading_hinglish_text": "📝 Hinglish Text (Transcription)",
        "heading_answers": "💡 Jawab (Answers)",
        "label_english": "English",
        "label_hindi": "Hindi",
        "label_audio_en": "Audio (English)",
        "label_audio_hi": "Audio (Hindi)",
    },
    "hinglish": {
        "title": "KissanVaani AI - Voice Farming Sahayak",
        "subtitle": "Apne kheti ke sawal aawaaz se pucho. English aur Hindi mein jawab + audio pao.",
        "record_tab": "🎙️ Aawaaz se record karo",
        "upload_tab": "📂 Audio upload karo",
        "hero_greet_morning": "Suprabhat kisan bhai!",
        "hero_greet_noon": "Namaste kisan bhai!",
        "hero_greet_evening": "Shubh sandhya kisan bhai!",
        "hero_greet_night": "Raat ki kheti planning ke liye taiyaar?",
        "rec_card_title": "🎙️ Mic se sawaal pucho",
        "rec_card_text": "Start dabao, apna kheti ka sawaal bolo, phir stop karke AI se jawab lo.",
        "upl_card_title": "📂 Pehle se record kiya hua audio upload karo",
        "upl_card_text": "WAV / MP3 / WEBM / OPUS upload karo aur AI se krishi jawab lo.",
        "btn_get_answer": "🚀 Jawab lao",
        "heading_hinglish_text": "📝 Hinglish Text (Aapka sawaal)",
        "heading_answers": "💡 Jawab (Answers)",
        "label_english": "English",
        "label_hindi": "Hindi",
        "label_audio_en": "Audio (English)",
        "label_audio_hi": "Audio (Hindi)",
    },
    "hi": {
        "title": "किसानवाणी AI - वॉइस फार्मिंग सहायक",
        "subtitle": "अपना खेती से जुड़ा सवाल आवाज़ से पूछें। जवाब अंग्रेज़ी और हिन्दी में, साथ में ऑडियो के साथ पाएँ।",
        "record_tab": "🎙️ रिकॉर्ड करें",
        "upload_tab": "📂 ऑडियो अपलोड करें",
        "hero_greet_morning": "सुप्रभात किसान भाई!",
        "hero_greet_noon": "नमस्ते किसान भाई!",
        "hero_greet_evening": "शुभ संध्या किसान भाई!",
        "hero_greet_night": "रात की खेती प्लानिंग के लिए तैयार?",
        "rec_card_title": "🎙️ माइक से सवाल पूछें",
        "rec_card_text": "स्टार्ट दबाएँ, अपना खेती का सवाल बोलें, फिर स्टॉप दबाकर AI से जवाब लें।",
        "upl_card_title": "📂 पहले से रिकॉर्ड किया ऑडियो अपलोड करें",
        "upl_card_text": "WAV / MP3 / WEBM / OPUS फाइल अपलोड करें और AI से कृषि सम्बंधित जवाब लें।",
        "btn_get_answer": "🚀 जवाब प्राप्त करें",
        "heading_hinglish_text": "📝 Hinglish Text (आपका सवाल)",
        "heading_answers": "💡 जवाब (Answers)",
        "label_english": "अंग्रेज़ी (English)",
        "label_hindi": "हिन्दी (Hindi)",
        "label_audio_en": "ऑडियो (English)",
        "label_audio_hi": "ऑडियो (Hindi)",
    },
}

# ---------- STATE ----------
now_ist = datetime.now(IST)

if "theme" not in st.session_state:
    # auto: day between 6-18
    st.session_state["theme"] = "day" if 6 <= now_ist.hour < 18 else "night"

if "ui_lang" not in st.session_state:
    st.session_state["ui_lang"] = "hinglish"   # "en" or "hinglish" or "hi"

# =============== TOP BAR (THEME + LANGUAGE) ===============
top_c1, top_c2, top_c3 = st.columns([3, 1.5, 2])

with top_c2:
    theme_toggle = st.toggle(
        "🌞 / 🌙 Theme",
        value=(st.session_state["theme"] == "day"),
        help="Switch day / night look",
    )
    st.session_state["theme"] = "day" if theme_toggle else "night"

with top_c3:
    lang_choice = st.radio(
        "UI Language",
        ["Hinglish", "English", "Hindi"],
        index=0 if st.session_state["ui_lang"] == "hinglish"
        else 1 if st.session_state["ui_lang"] == "en"
        else 2,
        horizontal=True,
    )
    if lang_choice == "Hinglish":
        st.session_state["ui_lang"] = "hinglish"
    elif lang_choice == "English":
        st.session_state["ui_lang"] = "en"
    else:
        st.session_state["ui_lang"] = "hi"

# Language dict for this run (after user choices)
L = LANG[st.session_state["ui_lang"]]

# ---------- THEME COLORS + BACKGROUND IMAGE ----------
if st.session_state["theme"] == "day":
    overlay_color = "linear-gradient(rgba(255,255,255,0.82), rgba(255,255,255,0.96))"
    hero_gradient = "linear-gradient(135deg, #2e7d32 0%, #66bb6a 100%)"
    card_bg = "rgba(255,255,255,0.88)"
    card_border = "rgba(255,255,255,0.7)"
    text_primary = "#1b5e20"
    text_secondary = "#2c3e50"
    shadow_color = "rgba(46,125,50,0.35)"
    # farm image (day)
    bg_image_url = "https://images.pexels.com/photos/158827/field-corn-agriculture-farm-158827.jpeg?auto=compress&cs=tinysrgb&w=1600"
else:
    overlay_color = "linear-gradient(rgba(0,0,0,0.82), rgba(0,0,0,0.96))"
    hero_gradient = "linear-gradient(135deg, #0d47a1 0%, #1b5e20 55%, #000000 100%)"
    card_bg = "rgba(13,25,35,0.9)"
    card_border = "rgba(255,255,255,0.06)"
    text_primary = "#e8f5e9"
    text_secondary = "#eceff1"
    shadow_color = "rgba(0,0,0,0.75)"
    # farm image (night / dawn)
    bg_image_url = "https://images.pexels.com/photos/162568/fog-dawn-landscape-morning-162568.jpeg?auto=compress&cs=tinysrgb&w=1600"

# =============== CSS + PARALLAX BACKGROUND ===============
st.markdown(
    f"""
<style>
@import url("https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap");

html, body, [class*="css"] {{
  font-family: "Poppins", sans-serif;
}}

:root {{
  --card-bg: {card_bg};
  --card-border: {card_border};
  --text-primary: {text_primary};
  --text-secondary: {text_secondary};
  --hero-gradient: {hero_gradient};
  --shadow-color: {shadow_color};
}}

body, .stApp {{
  color: var(--text-secondary);
}}

.stApp {{
  background: transparent;
}}

/* Parallax farm background */
#parallax-bg {{
  position: fixed;
  top: -5%;
  left: -5%;
  width: 110%;
  height: 110%;
  background-image: url("{bg_image_url}");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  will-change: transform;
  transform: translate3d(0,0,0) scale(1.05);
  z-index: -3;
}}

.bg-overlay {{
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: {overlay_color};
  z-index: -2;
}}

.hero-box {{
  background: var(--hero-gradient);
  color: white;
  padding: 1.6rem 2rem;
  border-radius: 20px;
  box-shadow: 0 20px 40px var(--shadow-color);
  margin-bottom: 1.6rem;
}}

.hero-top {{
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
}}

.hero-title {{
  font-size: 2.6rem;
  font-weight: 800;
  margin-bottom: 0.35rem;
}}

.hero-subtitle {{
  font-size: 1.05rem;
  opacity: 0.95;
}}

.hero-time {{
  text-align: right;
  font-size: 0.9rem;
  line-height: 1.4;
}}

.hero-greet {{
  font-weight: 700;
}}

.glass-card {{
  background: var(--card-bg);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-radius: 16px;
  padding: 1.3rem 1.5rem;
  border: 1px solid var(--card-border);
  box-shadow: 0 10px 30px var(--shadow-color);
}}

.answer-card {{
  background: var(--card-bg);
  border-radius: 14px;
  padding: 1rem 1.3rem;
  border: 1px solid var(--card-border);
  margin-bottom: 1rem;
  box-shadow: 0 8px 26px var(--shadow-color);
}}

.answer-index {{
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.4rem;
}}

.answer-text-label {{
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
}}

.answer-text-value {{
  font-size: 0.95rem;
  color: var(--text-secondary);
}}

div.stButton > button {{
  background: #2e7d32;
  color: white;
  border-radius: 999px;
  border: none;
  padding: 0.45rem 1.6rem;
  font-weight: 600;
}}

div.stButton > button:hover {{
  background: #1b5e20;
  box-shadow: 0 6px 18px rgba(46,125,50,0.6);
}}

.stTabs [data-baseweb="tab-list"] {{
  justify-content: center;
}}

.stTabs [data-baseweb="tab"] {{
  background-color: rgba(0,0,0,0.18);
  color: var(--text-secondary);
  border-radius: 999px;
  padding: 0.35rem 0.9rem;
  margin: 0 0.25rem;
  border: 1px solid rgba(255,255,255,0.2);
  font-weight: 600;
  font-size: 0.95rem;
}}

.stTabs [data-baseweb="tab"][aria-selected="true"] {{
  background: #2e7d32;
  color: #ffffff !important;
  border-color: #2e7d32;
}}
</style>

<div id="parallax-bg"></div>
<div class="bg-overlay"></div>

<script>
  // Simple mouse-move parallax effect
  if (!window.__kissan_parallax_bound) {{
    window.__kissan_parallax_bound = true;
    document.addEventListener('mousemove', function(e) {{
      const moveX = (e.clientX / window.innerWidth - 0.5) * 20;
      const moveY = (e.clientY / window.innerHeight - 0.5) * 20;
      const bg = document.getElementById('parallax-bg');
      if (bg) {{
        bg.style.transform = 'translate3d(' + moveX + 'px,' + moveY + 'px,0) scale(1.05)';
      }}
    }});
  }}
</script>
""",
    unsafe_allow_html=True,
)

# =============== HERO ===============
now_ist = datetime.now(IST)

if 5 <= now_ist.hour < 12:
    greet = L["hero_greet_morning"]
elif 12 <= now_ist.hour < 17:
    greet = L["hero_greet_noon"]
elif 17 <= now_ist.hour < 21:
    greet = L["hero_greet_evening"]
else:
    greet = L["hero_greet_night"]

st.markdown(
    f"""
<div class="hero-box">
  <div class="hero-top">
    <div>
      <div class="hero-title">🌾 KissanVaani AI</div>
      <div class="hero-subtitle">{L["subtitle"]}</div>
    </div>
    <div class="hero-time">
      <div class="hero-greet">{greet}</div>
      <div>🕒 {now_ist.strftime("%I:%M %p")} IST</div>
      <div>{now_ist.strftime("%d %b %Y")}</div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# =============== PROCESS AUDIO FUNCTION ===============
def process_audio(path: str):
    try:
        with open(path, "rb") as f:
            res = requests.post(
                BACKEND_URL,
                files={"file": (os.path.basename(path), f)},
            )
    except Exception as e:
        st.error(f"Backend request failed: {e}")
        return

    if res.status_code != 200:
        st.error(f"API Error: {res.text}")
        return

    data = res.json()

    # Hinglish transcription of query
    st.markdown(f"### {L['heading_hinglish_text']}")
    st.markdown(
        f"<div class='glass-card'>{data.get('hinglish_text', 'No transcription received.')}</div>",
        unsafe_allow_html=True,
    )

    # Answers
    st.markdown(f"### {L['heading_answers']}")
    answers = data.get("answers", [])
    if not answers:
        st.info("No answers returned from backend.")
        return

    for i, a in enumerate(answers, 1):
        st.markdown(
            f"""
<div class="answer-card">
  <div class="answer-index">Answer {i}</div>
  <div class="answer-text-label">{L['label_english']}:</div>
  <div class="answer-text-value">{a.get('english', '')}</div>
  <br/>
  <div class="answer-text-label">{L['label_hindi']}:</div>
  <div class="answer-text-value">{a.get('hindi', '')}</div>
</div>
""",
            unsafe_allow_html=True,
        )
        col_en, col_hi = st.columns(2)
        with col_en:
            st.caption(L["label_audio_en"])
            if a.get("audio_en"):
                st.audio(a["audio_en"])
        with col_hi:
            st.caption(L["label_audio_hi"])
            if a.get("audio_hi"):
                st.audio(a["audio_hi"])

# =============== MAIN TABS ===============
tab1, tab2 = st.tabs([L["record_tab"], L["upload_tab"]])

# --- TAB 1: RECORD ---
with tab1:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(
            f"""
<div class="glass-card" style="text-align:center;">
  <h4>{L['rec_card_title']}</h4>
  <p>{L['rec_card_text']}</p>
</div>
""",
            unsafe_allow_html=True,
        )

        audio = mic_recorder(
            start_prompt="Start Recording",
            stop_prompt="Stop Recording",
            key="mic",
            use_container_width=True,
        )

    if audio and "bytes" in audio:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(audio["bytes"])
            rec_path = tmp.name

        st.audio(rec_path)
        center1, center2, center3 = st.columns([1, 1, 1])
        with center2:
            if st.button(L["btn_get_answer"], key="btn_record"):
                process_audio(rec_path)

# --- TAB 2: UPLOAD ---
with tab2:
    st.markdown(
        f"""
<div class="glass-card" style="text-align:center;">
  <h4>{L['upl_card_title']}</h4>
  <p>{L['upl_card_text']}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    file = st.file_uploader(
        "Select audio file",
        type=["wav", "mp3", "webm", "opus"],
    )
    if file:
        suffix = "." + file.name.split(".")[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file.read())
            up_path = tmp.name

        st.audio(up_path)
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            if st.button(L["btn_get_answer"], key="btn_upload"):
                process_audio(up_path)

# =============== FOOTER ===============
st.markdown(
    """
<div style="text-align:center; margin-top:25px; color:#ddd; font-size:0.8rem;">
  Made for Indian Farmers | KissanVaani AI | LLM + Retrieval + Voice
</div>
""",
    unsafe_allow_html=True,
)
