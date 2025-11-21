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
      padding: 0 6px;
    }

    .faq-section-label {
      font-size:0.8rem;
      letter-spacing:0.16em;
      text-transform:uppercase;
      color:rgba(148,163,184,0.9);
      margin-bottom:6px;
    }

    .faq-question-box {
      border-radius: 14px;
      border: 1px solid rgba(148,163,184,0.55);
      padding: 8px 10px;
      background: radial-gradient(circle at 0 0, rgba(56,189,248,0.18), transparent 55%),
                  linear-gradient(145deg, rgba(15,23,42,0.96), rgba(15,23,42,0.98));
      box-shadow: 0 10px 25px rgba(15,23,42,0.9);
      margin-bottom: 10px;
    }

    .faq-answer-box {
      margin-top: 12px;
      border-radius: 14px;
      border: 1px solid rgba(148,163,184,0.5);
      padding: 10px 14px;
      background: rgba(15,23,42,0.96);
      box-shadow: 0 10px 25px rgba(15,23,42,0.7);
      font-size:0.92rem;
      color:var(--muted);
    }

    .faq-question-title {
      font-size:0.95rem;
      font-weight:600;
      color:#e5e7eb;
    }

    .stRadio > label {
      font-size:0.9rem;
      color:#e5e7eb;
    }
    .stRadio div[role="radiogroup"] > label {
      margin-bottom:4px;
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
        <span>ALZY • SIGNA-LINK • UNSEEN</span>
      </div>
      <div class="faq-hero-title">ANTIDOTE – FAQ</div>
      <p class="faq-hero-sub">
        ANTIDOTE is our science project where we bring three ideas together:
        memory support (ALZY), sign language support (SIGNA-LINK),
        and visual support (UNSEEN).
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------- SMALL SIMPLE STATS --------------------
st.markdown(
    """
    <div class="faq-stats-row">
      <div class="faq-stat-card">
        <div class="faq-stat-label">ALZY – Memory</div>
        <div class="faq-stat-value">Helps remember</div>
        <div class="faq-stat-note">
          We designed ALZY to remind about medicine, daily work, and faces
          using simple photos and clear steps.
        </div>
      </div>
      <div class="faq-stat-card">
        <div class="faq-stat-label">SIGNA-LINK – Hands</div>
        <div class="faq-stat-value">Learns signs</div>
        <div class="faq-stat-note">
          We use camera and hand landmarks so we can slowly learn and test
          basic sign language shapes.
        </div>
      </div>
      <div class="faq-stat-card">
        <div class="faq-stat-label">UNSEEN – Vision</div>
        <div class="faq-stat-value">Describes images</div>
        <div class="faq-stat-note">
          We let AI describe pictures in short sentences to support students
          who like listening more than reading.
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")
st.markdown('<div class="faq-container">', unsafe_allow_html=True)

# -------------------- FAQ DATA (simple, class 8 level) --------------------
faq_data = {
    "Our Journey": [
        {
            "q": "Why did we start the ANTIDOTE project?",
            "a": """
We saw real problems around us. Some elders forget medicine and faces, some people use
sign language, and some students find pictures hard to understand without a voice.
We wanted one project where we try to help all three using AI and simple tools.
""",
        },
        {
            "q": "What difficulties did we face while building this project?",
            "a": """
We struggled with many things: camera and mic permissions in the browser, Python package
versions, slow video in the app, and making the screen easy for elders to read.
Sometimes the app broke, and we had to fix errors step by step with patience.
""",
        },
        {
            "q": "What did we learn from these difficulties?",
            "a": """
We learned to debug slowly instead of changing everything at once. We learned to split
our work into three clear parts – ALZY, SIGNA-LINK, and UNSEEN – and to think about
how a real person will feel when using the screen, not only about the code.
""",
        },
    ],
    "How ALZY Works": [
        {
            "q": "How does ALZY help with memory and medicine reminders?",
            "a": """
In ALZY we store small records: title, date, time, photo, and simple steps.
We use the local time zone so reminders stay correct for our place.
We also repeat some reminders after a few days, so the person sees the same face
or task again and slowly remembers better.
""",
        },
        {
            "q": "How do we use AI models inside the project?",
            "a": """
For ALZY, we mix simple rules with a language model. Rules handle the date and time,
and the model helps us answer questions in friendly, short sentences.
SIGNA-LINK uses hand points from the camera to guess signs.
UNSEEN uses image features to create short text about the scene.
""",
        },
        {
            "q": "How did we connect ChatGPT-style models with our app?",
            "a": """
We send the chat history and a short instruction message from our app to a language
model API. In that message we explain that this is for memory support, so the answers
must be calm, clear, and not too long. Simple questions like today’s date are answered
directly from our own code so that the date always matches our real calendar.
""",
        },
    ],
    "For Guardians & Teachers": [
        {
            "q": "How can guardians use this project in daily life?",
            "a": """
Guardians can set reminders in ALZY with photos and steps for medicine or daily tasks.
The person can open the app and see the picture, read the steps, or listen to a short
answer from the chatbot. This does not replace human care; it only gives extra support.
""",
        },
        {
            "q": "How can teachers use these ideas in a classroom?",
            "a": """
Teachers can show SIGNA-LINK to explain how computers see hand shapes,
and UNSEEN to show how AI turns pictures into text.
This can start discussions about disability, inclusion, and how technology
can support people in kind ways.
""",
        },
        {
            "q": "What do we want to improve next?",
            "a": """
Next, we want to add more languages like Bengali with English, make the system work
better on slow internet, and train the sign part with more clean examples.
We also want to test the app with real families and teachers to see which parts
feel helpful and which parts need to be changed.
""",
        },
    ],
}

# -------------------- SECTION SELECTION --------------------
section_names = list(faq_data.keys())

st.markdown(
    '<div class="faq-section-label">Frequently Asked Questions</div>',
    unsafe_allow_html=True,
)

selected_section = st.radio(
    "Choose a topic",
    section_names,
    horizontal=True,
)

questions = faq_data[selected_section]
question_texts = [item["q"] for item in questions]

st.markdown("### Questions")
with st.container():
    st.markdown('<div class="faq-question-box">', unsafe_allow_html=True)
    selected_question = st.radio(
        "Questions",
        question_texts,
        index=0,
        label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- SHOW ANSWER FOR SELECTED QUESTION --------------------
selected_item = next(item for item in questions if item["q"] == selected_question)

st.markdown(
    f"""
    <div class="faq-answer-box">
      <div class="faq-question-title">{selected_item['q']}</div>
      <div style="margin-top:6px;">{selected_item['a']}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)
