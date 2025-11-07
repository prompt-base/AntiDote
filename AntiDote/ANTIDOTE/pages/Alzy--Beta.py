# pages/Alzy--Beta.py
import streamlit as st
from shared.helpers import load_css

st.set_page_config(page_title="ALZY – Memory Assistant", layout="centered")
load_css("style.css")

# -------------------------------
# Role check at top
# -------------------------------
if st.session_state.get("role") is None:
    st.title("🧠 ALZY – Memory Assistant")
    st.markdown("Select your role to continue:")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👩‍🦳 Patient", use_container_width=True):
            st.session_state.role = "patient"
            st.switch_page("Patient")  # just page name, not path
    with col2:
        if st.button("🧑‍⚕️ Caregiver", use_container_width=True):
            st.session_state.role = "caregiver"
            st.switch_page("Caregiver")  # just page name
else:
    # Optional: redirect automatically if role is already set
    role = st.session_state["role"]
    if role == "patient":
        st.switch_page("Patient")
    elif role == "caregiver":
        st.switch_page("Caregiver")
