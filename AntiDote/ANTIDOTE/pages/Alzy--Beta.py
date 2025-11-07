import streamlit as st
from shared.helpers import load_css

st.set_page_config(page_title="ALZY – Memory Assistant", layout="centered")
load_css("style.css")

st.title("🧠 ALZY – Memory Assistant")
st.markdown("Select your role to continue:")

col1, col2 = st.columns(2)

with col1:
    if st.button("👩‍🦳 Patient", use_container_width=True):
        st.switch_page("pages/Patient.py")

with col2:
    if st.button("🧑‍⚕️ Caregiver", use_container_width=True):
        st.switch_page("pages/Caregiver.py")

