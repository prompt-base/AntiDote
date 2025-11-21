# ANTIDOTE/pages/Signalink--Beta.py
# --------------------------------------------------
# SIGNALINK – Landing (2 CTAs) → Learn (Learn/Practice/Progress) OR Sign→Text Translator
# --------------------------------------------------
import os
import json
import time
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import streamlit as st
from PIL import Image

# optional: for saving/loading the trained model on disk (shared for all visitors)
try:
    import joblib
except Exception:
    joblib = None

# ===== small compatibility helper for rerun =====
def _rerun():
    # Prefer st.rerun() (new), fallback to st.experimental_rerun() (old)
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


# ===== Optional deps (we show install hints if missing) =====
MISSING: List[str] = []
try:
    import mediapipe as mp  # type: ignore
except Exception:
    mp = None
    MISSING.append("mediapipe")

try:
    import cv2  # type: ignore

    cv2.setUseOptimized(True)
    try:
        cv2.setNumThreads(2)
    except Exception:
        pass
except Exception:
    cv2 = None
    MISSING.append("opencv-python")

try:
    from sklearn.neighbors import KNeighborsClassifier  # type: ignore
except Exception:
    KNeighborsClassifier = None
    MISSING.append("scikit-learn")

try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration  # type: ignore

    WEBRTC_OK = True
except Exception:
    WEBRTC_OK = False

# --------------------------------------------------
# 1) PATHS / ASSETS
# --------------------------------------------------
PROJECT_DIR = Path(__file__).resolve().parent      # .../ANTIDOTE/pages
REPO_ROOT = PROJECT_DIR.parent                     # .../ANTIDOTE

# All sign images live in: AntiDote/ANTIDOTE/images/
IMAGES_DIR = REPO_ROOT / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Gesture DB + persistent model under signalink_assets
SIGNALINK_ASSETS = REPO_ROOT / "signalink_assets"
SIGNALINK_ASSETS.mkdir(parents=True, exist_ok=True)
GESTURE_DB_PATH = SIGNALINK_ASSETS / "gesture_db.json"

# Model file shared by all users on this server
PERSISTENT_MODEL_PATH = SIGNALINK_ASSETS / "signalink_knn.pkl"

MODEL_STATE_KEY = "signalink_knn_model"

# --------------------------------------------------
# 2) SIGN DATA  (now includes Alphabet A–E preloaded)
# --------------------------------------------------
# NOTE: make sure these files exist in ANTIDOTE/images/:
#   alphabet_A.png, alphabet_B.png, alphabet_C.png, alphabet_D.png, alphabet_E.png
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

