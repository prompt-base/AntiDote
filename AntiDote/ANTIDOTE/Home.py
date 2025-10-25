# ANTIDOTE/Home.py
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="ANTIDOTE — Care Toolkit",
    page_icon="🧩",
    layout="wide"
)

# ---------- Colorful theme (CSS) ----------
st.markdown("""
<style>
/* Full-page animated gradient */
.stApp {
  background: linear-gradient(120deg,#f9f9ff 0%,#e8f0ff 35%,#ffe9f3 70%,#fff8e6 100%);
  background-size: 200% 200%;
  animation: bgmove 14s ease infinite;
}
@keyframes bgmove {
  0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%}
}

/* Center container */
.hero {
  padding: 24px 28px;
  border-radius: 22px;
  backdrop-filter: blur(6px);
  background: rgba(255,255,255,0.6);
  box-shadow: 0 20px 60px rgba(58,111,247,0.18);
  border: 1px solid rgba(255,255,255,0.7);
}

/* Headline */
h1.hero-title {
  font-size: 46px;
  line-height: 1.15;
  margin: 0 0 6px 0;
  background: linear-gradient(90deg,#6a11cb,#2575fc,#ff7eb3,#ffc371);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}

/* Subheadline */
p.hero-sub {
  font-size: 16px;
  color: #334155;
  margin-top: 4px;
}

/* Pill chips */
.pill {
  display:inline-block; padding:6px 12px; border-radius:999px;
  background:#ffffff; border:1px solid #e6eaff; color:#3A6FF7; font-weight:600;
  margin-right:8px; margin-bottom:8px; font-size:12px;
}

/* Feature cards */
.card {
  border-radius:18px; padding:18px; height:100%;
  background: linear-gradient(145deg,#ffffff 0%,#f0f4ff 100%);
  border:1px solid #e8ecff;
  box-shadow: 0 12px 30px rgba(37,117,252,0.12);
}
.card h3 { margin-top:0; color:#1e293b; }
.card p { color:#475569; }

/* CTA button */
a.cta {
  display:inline-block; text-decoration:none; font-weight:700;
  padding:10px 16px; border-radius:12px; color:#fff;
  background: linear-gradient(90deg,#6a11cb 0%,#2575fc 100%);
  box-shadow: 0 10px 24px rgba(37,117,252,0.25);
  border: 0;
}
a.cta:hover { filter: brightness(1.05); }

/* Small footer */
.footer { color:#475569; font-size:12px; }
</style>
""", unsafe_allow_html=True)

# ---------- Hero ----------
st.markdown(
    """
<div class="hero">
  <h1 class="hero-title">🧩 ANTIDOTE — Care Toolkit</h1>
  <p class="hero-sub">
    A colorful hub for memory assistance and hands-free communication.
  </p>
  <div>
    <span class="pill">🧠 Reminders & Face Quiz</span>
    <span class="pill">🤟 ASL Recognition</span>
    <span class="pill">⚡ Fast & Private (local)</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")

# ---------- Feature cards ----------
col1, col2, col3 = st.columns([1.05, 1.05, 0.9])

with col1:
    st.markdown(
        """
<div class="card">
  <h3>🧠 Memory Assistant</h3>
  <p>Create image/audio-first reminders, manage loved ones, and practice recognition with spaced repetition.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    # Link to the Memory Assistant page
    if hasattr(st, "page_link"):
        st.page_link("pages/Alzy--Beta.py", label="Open Memory Assistant", icon="🧠")
    else:
        st.markdown('<a class="cta" href="#" title="Use the Pages sidebar → Memory Assistant">Open Memory Assistant</a>', unsafe_allow_html=True)

with col2:
    st.markdown(
        """
<div class="card">
  <h3>🤟 ASL Sign</h3>
  <p>Use your webcam to collect examples and train a k-NN recognizer on the fly (MediaPipe, no OpenCV).</p>
</div>
""",
        unsafe_allow_html=True,
    )
    # Link to the ASL page
    if hasattr(st, "page_link"):
        st.page_link("pages/Signalink--Beta.py", label="Open ASL Sign", icon="🤟")
    else:
        st.markdown('<a class="cta" href="#" title="Use the Pages sidebar → ASL Sign">Open ASL Sign</a>', unsafe_allow_html=True)

with col3:
    st.markdown(
        """
<div class="card">
  <h3>🎛️ Tips</h3>
  <p>Use good lighting, keep the hand centered for ASL, and attach photos/voice cues to make reminders easier to recognize.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='footer'>Last loaded: {datetime.now().strftime('%b %d, %Y • %I:%M %p')}</div>",
        unsafe_allow_html=True,
    )

st.write("")
st.info("Use the **Pages** menu (left) to navigate. If you see buttons above, they’ll jump straight to each page.")
