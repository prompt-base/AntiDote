import streamlit as st
from ANTIDOTE.shared.helpers import load_css, get_openai_client
from utils.alzy_utils import add_reminder, load_data

st.set_page_config(page_title="ALZY – Caregiver", layout="centered")
load_css("shared/style.css")

st.title("🧑‍⚕️ Caregiver Dashboard")
st.markdown("Add reminders or view logs for your patient.")

# =======================
# Add Reminder
# =======================
with st.form("reminder_form"):
    task = st.text_input("Reminder Task")
    time = st.time_input("Time")
    submitted = st.form_submit_button("Add Reminder")
    if submitted and task:
        add_reminder(task, time.strftime("%H:%M"))
        st.success("✅ Reminder added successfully!")

# =======================
# Reminder List
# =======================
st.subheader("📋 All Reminders")
data = load_data()
if data["reminders"]:
    for r in data["reminders"]:
        st.write(f"🕒 {r['time']} — {r['task']}")
else:
    st.info("No reminders yet.")
