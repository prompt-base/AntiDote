# ANTIDOTE/pages/Signalink.py
# --------------------------------------------------
# SIGNALINK – Sign / Gesture Communication Module
# Inspired by your ALZY style
# --------------------------------------------------
import os
from pathlib import Path
import random
import json
import datetime
import streamlit as st

# --------------------------------------------------
# 1. PATHS / ASSETS
# --------------------------------------------------
# your project root (same as we used in alzy)
PROJECT_ROOT = Path(r"C:\Users\Anurag\PycharmProjects\AntiDote")
SIGNALINK_ASSETS = PROJECT_ROOT / "signalink_assets"  # put images here

# small demo sign dataset (you can expand later)
SIGN_DATA = [
    {
        "word": "Hello",
        "category": "Basic",
        "image": str(SIGNALINK_ASSETS / "hello.png"),
        "hint": "Hand up, small wave."
    },
    {
        "word": "Thank you",
        "category": "Basic",
        "image": str(SIGNALINK_ASSETS / "thankyou.png"),
        "hint": "From chin outward."
    },
    {
        "word": "Sorry",
        "category": "Basic",
        "image": str(SIGNALINK_ASSETS / "sorry.png"),
        "hint": "Closed fist over chest."
    },
    {
        "word": "Eat",
        "category": "Daily",
        "image": str(SIGNALINK_ASSETS / "eat.png"),
        "hint": "Fingers to mouth."
    },
    {
        "word": "Help",
        "category": "Daily",
        "image": str(SIGNALINK_ASSETS / "help.png"),
        "hint": "Thumb-up on palm."
    },
    {
        "word": "Mother",
        "category": "People",
        "image": str(SIGNALINK_ASSETS / "mother.png"),
        "hint": "Thumb to chin."
    },
    {
        "word": "Father",
        "category": "People",
        "image": str(SIGNALINK_ASSETS / "father.png"),
        "hint": "Thumb to forehead."
    },
]

CATEGORIES = sorted(list({s["category"] for s in SIGN_DATA}))


