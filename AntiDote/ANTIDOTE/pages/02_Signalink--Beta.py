# ANTIDOTE/pages/Signalink--Beta.py
# --------------------------------------------------
# SIGNALINK – Learn signs + Snapshot Sign → Text (Template Matching)
# --------------------------------------------------
import os
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np
import streamlit as st
from PIL import Image

# --------------------------------------------------
# 1) PATHS / ASSETS
# --------------------------------------------------
PROJECT_DIR = Path(__file__).resolve().parent      # .../ANTIDOTE/pages
REPO_ROOT = PROJECT_DIR.parent                     # .../ANTIDOTE

# Images folder: ANTIDOTE/images/
IMAGES_DIR = REPO_ROOT / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Signalink", page_icon="🤟", layout="wide")

# --------------------------------------------------
# 2) SIGN DATA (A–E + basic phrases)
# --------------------------------------------------
SIGN_DATA = [
    # ===== ENGLISH ALPHABET (A–E) =====
    {
        "word": "A",
        "category": "Alphabet",
        "image": str(IMAGES_DIR / "alphabet_A.png"),
        "hint": "Finger-spelled A with thumb along the fist.",
    },
    {
        "word": "B",
        "category": "Alphabet",
        "image": str(IMAGES_DIR / "alphabet_B.png"),
        "hint": "Flat palm facing forward, fingers together.",
    },
    {
        "word": "C",
        "category": "Alphabet",
        "image": str(IMAGES_DIR / "alphabet_C.png"),
        "hint": "Hand makes a C-shape, like holding a cup.",
    },
    {
        "word": "D",
        "category": "Alphabet",
        "image": str(IMAGES_DIR / "alphabet_D.png"),
        "hint": "Pointer finger up, other fingers touching thumb.",
    },
    {
        "word": "E",
        "category": "Alphabet",
        "image": str(IMAGES_DIR / "alphabet_E.png"),
        "hint": "Fingers curled down to the thumb, palm facing in.",
    },

    # ===== BASIC / POLITE PHRASES =====
    {
        "word": "Hello",
        "category": "Basic",
        "image": str(IMAGES_DIR / "hello.png"),
        "hint": "Hand up, small wave.",
    },
    {
        "word": "Goodbye",
        "category": "Basic",
        "image": str(IMAGES_DIR / "goodbye.png"),
        "hint": "Open hand, small wave away.",
    },
    {
        "word": "Yes",
        "category": "Basic",
        "image": str(IMAGES_DIR / "yes.png"),
        "hint": "Fist nodding up and down.",
    },
    {
        "word": "Please",
        "category": "Basic",
        "image": str(IMAGES_DIR / "please.png"),
        "hint": "Flat hand circles over chest.",
    },
    {
        "word": "Sorry",
        "category": "Basic",
        "image": str(IMAGES_DIR / "sorry.png"),
        "hint": "Closed fist over chest.",
    },
    {
        "word": "Thank you",
        "category": "Basic",
        "image": str(IMAGES_DIR / "thankyou.png"),
        "hint": "From chin outward.",
    },

    # ===== DAILY ACTIONS =====
    {
        "word": "Eat",
        "category": "Daily",
        "image": str(IMAGES_DIR / "eat.png"),
        "hint": "Fingertips move toward mouth.",
    },

    # ===== PEOPLE / FAMILY =====
    {
        "word": "Mother",
        "category": "People",
        "image": str(IMAGES_DIR / "mother.png"),
        "hint": "Thumb taps chin, fingers spread.",
    },
    {
        "word": "Father",
        "category": "People",
        "image": str(IMAGES_DIR / "father.png"),
        "hint": "Thumb taps forehead, fingers spread.",
    },
    {
        "word": "Brother",
        "category": "People",
        "image": str(IMAGES_DIR / "brother.jpg"),
        "hint": "Two L-hands tap together at chest.",
    },
    {
        "word": "Daughter",
        "category": "People",
        "image": str(IMAGES_DIR / "daughter.jpg"),
        "hint": "Hand from chin down to cradled arm.",
    },
]

CATEGORIES = sorted(list({s["category"] for s in SIGN_DATA}))
LABELS = [s["word"] for s in SIGN_DATA]

# Alphabet templates to match against
TEMPLATE_LABELS = ["A", "B", "C", "D", "E"]

