import streamlit as st
from shared.helpers import load_css

st.set_page_config(page_title="ALZY – Memory Assistant", layout="centered")
load_css("style.css")

# Role selection only if role not set
if st.session_state.get("role") is None:
    st.title("🧠 ALZY – Memory Assistant")
    st.markdown("Select your role to continue:")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👩‍🦳 Patient", use_container_width=True):
            st.session_state.role = "patient"
            st.experimental_rerun()  # safer fallback
    with col2:
        if st.button("🧑‍⚕️ Caregiver", use_container_width=True):
            st.session_state.role = "caregiver"
            st.experimental_rerun()
else:
    # Redirect automatically based on role
    role = st.session_state["role"]
    if role == "patient":
        st.experimental_rerun()  # rerun will take user to Patient page if you handle role there
    elif role == "caregiver":
        st.experimental_rerun()  # same for Caregiver
