import streamlit as st
from pathlib import Path

def load_css(relative_path: str):
    """Safely load a CSS file regardless of working directory."""
    base_path = Path(__file__).parent  # This gives /AntiDote/ANTIDOTE/shared
    css_path = base_path / relative_path  # e.g. shared/style.css -> /AntiDote/ANTIDOTE/shared/style.css

    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ CSS file not found: {css_path}")
