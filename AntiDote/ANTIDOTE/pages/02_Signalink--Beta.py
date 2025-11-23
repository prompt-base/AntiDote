# ANTIDOTE/pages/Signalink--Beta.py
# --------------------------------------------------
# SIGNALINK – Learn (Learn/Practice/Progress) OR Sign → Text Translator (Snapshot)
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

# --------------------------------------------------
# 1) PATHS / ASSETS
# --------------------------------------------------
PROJECT_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_DIR.parent

IMAGES_DIR = REPO_ROOT / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

SIGNALINK_ASSETS = REPO_ROOT / "signalink_assets"
SIGNALINK_ASSETS.mkdir(parents=True, exist_ok=True)
GESTURE_DB_PATH = SIGNALINK_ASSETS / "gesture_db.json"
PERSISTENT_MODEL_PATH = SIGNALINK_ASSETS / "signalink_knn.pkl"

MODEL_STATE_KEY = "signalink_knn_model"

# --------------------------------------------------
# 2) SIGN DATA (includes Alphabet A–E)
# --------------------------------------------------
SIGN_DATA = [
    # Alphabet A–E
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

    # Basic polite phrases
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

    # Daily action
    {
        "word": "Eat",
        "category": "Daily",
        "image": str(IMAGES_DIR / "eat.png"),
        "hint": "Fingertips move toward mouth.",
    },

    # People / family
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

    div[data-testid="stImage"] {
      background: rgba(3,16,22,.45);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 16px;
      padding: 12px 14px;
      margin-bottom: 12px;
      box-shadow: 0 10px 30px rgba(0,0,0,.25);
    }

    div[data-testid="stImage"] img {
      width: 100% !important;
      height: 190px !important;
      object-fit: contain;
      background: rgba(6,16,24,0.9);
      border-radius: 12px;
      padding: 6px;
    }

    div.stTabs [data-baseweb="tab"] {
      color: #ffffff !important;
      font-weight: 500;
    }
    div.stTabs [data-baseweb="tab"][aria-selected="true"] {
      color: #ff4b4b !important;
    }

    .st-emotion-cache-12j140x.et2rgd20 p{
      color:#0b1220;
    }
    .st-emotion-cache-12j140x.et2rgd20:hover p{
      color:#ffffff;
    }
    .st-emotion-cache-1s2v671.e1gk92lc0 p{
      color:#ffffff;
    }

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
st.session_state.setdefault("signalink_started", False)
st.session_state.setdefault("signalink_route", None)  # "learn" | "translator"
st.session_state.setdefault("signalink_cat", "All")
st.session_state.setdefault("learn_progress", {"learned": [], "quiz_scores": []})
st.session_state.setdefault(MODEL_STATE_KEY, {"clf": None, "labels": []})

# --------------------------------------------------
# 5) DB HELPERS
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
    def mk(seed: int) -> List[float]:
        rng = np.random.default_rng(seed)
        v = rng.normal(0, 0.15, 63).astype(np.float32)
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
    db = default_gesture_db()
    save_db(db)
    return db


def save_db(db: Dict[str, List[List[float]]]) -> None:
    with open(GESTURE_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)


def db_counts(db: Dict[str, List[List[float]]]) -> Dict[str, int]:
    return {k: len(v) for k, v in db.items()}

# --------------------------------------------------
# 6) MEDIAPIPE FEATURE EXTRACTION
# --------------------------------------------------
def _img_to_rgb_ndarray(file_or_nd: Image.Image | np.ndarray) -> np.ndarray:
    if isinstance(file_or_nd, np.ndarray):
        return file_or_nd
    return np.array(file_or_nd.convert("RGB"))


class _HandsSingleton:
    """
    Reuse MediaPipe Hands across calls.
    For our use case (snapshots), we use static_image_mode=True
    so each photo is treated as a fresh image.
    """

    def __init__(self):
        self.hands = None
        self.last_init = 0.0
        self.drawing = None
        self.mp = None

    def get(self):
        # If mediapipe is not available in this environment, just disable hands.
        if mp is None:
            return None, None, None

        # Re-create the Hands object every 10 minutes just to be safe
        if self.hands is None or (time.time() - self.last_init) > 600:
            import mediapipe as _mp

            self.mp = _mp
            self.hands = _mp.solutions.hands.Hands(
                static_image_mode=True,       # 🔴 important for single photos
                model_complexity=1,
                max_num_hands=1,
                min_detection_confidence=0.4,  # a bit less strict than 0.6
                min_tracking_confidence=0.4,
            )
            self.drawing = _mp.solutions.drawing_utils
            self.last_init = time.time()
        return self.hands, self.drawing, self.mp


_HANDS = _HandsSingleton()


def vector_from_landmarks(landmarks, handed_label: Optional[str]) -> np.ndarray:
    pts = np.array([(lm.x, lm.y, lm.z) for lm in landmarks.landmark], dtype=np.float32)
    origin = pts[0].copy()
    pts -= origin
    scale = float(np.linalg.norm(pts[9])) or 1.0
    pts /= scale
    if handed_label and handed_label.lower().startswith("right"):
        pts[:, 0] *= -1.0
    return pts.flatten()


def extract_hand_vector_snapshot(img: Image.Image | np.ndarray) -> Tuple[Optional[np.ndarray], Optional[str]]:
    """
    Take a single image (PIL or numpy), run MediaPipe Hands,
    and return a 63-dimensional normalized vector if a hand is found.
    """
    rgb = _img_to_rgb_ndarray(img)

    # Ensure shape (H, W, 3)
    if rgb.ndim == 2:
        # grayscale -> fake 3-channel
        rgb = np.stack([rgb] * 3, axis=-1)
    if rgb.shape[-1] > 3:
        rgb = rgb[:, :, :3]

    hands, _, mp_mod = _HANDS.get()
    if hands is None:
        return None, None

    # MediaPipe expects RGB uint8
    rgb = rgb.astype(np.uint8)

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


def _init_persistent_model():
    state = st.session_state[MODEL_STATE_KEY]
    if state.get("clf") is not None:
        return

    # Try load saved model
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
            pass

    # Train from DB (includes default A–E on first run)
    db = load_db()
    clf, class_labels = train_classifier(db)
    state["clf"] = clf
    state["labels"] = class_labels

    if clf is not None and joblib is not None:
        try:
            PERSISTENT_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(clf, PERSISTENT_MODEL_PATH)
        except Exception:
            pass


_init_persistent_model()

# --------------------------------------------------
# 8) LANDING (two big buttons)
# --------------------------------------------------
current_route = st.session_state.get("signalink_route", None)

if not st.session_state["signalink_started"] or current_route not in ("learn", "translator"):
    st.markdown(
        "<h1 style='text-align:center; margin-top:10px;'>🤟 SIGNALINK</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; font-size:1.05rem; opacity:0.9;'>"
        "Learn sign language basics, or try the Sign → Text translator."
        "</p>",
        unsafe_allow_html=True,
    )

    l, center_block, r = st.columns([1, 2, 1])
    with center_block:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="cta learn">', unsafe_allow_html=True)
            if st.button("📚 Learn Signs", key="cta_learn", use_container_width=True):
                st.session_state["signalink_started"] = True
                st.session_state["signalink_route"] = "learn"
                _rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="cta signtext">', unsafe_allow_html=True)
            if st.button("✋ Sign to Text (Snapshot)", key="cta_translator", use_container_width=True):
                st.session_state["signalink_started"] = True
                st.session_state["signalink_route"] = "translator"
                _rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

route = st.session_state.get("signalink_route", "learn")

# --------------------------------------------------
# 9) TITLE + BACK
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
# 10) LEARN ROUTE
# --------------------------------------------------
if route == "learn":
    tab_learn, tab_practice, tab_progress = st.tabs(
        ["📚 Learn Signs", "🧪 Practice", "📊 Progress"]
    )

    # LEARN
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

    # PRACTICE
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

# --------------------------------------------------
# 11) TRANSLATOR ROUTE – SNAPSHOT VERSION
# --------------------------------------------------
else:
    tab_live, tab_samples, tab_help = st.tabs(
        ["✋ Sign → Text (Snapshot)", "📸 Samples & Train", "ℹ️ Help"]
    )

    # LIVE (SNAPSHOT) TRANSLATOR
    with tab_live:
        st.subheader("✋ Sign → Text (Snapshot)")
        st.caption("Take a photo of a hand sign. The AI will guess the matching label.")

        st.markdown(
            """
            **How to use this demo:**
            - Hold **one hand** in front of the camera in a clear sign shape.  
            - Try not to cover the hand with the face or other objects.  
            - Use normal lighting (not too dark, not too bright).  
            - Press **Take snapshot**, then **Predict sign**.
            """
        )

        if mp is None:
            st.info(
                "Hand detection is not available in this environment "
                "(mediapipe is missing). Only Learn and Practice tabs will work.",
                icon="ℹ️",
            )
        else:
            state = st.session_state[MODEL_STATE_KEY]
            clf = state.get("clf")
            if clf is None:
                st.info(
                    "The sign classifier is not ready yet. "
                    "Please record some samples and train once in **📸 Samples & Train** "
                    "to improve sign recognition.",
                    icon="ℹ️",
                )
            else:
                snap = st.camera_input("Take a snapshot of the hand sign")

                pred_text = None
                conf_text = None

                if st.button("🔍 Predict sign", use_container_width=True):
                    if snap is None:
                        st.error("Please take a snapshot first.")
                    else:
                        img = Image.open(snap)
                        vec, _ = extract_hand_vector_snapshot(img)
                        if vec is None:
                            st.error(
                                "We could not clearly detect a hand in this photo.\n\n"
                                "Please try again:\n"
                                "- Show **one hand** clearly inside the frame.\n"
                                "- Keep the hand open in a fixed sign shape.\n"
                                "- Use better lighting so the hand is visible."
                            )
                        else:
                            label, prob = predict_vector(vec)
                            if label is None:
                                st.warning(
                                    "The model could not decide a label. "
                                    "Please collect more training samples in **📸 Samples & Train**."
                                )
                            else:
                                pred_text = label
                                conf_text = f"{(prob or 0.0)*100:.1f}%"
                                st.success(f"Predicted sign: **{pred_text}**  (confidence: {conf_text})")

                if pred_text is None:
                    st.info("After taking a snapshot, click **Predict sign** to see the result.")

    # SAMPLES & TRAIN
    with tab_samples:
        st.subheader("📸 Samples & Train")
        st.caption(
            "A–E already have some starter samples so the demo works immediately. "
            "More real samples can be collected here to improve accuracy."
        )

        if mp is None:
            st.info(
                "Camera-based training is not available in this environment. "
                "Only the Learn / Practice tabs will work.",
                icon="ℹ️",
            )
        elif not _require(["opencv-python", "scikit-learn"]):
            st.info(
                "Install the missing packages shown above, then reload the app.",
                icon="ℹ️",
            )
        else:
            db = load_db()
            counts = db_counts(db)

            st.markdown("**How many pictures are saved for each sign?**")
            if counts:
                lines = []
                for label in sorted(counts.keys()):
                    lines.append(f"- **{label}** → {counts[label]} sample(s)")
                st.markdown("\n".join(lines))
                st.caption(
                    "Example: '**A → 3 samples**' means three training photos are saved for the sign A."
                )
            else:
                st.info("No samples saved yet. Choose a sign and start capturing images.")

            st.markdown("---")

            label = st.selectbox("Choose a sign label to record", LABELS, index=0)
            st.write("1) Capture an image. 2) Click **Add sample**.")
            st.caption(
                "Tip: Hold one hand clearly in front of the camera. "
                "Make sure the hand is not too dark or too bright."
            )
            snap = st.camera_input("Capture a hand image")

            c1, c2, c3 = st.columns(3)
            with c1:
                add_ok = st.button("➕ Add sample to dataset")
            with c2:
                clear_ok = st.button("🗑️ Clear all samples for this sign")
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
                        st.success(
                            f"Model trained on signs: {', '.join(class_labels)}"
                        )

    # HELP
    with tab_help:
        st.subheader("ℹ️ Help – How SIGNALINK works")
        st.markdown(
            """
            **What happens inside this AI demo?**

            1. The camera takes a picture of the hand.  
            2. A library called **MediaPipe** finds 21 key points on the hand (finger tips, joints, etc.).  
            3. These 21 points are converted into a **63-number vector** (x, y, z for each point), normalized so the hand size and position do not matter too much.  
            4. A simple AI model called **K-Nearest Neighbours (KNN)** compares this vector to all saved training examples.  
            5. The AI picks the sign label (A, B, C, Hello, etc.) that is closest to the new vector and shows the prediction.

            **Why are more training pictures helpful?**

            - Different people show the same sign slightly differently.  
            - More examples (10–30 photos per sign) teach the model to handle different hand shapes, camera angles, and lighting.  
            - This makes the final prediction more stable and accurate.

            **How to explain this in the science fair:**

            - SIGNALINK is an **AI-based sign language helper**.  
            - It uses **computer vision** to find the hand and **machine learning** (KNN) to guess the sign.  
            - Students can **add their own samples** and retrain the model live during the demo.  
            """
        )

