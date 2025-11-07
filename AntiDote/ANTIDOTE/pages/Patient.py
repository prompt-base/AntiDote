import streamlit as st
from shared.helpers import load_css, get_openai_client
from utils.alzy_utils import get_due_reminders

st.set_page_config(page_title="ALZY – Patient", layout="wide")
load_css("shared/style.css")

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
