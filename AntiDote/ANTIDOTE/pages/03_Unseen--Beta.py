# ANTIDOTE/pages/Unseen--Beta.py
# --------------------------------------------------
# UNSEEN – Voice-Driven Assistant for Low Vision
# --------------------------------------------------
import os
import json
import datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# Small helper for rerun (new vs old Streamlit)
def _rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# ---------- PATHS (for local hero GIF) ----------
PROJECT_DIR = Path(__file__).resolve().parent      # .../ANTIDOTE/pages
REPO_ROOT = PROJECT_DIR.parent                     # .../ANTIDOTE
IMAGES_DIR = REPO_ROOT / "images"
HERO_GIF = IMAGES_DIR / "unseen-hero.gif"          # optional local GIF

st.set_page_config(page_title="UNSEEN – Beta", page_icon="👁‍🗨", layout="wide")

# ---------- GLOBAL STYLES ----------
st.markdown(
    """
    <style>
    .stApp {
      background: radial-gradient(circle at top, #0f172a 0%, #020617 100%);
      color: #fff;
    }
    h1,h2,h3,h4 { color:#fff !important; }

    .big-btn {
      background: linear-gradient(120deg, #f97316 0%, #fb7185 80%);
      border:none;
      color:white;
      border-radius:16px;
      padding:16px 20px;
      font-size:1.25rem;
      font-weight:700;
      width:100%;
      box-shadow: 0 12px 25px rgba(251,113,133,0.35);
      cursor:pointer;
    }

    .panel {
      background: rgba(15,23,42,0.35);
      border: 1px solid rgba(255,255,255,0.04);
      border-radius: 16px;
      padding: 12px 14px;
      margin-bottom: 12px;
    }

    /* Tabs text color tweaks */
    div.stTabs [data-baseweb="tab"] {
      color: #ffffff !important;
      font-weight: 500;
    }
    div.stTabs [data-baseweb="tab"][aria-selected="true"] {
      color: #ff4b4b !important;
    }

    /* Button text color overrides (these selectors change with Streamlit versions) */
    .stButton.st-emotion-cache-8atqhb.e1mlolmg0 button p{
      color:#FFF;
    }
    .stButton.st-emotion-cache-8atqhb.e1mlolmg0 button:hover p{
      color:#ffffff;
    }

    .st-emotion-cache-79elbk.e1o1zy6o0 p,
    .st-emotion-cache-0.e16n7gab17 p,
    .st-emotion-cache-1sm2s1z.e1r0q00f0 p{
      color:#ffffff;
    }

    /* Back to Dashboard button */
    .back-btn .stButton>button {
      background: linear-gradient(120deg, #22c55e, #0ea5e9);
      border:none;
      color:#0b1220;
      font-weight:700;
      border-radius: 999px;
      padding: 0.4rem 1.4rem;
      box-shadow: 0 10px 22px rgba(14,165,233,0.45);
    }
    .back-btn .stButton>button:hover {
      filter: brightness(1.05);
      transform: translateY(-1px);
    }
    .back-btn .stButton>button:active {
      transform: translateY(0);
      filter: brightness(0.97);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- SESSION STATE ----------
st.session_state.setdefault("unseen_started", False)
st.session_state.setdefault("unseen_mode", None)          # "voice" | "text"
st.session_state.setdefault("unseen_tasks", [])

# ---------- LANDING (Mode selection) ----------
if not st.session_state["unseen_started"]:
    # Simple title for landing
    st.markdown("<h1>👁‍🗨 UNSEEN – Voice Assistant</h1>", unsafe_allow_html=True)
    st.caption("Seeing beyond sight. Voice-first helper inside ANTIDOTE.")

    c1, c2 = st.columns([2, 1])
    with c1:
        st.write("Welcome to **UNSEEN** — your voice-powered daily assistant.")
        st.write("Choose how you want to interact:")

        if st.button("🎤 Voice Mode (recommended)", use_container_width=True, key="start_voice"):
            st.session_state["unseen_started"] = True
            st.session_state["unseen_mode"] = "voice"
            _rerun()

        if st.button("💬 Text Mode (low-vision)", use_container_width=True, key="start_text"):
            st.session_state["unseen_started"] = True
            st.session_state["unseen_mode"] = "text"
            _rerun()

    with c2:
        # Only show local GIF if it exists – no external fallback
        if HERO_GIF.exists():
            st.image(str(HERO_GIF), use_container_width=True)

    st.stop()

# ---------- AFTER MODE CHOSEN: HEADER + BACK BUTTON ----------
mode = st.session_state.get("unseen_mode", "voice")

title_col, back_col = st.columns([5, 2])
with title_col:
    st.markdown("<h1>👁‍🗨 UNSEEN – Voice Assistant</h1>", unsafe_allow_html=True)
    if mode == "voice":
        st.caption("Voice-first mode. Ideal for low-vision users with a screen-reader or helper.")
    else:
        st.caption("Text mode selected. You can type instead of speaking.")

with back_col:
    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
    back_clicked = st.button("⬅️ Back to Dashboard", key="unseen_back", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if back_clicked:
        st.session_state["unseen_started"] = False
        st.session_state["unseen_mode"] = None
        _rerun()

# ---------- MAIN TABS ----------
tab_daily, tab_talk, tab_reader, tab_nav, tab_about = st.tabs(
    ["🕓 Daily", "🗣 Smart Talk", "📖 Text / Label Reader", "🧭 Navigation", "ℹ About"]
)

# ---------------- DAILY ----------------
with tab_daily:
    st.subheader("🕓 Voice-based Daily Routine")
    st.caption("Say: 'add reminder take medicine at 9pm' (browser mic must be allowed).")

    # Mic button + status rendered via components.html to avoid script showing as text
    components.html(
        """
        <div class="panel">
          <button id="unseen-stt-btn"
                  style="padding:6px 14px;border:none;background:#0ea5e9;color:white;
                         border-radius:8px;cursor:pointer;">
            🎤 Speak command
          </button>
          <span id="unseen-stt-status"
                style="margin-left:6px;font-size:12px;color:#fff;"></span>
        </div>

        <script>
        (function () {
          const btn  = document.getElementById("unseen-stt-btn");
          const stat = document.getElementById("unseen-stt-status");
          if (!btn || !stat) return;

          btn.addEventListener("click", function () {
            const isLocal =
              (location.hostname === "localhost" || location.hostname === "127.0.0.1");

            // Security: mic needs HTTPS or localhost
            if (!window.isSecureContext && !isLocal) {
              stat.innerText = "❌ Mic needs HTTPS or localhost.";
              return;
            }

            const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SR) {
              stat.innerText = "❌ SpeechRecognition not supported in this browser.";
              return;
            }

            const rec = new SR();
            rec.lang = "en-US";

            rec.onstart = function () {
              stat.innerText = "🎧 Listening...";
            };

            rec.onerror = function (e) {
              stat.innerText = "❌ " + (e.error || "error");
            };

            rec.onresult = function (e) {
              const text = e.results[0][0].transcript;
              stat.innerText = "Heard: " + text;

              // Try to send text back to Streamlit via query param
              try {
                const u = new URL(window.location.href);
                u.searchParams.set("cmd", text);
                window.location.href = u.toString();
              } catch (err) {
                console.error("Navigation blocked:", err);
              }
            };

            rec.start();
          });
        })();
        </script>
        """,
        height=120,
    )

    # Read voice command from query param (if navigation succeeded)
    cmd = st.query_params.get("cmd")
    if isinstance(cmd, list):
        cmd = cmd[0]

    # Text fallback (works even if mic fails)
    typed_cmd = st.text_input("Or type your command here")
    run_cmd = st.button("Run typed command", key="run_typed_cmd")

    # Ensure reminders list exists
    if "unseen_tasks" not in st.session_state:
        st.session_state["unseen_tasks"] = []

    def process_unseen_cmd(command: str):
        """Process any command string for the Daily tab."""
        if not command:
            return
        txt = command.lower()
        if "add reminder" in txt or "take" in txt:
            st.session_state["unseen_tasks"].append(
                {
                    "time": datetime.datetime.now().isoformat(timespec="seconds"),
                    "text": command,
                }
            )
            st.success(f"✅ Reminder added: {command}")
        elif "what's on my list" in txt or "list" in txt:
            st.info("Here is your reminder list below.")
        else:
            st.info(f"Heard command: {command}")

    # 1) Process voice command (?cmd=...)
    if cmd:
        process_unseen_cmd(cmd)

    # 2) Process typed command when button clicked
    if run_cmd and typed_cmd.strip():
        process_unseen_cmd(typed_cmd.strip())

    st.write("**Your reminders:**")
    if not st.session_state["unseen_tasks"]:
        st.info("No reminders yet.")
    else:
        for t in reversed(st.session_state["unseen_tasks"]):
            st.write(f"• {t['time']} — {t['text']}")

# ---------------- TALK ----------------
with tab_talk:
    st.subheader("🗣 Smart Talk")
    st.caption("Ask: time, date, hello, who are you...")

    user_text = st.text_input("Say / type something")
    if st.button("Reply"):
        if not user_text:
            st.warning("Type something.")
        else:
            low = user_text.lower()
            if "time" in low:
                ans = f"The time is {datetime.datetime.now().strftime('%I:%M %p')}"
            elif "date" in low or "day" in low:
                ans = f"Today is {datetime.datetime.now().strftime('%A, %d %B %Y')}"
            else:
                ans = "I am UNSEEN, your voice helper inside ANTIDOTE."
            st.success(ans)
            # speak via browser
            st.markdown(
                f"""
                <script>
                (function(){{
                  if (!window.speechSynthesis) return;
                  const u = new SpeechSynthesisUtterance({json.dumps(ans)});
                  u.lang = "en-US";
                  u.rate = 0.98;
                  window.speechSynthesis.speak(u);
                }})();
                </script>
                """,
                unsafe_allow_html=True,
            )

# ---------------- READER ----------------
with tab_reader:
    st.subheader("📖 Text / Label Reader")
    st.caption("Upload an image of a medicine label, or paste text, and UNSEEN will read it aloud.")

    up = st.file_uploader("Upload image (demo only)", type=["png", "jpg", "jpeg"])
    txt = st.text_area("Paste text to read")

    if st.button("🔊 Read"):
        if txt.strip():
            readout = txt.strip()
        elif up:
            # No real OCR yet – placeholder message
            readout = "I see an uploaded image. (Add pytesseract here to read text.)"
        else:
            readout = "No text to read."

        st.success(readout)
        st.markdown(
            f"""
            <script>
            (function(){{
              if (!window.speechSynthesis) return;
              const u = new SpeechSynthesisUtterance({json.dumps(readout)});
              u.lang = "en-US";
              u.rate = 1;
              window.speechSynthesis.speak(u);
            }})();
            </script>
            """,
            unsafe_allow_html=True,
        )

# ---------------- NAV ----------------
with tab_nav:
    st.subheader("🧭 Navigation / Location")
    st.caption("This is simplified – we open Google Maps with your saved home.")

    HOME_URL = (
        "https://www.google.com/maps/dir//Garia,+Kolkata,+West+Bengal/@22.4624833,88.3695706,14z/"
        "data=!4m18!1m8!3m7!1s0x3a0271a00d52ca53:0x84c91e76a182e37a!2sGaria,+Kolkata,+West+Bengal!"
        "3b1!8m2!3d22.4660129!4d88.3928446!16zL20vMGMwMnYx!4m8!1m0!1m5!1m1!1s0x3a0271a00d52ca53:"
        "0x84c91e76a182e37a!2m2!1d88.3928446!2d22.4660129!3e0?entry=ttu"
    )

    if st.button("🧭 Take me home"):
        components.html(
            f"<script>window.open('{HOME_URL}', '_blank');</script>",
            height=0,
        )

    st.divider()
    st.write("📍 Get current location (browser):")
    components.html(
        """
        <button onclick="getLoc()" style="padding:6px 14px;border:none;background:#22c55e;color:white;border-radius:8px;cursor:pointer;">
          📍 Where am I?
        </button>
        <p id="loc-status" style="color:white;font-size:12px;margin-top:4px;"></p>
        <script>
        function getLoc(){
          const p = document.getElementById("loc-status");
          if (!navigator.geolocation){ p.innerText = "Geolocation not supported."; return; }
          navigator.geolocation.getCurrentPosition(function(pos){
            p.innerText = "You are at: " + pos.coords.latitude + ", " + pos.coords.longitude;
          }, function(err){
            p.innerText = "Error: " + err.message;
          });
        }
        </script>
        """,
        height=90,
    )

# ---------------- ABOUT ----------------
with tab_about:
    st.subheader("ℹ About UNSEEN")
    st.write(
        """
        UNSEEN is the third module of the ANTIDOTE care toolkit.  
        It is designed for visually impaired / low-vision users and is fully voice-first.  
        Features: voice commands, daily reminders, text reader, navigation helper.
        """
    )

