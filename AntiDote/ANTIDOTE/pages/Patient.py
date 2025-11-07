# pages/Patient.py
# ===============================
# ALZY – Patient Page (full features + voice+text AI chat)
# ===============================
import os
import json
import random
import datetime
from pathlib import Path
import streamlit as st

# Robust imports for helpers and utils (works with package or plain imports)
try:
    from ANTIDOTE.shared.helpers import load_css, get_openai_client
except Exception:
    from shared.helpers import load_css, get_openai_client

# Try to import full utils; fall back to safe stubs if missing
try:
    from ANTIDOTE.utils.alzy_utils import (
        load_data,
        save_data,
        reminder_due,
        parse_iso,
        human_time,
        next_sr_due,
        add_log,
        save_upload,
        get_memory_book_images,
        add_person,
        mark_quiz_result,
        advance_reminder,
        snooze_reminder,
    )
except Exception:
    # Minimal safe stubs so the page still runs
    def load_data():
        return {
            "profile": {"name": "Friend"},
            "reminders": {},
            "people": {},
            "logs": [],
            "gps": {"home_address": "", "lat": "", "lon": ""},
        }

    def save_data(d): st.session_state.data = d

    def reminder_due(rec): return False
    def parse_iso(s): return datetime.datetime.now()
    def human_time(s): return s
    def next_sr_due(stage): return datetime.datetime.now()
    def add_log(data, reminder, action): pass
    def save_upload(upload, subdir): return ""
    def get_memory_book_images(): return []
    def add_person(data, name, rel, img): pass
    def mark_quiz_result(data, person_id, correct): pass
    def advance_reminder(rec): pass
    def snooze_reminder(rec, minutes=10): pass

# -------------------------------
# Page config & styling
# -------------------------------
st.set_page_config(page_title="ALZY – Patient", page_icon="🧑‍🦽", layout="wide")

# Load shared CSS (helper will search likely locations)
# Call with just "style.css" as helper resolves the shared folder
load_css("style.css")

# -------------------------------
# Session & Data init
# -------------------------------
if "data" not in st.session_state:
    st.session_state.data = load_data()
data = st.session_state.data

if "patient_ai_chat" not in st.session_state:
    st.session_state.patient_ai_chat = [
        {"role": "assistant", "content": "Hello 👋 I'm your Memory Assistant. How can I help you today?"}
    ]

# Quiz state
if "quiz_target_id" not in st.session_state:
    st.session_state.quiz_target_id = None
    st.session_state.quiz_option_ids = []

# Read query params using modern API (no experimental_get_query_params)
qp = st.query_params
spoken_qp = None
if "say" in qp:
    val = qp.get("say")
    if isinstance(val, list):
        spoken_qp = val[0]
    else:
        spoken_qp = val

# -------------------------------
# Header
# -------------------------------
# -------------------------------
# Header (Patient) with Role + Back
# -------------------------------
st.title("🧠 ALZY – Memory Assistant (Patient)")

left, right = st.columns([3, 2])

with left:
    nm = data.get("profile", {}).get("name", "Friend")
    st.markdown(f"**Hello, {nm}!**")

with right:
    # Flex container for Role + Back button
    st.markdown("""
    <div style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(255,255,255,0.06);
        padding: 6px 12px;
        border-radius: 8px;
        font-weight: 500;
    ">
        <span>Role: Patient</span>
        <button id='back-btn' style='
            background-color:#4CAF50;
            color:white;
            border:none;
            border-radius:5px;
            padding:4px 8px;
            cursor:pointer;
        '>🔁 Back</button>
    </div>
    """, unsafe_allow_html=True)

# Functional Streamlit button using switch_page
if st.button("🔁 Back to role selection", key="back_role"):
    st.session_state.role = None
    # Simulate page switch using query params
    st.experimental_set_query_params(page="Alzy--Beta")
    st.experimental_rerun()

# -------------------------------
# Tabs for Patient
# -------------------------------
tab_act, tab_med, tab_quiz, tab_mbook, tab_gps, tab_ai = st.tabs(
    ["🧑‍🦽 Activity", "💊 Medicine", "🧩 Quiz", "📘 Memory Book", "📍 GPS", "🤖 AI Chatbot"]
)

# ---------- helper to ensure data saved ----------
def persist():
    save_data(st.session_state.data)

