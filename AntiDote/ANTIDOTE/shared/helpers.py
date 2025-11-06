import streamlit as st
from pathlib import Path

def load_css(file_path):
    """Load and inject CSS file into Streamlit app."""
    try:
        # Get current file directory (shared/)
        current_dir = Path(__file__).parent
        css_path = current_dir / file_path

        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file not found: {css_path}")