# --------------------------------------------------
# 3) GLOBAL STYLES
# --------------------------------------------------
st.set_page_config(page_title="Signalink", page_icon="🤟", layout="wide")
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

    /* Button text color overrides (these selectors may change with Streamlit updates) */
    .st-emotion-cache-12j140x.et2rgd20 p{
      color:#0b1220;
    }
    .st-emotion-cache-12j140x.et2rgd20:hover p{
      color:#ffffff;
    }
    .st-emotion-cache-1s2v671.e1gk92lc0 p{
      color:#ffffff;
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
st.session_state.setdefault("signalink_started", False)           # show landing first
st.session_state.setdefault("signalink_route", None)              # "learn" | "translator"
st.session_state.setdefault("signalink_cat", "All")
st.session_state.setdefault("learn_progress", {"learned": [], "quiz_scores": []})
st.session_state.setdefault(MODEL_STATE_KEY, {"clf": None, "labels": []})

# --------------------------------------------------
# 5) DB HELPERS (for KNN samples)
# --------------------------------------------------
def _require(pkgs: List[str]) -> bool:
    if not pkgs:
        return True
    missing = [p for p in pkgs if p in MISSING]
    if missing:
        st.error(
            "Missing dependencies:\n\n```\n"
            + "\n".join(f"pip install {p}" for p in missing)
            + "\n```",
            icon="⚠️",
        )
        return False
    return True


def default_gesture_db() -> Dict[str, List[List[float]]]:
    """
    Create a tiny synthetic dataset so A–E work out-of-the-box.
    For real accuracy, more samples can be collected in 📸 Samples & Train.
    """
    def mk(seed: int) -> List[float]:
        rng = np.random.default_rng(seed)
        v = rng.normal(0, 0.15, 63).astype(np.float32)  # 21 landmarks * 3 coords
        return v.tolist()

    return {
        "A": [mk(11), mk(12), mk(13)],
        "B": [mk(21), mk(22), mk(23)],
        "C": [mk(31), mk(32), mk(33)],
        "D": [mk(41), mk(42), mk(43)],
        "E": [mk(51), mk(52), mk(53)],
    }


def load_db() -> Dict[str, List[List[float]]]:
    if GESTURE_DB_PATH.exists():
        try:
            with open(GESTURE_DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and data:
                    return data
        except Exception:
            pass

    # If file missing or empty → start with default A–E data
    db = default_gesture_db()
    save_db(db)
    return db


def save_db(db: Dict[str, List[List[float]]]) -> None:
    with open(GESTURE_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)


def db_counts(db: Dict[str, List[List[float]]]) -> Dict[str, int]:
    return {k: len(v) for k, v in db.items()}


# --------------------------------------------------
# 6) MEDIAPIPE FEATURE EXTRACTION (optimized)
# --------------------------------------------------
def _img_to_rgb_ndarray(file_or_nd: Image.Image | np.ndarray) -> np.ndarray:
    if isinstance(file_or_nd, np.ndarray):
        arr = file_or_nd
    else:
        arr = np.array(file_or_nd.convert("RGB"))
    return arr


class _HandsSingleton:
    """Reuse MediaPipe Hands across frames to avoid reinit cost."""

    def __init__(self):
        self.hands = None
        self.last_init = 0.0
        self.drawing = None
        self.mp = None

    def get(self):
        # If mediapipe is not available in this environment, just disable hands.
        if mp is None:
            return None, None, None

        if self.hands is None or (time.time() - self.last_init) > 600:
            import mediapipe as _mp

            self.mp = _mp
            self.hands = _mp.solutions.hands.Hands(
                model_complexity=0,
                max_num_hands=1,
                min_detection_confidence=0.6,
                min_tracking_confidence=0.5,
            )
            self.drawing = _mp.solutions.drawing_utils
            self.last_init = time.time()
        return self.hands, self.drawing, self.mp


_HANDS = _HandsSingleton()


def vector_from_landmarks(landmarks, handed_label: Optional[str]) -> np.ndarray:
    pts = np.array([(lm.x, lm.y, lm.z) for lm in landmarks.landmark], dtype=np.float32)  # (21,3)
    origin = pts[0].copy()
    pts -= origin
    scale = float(np.linalg.norm(pts[9])) or 1.0
    pts /= scale
    if handed_label and handed_label.lower().startswith("right"):
        pts[:, 0] *= -1.0
    return pts.flatten()  # (63,)


def extract_hand_vector_snapshot(img: Image.Image | np.ndarray) -> Tuple[Optional[np.ndarray], Optional[str]]:
    rgb = _img_to_rgb_ndarray(img)
    hands, _, mp_mod = _HANDS.get()
    if hands is None:
        return None, None
    res = hands.process(rgb)
    if not res.multi_hand_landmarks:
        return None, None
    lms = res.multi_hand_landmarks[0]
    handed: Optional[str] = None
    if res.multi_handedness:
        handed = res.multi_handedness[0].classification[0].label
    vec = vector_from_landmarks(lms, handed)
    return vec, handed


# --------------------------------------------------
# 7) CLASSIFIER
# --------------------------------------------------
def train_classifier(db: Dict[str, List[List[float]]]):
    if not _require(["scikit-learn"]):
        return None, []
    X, y = [], []
    for label, samples in db.items():
        for s in samples:
            X.append(s)
            y.append(label)
    if len(X) < 2:
        return None, []
    X_arr = np.array(X, dtype=np.float32)
    y_arr = np.array(y, dtype=object)
    k = min(5, len(X_arr))
    clf = KNeighborsClassifier(n_neighbors=k, weights="distance", metric="euclidean")
    clf.fit(X_arr, y_arr)
    return clf, sorted(list(set(y_arr.tolist())))


def predict_vector(vec: np.ndarray):
    state = st.session_state[MODEL_STATE_KEY]
    clf = state.get("clf")
    if clf is None:
        return None, None
    pred = clf.predict([vec])[0]
    prob = None
    if hasattr(clf, "predict_proba"):
        idx = list(clf.classes_).index(pred)
        p = clf.predict_proba([vec])[0]
        prob = float(p[idx]) if 0 <= idx < len(p) else None
    return pred, prob


def _webrtc_mode_any():
    if not WEBRTC_OK:
        return None
    return getattr(WebRtcMode, "LIVE", None) or getattr(WebRtcMode, "SENDRECV")


def _init_persistent_model():
    """
    1) If a saved model exists on disk, load it into session.
    2) Otherwise, train once from default A–E DB and (if possible) save.
    """
    state = st.session_state[MODEL_STATE_KEY]
    if state.get("clf") is not None:
        return  # already initialized

    # Case 1: try persistent file
    if joblib is not None and PERSISTENT_MODEL_PATH.exists():
        try:
            clf = joblib.load(PERSISTENT_MODEL_PATH)
            state["clf"] = clf
            try:
                state["labels"] = list(getattr(clf, "classes_", []))
            except Exception:
                pass
            return
        except Exception:
            # fall through to retrain
            pass

    # Case 2: train from DB (will include default A–E on first run)
    db = load_db()
    clf, class_labels = train_classifier(db)
    state["clf"] = clf
    state["labels"] = class_labels

    # Save for everyone if possible
    if clf is not None and joblib is not None:
        try:
            PERSISTENT_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(clf, PERSISTENT_MODEL_PATH)
        except Exception:
            pass


# run model init at startup
_init_persistent_model()

# --------------------------------------------------
# 8) LANDING (two centered big buttons)
# --------------------------------------------------
current_route = st.session_state.get("signalink_route", None)

# If we have not started yet, or route is invalid, show the landing dashboard
if not st.session_state["signalink_started"] or current_route not in ("learn", "translator"):
    st.markdown(
        "<h1 style='text-align:center; margin-top:10px;'>🤟 SIGNALINK</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; font-size:1.05rem; opacity:0.9;'>"
        "Learn signs step by step, or try the live Sign → Text translator."
        "</p>",
        unsafe_allow_html=True,
    )

    # Centered two-CTA layout: [spacer] [buttons block] [spacer]
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
            if st.button("✋ Sign to Text Translator", key="cta_translator", use_container_width=True):
                st.session_state["signalink_started"] = True
                st.session_state["signalink_route"] = "translator"
                _rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# From here on, we know we are in an inner route
route = st.session_state.get("signalink_route", "learn")

# --------------------------------------------------
# 9) TITLE + BACK TO DASHBOARD (RIGHT ALIGNED, WIDE)
# --------------------------------------------------
title_col, back_col = st.columns([5, 2])

with title_col:
    st.title("🤟 SIGNALINK")

with back_col:
    st.markdown("<div style='height: 0.8rem'></div>", unsafe_allow_html=True)
    back_clicked = st.button(
        "⬅️ Back to Dashboard",
        key="btn_back_dashboard",
        use_container_width=True,
    )
    if back_clicked:
        st.session_state["signalink_started"] = False
        st.session_state["signalink_route"] = None
        _rerun()

# -------------- LEARN ROUTE --------------
if route == "learn":
    # Tabs: Learn Signs | Practice | Progress
    tab_learn, tab_practice, tab_progress = st.tabs(
        ["📚 Learn Signs", "🧪 Practice", "📊 Progress"]
    )

    # LEARN SIGNS
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
        filtered = (
            SIGN_DATA
            if cat == "All"
            else [s for s in SIGN_DATA if s["category"] == cat]
        )

        cols = st.columns(3)
        for i, sign in enumerate(filtered):
            with cols[i % 3]:
                img_path = sign["image"]
                st.image(
                    img_path
                    if (img_path and os.path.exists(img_path))
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

    # PRACTICE
    with tab_practice:
        st.subheader("🧪 Practice")
        st.caption("Tap the correct word for this sign.")

        # Initial state for practice flow
        if "practice_idx" not in st.session_state:
            st.session_state.practice_idx = 0
            st.session_state.practice_order = list(range(len(SIGN_DATA)))
            st.session_state.pop("practice_options", None)
            st.session_state.pop("practice_feedback", None)

        idx = st.session_state.practice_order[
            st.session_state.practice_idx % len(SIGN_DATA)
        ]
        item = SIGN_DATA[idx]

        # Show the sign image
        st.image(
            item["image"]
            if os.path.exists(item["image"])
            else "https://via.placeholder.com/420x240?text=SIGN",
            use_container_width=False,
        )

        # Prepare / reuse options for this question
        if (
            "practice_options" not in st.session_state
            or st.session_state.practice_options.get("target") != item["word"]
        ):
            # Build 1 correct + up to 2 random wrong options -> total 3 or fewer
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

        # Render options as buttons (in one row, up to 3 columns)
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

        # Show feedback if available for this question
        fb = st.session_state.get("practice_feedback")
        if fb and fb.get("word") == item["word"]:
            if fb["correct"]:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. It was **{item['word']}**")

        # Centered NEXT button with custom color
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

    # PROGRESS
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

# -------------- TRANSLATOR ROUTE --------------
else:
    # Tabs: Live Translator | Samples & Train | Help
    tab_live, tab_samples, tab_help = st.tabs(
        ["✋ Live Translator", "📸 Samples & Train", "ℹ️ Help"]
    )

    # LIVE TRANSLATOR
    with tab_live:
        st.subheader("✋ Live Sign → Text")
        st.caption(
            "A–E are pre-loaded on this server. More signs can be added in 📸 Samples & Train."
        )
        st.markdown(
            "- Hold **one hand** clearly in front of the camera.\n"
            "- Try not to cover the hand with your face.\n"
            "- Keep the hand steady for a moment so the model can read it.",
        )

        # If mediapipe is not available (e.g., Python 3.13), disable this feature
        if mp is None:
            st.info(
                "Live sign → text is not available on this server environment "
                "(mediapipe does not support this Python version yet). "
                "Learn and Practice tabs are still available.",
                icon="ℹ️",
            )
        else:
            state = st.session_state[MODEL_STATE_KEY]
            if state["clf"] is None:
                st.info(
                    "The live model is not ready yet. Please record a few samples and train once "
                    "in **📸 Samples & Train** to improve predictions.",
                    icon="ℹ️",
                )
            else:
                FRAME_SKIP = 3       # process 1 of every N frames
                INFER_W = 320
                _last = {"n": 0}

                def _resize_keep_aspect(img_bgr, target_w):
                    h, w = img_bgr.shape[:2]
                    if w <= target_w:
                        return img_bgr
                    sc = target_w / float(w)
                    nh = int(h * sc)
                    return cv2.resize(
                        img_bgr,
                        (target_w, nh),
                        interpolation=cv2.INTER_AREA,
                    )

                if WEBRTC_OK and _require(["opencv-python"]):
                    rtc_config = RTCConfiguration(
                        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
                    )

                    def video_frame_callback(frame):
                        _last["n"] += 1
                        img_bgr = frame.to_ndarray(format="bgr24")

                        if _last["n"] % FRAME_SKIP != 0:
                            return img_bgr

                        small = _resize_keep_aspect(img_bgr, INFER_W)
                        small_rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

                        hands, drawing, mp_mod = _HANDS.get()
                        if hands is None:
                            return img_bgr

                        res = hands.process(small_rgb)
                        pred_text = "Show one clear hand"
                        conf_text = ""
                        if res and res.multi_hand_landmarks:
                            lms = res.multi_hand_landmarks[0]
                            handed = None
                            if res.multi_handedness:
                                handed = (
                                    res.multi_handedness[0]
                                    .classification[0]
                                    .label
                                )

                            # Draw occasionally (cheaper)
                            if ((_last["n"] // FRAME_SKIP) % 2) == 0:
                                drawing.draw_landmarks(
                                    small,
                                    lms,
                                    mp_mod.solutions.hands.HAND_CONNECTIONS,
                                    drawing.DrawingSpec(
                                        color=(0, 255, 255),
                                        thickness=2,
                                        circle_radius=2,
                                    ),
                                    drawing.DrawingSpec(
                                        color=(255, 0, 255),
                                        thickness=2,
                                    ),
                                )

                            vec = vector_from_landmarks(lms, handed)
                            label, prob = predict_vector(vec)
                            if label is not None:
                                pred_text = label
                                conf_text = f"{(prob or 0.0)*100:.1f}%"

                        out = cv2.resize(
                            small,
                            (img_bgr.shape[1], img_bgr.shape[0]),
                            interpolation=cv2.INTER_LINEAR,
                        )
                        cv2.rectangle(out, (10, 10), (420, 80), (0, 0, 0), -1)
                        cv2.putText(
                            out,
                            f"Pred: {pred_text}",
                            (20, 45),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.9,
                            (255, 255, 255),
                            2,
                        )
                        if conf_text:
                            cv2.putText(
                                out,
                                conf_text,
                                (260, 45),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.9,
                                (0, 255, 0),
                                2,
                            )
                        return out

                    webrtc_streamer(
                        key="signalink-live",
                        mode=_webrtc_mode_any(),  # LIVE if available; else SENDRECV
                        rtc_configuration=rtc_config,
                        media_stream_constraints={
                            "video": {
                                "width": {"ideal": 320},
                                "height": {"ideal": 240},
                                "frameRate": {"ideal": 12, "max": 12},
                            },
                            "audio": False,
                        },
                        video_frame_callback=video_frame_callback,
                        async_processing=True,
                    )
                else:
                    st.info(
                        "WebRTC is not available; live camera prediction is disabled on this server.",
                        icon="ℹ️",
                    )

    # SAMPLES & TRAIN
    with tab_samples:
        st.subheader("📸 Samples & Train")
        st.caption(
            "A–E already have some starter samples so the demo works immediately. "
            "More real samples can be collected here to improve accuracy."
        )

        # If mediapipe is not available (e.g., Python 3.13 on Streamlit Cloud),
        # disable this feature with a clear message.
        if mp is None:
            st.info(
                "Camera-based training is not available on this server environment "
                "(mediapipe does not support this Python version yet). "
                "Learn and Practice tabs are still available.",
                icon="ℹ️",
            )
        elif not _require(["opencv-python", "scikit-learn"]):
            st.info(
                "Install missing packages shown above, then reload.",
                icon="ℹ️",
            )
        else:
            db = load_db()
            counts = db_counts(db)

            st.markdown("**How many pictures are saved for each sign?**")
            if counts:
                # Show as simple text, not raw JSON
                lines = []
                for label in sorted(counts.keys()):
                    lines.append(f"- **{label}** → {counts[label]} sample(s)")
                st.markdown("\n".join(lines))
                st.caption("Example: '**A → 3 samples**' means three training photos are saved for the sign A.")
            else:
                st.info("No samples saved yet. Choose a label and start capturing images.")

            st.markdown("---")

            label = st.selectbox("Choose a label to record", LABELS, index=0)
            st.write("1) Capture an image. 2) Click **Add sample**.")
            st.caption("Tip: Hold one hand clearly in front of the camera. Make sure the hand is not too dark or too bright.")
            snap = st.camera_input("Capture a hand image")

            c1, c2, c3 = st.columns(3)
            with c1:
                add_ok = st.button("➕ Add sample to dataset")
            with c2:
                clear_ok = st.button("🗑️ Clear all samples for this label")
            with c3:
                train_ok = st.button("🧠 Train / Retrain model")

            if add_ok:
                if snap is None:
                    st.error("Please capture an image first.")
                else:
                    img = Image.open(snap)
                    vec, _ = extract_hand_vector_snapshot(img)
                    if vec is None:
                        st.error(
                            "We could not find a clear hand in this photo.\n\n"
                            "Please try again:\n"
                            "- Hold **one hand** in front of the camera.\n"
                            "- Keep the hand inside the frame.\n"
                            "- Use good lighting so the hand is visible."
                        )
                    else:
                        db.setdefault(label, []).append(vec.tolist())
                        save_db(db)
                        st.success(
                            f"Added 1 sample to **{label}**. "
                            f"Now we have {len(db[label])} sample(s) for this sign."
                        )

            if clear_ok:
                if label in db:
                    db[label] = []
                    save_db(db)
                    st.warning(f"Cleared all samples for **{label}**")

            if train_ok:
                clf, class_labels = train_classifier(db)
                st.session_state[MODEL_STATE_KEY] = {
                    "clf": clf,
                    "labels": class_labels,
                }

                if clf is None:
                    st.error(
                        "Need at least 2 samples total "
                        "(ideally 10 or more per sign) to train."
                    )
                else:
                    # Save for all visitors on this server (persistent while container is running)
                    if joblib is not None:
                        try:
                            PERSISTENT_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
                            joblib.dump(clf, PERSISTENT_MODEL_PATH)
                            st.success(
                                f"Model trained on signs: {', '.join(class_labels)} "
                                "and saved for all visitors on this server."
                            )
                        except Exception as e:
                            st.warning(
                                f"Model trained on signs: {', '.join(class_labels)}, "
                                f"but could not save persistent file: {e}"
                            )
                    else:
                        # joblib not installed – still trained in memory for this session
                        st.success(
                            f"Model trained on signs: {', '.join(class_labels)}"
                        )

    # HELP
    with tab_help:
        st.subheader("ℹ️ Help")
        st.markdown(
            """
            **For local development (Python ≤ 3.12):**
            ```bash
            pip install mediapipe opencv-python scikit-learn
            pip install streamlit-webrtc joblib
            ```

            **Workflow for better accuracy:**

            1. Go to **📸 Samples & Train**, pick a sign (for example, "A"), capture 10–30 snapshots, and click **Train / Retrain model**.  
            2. Repeat for other signs (B, C, Hello, Thank you, …).  
            3. Open **✋ Live Translator** and show one hand sign to the camera—predictions appear with confidence (on supported environments).
            """
        )
