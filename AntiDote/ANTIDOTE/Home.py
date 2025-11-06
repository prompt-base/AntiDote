import streamlit as st

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="AntiDote Care Toolkit", layout="wide")

# ===============================
# GLOBAL STYLING (Dark blue gradient + buttons)
# ===============================
st.markdown("""
<style>
.stApp {
  background: linear-gradient(135deg, #0f172a 0%, #0f172a 40%, #111827 100%);
  color: #ffffff;
  min-height: 100vh;
  font-family: 'Segoe UI', sans-serif;
}
h1,h2,h3,h4 { color: #ffffff !important; }

.section-title {
  font-size: 2.4rem;
  font-weight: 800;
  letter-spacing: .02em;
  margin-bottom: .4rem;
}

.sub-text {
  opacity: .75;
  margin-bottom: 1.6rem;
}

/* Floating gif */
.floating-gif {
  position: fixed;
  top: 12px;
  left: 12px;
  width: 85px;
  height: 85px;
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
  min-height: 260px;
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

/* Custom Streamlit buttons */
div.stButton > button:first-child {
    background: linear-gradient(135deg, #2563eb, #1e40af);
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 12px;
    padding: 10px 20px;
    font-size: 1rem;
    font-weight: 600;
    transition: all 0.3s ease;
}
div.stButton > button:first-child:hover {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    transform: translateY(-2px);
    box-shadow: 0 0 15px rgba(37,99,235,0.5);
}
div.stButton > button:focus:not(:active) {
    outline: none;
    box-shadow: 0 0 0 2px rgba(37,99,235,0.3);
}

/* Team member cards */
.team-card {
  background: rgba(15,23,42,0.35);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 18px;
  text-align: center;
  padding: 18px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  min-height: 280px;
}
.team-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.25);
}
.team-card img {
  border-radius: 12px;
  width: 100%;
  height: 180px;
  object-fit: cover;
  margin-bottom: 12px;
}
.team-name {
  font-size: 1.2rem;
  font-weight: 700;
}
.team-class {
  font-size: 0.95rem;
  opacity: 0.8;
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
# TEAM MEMBERS SECTION
# ===============================
st.markdown("<br><div class='section-title'>👩‍💻 Team Members</div>", unsafe_allow_html=True)

team = [
    {"name": "Anurag Mondal", "class": "8-C", "img": "https://raw.githubusercontent.com/prompt-base/AntiDote/main/AntiDote/ANTIDOTE/images/anurag.jpg"},
    {"name": "Aarav", "class": "8-C", "img": "https://raw.githubusercontent.com/prompt-base/AntiDote/main/AntiDote/ANTIDOTE/images/aarav.jpg"},
    {"name": "Tejash", "class": "8-A", "img": "https://raw.githubusercontent.com/prompt-base/AntiDote/main/AntiDote/ANTIDOTE/images/tejash.jpg"},
    {"name": "Priyanshu", "class": "8-A", "img": "https://raw.githubusercontent.com/prompt-base/AntiDote/main/AntiDote/ANTIDOTE/images/priyanshu.jpg"},
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
    <p style='font-size:17px; line-height:1.6; color:#333; max-width:800px; margin: 10px auto;'>
        <a href='https://sriaurobindoschools.org' target='_blank' 
           style='color:#2563eb; font-weight:600; text-decoration:none;'>
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