# --------------------------------------------------
# 3) GLOBAL STYLES
# --------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
      background:
        radial-gradient(1200px 600px at 10% -10%, #0e7490 0%, #0b2530 40%),
        linear-gradient(180deg, #0b2530, #06131a);
      color: #fff;
    }
    h1,h2,h3,h4 { color: #fff !important; }
    img { border-radius: 12px; }

    /* Reusable big CTA buttons */
    .cta .stButton>button {
      width: 100%;
      padding: 22px 28px;
      border-radius: 22px;
      font-size: 1.25rem;
      font-weight: 900;
      letter-spacing: .2px;
      border: none;
      color: #061018;
      transform: translateZ(0);
      transition: transform .06s ease, box-shadow .12s ease, filter .12s ease;
    }
    .cta.learn .stButton>button {
      background: linear-gradient(135deg, #34d399 0%, #06b6d4 55%, #22d3ee 110%);
      box-shadow: 0 18px 44px rgba(6,182,212,0.45);
    }
    .cta.signtext .stButton>button {
      background: linear-gradient(135deg, #60a5fa 0%, #7c3aed 55%, #f472b6 110%);
      box-shadow: 0 18px 44px rgba(124,58,237,0.45);
    }
    .cta .stButton>button:hover {
      transform: translateY(-2px);
      filter: brightness(1.04) saturate(1.03);
    }
    .cta .stButton>button:active {
      transform: translateY(0);
      filter: brightness(0.98);
    }

    /* Card look for all Streamlit images (sign cards) */
    div[data-testid="stImage"] {
      background: rgba(3,16,22,.45);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 16px;
      padding: 12px 14px;
      margin-bottom: 12px;
      box-shadow: 0 10px 30px rgba(0,0,0,.25);
    }

    /* Make all sign images uniform */
    div[data-testid="stImage"] img {
      width: 100% !important;
      height: 190px !important;
      object-fit: contain;
      background: rgba(6,16,24,0.9);
      border-radius: 12px;
      padding: 6px;
    }

    /* Tabs text color tweaks */
    div.stTabs [data-baseweb="tab"] {
      color: #ffffff !important;
      font-weight: 500;
    }
    div.stTabs [data-baseweb="tab"][aria-selected="true"] {
      color: #ff4b4b !important;
    }

    /* NEXT button style on Practice tab */
    .next-btn .stButton>button {
      background: linear-gradient(135deg, #f59e0b, #ec4899);
      color: #0b1220;
      font-weight: 700;
      border-radius: 999px;
      padding: 0.5rem 1.6rem;
      border: none;
      box-shadow: 0 10px 25px rgba(236,72,153,0.45);
    }
    .next-btn .stButton>button:hover {
      transform: translateY(-1px);
      filter: brightness(1.05);
    }
    .next-btn .stButton>button:active {
      transform: translateY(0);
      filter: brightness(0.98);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 4) SESSION STATE
# --------------------------------------------------
st.session_state.setdefault("signalink_started", False)   # show landing first
st.session_state.setdefault("signalink_route", None)      # "learn" | "translator"
st.session_state.setdefault("signalink_cat", "All")
st.session_state.setdefault("learn_progress", {"learned": [], "quiz_scores": []})

# --------------------------------------------------
# 5) TEMPLATE-BASED MATCHING HELPERS
# --------------------------------------------------
def _preprocess_image_for_template(img: Image.Image, size: Tuple[int, int] = (128, 128)) -> np.ndarray:
    """
    Convert an image to a normalized grayscale vector for similarity comparison.
    """
    gray = img.convert("L")
    resized = gray.resize(size)
    arr = np.array(resized, dtype=np.float32) / 255.0
    return arr.flatten()  # 128*128 vector


@st.cache_resource(show_spinner=False)
def load_template_vectors() -> Dict[str, np.ndarray]:
    """
    Load alphabet template images A–E and store their preprocessed vectors.
    If a file is missing, that label is skipped.
    """
    template_vecs: Dict[str, np.ndarray] = {}
    for label in TEMPLATE_LABELS:
        path = IMAGES_DIR / f"alphabet_{label}.png"
        if path.exists():
            img = Image.open(path)
            template_vecs[label] = _preprocess_image_for_template(img)
    return template_vecs


def find_best_match(
    uploaded_img: Image.Image,
    templates: Dict[str, np.ndarray],
    threshold: float = 0.35,
) -> Tuple[Optional[str], float]:
    """
    Compare the uploaded image with each template using mean squared error (MSE).
    Lower MSE = more similar.

    Returns:
      (best_label, best_mse)
      If best_mse is above threshold => treat as "no clear match".
    """
    if not templates:
        return None, 9999.0

    vec = _preprocess_image_for_template(uploaded_img)
    best_label = None
    best_mse = 9999.0

    for label, tvec in templates.items():
        mse = float(np.mean((vec - tvec) ** 2))
        if mse < best_mse:
            best_mse = mse
            best_label = label

    if best_mse > threshold:
        return None, best_mse
    return best_label, best_mse


TEMPLATE_VECS = load_template_vectors()

# --------------------------------------------------
# 6) SMALL RERUN HELPER
# --------------------------------------------------
def _rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# --------------------------------------------------
# 7) LANDING (two centered big buttons)
# --------------------------------------------------
current_route = st.session_state.get("signalink_route", None)

if not st.session_state["signalink_started"] or current_route not in ("learn", "translator"):
    st.markdown(
        "<h1 style='text-align:center; margin-top:10px;'>🤟 SIGNALINK</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; font-size:1.05rem; opacity:0.9;'>"
        "Learn signs step by step, or try the Snapshot Sign → Text demo."
        "</p>",
        unsafe_allow_html=True,
    )

    left_spacer, center_block, right_spacer = st.columns([1, 2, 1])
    with center_block:
        btn_col1, btn_col2 = st.columns(2)

        with btn_col1:
            st.markdown('<div class="cta learn">', unsafe_allow_html=True)
            if st.button("📚 Learn Signs", key="cta_learn", use_container_width=True):
                st.session_state["signalink_started"] = True
                st.session_state["signalink_route"] = "learn"
                _rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with btn_col2:
            st.markdown('<div class="cta signtext">', unsafe_allow_html=True)
            if st.button("📷 Snapshot Sign → Text", key="cta_translator", use_container_width=True):
                st.session_state["signalink_started"] = True
                st.session_state["signalink_route"] = "translator"
                _rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

route = st.session_state.get("signalink_route", "learn")

# --------------------------------------------------
# 8) TITLE + BACK BUTTON
# --------------------------------------------------
title_col, back_col = st.columns([5, 2])

with title_col:
    st.title("🤟 SIGNALINK")

with back_col:
    st.markdown("<div style='height: 0.8rem'></div>", unsafe_allow_html=True)
    if st.button("⬅️ Back to Dashboard", key="btn_back_dashboard", use_container_width=True):
        st.session_state["signalink_started"] = False
        st.session_state["signalink_route"] = None
        _rerun()

# --------------------------------------------------
# 9) LEARN ROUTE
# --------------------------------------------------
if route == "learn":
    tab_learn, tab_practice, tab_progress = st.tabs(
        ["📚 Learn Signs", "🧪 Practice", "📊 Progress"]
    )

    # ---- LEARN SIGNS ----
    with tab_learn:
        st.subheader("📚 Learn Signs")
        st.caption("Browse alphabet A–E plus other sample signs and hints.")

        st.write("**Categories**")
        all_cats = ["All"] + CATEGORIES
        pill_cols = st.columns(len(all_cats))

        for i, cat_name in enumerate(all_cats):
            is_active = st.session_state.get("signalink_cat", "All") == cat_name
            label = f"✅ {cat_name}" if is_active else cat_name
            if pill_cols[i].button(label, key=f"pill_{cat_name}"):
                st.session_state["signalink_cat"] = cat_name
                _rerun()

        cat = st.session_state.get("signalink_cat", "All")
        filtered = SIGN_DATA if cat == "All" else [s for s in SIGN_DATA if s["category"] == cat]

        cols = st.columns(3)
        for i, sign in enumerate(filtered):
            with cols[i % 3]:
                img_path = sign["image"]
                st.image(
                    img_path if (img_path and os.path.exists(img_path))
                    else "https://via.placeholder.com/300x180?text=SIGN",
                    use_container_width=True,
                )
                st.markdown(f"**{sign['word']}**")
                st.caption(f"Category: {sign['category']}")
                st.caption(f"Hint: {sign['hint']}")
                if st.button(f"Mark learned", key=f"learn_{sign['word']}"):
                    learned = st.session_state["learn_progress"]["learned"]
                    if sign["word"] not in learned:
                        learned.append(sign["word"])
                    st.success(f"Marked {sign['word']} as learned ✅")

    # ---- PRACTICE ----
    with tab_practice:
        st.subheader("🧪 Practice")
        st.caption("Tap the correct word for this sign.")

        if "practice_idx" not in st.session_state:
            st.session_state.practice_idx = 0
            st.session_state.practice_order = list(range(len(SIGN_DATA)))
            st.session_state.pop("practice_options", None)
            st.session_state.pop("practice_feedback", None)

        idx = st.session_state.practice_order[
            st.session_state.practice_idx % len(SIGN_DATA)
        ]
        item = SIGN_DATA[idx]

        st.image(
            item["image"]
            if os.path.exists(item["image"])
            else "https://via.placeholder.com/420x240?text=SIGN",
            use_container_width=False,
        )

        if (
            "practice_options" not in st.session_state
            or st.session_state.practice_options.get("target") != item["word"]
        ):
            other_words = [w for w in LABELS if w != item["word"]]
            num_wrong = min(2, len(other_words))
            wrong = random.sample(other_words, k=num_wrong) if num_wrong > 0 else []
            options = wrong + [item["word"]]
            random.shuffle(options)
            st.session_state.practice_options = {
                "target": item["word"],
                "options": options,
            }
            st.session_state.pop("practice_feedback", None)

        options = st.session_state.practice_options["options"]

        st.write("Choose the correct word:")
        num_cols = max(1, min(3, len(options)))
        opt_cols = st.columns(num_cols)

        for i, opt in enumerate(options):
            col = opt_cols[i % num_cols]
            with col:
                if st.button(
                    opt,
                    key=f"practice_opt_{st.session_state.practice_idx}_{i}",
                ):
                    is_correct = (opt == item["word"])
                    st.session_state["practice_feedback"] = {
                        "word": item["word"],
                        "correct": is_correct,
                    }
                    st.session_state["learn_progress"]["quiz_scores"].append(
                        {"word": item["word"], "correct": is_correct}
                    )

        fb = st.session_state.get("practice_feedback")
        if fb and fb.get("word") == item["word"]:
            if fb["correct"]:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. It was **{item['word']}**")

        spacer_l, center_next, spacer_r = st.columns([4, 1, 4])
        with center_next:
            st.markdown("<div class='next-btn'>", unsafe_allow_html=True)
            next_clicked = st.button(
                "Next",
                key=f"practice_next_{st.session_state.practice_idx}",
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        if next_clicked:
            st.session_state.practice_idx += 1
            st.session_state.pop("practice_options", None)
            st.session_state.pop("practice_feedback", None)
            _rerun()

    # ---- PROGRESS ----
    with tab_progress:
        st.subheader("📊 Progress")
        learned = st.session_state["learn_progress"]["learned"]
        scores = st.session_state["learn_progress"]["quiz_scores"]
        st.write(f"✅ Signs learned: {len(learned)}")
        if learned:
            st.write(", ".join(learned))
        st.divider()
        st.write("🧪 Quiz history:")
        if not scores:
            st.info("No practice attempts yet.")
        else:
            for s in reversed(scores):
                status = "✅" if s["correct"] else "❌"
                st.write(f"{status} – {s['word']}")

# --------------------------------------------------
# 10) SNAPSHOT TRANSLATOR ROUTE (TEMPLATE MATCH)
# --------------------------------------------------
else:
    tab_snap, tab_help = st.tabs(
        ["📷 Snapshot Sign → Text", "ℹ️ How this demo works"]
    )

    # ---- SNAPSHOT TAB ----
    with tab_snap:
        st.subheader("📷 Snapshot Sign → Text (A–E)")
        st.caption(
            "Show a hand sign for A, B, C, D, or E and take a photo. "
            "The system compares it with saved templates and picks the closest match."
        )

        st.markdown(
            """
            **Tips for better results:**
            - Use a **plain background** if possible.
            - Show **one hand** clearly in the frame.
            - Try to copy the alphabet hand shapes shown in the **Learn Signs** tab.
            """
        )

        col_cam, col_uploaded = st.columns(2)
        with col_cam:
            camera_img = st.camera_input("Take a photo of your hand sign")

        with col_uploaded:
            uploaded = st.file_uploader("Or upload a photo", type=["png", "jpg", "jpeg"])

        img: Optional[Image.Image] = None
        if camera_img is not None:
            img = Image.open(camera_img)
        elif uploaded is not None:
            img = Image.open(uploaded)

        if img is not None:
            st.image(img, caption="Input image", use_container_width=True)

            if not TEMPLATE_VECS:
                st.error(
                    "Template images alphabet_A.png to alphabet_E.png are missing. "
                    "Please add them to the images folder."
                )
            else:
                if st.button("🔍 Predict Sign", use_container_width=True):
                    label, mse = find_best_match(img, TEMPLATE_VECS)
                    if label is None:
                        st.error(
                            "We could not find a clear match to A–E.\n\n"
                            "This demo uses simple image comparison, so it works best when:\n"
                            "- The hand sign looks similar to the template images.\n"
                            "- Lighting is good and background is simple."
                        )
                    else:
                        st.success(f"Predicted sign: **{label}**")
                        st.caption(f"(Lower error = closer match. This image error: {mse:.3f})")

        else:
            st.info("Take a photo or upload a hand-sign image to start.")

    # ---- HELP TAB ----
    with tab_help:
        st.subheader("ℹ️ How this demo works")
        st.markdown(
            """
            This is a **simple AI-style demo** for the science fair:

            1. The system stores template images for the letters **A, B, C, D, and E** in sign language.  
            2. When a new photo is captured or uploaded, it is converted to a small grayscale grid of numbers.  
            3. The same is done for each template image.  
            4. The program calculates **how different** the new image is from each template (using a simple error score).  
            5. The sign with the **smallest error** is chosen as the prediction.

            It is not a full real-world sign language recognizer.  
            But it clearly shows the **core AI idea**:  
            > *compare patterns and pick the closest match based on numbers*.
            """
        )
