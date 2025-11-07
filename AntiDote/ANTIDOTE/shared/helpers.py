# ==============================================
# shared/helpers.py
# ==============================================
import streamlit as st
from openai import OpenAI

# ----------------------------------------------
# Load CSS (Unified styling)
# ----------------------------------------------
def load_css(file_path):
    """Load and apply custom CSS from shared/style.css"""
    try:
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"❌ CSS file not found: {file_path}")


# ----------------------------------------------
# OpenAI Client Loader
# ----------------------------------------------
def get_openai_client():
    """Initialize OpenAI client using Streamlit secrets"""
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
        if not api_key:
            st.error("⚠️ OpenAI API key is empty. Please check your Streamlit secrets.")
            return None
        client = OpenAI(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"❌ Error loading OpenAI client: {e}")
        return None
