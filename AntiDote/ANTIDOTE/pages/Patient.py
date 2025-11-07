# ==============================================
# pages/Patient.py
# ==============================================
import streamlit as st
from shared.helpers import load_css, get_openai_client

# ----------------------------------------------
# Page Config
# ----------------------------------------------
st.set_page_config(page_title="AntiDote – Patient Assistant", layout="wide")

# ----------------------------------------------
# Load Styles
# ----------------------------------------------
load_css("shared/style.css")

# ----------------------------------------------
# Initialize OpenAI Client
# ----------------------------------------------
client = get_openai_client()

st.title("🧠 ALZY – Memory Assistant (Patient)")

st.markdown("""
Welcome to the **Alzy Patient Companion** — your friendly reminder and communication assistant.  
Type or speak your question below to interact.
""")

# ----------------------------------------------
# Text Chat Section
# ----------------------------------------------
user_input = st.text_input("💬 Type your question here:")
if st.button("Send"):
    if not client:
        st.warning("⚠️ AI not connected. Please check your API key setup.")
    elif user_input:
        with st.spinner("Thinking..."):
            try:
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=user_input
                )
                st.success(response.output[0].content[0].text)
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ----------------------------------------------
# Optional Voice Section (Future)
# ----------------------------------------------
st.markdown("---")
st.markdown("🎙️ *Voice interaction feature coming soon!*")
