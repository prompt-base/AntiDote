import streamlit as st
import sys
import os

# --- Ensure shared module is discoverable ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
shared_path = os.path.join(parent_dir, "shared")
if shared_path not in sys.path:
    sys.path.append(shared_path)

# --- Now safe to import helpers ---
from helpers import load_css, get_openai_client
from utils.alzy_utils import get_due_reminders

# --- Page Config ---
st.set_page_config(page_title="ALZY – Patient", layout="wide")
load_css(os.path.join(parent_dir, "shared", "style.css"))

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
