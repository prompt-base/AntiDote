# pages/Alzy--Beta.py
# ===============================
# ALZY – Landing / Role Selection Page
# ===============================
import streamlit as st
from shared.helpers import load_css

# -------------------------------
# Page config & CSS
# -------------------------------
st.set_page_config(page_title="ALZY – Memory Assistant", layout="centered")
load_css("style.css")

# -------------------------------
# Initialize session state
# -------------------------------
if "role" not in st.session_state:
    st.session_state.role = None  # None, "patient", or "caregiver"

# -------------------------------
# Role selection UI
# -------------------------------
if st.session_state.role is None:
    st.title("🧠 ALZY – Memory Assistant")
    st.markdown("Select your role to continue:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("👩‍🦳 Patient", key="btn_patient"):
            st.session_state.role = "patient"
            st.experimental_rerun()  # safe: only triggered by button click

    with col2:
        if st.button("🧑‍⚕️ Caregiver", key="btn_caregiver"):
            st.session_state.role = "caregiver"
            st.experimental_rerun()  # safe: only triggered by button click

# -------------------------------
# Role already selected
# -------------------------------
else:
    st.success(f"Role selected: **{st.session_state.role.capitalize()}**")
    st.markdown("Use the buttons below to navigate or go back:")

    col1, col2 = st.columns(2)

    # Back button to role selection
    with col1:
        if st.button("🔙 Back to role selection", key="back_role"):
            st.session_state.role = None
            st.experimental_rerun()  # safe: only triggered by button click

    # Navigate to the appropriate page
    with col2:
        if st.session_state.role == "patient":
            if st.button("➡️ Go to Patient", key="go_patient"):
                # Optional: clear query params
                st.experimental_set_query_params()
                # Try to use switch_page if available
                try:
                    from streamlit import switch_page
                    switch_page("Patient")  # name of the page file without .py
                except Exception:
                    st.info("Cannot navigate automatically. Please click the Patient tab manually.")

        elif st.session_state.role == "caregiver":
            if st.button("➡️ Go to Caregiver", key="go_caregiver"):
                st.experimental_set_query_params()
                try:
                    from streamlit import switch_page
                    switch_page("Caregiver")  # name of the page file without .py
                except Exception:
                    st.info("Cannot navigate automatically. Please click the Caregiver tab manually.")
