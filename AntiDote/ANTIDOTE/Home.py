import streamlit as st
from pathlib import Path
import uuid

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="AntiDote Care Toolkit", layout="wide")

# ===============================
# GLOBAL STYLING (Dark blue gradient)
# ===============================
st.markdown("""
<style>
.stApp {
  background: linear-gradient(135deg, #0f172a 0%, #0f172a 40%, #111827 100%);
  color: #ffffff;
  min-height: 100vh;
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

/* About section */
.about-box {
  background: rgba(15,23,42,0.25);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 18px;
  margin-top: 30px;
}
</style>

<div class="floating-gif">
  <img src="https://i.pinimg.com/originals/e9/f7/bf/e9f7bf6cd7b5f1f6b954ed7be35d8aac.gif">
</div>
""", unsafe_allow_html=True)

# ===============================
# PATHS
# ===============================
ABOUT_IMG_DIR = Path("about_uploads")
ABOUT_IMG_DIR.mkdir(exist_ok=True, parents=True)

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
    if st.button("🧠 Open ALZY ", use_container_width=True, key="btn_alzy"):
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
# ABOUT-US SECTION
# ===============================
st.markdown("<div class='section-title'>📄 About Us</div>", unsafe_allow_html=True)
st.write("Tell your story — upload images of your team, patients, or fieldwork.")

uploaded_files = st.file_uploader("Upload About-Us Photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
for file in uploaded_files:
    ext = Path(file.name).suffix
    fname = f"{uuid.uuid4().hex}{ext}"
    path = ABOUT_IMG_DIR / fname
    with open(path, "wb") as f:
        f.write(file.read())

# Show gallery
about_imgs = list(ABOUT_IMG_DIR.glob("*.jpg")) + list(ABOUT_IMG_DIR.glob("*.jpeg")) + list(ABOUT_IMG_DIR.glob("*.png"))
if about_imgs:
    cols = st.columns(4)
    for i, img_path in enumerate(about_imgs):
        with cols[i % 4]:
            st.image(str(img_path), use_container_width=True)
else:
    st.caption("No About Us photos yet — upload above.")
import streamlit as st
from pathlib import Path
import uuid

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="AntiDote Care Toolkit", layout="wide")

# ===============================
# GLOBAL STYLING (Dark blue gradient)
# ===============================
st.markdown("""
<style>
.stApp {
  background: linear-gradient(135deg, #0f172a 0%, #0f172a 40%, #111827 100%);
  color: #ffffff;
  min-height: 100vh;
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

/* About section */
.about-box {
  background: rgba(15,23,42,0.25);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 18px;
  margin-top: 30px;
}
</style>

<div class="floating-gif">
  <img src="https://i.pinimg.com/originals/e9/f7/bf/e9f7bf6cd7b5f1f6b954ed7be35d8aac.gif">
</div>
""", unsafe_allow_html=True)

# ===============================
# PATHS
# ===============================
ABOUT_IMG_DIR = Path("about_uploads")
ABOUT_IMG_DIR.mkdir(exist_ok=True, parents=True)

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
# ABOUT-US SECTION
# ===============================
st.markdown("<div class='section-title'>📄 About Us</div>", unsafe_allow_html=True)
st.write("Tell your story — upload images of your team, patients, or fieldwork.")

uploaded_files = st.file_uploader("Upload About-Us Photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
for file in uploaded_files:
    ext = Path(file.name).suffix
    fname = f"{uuid.uuid4().hex}{ext}"
    path = ABOUT_IMG_DIR / fname
    with open(path, "wb") as f:
        f.write(file.read())

# Show gallery
about_imgs = list(ABOUT_IMG_DIR.glob("*.jpg")) + list(ABOUT_IMG_DIR.glob("*.jpeg")) + list(ABOUT_IMG_DIR.glob("*.png"))
if about_imgs:
    cols = st.columns(4)
    for i, img_path in enumerate(about_imgs):
        with cols[i % 4]:
            st.image(str(img_path), use_container_width=True)
else:
    st.caption("No About Us photos yet — upload above.")
import streamlit as st
from pathlib import Path
import uuid

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="AntiDote Care Toolkit", layout="wide")

# ===============================
# GLOBAL STYLING (Dark blue gradient)
# ===============================
st.markdown("""
<style>
.stApp {
  background: linear-gradient(135deg, #0f172a 0%, #0f172a 40%, #111827 100%);
  color: #ffffff;
  min-height: 100vh;
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

/* About section */
.about-box {
  background: rgba(15,23,42,0.25);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 18px;
  margin-top: 30px;
}
</style>

<div class="floating-gif">
  <img src="https://i.pinimg.com/originals/e9/f7/bf/e9f7bf6cd7b5f1f6b954ed7be35d8aac.gif">
</div>
""", unsafe_allow_html=True)

# ===============================
# PATHS
# ===============================
ABOUT_IMG_DIR = Path("about_uploads")
ABOUT_IMG_DIR.mkdir(exist_ok=True, parents=True)

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
# ABOUT-US SECTION
# ===============================
st.markdown("<div class='section-title'>📄 About Us</div>", unsafe_allow_html=True)
st.write("Tell your story — upload images of your team, patients, or fieldwork.")

uploaded_files = st.file_uploader("Upload About-Us Photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
for file in uploaded_files:
    ext = Path(file.name).suffix
    fname = f"{uuid.uuid4().hex}{ext}"
    path = ABOUT_IMG_DIR / fname
    with open(path, "wb") as f:
        f.write(file.read())

# Show gallery
about_imgs = list(ABOUT_IMG_DIR.glob("*.jpg")) + list(ABOUT_IMG_DIR.glob("*.jpeg")) + list(ABOUT_IMG_DIR.glob("*.png"))
if about_imgs:
    cols = st.columns(4)
    for i, img_path in enumerate(about_imgs):
        with cols[i % 4]:
            st.image(str(img_path), use_container_width=True)
else:
    st.caption("No About Us photos yet — upload above.")

