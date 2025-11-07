import streamlit as st
from shared.helpers import load_css, get_openai_client

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="Patient Assistant", layout="wide")

# ===============================
# LOAD CUSTOM CSS
# ===============================
load_css("shared/style.css")

# ===============================
# INIT OPENAI CLIENT
# ===============================
client = get_openai_client()

# ===============================
# HEADER
# ===============================
st.markdown("<h2>🧠 ALZY – Patient Memory Assistant</h2>", unsafe_allow_html=True)
st.markdown("<p>Type or speak your question below to interact.</p>", unsafe_allow_html=True)

# ===============================
# CHAT HISTORY
# ===============================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ===============================
# USER INPUT AREA
# ===============================
col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.text_input("💬 Your Message:", placeholder="Ask something...")

with col2:
    record = st.button("🎙️ Speak")

# (Optional) Voice input simulation
if record:
    st.info("🎤 Voice input feature coming soon!")

# ===============================
# PROCESS CHAT
# ===============================
if st.button("Send", use_container_width=True) and user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You are a kind memory assistant for patients."}] +
                         st.session_state.chat_history
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"⚠️ API Error: {e}"
    else:
        reply = "🧠 (Offline mode) This is a simulated response."

    st.session_state.chat_history.append({"role": "assistant", "content": reply})

# ===============================
# DISPLAY CHAT
# ===============================
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"🧑 **You:** {msg['content']}")
    else:
        st.markdown(f"🤖 **Alzy:** {msg['content']}")

# ===============================
# FOOTER
# ===============================
st.markdown("<br><hr><center>🧬 ALZY – An AntiDote Project</center>", unsafe_allow_html=True)
