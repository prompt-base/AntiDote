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
.stApp {
  background: linear-gradient(135deg, #0f172a 0%, #0f172a 40%, #111827 100%);
  color: #ffffff;
  font-family: 'Poppins', sans-serif;
  min-height: 100vh;
}
h1,h2,h3,h4 { color: #ffffff !important; }

.section-title {
  font-size: 2.4rem;
  font-weight: 800;
  letter-spacing: .02em;
  margin-bottom: .8rem;
  text-align: center;
}

.sub-text {
  opacity: .75;
  text-align: center;
  margin-bottom: 2rem;
}

/* Floating gif */
.floating-gif {
  position: fixed;
  top: 15px;
  left: 15px;
  width: 80px;
  height: 80px;
  z-index: 9999;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 6px 18px rgba(0,0,0,0.25);
}
.floating-gif img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Feature boxes */
.feature-box {
  background: linear-gradient(135deg, rgba(37,99,235,0.35), rgba(14,165,233,0.25));
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 20px;
  padding: 24px 16px;
  min-height: 160px;
  box-shadow: 0 15px 45px rgba(0,0,0,0.15);
  text-align: center;
  transition: transform .25s ease, box-shadow .25s ease;
  cursor: pointer;
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

/* About + Team + School sections */
.info-box {
  background: rgba(15,23,42,0.4);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 25px;
  margin: 25px 0;
  box-shadow: 0 10px 30px rgba(0,0,0,0.15);
}

.team-card {
  text-align: center;
  background: rgba(255,255,255,0.05);
  padding: 15px;
  border-radius: 15px;
  margin: 10px;
  transition: transform .3s ease;
}
.team-card:hover {
  transform: scale(1.05);
  background: rgba(255,255,255,0.08);
}
.team-card img {
  border-radius: 50%;
  width: 140px;
  height: 140px;
  object-fit: cover;
  margin-bottom: 10px;
  border: 2px solid rgba(255,255,255,0.25);
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
# FEATURE BOXES (three apps)
# ===============================
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🧠 Open ALZY", use_container_width=True, key="btn_alzy"):
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
    if st.button("📶 Open SIGNA·LINK", use_container_width=True, key="btn_signalink"):
        st.switch_page("pages/SignaLink--Beta.py")
    st.markdown("""
    <div class='feature-box'>
        <div class='feature-title'>SIGNA·LINK</div>
        <div class='feature-desc'>
            A voice-free communication tool for speech-impaired users using gestures & text.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if st.button("🦯 Open UNSEEN", use_container_width=True, key="btn_unseen"):
        st.switch_page("pages/Unseen--Beta.py")
    st.markdown("""
    <div class='feature-box'>
        <div class='feature-title'>UNSEEN</div>
        <div class='feature-desc'>
            Navigation and voice-assist system for visually impaired users.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ===============================
# ABOUT PROJECT SECTION
# ===============================
st.markdown("<div class='section-title'>📘 About the Project</div>", unsafe_allow_html=True)
st.markdown("""
<div class='info-box'>
<b>AntiDote Care Toolkit</b> is a unified assistive technology platform designed to support individuals with cognitive, speech, and vision disabilities. 
It comprises three smart modules:
<ul>
<li><b>ALZY:</b> A Memory Assistant for Alzheimer’s patients with reminders, caregiver tools, and GPS tracking.</li>
<li><b>SIGNA·LINK:</b> A gesture and text-based voice-free communication system for speech-impaired users.</li>
<li><b>UNSEEN:</b> A navigation and voice-assist solution for visually impaired individuals.</li>
</ul>
This project aims to leverage AI, IoT, and accessible design to enhance independence, safety, and communication for differently-abled users.
</div>
""", unsafe_allow_html=True)

# ===============================
# TEAM MEMBERS SECTION
# ===============================
st.markdown("<div class='section-title'>👥 Team Members</div>", unsafe_allow_html=True)
team_members = [
    {"name": "Anurag Mondal", "class": "8-C", "img": "https://raw.githubusercontent.com/prompt-base/AntiDote/main/AntiDote/ANTIDOTE/images/anurag.jpg"},
    {"name": "Aarav", "class": "8-C", "img": "https://raw.githubusercontent.com/prompt-base/AntiDote/main/AntiDote/ANTIDOTE/images/aarav.jpg"},
    {"name": "Tejash", "class": "8-A", "img": "https://raw.githubusercontent.com/prompt-base/AntiDote/main/AntiDote/ANTIDOTE/images/tejash.jpg"},
    {"name": "Priyanshu", "class": "8-A", "img": "https://raw.githubusercontent.com/prompt-base/AntiDote/main/AntiDote/ANTIDOTE/images/priyanshu.jpg"},
]

cols = st.columns(4)
for i, member in enumerate(team_members):
    with cols[i]:
        st.markdown(f"""
        <div class='team-card'>
            <img src='{member['img']}' alt='{member['name']}'>
            <h4>{member['name']}</h4>
            <p>Class {member['class']}</p>
        </div>
        """, unsafe_allow_html=True)

# ===============================
# ABOUT SCHOOL SECTION
# ===============================
st.markdown("<div class='section-title'>🏫 About the School</div>", unsafe_allow_html=True)
st.markdown("""
<div class='info-box'>
<b><a href='https://sriaurobindoschools.org' target='_blank' style='color:#60a5fa;text-decoration:none;'>The Future Foundation School</a></b> 
is inspired by the teachings of Sri Aurobindo and The Mother.  
It aims to cultivate holistic development — intellectual, emotional, and spiritual — in every student.  
The school encourages innovation, empathy, and collaboration, which inspired the creation of the <b>AntiDote Care Toolkit</b> by its students.
</div>
""", unsafe_allow_html=True)
