import streamlit as st
import sys
import os

# ======================================
# FIX: Make sure shared folder is visible
# ======================================
current_dir = os.path.dirname(os.path.abspath(__file__))        # /ANTIDOTE/pages
project_root = os.path.dirname(current_dir)                     # /ANTIDOTE
shared_dir = os.path.join(project_root, "shared")               # /ANTIDOTE/shared

# Add project root & shared folder to sys.path
for path in [project_root, shared_dir]:
    if path not in sys.path:
        sys.path.append(path)

# ======================================
# IMPORTS (after path fix)
# ======================================
from shared.helpers import load_css, get_openai_client
from utils.alzy_utils import get_due_reminders

# ======================================
# PAGE CONFIG
# ======================================
st.set_page_config(page_title="ALZY – Patient", layout="wide")

# Load CSS safely (absolute path)
css_path = os.path.join(shared_dir, "style.css")
load_css(css_path)

# ======================================
# PAGE CONTENT
# ======================================
st.title("👩‍🦳 Patient Dashboard")
st.markdown("Welcome! Here you can see your reminders and talk to ALZY assistant.")

# =======================
# Reminders
# =======================
st.subheader("🔔 Today's Reminders")
reminders = get_due_reminders()
if reminders:
    for r in reminders:
        st.success(f"🕒 {r['time']} — {r['task']}")
else:
    st.info("✅ No due reminders now!")

# =======================
# Chatbot
# =======================
st.subheader("💬 Chat with ALZY")
client = get_openai_client()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for chat in st.session_state.chat_history:
    st.chat_message(chat["role"]).write(chat["content"])

prompt = st.chat_input("Say something to ALZY...")
if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are ALZY, a kind, gentle caregiver assistant for memory support."},
                    *st.session_state.chat_history
                ],
            )
            reply = response.choices[0].message.content
            st.write(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
