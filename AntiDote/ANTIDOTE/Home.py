import streamlit as st
from shared.helpers import load_css

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="AntiDote Care Toolkit", layout="wide")

# ===============================
# GLOBAL STYLING
# ===============================
# Load CSS once from shared/style.css
load_css("style.css")

# Floating gif
st.markdown("""
<div class="floating-gif">
  <img src="https://i.pinimg.com/originals/e9/f7/bf/e9f7bf6cd7b5f1f6b954ed7be35d8aac.gif">
</div>
""", unsafe_allow_html=True)

# ===============================
# HEADER
# ===============================
st.markdown("<div class='section-title'>🧪 AntiDote Care Toolkit</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-text'>Unified support for cognitive, speech, and vision disabilities.</div>", unsafe_allow_html=True)

# ===============================
# FEATURE BOXES (three apps)
# ===============================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='feature-box'>
        <div class='feature-title'>ALZY</div>
        <div class='feature-desc'>
            Memory Assistant for Alzheimer’s patients with reminders, caregiver tools & GPS tracking.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🧠 Open ALZY", use_container_width=True):
        st.switch_page("pages/Alzy--Beta.py")

with col2:
    st.markdown("""
    <div class='feature-box'>
        <div class='feature-title'>SIGNA·LINK</div>
        <div class='feature-desc'>
            A voice-free communication tool for speech-impaired users using gestures & text.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("📶 Open SIGNA·LINK", use_container_width=True):
        st.switch_page("pages/SignaLink--Beta.py")

with col3:
    st.markdown("""
    <div class='feature-box'>
        <div class='feature-title'>UNSEEN</div>
        <div class='feature-desc'>
            Navigation and voice-assist system for visually impaired users.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🦯 Open UNSEEN", use_container_width=True):
        st.switch_page("pages/Unseen--Beta.py")

# ===============================
# ABOUT THE PROJECT
# ===============================
st.markdown("<br><br><div class='section-title'>🧬 About the Project</div>", unsafe_allow_html=True)
st.markdown("""
The **AntiDote Care Toolkit** is an integrated assistive technology suite designed to empower individuals
with cognitive, speech, and vision disabilities. It combines three innovative solutions — **ALZY**, **SIGNA·LINK**, 
and **UNSEEN** — into one unified platform.  
Each module addresses unique needs through AI-assisted communication, memory, and navigation tools.
""")

# ===============================
# TEAM MEMBERS
# ===============================
st.markdown("<br><div class='section-title'>👩‍💻 Team Members</div>", unsafe_allow_html=True)

team = [
    {"name": "Anurag Mondal", "class": "8-C", "img": "https://raw.githubusercontent.com/prompt-base/AntiDote/main/AntiDote/ANTIDOTE/images/anurag.jpg"},
    {"name": "Aarav Kumar Shaw", "class": "8-C", "img": "https://raw.githubusercontent.com/prompt-base/AntiDote/main/AntiDote/ANTIDOTE/images/aarav.jpg"},
    {"name": "Tejas Singh", "class": "8-A", "img": "https://raw.githubusercontent.com/prompt-base/AntiDote/main/AntiDote/ANTIDOTE/images/tejash.jpg"},
    {"name": "Priyanshu Das", "class": "8-A", "img": "https://raw.githubusercontent.com/prompt-base/AntiDote/main/AntiDote/ANTIDOTE/images/priyanshu.jpg"},
]

cols = st.columns(4)
for i, member in enumerate(team):
    with cols[i % 4]:
        st.markdown(f"""
        <div class='team-card'>
            <img src='{member["img"]}' alt='{member["name"]}'>
            <div class='team-name'>{member["name"]}</div>
            <div class='team-class'>{member["class"]}</div>
        </div>
        """, unsafe_allow_html=True)

# ===============================
# ABOUT THE SCHOOL
# ===============================
st.markdown("""
<br><br>
<div style='text-align:center;'>
    <h2 style='color:#2563eb; font-size:28px; font-weight:700;'>🏫 About the School</h2>
    <p style='font-size:17px; line-height:1.6; color:#d1d5db; max-width:800px; margin: 10px auto;'>
        <a href='https://sriaurobindoschools.org' target='_blank' 
           style='color:#60a5fa; font-weight:600; text-decoration:none;'>
           The Future Foundation School
        </a> 
        is inspired by the profound teachings of <b>Sri Aurobindo</b> and <b>The Mother</b>.  
        It strives to nurture every student’s <b>intellectual</b>, <b>emotional</b>, and <b>spiritual</b> growth through a 
        harmonious blend of values and modern learning.  
        The school fosters creativity, empathy, and teamwork — values that inspired the creation of the 
        <b>AntiDote Care Toolkit</b> by its young innovators.
    </p>
</div>
""", unsafe_allow_html=True)