# -------------------------------
# Activity & Medicine renderer (shared)
# -------------------------------
def render_patient_tab(rem_type: str, container):
    with container:
        st.subheader("🔔 Due now")
        due_rems = [
            r for r in data["reminders"].values()
            if reminder_due(r) and r.get("reminder_type", "activity") == rem_type
        ]
        if not due_rems:
            st.info("Nothing to do right now ✅")
        else:
            for r in sorted(due_rems, key=lambda x: x["next_due_iso"]):
                st.markdown("<div style='padding:12px;border-radius:12px;background:linear-gradient(135deg,#0ea5e9 0%, #6366f1 80%); color:white;'>", unsafe_allow_html=True)
                c1, c2 = st.columns([1, 2])
                with c1:
                    ip = r.get("image_path", "")
                    if ip and Path(ip).exists():
                        st.image(ip, use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/200x150?text=Photo", use_container_width=True)
                with c2:
                    st.markdown(f"**{r['title']}**")
                    st.caption(human_time(r["next_due_iso"]))
                    steps = r.get("steps", [])
                    for i, s in enumerate(steps, 1):
                        st.write(f"{i}. {s}")
                    b1, b2 = st.columns(2)
                    if b1.button("✅ I did it", key=f"pt_done_{rem_type}_{r['id']}"):
                        advance_reminder(r)
                        if rem_type == "medicine":
                            add_log(data, r, "taken (patient)")
                        persist()
                        st.experimental_rerun()
                    if b2.button("⏰ Later", key=f"pt_snooze_{rem_type}_{r['id']}"):
                        snooze_reminder(r)
                        if rem_type == "medicine":
                            add_log(data, r, "snoozed (patient)")
                        persist()
                        st.experimental_rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.subheader("🟡 Coming soon (24h)")
        upcoming = []
        now_ = datetime.datetime.now()
        for r in data["reminders"].values():
            if r.get("reminder_type", "activity") != rem_type:
                continue
            dt = parse_iso(r["next_due_iso"])
            if now_ < dt <= now_ + datetime.timedelta(hours=24):
                upcoming.append(r)
        if not upcoming:
            st.caption("No upcoming reminders.")
        else:
            for r in sorted(upcoming, key=lambda x: x["next_due_iso"]):
                st.markdown(f"<div style='padding:8px;border-radius:10px;background:linear-gradient(135deg,#f97316 0%,#f43f5e 80%);color:white;'>🕒 <strong>{r['title']}</strong> — {human_time(r['next_due_iso'])}</div>", unsafe_allow_html=True)

# Activity tab
with tab_act:
    render_patient_tab("activity", st.container())

# Medicine tab
with tab_med:
    render_patient_tab("medicine", st.container())

# -------------------------------
# Quiz tab (face/people)
# -------------------------------
with tab_quiz:
    st.subheader("🧩 Face quiz")
    if not data.get("people"):
        st.info("No people added yet.")
    else:
        if st.session_state.quiz_target_id is None:
            due = [p for p in data["people"].values() if parse_iso(p["next_due_iso"]) <= datetime.datetime.now()]
            if not due:
                st.success("No one due for quiz right now.")
            else:
                target = random.choice(due)
                others = [p for p in data["people"].values() if p["id"] != target["id"]]
                random.shuffle(others)
                others = others[:2]
                st.session_state.quiz_target_id = target["id"]
                st.session_state.quiz_option_ids = [target["id"]] + [o["id"] for o in others]

        if st.session_state.quiz_target_id:
            target = data["people"][st.session_state.quiz_target_id]
            st.write("Who is this?")
            ip = target.get("image_path", "")
            if ip and Path(ip).exists():
                st.image(ip, use_container_width=True)
            else:
                st.image("https://via.placeholder.com/200x150?text=Photo", use_container_width=True)
            opts = [data["people"][pid] for pid in st.session_state.quiz_option_ids if pid in data["people"]]
            random.shuffle(opts)
            cols = st.columns(len(opts))
            for i, p in enumerate(opts):
                with cols[i]:
                    if p.get("image_path") and Path(p["image_path"]).exists():
                        st.image(p["image_path"], use_container_width=True)
                    if st.button(f"{p['name']} — {p.get('relation','Family')}", key=f"ans_{p['id']}"):
                        correct = p["id"] == target["id"]
                        mark_quiz_result(data, target["id"], correct)
                        if correct:
                            st.success("✅ Correct!")
                        else:
                            st.error("❌ Not correct.")
                        st.session_state.quiz_target_id = None
                        st.session_state.quiz_option_ids = []
                        persist()
                        st.experimental_rerun()

# -------------------------------
# Memory Book tab
# -------------------------------
with tab_mbook:
    st.subheader("📘 Memory Book")
    uploads_dir = Path(__file__).resolve().parents[1] / "uploads"
    st.caption(f"Looking in: {uploads_dir}")
    imgs = get_memory_book_images()
    if not imgs:
        st.info("No images found.")
    else:
        for img_path in imgs:
            c1, c2 = st.columns([1, 2])
            c1.image(str(img_path), use_container_width=True)
            name_guess = img_path.stem.replace("_", " ").title()
            c2.markdown(f"**Name:** {name_guess}  \n**Relation:** Family  \n**Message:** Hi 👋 remember me?")
            st.divider()

# -------------------------------
# GPS tab
# -------------------------------
with tab_gps:
    st.subheader("📍 GPS (Patient)")
    gps = data.get("gps", {})
    home_addr = gps.get("home_address", "")
    st.write(f"Home: **{home_addr or 'Not set'}**")
    if st.button("🧭 Go home"):
        GO_HOME_URL = "https://www.google.com/maps"
        st.markdown(f"<script>window.open('{GO_HOME_URL}', '_blank')</script>", unsafe_allow_html=True)

# -------------------------------
# AI Chat tab (Text + Voice)
# -------------------------------
with tab_ai:
    st.subheader("🤖 AI Chatbot")
    st.caption("You can type below or use the 'Speak' button. Short, friendly answers.")

    # Show chat history
    for msg in st.session_state.patient_ai_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # JS button for browser SpeechRecognition -> writes ?say=... in URL
    st.markdown(
        """
        <div style="margin:8px 0 12px 0;">
          <button id="stt-btn"
                  style="padding:6px 14px;border:none;background:#f97316;color:white;border-radius:8px;cursor:pointer;">
            🎤 Speak
          </button>
          <span id="stt-status" style="margin-left:8px;font-size:12px;color:#222;"></span>
        </div>
        <script>
        (function(){
          const btn = document.getElementById("stt-btn");
          const status = document.getElementById("stt-status");
          if (!btn) return;
          btn.addEventListener("click", function(){
            const isLocal = (location.hostname === "localhost" || location.hostname === "127.0.0.1");
            if (!window.isSecureContext && !isLocal){
              status.innerText = "❌ Mic blocked: use https or localhost.";
              return;
            }
            const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SR){
              status.innerText = "❌ SpeechRecognition not supported.";
              return;
            }
            const rec = new SR();
            rec.lang = "en-US";
            rec.onstart = ()=>{ status.innerText = "Listening..."; };
            rec.onerror = (e)=>{ status.innerText = "❌ " + e.error; };
            rec.onresult = (e)=>{
              const text = e.results[0][0].transcript;
              const u = new URL(window.location.href);
              u.searchParams.set('say', text);
              window.location.href = u.toString();
            };
            rec.start();
          });
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )

    # prefer spoken param if present
    typed = st.chat_input("Type your message")
    user_input = spoken_qp or typed

    last_reply = None
    if user_input:
        # append user message to history and show
        st.session_state.patient_ai_chat.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        client = get_openai_client()
        reply_text = "I couldn't reach AI right now."

        if client:
            try:
                # Use OpenAI Python SDK (new style) - responses
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=user_input,
                    max_output_tokens=250,
                    temperature=0.6,
                )
                # try to extract text from different response shapes
                out = ""
                # Common SDK shape: response.output is a list of blocks
                if hasattr(response, "output") and isinstance(response.output, list):
                    for block in response.output:
                        if isinstance(block, dict) and "content" in block:
                            for c in block["content"]:
                                if isinstance(c, dict) and "text" in c:
                                    out += c["text"]
                # Fallback: response.output_text or raw dict
                if not out:
                    out = getattr(response, "output_text", "") or ""
                if not out and isinstance(response, dict):
                    out = response.get("output_text", "") or str(response)
                reply_text = out or reply_text
            except Exception as e:
                reply_text = f"⚠️ API error: {e}"
        else:
            # no client -> mock friendly reply (demo mode)
            reply_text = "Hi — I'm running in demo mode and cannot reach the AI. Please contact the admin."

        # append assistant reply and show
        st.session_state.patient_ai_chat.append({"role": "assistant", "content": reply_text})
        with st.chat_message("assistant"):
            st.markdown(reply_text)

    # show TTS (browser) button for the latest assistant reply
    for m in reversed(st.session_state.patient_ai_chat):
        if m["role"] == "assistant":
            last_reply = m["content"]
            break

    if last_reply:
        safe_last = json.dumps(last_reply)
        st.markdown(
            f"""
            <button id="tts-btn" style="margin-top:10px;padding:6px 14px;border:none;background:#0ea5e9;color:white;border-radius:8px;cursor:pointer;">
              🔊 Read aloud
            </button>
            <script>
            (function(){{
              const btn = document.getElementById("tts-btn");
              if (!btn) return;
              btn.addEventListener("click", function(){{
                if (!window.speechSynthesis){{ alert("Speech not supported here."); return; }}
                const txt = {safe_last};
                const u = new SpeechSynthesisUtterance(txt);
                u.lang = "en-US";
                u.rate = 0.95;
                window.speechSynthesis.speak(u);
              }});
            }})();
            </script>
            """,
            unsafe_allow_html=True,
        )
