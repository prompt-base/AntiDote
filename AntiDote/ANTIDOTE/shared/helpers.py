import streamlit as st
from pathlib import Path
import os
from openai import OpenAI

# =====================================
# Load CSS File
# =====================================
def load_css(file_path):
    """Load and inject CSS file into Streamlit app."""
    try:
        current_dir = Path(__file__).parent
        css_path = current_dir / file_path

        if not css_path.exists():
            st.error(f"❌ CSS file not found: {css_path}")
            return

        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"⚠️ Error loading CSS: {e}")


# =====================================
# OpenAI Client Loader
# =====================================
def get_openai_client():
    """Return a configured OpenAI client using Streamlit secrets or environment variable."""
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
        if not api_key:
            st.warning("⚠️ OpenAI API key not found. Running in mock mode.")
            return None  # Return None instead of stopping app (safe for demo mode)
        return OpenAI(api_key=api_key)
    except Exception as e:
        st.error(f"⚠️ Error initializing OpenAI client: {e}")
        return None
