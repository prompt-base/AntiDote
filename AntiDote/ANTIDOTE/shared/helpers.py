import streamlit as st
from pathlib import Path
import os
from openai import OpenAI

# =====================================
# Load CSS File (clean + silent)
# =====================================
def load_css(candidate: str = "style.css"):
    """
    Load and inject CSS into Streamlit app.
    Automatically searches common locations.
    """
    try:
        base_shared = Path(__file__).parent  # .../ANTIDOTE/shared
        paths_to_try = [
            Path(candidate),
            base_shared / candidate,
            base_shared.parent / candidate,
            Path.cwd() / candidate,
        ]

        for path in paths_to_try:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
                return  # ✅ stop after successful load

        # if not found, show a single clean error (no ✅ messages)
        st.error(f"❌ CSS file not found: {candidate}")
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
