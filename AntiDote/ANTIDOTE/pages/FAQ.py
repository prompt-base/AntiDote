# ANTIDOTE/pages/FAQ.py
import streamlit as st

st.set_page_config(
    page_title="ANTIDOTE – FAQ",
    page_icon="❓",
    layout="wide",
)

# -------------------- THEME / CSS --------------------
st.markdown(
    """
    <style>
    :root{
      --bg0:#0b1220; --bg1:#0f172a; --bg2:#020617;
      --card:#020617;
      --brand:#7c3aed; --brand-2:#22d3ee;
      --ok:#10b981; --warn:#f59e0b; --danger:#ef4444;
      --border:rgba(148,163,184,0.45);
      --muted:rgba(226,232,240,0.82);
    }

    .stApp {
      background:
        radial-gradient(1200px 600px at 5% -10%, #1e293b 0%, var(--bg0) 40%),
        radial-gradient(1000px 500px at 100% 0%, #1f2937 0%, var(--bg1) 35%),
        linear-gradient(180deg, var(--bg0), var(--bg2));
      color:#e5e7eb;
    }

    h1, h2, h3, h4 {
      color:#f9fafb !important;
      letter-spacing:0.03em;
    }

    .faq-hero {
      text-align:center;
      padding: 10px 0 6px 0;
    }

    .faq-pill {
      display:inline-flex;
      align-items:center;
      gap:0.4rem;
      padding:4px 12px;
      border-radius:999px;
      border:1px solid rgba(148,163,184,0.5);
      font-size:0.78rem;
      background:linear-gradient(120deg, rgba(148,163,184,0.16), rgba(15,23,42,0.9));
      color: var(--muted);
    }

    .faq-hero-title {
      font-size:2.0rem;
      font-weight:800;
      margin-top:10px;
      margin-bottom:6px;
      background:linear-gradient(90deg,#e5e7eb,#a5b4fc,#22d3ee);
      -webkit-background-clip:text;
      color:transparent;
    }

    .faq-hero-sub {
      font-size:0.94rem;
      color:var(--muted);
      max-width:540px;
      margin:0 auto;
    }

    .faq-stats-row {
      display:flex;
      flex-wrap:wrap;
      justify-content:center;
      gap:12px;
      margin:18px auto 4px auto;
      max-width:720px;
    }

    .faq-stat-card {
      min-width: 180px;
      flex: 1 1 0;
      padding:10px 12px;
      border-radius:14px;
      border:1px solid rgba(148,163,184,0.55);
      background:radial-gradient(circle at 0 0, rgba(56,189,248,0.18), transparent 60%),
                 radial-gradient(circle at 100% 100%, rgba(129,140,248,0.18), transparent 60%),
                 rgba(15,23,42,0.95);
      box-shadow: 0 12px 30px rgba(15,23,42,0.8);
    }

    .faq-stat-label {
      font-size:0.78rem;
      text-transform:uppercase;
      letter-spacing:0.14em;
      color:rgba(148,163,184,0.9);
      margin-bottom:3px;
    }

    .faq-stat-value {
      font-size:1.15rem;
      font-weight:700;
      color:#e5e7eb;
    }

    .faq-stat-note {
      font-size:0.75rem;
      color:rgba(148,163,184,0.9);
      margin-top:2px;
    }

    .faq-container {
      max-width:900px;
      margin: 10px auto 40px auto;
    }

    .faq-section-label {
      font-size:0.8rem;
      letter-spacing:0.16em;
      text-transform:uppercase;
      color:rgba(148,163,184,0.9);
      margin-bottom:6px;
    }

    .faq-expander {
      border-radius:14px !important;
      border: 1px solid rgba(148,163,184,0.55) !important;
      background: radial-gradient(circle at 0 0, rgba(56,189,248,0.18), transparent 55%),
                  linear-gradient(145deg, rgba(15,23,42,0.96), rgba(15,23,42,0.98));
      box-shadow: 0 10px 25px rgba(15,23,42,0.9);
      padding: 2px 6px !important;
      margin-bottom: 10px;
    }

    .faq-expander:hover {
      border-color: rgba(129,140,248,0.9) !important;
      box-shadow: 0 16px 36px rgba(15,23,42,1);
    }

    .faq-question {
      font-weight:600;
      font-size:0.96rem;
      color:#e5e7eb;
    }

    .faq-answer {
      font-size:0.9rem;
      color:var(--muted);
    }

    .faq-tag-row {
      display:flex;
      flex-wrap:wrap;
      gap:6px;
      margin-bottom:4px;
    }

    .faq-tag {
      font-size:0.72rem;
      padding:2px 8px;
      border-radius:999px;
      border:1px solid rgba(148,163,184,0.6);
      color:rgba(226,232,240,0.9);
      background:rgba(15,23,42,0.85);
    }

    .stButton > button {
      background-image: linear-gradient(90deg, var(--brand), var(--brand-2));
      color: #020617 !important;
      border-radius: 999px !important;
      padding: 6px 16px !important;
      font-weight: 700;
      border:none;
      box-shadow: 0 8px 22px rgba(124,58,237,.55);
      font-size:0.9rem;
    }

    .stButton > button:hover {
      transform: translateY(-1px);
      box-shadow: 0 12px 30px rgba(124,58,237,.7);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- HEADER --------------------
st.markdown(
    """
    <div class="faq-hero">
      <div class="faq-pill">
        <span>🔬 School Science Fair Project</span>
        <span>•</span>
        <span>AI • Memory • Sign Language • Vision</span>
      </div>
      <div class="faq-hero-title">ANTIDOTE – Project FAQ</div>
      <p class="faq-hero-sub">
        ANTIDOTE brings together three ideas – ALZY, SIGNA-LINK, and UNSEEN – to support memory,
        communication, and visual understanding using AI, cameras, and simple interfaces.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------- SMALL STATS (short & simple) --------------------
st.markdown(
    """
    <div class="faq-stats-row">
      <div class="faq-stat-card">
        <div class="faq-stat-label">Why ALZY?</div>
        <div class="faq-stat-value">Memory challenges are rising</div>
        <div class="faq-stat-note">
          Around the world, many older people live with memory loss or early dementia.
          Even small reminders for medicine, faces, and places can reduce confusion and stress.
        </div>
      </div>
      <div class="faq-stat-card">
        <div class="faq-stat-label">Why SIGNA-LINK?</div>
        <div class="faq-stat-value">Sign language is a bridge</div>
        <div class="faq-stat-note">
          Not everyone speaks with voice. Camera-based sign support can help us notice hand shapes 
          and learn basic signs in a playful way.
        </div>
      </div>
      <div class="faq-stat-card">
        <div class="faq-stat-label">Why UNSEEN?</div>
        <div class="faq-stat-value">Images hide stories</div>
        <div class="faq-stat-note">
          Simple AI vision can turn scenes into short descriptions, which can support students
          who prefer listening or need help understanding pictures.
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")
st.markdown('<div class="faq-container">', unsafe_allow_html=True)

# -------------------- FAQ DATA --------------------
faq_blocks = {
    "Our Journey & Motivation": [
        {
            "q": "Why did we start the ANTIDOTE project?",
            "tags": ["Story", "Motivation"],
            "a": """
We noticed three daily situations around us – grandparents forgetting medicine or faces, 
friends being curious about sign language, and students who understand better by hearing 
a picture description instead of only looking at it. We wanted one project that connects 
all three: memory support (ALZY), sign support (SIGNA-LINK), and visual support (UNSEEN) 
using a single AI-powered platform.
""",
        },
        {
            "q": "What difficulties did we face during this project?",
            "tags": ["Challenges", "Learning"],
            "a": """
We faced several challenges: getting the camera and microphone permissions to work in the 
browser, finding the right Python and Mediapipe versions, managing real-time video in 
Streamlit, and keeping the interface simple enough for seniors. Each problem forced us to 
read documentation carefully, test many small changes, and sometimes fully redesign parts 
of the code until the system became stable.
""",
        },
        {
            "q": "What did we learn from solving these problems?",
            "tags": ["Reflection", "Skills"],
            "a": """
We learned to debug step-by-step instead of changing everything at once, to read error 
logs with patience, and to separate the project into clear modules: one for memory, one 
for sign language, and one for vision. We also learned that user experience is as 
important as model accuracy – if the interface is confusing, the smartest AI still feels 
hard to use.
""",
        },
    ],
    "Technology Behind ALZY": [
        {
            "q": "How does ALZY help with memory and medicine reminders?",
            "tags": ["ALZY", "Reminders"],
            "a": """
ALZY stores reminders, photos, and simple step-by-step instructions in a structured JSON 
format. We schedule next reminder times using spaced repetition ideas and local time (IST), 
so medicine alerts and face-recall sessions can repeat gently over days. A chatbot layer 
then uses this stored context – such as today’s date or upcoming reminders – to answer 
questions in short, calm sentences.
""",
        },
        {
            "q": "How are AI models used and connected inside the project?",
            "tags": ["AI", "Architecture"],
            "a": """
For ALZY, we combine rule-based logic (for dates, times, and reminders) with a language 
model. SIGNA-LINK uses Mediapipe to detect hand landmarks and a machine-learning model to 
classify hand shapes. UNSEEN uses image features plus a language model to turn visual 
information into short spoken or written descriptions. All three parts share a common 
idea: the model produces smart suggestions, and the interface shows them in a way that 
feels safe and easy.
""",
        },
        {
            "q": "How did we integrate ChatGPT or similar language models?",
            "tags": ["ChatGPT", "Integration"],
            "a": """
We created a small backend layer that sends our chat history and a careful system prompt 
to a language-model API. The system prompt explains that this is a memory assistant for 
an elder person and should reply in short, friendly sentences. We also pre-answer simple 
questions like “What is today’s date?” locally, so the assistant feels fast and always 
aligned with the real calendar and time zone.
""",
        },
    ],
    "Guardian & Teacher Questions": [
        {
            "q": "How is this project useful for guardians and teachers?",
            "tags": ["Guardians", "Teachers"],
            "a": """
Guardians can use ALZY to set medicine and daily activity reminders with photos and 
simple instructions that can be replayed any time. Teachers can use SIGNA-LINK to 
introduce basic sign concepts in class and UNSEEN to demonstrate how AI can describe 
images in plain language. The goal is not to replace human care or teaching, but to add 
small digital helpers that make communication easier.
""",
        },
        {
            "q": "Is this project meant to be a medical device?",
            "tags": ["Safety", "Scope"],
            "a": """
No. ANTIDOTE is a school science project and a technology prototype. It is not a medical 
device and does not make medical decisions. It only offers reminders, visual support, and 
simple explanations. For any medical decision, elders and families should always follow 
professional doctors and official advice.
""",
        },
        {
            "q": "What are the next steps we want to explore?",
            "tags": ["Future", "Ideas"],
            "a": """
Next, we want to add multi-language support (for example Bengali and English together), 
better offline behaviour for limited internet situations, and more accurate sign 
recognition by collecting a larger, carefully consented training dataset. We also hope to 
run small usability tests with families and teachers to see which features feel most 
comfortable in real daily life.
""",
        },
    ],
}

# -------------------- RENDER FAQ (single open at a time) --------------------
st.markdown(
    '<div class="faq-section-label">Frequently Asked Questions</div>',
    unsafe_allow_html=True,
)

# keep track of which question is open
if "faq_open_key" not in st.session_state:
    st.session_state.faq_open_key = ""

def render_faq_block(block_title: str, items):
    st.markdown(f"### {block_title}")
    for idx, item in enumerate(items):
        key = f"faq_{block_title}_{idx}"

        # build label row with tags
        tag_html = ""
        if item.get("tags"):
            tag_html = '<div class="faq-tag-row">' + "".join(
                f'<span class="faq-tag">{t}</span>' for t in item["tags"]
            ) + "</div>"

        # expander open state = matches current open key
        is_open = st.session_state.faq_open_key == key

        # we wrap expander title with our styled span
        with st.expander(
            label=f"🔹 {item['q']}",
            expanded=is_open,
        ):
            # question label
            st.markdown(
                f"""
                <div class="faq-question">{item['q']}</div>
                {tag_html}
                """,
                unsafe_allow_html=True,
            )
            st.markdown(f"<div class='faq-answer'>{item['a']}</div>", unsafe_allow_html=True)

            # small "Collapse" button so opening one closes others
            col_btn, _ = st.columns([1, 3])
            with col_btn:
                if st.button("Close", key=key + "_close"):
                    if st.session_state.faq_open_key == key:
                        st.session_state.faq_open_key = ""
                    st.experimental_rerun()

        # if user clicks on header, Streamlit sadly does not give a direct event,
        # so we use a small trick: a "Show answer" button row under each header
        # This row is outside the expander, so it is always visible.
        # (Lightweight helper for science-fair demo.)
        show_col, _ = st.columns([1, 3])
        with show_col:
            if st.button("Show / Focus this answer", key=key + "_focus"):
                st.session_state.faq_open_key = key
                st.experimental_rerun()

        st.markdown("", unsafe_allow_html=True)  # small spacing


for block_title, items in faq_blocks.items():
    render_faq_block(block_title, items)

st.markdown("</div>", unsafe_allow_html=True)