# --------------------------------------------------
# 2. GLOBAL STYLES
# --------------------------------------------------
st.set_page_config(page_title="Signalink", page_icon="🤟", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
      background: radial-gradient(circle at top, #0f172a 0%, #020617 100%);
      color: #fff;
    }
    h1,h2,h3,h4 {
      color: #fff !important;
    }
    .big-btn {
      background: linear-gradient(120deg, #38bdf8 0%, #6366f1 80%);
      border: none;
      color: #fff;
      padding: 18px 20px;
      border-radius: 18px;
      font-size: 1.4rem;
      font-weight: 700;
      width: 100%;
      box-shadow: 0 12px 30px rgba(99,102,241,0.3);
      cursor: pointer;
    }
    .sign-card {
      background: rgba(15,23,42,0.35);
      border: 1px solid rgba(255,255,255,0.05);
      border-radius: 16px;
      padding: 10px 12px;
      margin-bottom: 12px;
    }
    .cat-pill {
      display:inline-block;
      background: rgba(99,102,241,0.12);
      border: 1px solid rgba(99,102,241,0.25);
      padding: 3px 10px;
      border-radius: 999px;
      font-size: 12px;
      margin-right: 6px;
      margin-bottom: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 3. SESSION STATE
# --------------------------------------------------
if "signalink_started" not in st.session_state:
    st.session_state.signalink_started = False

if "signalink_progress" not in st.session_state:
    # store learned words and quiz scores
    st.session_state.signalink_progress = {
        "learned": [],
        "quiz_scores": []
    }

if "signalink_quiz_q" not in st.session_state:
    st.session_state.signalink_quiz_q = None  # current quiz question


# --------------------------------------------------
# 4. LANDING PAGE
# --------------------------------------------------
if not st.session_state.signalink_started:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("<h1>🤟 SIGNALINK</h1>", unsafe_allow_html=True)
        st.write("Sign / Gesture Communication helper inside ANTIDOTE.")
        st.write("Learn quick signs for patients, caregivers, and non-verbal users.")
        st.write("Tap **Start** to begin.")
    with col2:
        st.image(
            "https://i.pinimg.com/originals/e9/f7/bf/e9f7bf6cd7b5f1f6b954ed7be35d8aac.gif",
            use_container_width=True,
        )

    start = st.button("Start Signalink", use_container_width=True, key="start_signalink")
    if start:
        st.session_state.signalink_started = True
        st.rerun()
    st.stop()   # don't render rest


# --------------------------------------------------
# 5. MAIN SIGNALINK APP (after Start)
# --------------------------------------------------
st.title("🤟 SIGNALINK")

tab_learn, tab_practice, tab_quiz, tab_voice, tab_progress = st.tabs(
    ["📚 Learn Signs", "🧪 Practice", "📝 Quiz", "🗣 Voice → Sign", "📊 Progress"]
)

# --------------------------------------------------
# 📚 LEARN SIGNS
# --------------------------------------------------
with tab_learn:
    st.subheader("📚 Learn Signs")
    st.caption("Select a category and tap on a sign to view it.")

    cat = st.selectbox("Choose a category", ["All"] + CATEGORIES)

    filtered = SIGN_DATA if cat == "All" else [s for s in SIGN_DATA if s["category"] == cat]

    cols = st.columns(3)
    for i, sign in enumerate(filtered):
        with cols[i % 3]:
            st.markdown("<div class='sign-card'>", unsafe_allow_html=True)
            # image
            img_path = sign["image"]
            if img_path and os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            else:
                st.image("https://via.placeholder.com/300x180?text=SIGN", use_container_width=True)
            st.markdown(f"**{sign['word']}**")
            st.caption(f"Category: {sign['category']}")
            st.caption(f"Hint: {sign['hint']}")
            # mark as learned
            if st.button(f"Mark learned", key=f"learn_{sign['word']}"):
                if sign["word"] not in st.session_state.signalink_progress["learned"]:
                    st.session_state.signalink_progress["learned"].append(sign["word"])
                st.success(f"Marked {sign['word']} as learned ✅")
            st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------
# 🧪 PRACTICE
# --------------------------------------------------
with tab_practice:
    st.subheader("🧪 Practice Mode")
    st.caption("We will show you a sign. Tell us what it means.")

    # choose a random sign
    sign = random.choice(SIGN_DATA)
    c1, c2 = st.columns([1, 1])

    with c1:
        if sign["image"] and os.path.exists(sign["image"]):
            st.image(sign["image"], use_container_width=True)
        else:
            st.image("https://via.placeholder.com/400x220?text=SIGN", use_container_width=True)
    with c2:
        st.write("👇 What is this sign?")
        # make some options
        options = [sign["word"]]
        # pick 2 random wrong
        wrong = [s["word"] for s in SIGN_DATA if s["word"] != sign["word"]]
        random.shuffle(wrong)
        options += wrong[:2]
        random.shuffle(options)

        chosen = st.radio("Choose one:", options, key=f"pr_opt_{datetime.datetime.now().timestamp()}")
        if st.button("Check"):
            if chosen == sign["word"]:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Not correct. This is **{sign['word']}**.")
            st.info(f"Hint: {sign['hint']}")


# --------------------------------------------------
# 📝 QUIZ
# --------------------------------------------------
with tab_quiz:
    st.subheader("📝 Quiz Mode")
    st.caption("10/10 gets you a badge 😎")

    # if no current question, pick one
    if st.session_state.signalink_quiz_q is None:
        st.session_state.signalink_quiz_q = random.choice(SIGN_DATA)

    q = st.session_state.signalink_quiz_q

    c1, c2 = st.columns([1, 1])
    with c1:
        if q["image"] and os.path.exists(q["image"]):
            st.image(q["image"], use_container_width=True)
        else:
            st.image("https://via.placeholder.com/400x220?text=SIGN", use_container_width=True)

    with c2:
        st.write("What sign is this?")
        # make options
        opts = [q["word"]]
        others = [s["word"] for s in SIGN_DATA if s["word"] != q["word"]]
        random.shuffle(others)
        opts += others[:3]
        random.shuffle(opts)

        ans = st.radio("Select:", opts, key="quiz_ans")
        if st.button("Submit answer"):
            correct = (ans == q["word"])
            if correct:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Wrong. Correct answer: **{q['word']}**")
            # record score
            st.session_state.signalink_progress["quiz_scores"].append(
                {
                    "time": datetime.datetime.now().isoformat(timespec="seconds"),
                    "word": q["word"],
                    "correct": correct,
                }
            )
            # new question
            st.session_state.signalink_quiz_q = random.choice(SIGN_DATA)
            st.rerun()


# --------------------------------------------------
# 🗣 VOICE → SIGN
# (we'll keep this light — browser may block mic, so we show fallback)
# --------------------------------------------------
with tab_voice:
    st.subheader("🗣 Voice → Sign")
    st.caption("Say a word like 'Hello' or 'Thank you'. If browser blocks mic, type below.")

    # 1) small JS button for speech (if browser supports)
    st.markdown(
        """
        <button id="sig-stt-btn"
                style="padding:6px 14px;border:none;background:#f97316;color:white;border-radius:8px;cursor:pointer;">
          🎤 Speak
        </button>
        <span id="sig-stt-status" style="margin-left:6px;font-size:12px;color:#fff;"></span>
        <script>
        (function(){
          const btn = document.getElementById("sig-stt-btn");
          const stt = document.getElementById("sig-stt-status");
          if (!btn) return;
          btn.addEventListener("click", function(){
            const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SR){
              stt.innerText = "Speech not supported here. Type below.";
              return;
            }
            const rec = new SR();
            rec.lang = "en-US";
            rec.onstart = ()=>{ stt.innerText = "Listening..."; };
            rec.onerror = (e)=>{ stt.innerText = "Error: " + e.error; };
            rec.onresult = (e)=>{
              const text = e.results[0][0].transcript;
              const u = new URL(window.location.href);
              u.searchParams.set("say_sig", text);
              window.location.href = u.toString();
            };
            rec.start();
          });
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )

    # 2) get spoken
    spoken_sig = st.query_params.get("say_sig")
    if isinstance(spoken_sig, list):
        spoken_sig = spoken_sig[0]

    typed = st.text_input("or type the word here", value=spoken_sig or "")

    if st.button("Show sign"):
        if not typed:
            st.error("Type or speak a word first.")
        else:
            # try to find sign
            match = None
            for s in SIGN_DATA:
                if s["word"].lower() == typed.lower():
                    match = s
                    break
            if match:
                st.success(f"Found sign for: {match['word']}")
                if match["image"] and os.path.exists(match["image"]):
                    st.image(match["image"], use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/400x220?text=SIGN", use_container_width=True)
                st.caption(f"Hint: {match['hint']}")
            else:
                st.error("No sign found for that word. Add it to SIGNALINK later.")


# --------------------------------------------------
# 📊 PROGRESS
# --------------------------------------------------
with tab_progress:
    st.subheader("📊 My Signalink Progress")

    learned = st.session_state.signalink_progress["learned"]
    scores = st.session_state.signalink_progress["quiz_scores"]

    st.write(f"✅ Signs learned: {len(learned)}")
    if learned:
        st.write(", ".join(learned))

    st.divider()

    st.write("🧪 Quiz history:")
    if not scores:
        st.info("No quiz taken yet.")
    else:
        for s in reversed(scores):
            status = "✅" if s["correct"] else "❌"
            st.write(f"{status} {s['time']} – {s['word']}")
