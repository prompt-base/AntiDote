# ANTIDOTE/shared/helpers.py  (replace old load_css with this)
import streamlit as st
from pathlib import Path
import os
from openai import OpenAI

def load_css(candidate: str = "style.css"):
    """
    Robust CSS loader.
    - candidate: filename OR relative path (e.g. "style.css" or "shared/style.css").
    This function will try several likely locations and inject the CSS if found.
    """
    try:
        tried = []

        # 1) If an absolute path was passed, try it first
        cand_path = Path(candidate)
        if cand_path.is_absolute():
            tried.append(str(cand_path))
            if cand_path.exists():
                _inject_css(cand_path)
                return
        # 2) Path relative to this helpers.py file (shared/)
        base_shared = Path(__file__).parent  # .../ANTIDOTE/shared
        p1 = base_shared / candidate
        tried.append(str(p1))
        if p1.exists():
            _inject_css(p1)
            return

        # 3) candidate relative to repo package root (ANTIDOTE/)
        package_root = base_shared.parent  # .../ANTIDOTE
        p2 = package_root / candidate
        tried.append(str(p2))
        if p2.exists():
            _inject_css(p2)
            return

        # 4) candidate relative to current working directory (where Streamlit is running)
        cwd = Path.cwd()
        p3 = cwd / candidate
        tried.append(str(p3))
        if p3.exists():
            _inject_css(p3)
            return

        # 5) If user passed "shared/style.css" and we already tried shared/<that>, try removing leading "shared/"
        # (already covered by p2/p3, but keep for completeness)
        if str(candidate).startswith("shared" + os.sep):
            alt = candidate.split(os.sep, 1)[1]
            p4 = base_shared / alt
            tried.append(str(p4))
            if p4.exists():
                _inject_css(p4)
                return

        # Not found — show clear diagnostics
        st.error("❌ CSS file not found. Paths tried:")
        for t in tried:
            st.write(f"- {t}")
        st.info("Tip: If your style.css file is located in ANTIDOTE/shared/style.css, call `load_css(\"style.css\")` and make sure the file is committed to the repository.")
    except Exception as e:
        st.error(f"⚠️ Error in load_css: {e}")


def _inject_css(path: Path):
    """Helper: read and inject CSS, with success message."""
    try:
        text = path.read_text(encoding="utf-8")
        st.markdown(f"<style>{text}</style>", unsafe_allow_html=True)
        st.write(f"✅ Loaded CSS from: `{path}`")
    except Exception as e:
        st.error(f"⚠️ Failed to read/inject CSS: {e}")


# keep get_openai_client below (unchanged)
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
