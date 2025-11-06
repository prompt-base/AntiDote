import streamlit as st

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="AntiDote Care Toolkit", layout="wide")

# ===============================
# GLOBAL STYLING
# ===============================
st.markdown("""
<style>
/* App background */
.stApp {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
  color: #ffffff;
  min-height: 100vh;
}
h1, h2, h3, h4 {
  color: #ffffff !important;
}

/* Titles */
.section-title {
  font-size: 2.2rem;
  font-weight: 800;
  letter-spacing: .02em;
  margin: 1.2rem 0 0.5rem 0;
  text-align: center;
}
.sub-text {
  opacity: 0.75;
  text-align: center;
  margin-bottom: 2rem;
}

/* Floating gif */
.floating-gif {
  position: fixed;
  top: 10px;
  left: 10px;
  width: 85px;
  height: 85px;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 6px 18px rgba(0,0,0,0.25);
  z-index: 9999;
}
.floating-gif img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Custom Buttons */
div.stButton > button:first-child {
    background: linear-gradient(135deg, #2563eb, #1e40af);
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 12px;
    padding: 10px 22px;
    font-size: 1rem;
    font-weight: 600;
    transition: all 0.3s ease;
}
div.stButton > button:first-child:hover {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: #ffffff !important;
    transform: translateY(-2px);
    box-shadow: 0 0 15px rgba(37,99,235,0.5);
}

/* Feature Boxes */
.feature-box {
  background: linear-gradient(135deg, rgba(37,99,235,0.35), rgba(14,165,233,0.25));
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 20px;
  padding: 24px 16px;
  height: 220px;
  box-shadow: 0 15px 45px rgba(0,0,0,0.15);
  text-align: center;
  transition: transform .25s ease, box-shadow .25s ease;
}
.feature-box:hover {
  transform: translateY(-5px);
  box-shadow: 0 18px 48px rgba(0,0,0,0.25);
  border-color: rgba(255,255,255,0.35);
}
.feature-title {
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: .4rem;
}
.feature-desc {
  font-size: .95rem;
  opacity: .8;
  margin-top: .4rem;
}

/* Team Section */
.team-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 16px;
  text-align: center;
  transition: all 0.3s ease;
  height: 320px;
}
.team-card:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.2);
}
.team-card img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 12px;
  margin-bottom: 10px;
}
.team-name {
  font-size: 1.1rem;
  font-weight: 600;
}
.team-class {
  opacity: 0.8;
  font-size: 0.9rem;
}

/* About box */
.about-box {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 24px;
  text-align: justify;
}
</style>

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
# FEATURE BOXES SECTION
# ===============================
col1, col2, col3 = st.columns(3)

with col1:
    st.button("🧠 Open ALZY", use_container_width=True, key="btn_alzy")
    st.switch_page("pages/Alzy--Beta.py")
    st.markdown("""
    <div class='feature-box'>
        <div class='feature-title'>ALZY</div>
        <div class='feature-desc'>
            Memory Assistant for Alzheimer’s patients with reminders, caregiver tools & GPS tracking.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.button("📶 Open SIGNA·LINK", use_container_width=True, key="btn_signalink")
    st.switch_page("pages/SignaLink--Beta.py")  
    st.markdown("""
    <div class='feature-box'>
        <div class='feature-title'>SIGNA·LINK</div>
        <div class='feature-desc'>
            A gesture and text-based voice-free communication platform for speech-impaired users.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.button("🦯 Open UNSEEN", use_container_width=True, key="btn_unseen")
    st.switch_page("pages/Unseen--Beta.py")
    st.markdown("""
    <div class='feature-box'>
        <div class='feature-title'>UNSEEN</div>
        <div class='feature-desc'>
            Navigation and voice-assist system for visually impaired individuals to move safely and independently.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ===============================
# ABOUT PROJECT SECTION
# ===============================
st.markdown("<div class='section-title'>💡 About the Project</div>", unsafe_allow_html=True)
st.markdown("""
<div class='about-box'>
The <b>AntiDote Care Toolkit</b> is a unified platform designed to support individuals with cognitive, speech, and vision disabilities.
It integrates three innovative modules — <b>ALZY</b>, <b>SIGNA·LINK</b>, and <b>UNSEEN</b> — providing personalized digital assistance and accessibility tools.

The project focuses on bridging the gap between patients and caregivers using AI-powered interfaces,
gesture-based communication, and audio navigation technologies — creating a compassionate and inclusive digital ecosystem.
</div>
""", unsafe_allow_html=True)

# ===============================
# TEAM MEMBERS SECTION
# ===============================
st.markdown("<div class='section-title'>👥 Our Team</div>", unsafe_allow_html=True)
cols = st.columns(4)

team_data = [
    {"img": "https://raw.githubusercontent.com/prompt-base/AntiDote/main/AntiDote/ANTIDOTE/images/aarav.jpg", "name": "Anurag Mondal", "cls": "Class 8 • Section A"},
    {"img": "https://raw.githubusercontent.com/prompt-base/AntiDote/main/AntiDote/ANTIDOTE/images/anurag.jpg", "name": "Aarav", "cls": "Class 8 • Section A"},
    {"img": "https://raw.githubusercontent.com/prompt-base/AntiDote/main/AntiDote/ANTIDOTE/images/tejash.jpg", "name": "Tejash", "cls": "Class 8 • Section A"},
    {"img": "https://raw.githubusercontent.com/prompt-base/AntiDote/main/AntiDote/ANTIDOTE/images/priyanshu.jpg", "name": "Priyanshu", "cls": "Class 8 • Section A"}
]

for i, t in enumerate(team_data):
    with cols[i]:
        st.markdown(f"""
        <div class='team-card'>
            <img src="{t['img']}" alt="{t['name']}">
            <div class='team-name'>{t['name']}</div>
            <div class='team-class'>{t['cls']}</div>
        </div>
        """, unsafe_allow_html=True)

# ===============================
# ABOUT SCHOOL SECTION
# ===============================
st.markdown("<div class='section-title'>🏫 About Our School</div>", unsafe_allow_html=True)
st.markdown("""
<div class='about-box'>
<b><a href='https://sriaurobindoschools.org' target='_blank' style='color:#60a5fa;text-decoration:none;'>The Future Foundation School</a></b> 
is inspired by the teachings of Sri Aurobindo and The Mother.  
It aims to cultivate holistic development — intellectual, emotional, and spiritual — in every student.  
The school encourages innovation, empathy, and collaboration, which inspired the creation of the <b>AntiDote Care Toolkit</b> by its students.
</div>
""", unsafe_allow_html=True)

