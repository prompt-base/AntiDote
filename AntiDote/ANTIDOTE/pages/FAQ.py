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
      font-size:1.1rem;
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
      margin: 12px auto 40px auto;
      padding: 0 6px;
    }

    .faq-answer-box {
      border-radius: 14px;
      border: 1px solid rgba(148,163,184,0.5);
      padding: 10px 12px;
      background: rgba(15,23,42,0.96);
      box-shadow: 0 10px 25px rgba(15,23,42,0.7);
      font-size:0.94rem;
      color:var(--muted);
      margin-top:4px;
    }

    .faq-question-title {
      font-size:1.02rem;
      font-weight:700;
      color:#f9fafb;
      margin-bottom:4px;
    }

    /* Make expander headers (questions) bright white and larger */
    .streamlit-expanderHeader {
      font-size:1.02rem !important;
      font-weight:700 !important;
      color:#f9fafb !important;
    }
    .streamlit-expanderHeader p,
    .streamlit-expanderHeader span,
    .streamlit-expanderHeader div {
      color:#f9fafb !important;
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
        ANTIDOTE is our project where we explore three ideas together:
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
        <div class="faq-stat-value">Daily reminders</div>
        <div class="faq-stat-note">
          We use simple photos, steps, and local time to support medicine
          and routine memory.
        </div>
      </div>
      <div class="faq-stat-card">
        <div class="faq-stat-label">SIGNA-LINK – Hands</div>
        <div class="faq-stat-value">Hand landmarks</div>
        <div class="faq-stat-note">
          We read basic hand points from the camera to practise and test simple signs.
        </div>
      </div>
      <div class="faq-stat-card">
        <div class="faq-stat-label">UNSEEN – Vision</div>
        <div class="faq-stat-value">Picture to voice</div>
        <div class="faq-stat-note">
          We let AI describe an image in short sentences to help students
          who like listening.
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")
st.markdown('<div class="faq-container">', unsafe_allow_html=True)

# -------------------- FLAT FAQ LIST --------------------
faq_items = [
    {
        "q": "Why did we start the ANTIDOTE project?",
        "a": """
We saw real problems around us. Some elders have memory difficulty, some people
depend on sign language, and some students understand pictures better when
someone reads them aloud. We wanted one science project where we try to support
all three with simple, kind technology.
""",
    },
    {
        "q": "What is ALZY in simple words?",
        "a": """
ALZY is a memory helper. We store small reminders with a title, date, time,
photo, and easy steps. ALZY shows what to do next and can repeat some reminders
after a few days so that faces, tasks, and medicine routines become more familiar.
""",
    },
    {
        "q": "What is SIGNA-LINK in simple words?",
        "a": """
SIGNA-LINK is our sign language helper. Using the camera, we read hand points
(“landmarks”) and match them with basic sign shapes. This helps us learn, practise,
and test simple signs in a fun, interactive way.
""",
    },
    {
        "q": "What is UNSEEN in simple words?",
        "a": """
UNSEEN is our visual support tool. We send an image to an AI model and get back a
short description in easy sentences. This can help students who prefer listening
to understand what is happening in a picture or scene.
""",
    },
    {
        "q": "How does ALZY help with memory and medicine reminders?",
        "a": """
In ALZY we use the local time zone so reminders follow our real clock.
Each reminder can include photos and step-by-step text. For some items,
we use small spaced gaps (like 1, 2, 4, 7 days) so that important faces
and tasks return again, which can support long-term memory.
""",
    },
    {
        "q": "How do we use AI models inside this project?",
        "a": """
We combine simple rules with AI models. Rules handle things like dates,
times, and schedules. For friendly answers, we send short messages to a
language model and ask it to reply in clear, small sentences. For signs and
images, we use models that work with hand points and picture features.
""",
    },
    {
        "q": "How did we connect ChatGPT-style models with our app?",
        "a": """
From our app we send the last few chat messages plus an instruction telling
the model that this is for gentle support, not for medical advice.
We also give the correct local date, so when someone asks about today,
the model answer stays in sync with our own time functions in the code.
""",
    },
    {
        "q": "What difficulties did we face while building ANTIDOTE?",
        "a": """
We faced browser permission problems for camera and microphone, Python
package version conflicts, and slow video frames. Sometimes the layout was
too confusing for elders, so we redesigned the screens. When errors came,
we had to read logs carefully and fix them line by line.
""",
    },
    {
        "q": "What did we learn from these difficulties?",
        "a": """
We learned not to panic when the app breaks. We learned to change only
one part at a time, test it, and then move to the next part. We also
understood that good design is not only about code speed but also about
how calm and simple the screen feels for real people.
""",
    },
    {
        "q": "How can guardians use this project in daily life?",
        "a": """
Guardians can create reminders in ALZY for medicine, walking, drinking water,
or phone calls with family. They can add photos and short steps. The person
can open the app, see or hear what to do, and feel a bit more independent.
This is extra support, not a replacement for real care.
""",
    },
    {
        "q": "How can teachers use these ideas in the classroom?",
        "a": """
Teachers can show SIGNA-LINK to explain how computers see hand shapes and
UNSEEN to show how AI reads images. This can start discussions about
inclusion, disability, and how technology can support people if we design
it with empathy.
""",
    },
    {
        "q": "What do we want to improve next?",
        "a": """
Next, we want to add more language options like Bengali plus English,
make the app smoother on weak internet, train the sign part with more
correct examples, and test the system with real families and teachers
so we can adjust it based on honest feedback.
""",
    },
]

st.markdown("### Frequently Asked Questions")

# -------------------- EXPANDERS: QUESTION + ANSWER --------------------
for i, item in enumerate(faq_items):
    with st.expander(item["q"], expanded=(i == 0)):
        st.markdown(
            f"""
            <div class="faq-answer-box">
              <div class="faq-question-title">{item['q']}</div>
              <div>{item['a']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("</div>", unsafe_allow_html=True)
