# ANTIDOTE/pages/Signalink.py
# --------------------------------------------------
# SIGNALINK – Landing (2 CTAs) → Learn (Learn/Practice/Progress) OR Sign→Text Translator
# --------------------------------------------------
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import streamlit as st
from PIL import Image

# ===== small compatibility helper for rerun =====
def _rerun():
    # Prefer st.rerun() (new), fallback to st.experimental_rerun() (old)
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# ===== Optional deps (we show install hints if missing) =====
MISSING = []
try:
    import mediapipe as mp
except Exception:
    mp = None
    MISSING.append("mediapipe")

try:
    import cv2
    cv2.setUseOptimized(True)
    try:
        cv2.setNumThreads(2)
    except Exception:
        pass
except Exception:
    cv2 = None
    MISSING.append("opencv-python")

try:
    from sklearn.neighbors import KNeighborsClassifier
except Exception:
    KNeighborsClassifier = None
    MISSING.append("scikit-learn")

try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
    WEBRTC_OK = True
except Exception:
    WEBRTC_OK = False

# --------------------------------------------------
# 1) PATHS / ASSETS
# --------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]  # .../ANTIDOTE
SIGNALINK_ASSETS = (REPO_ROOT / "signalink_assets")
IMAGES_DIR = SIGNALINK_ASSETS / "images"
SIGNALINK_ASSETS.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

GESTURE_DB_PATH = SIGNALINK_ASSETS / "gesture_db.json"  # KNN training samples
MODEL_STATE_KEY = "signalink_knn_model"

# Demo dataset (expand with your own images in signalink_assets/images)
SIGN_DATA = [
    {"word": "Hello",     "category": "Basic",  "image": str(IMAGES_DIR / "hello.png"),     "hint": "Hand up, small wave."},
    {"word": "Thank you", "category": "Basic",  "image": str(IMAGES_DIR / "thankyou.png"),  "hint": "From chin outward."},
    {"word": "Sorry",     "category": "Basic",  "image": str(IMAGES_DIR / "sorry.png"),     "hint": "Closed fist over chest."},
    {"word": "Eat",       "category": "Daily",  "image": str(IMAGES_DIR / "eat.png"),       "hint": "Fingers to mouth."},
    {"word": "Help",      "category": "Daily",  "image": str(IMAGES_DIR / "help.png"),      "hint": "Thumb-up on palm."},
    {"word": "Mother",    "category": "People", "image": str(IMAGES_DIR / "mother.png"),    "hint": "Thumb to chin."},
    {"word": "Father",    "category": "People", "image": str(IMAGES_DIR / "father.png"),    "hint": "Thumb to forehead."},
]
CATEGORIES = sorted(list({s["category"] for s in SIGN_DATA}))
LABELS = [s["word"] for s in SIGN_DATA]

# --------------------------------------------------
# 2) GLOBAL STYLES
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

    /* Reusable big buttons */
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
    .cta .stButton>button:hover { transform: translateY(-2px); filter: brightness(1.04) saturate(1.03); }
    .cta .stButton>button:active { transform: translateY(0); filter: brightness(0.98); }

    .sign-card {
      background: rgba(3,16,22,.45);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 16px; padding: 12px 14px; margin-bottom: 12px;
      box-shadow: 0 10px 30px rgba(0,0,0,.25);
    }
    .cat-pill {
      display:inline-block; background: rgba(99,102,241,0.12);
      border: 1px solid rgba(99,102,241,0.25); padding: 7px 14px; border-radius: 999px;
      font-size: 14px; margin-right: 8px; margin-bottom: 8px; user-select:none;
    }
    .cat-pill.active {
      background: linear-gradient(120deg,#6366f1,#38bdf8);
      color:#061018; border-color: transparent; font-weight: 800;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 3) SESSION STATE
# --------------------------------------------------
st.session_state.setdefault("signalink_started", False)           # show landing first
st.session_state.setdefault("signalink_route", None)              # "learn" | "translator"
st.session_state.setdefault("signalink_cat", "All")
st.session_state.setdefault("learn_progress", {"learned": [], "quiz_scores": []})
st.session_state.setdefault(MODEL_STATE_KEY, {"clf": None, "labels": []})

# --------------------------------------------------
# 4) UTIL: right-aligned big button
# --------------------------------------------------
def right_aligned_button(label: str, key: str, css_class: str = "") -> bool:
    spacer, btncol = st.columns([8, 2])  # push right
    with btncol:
        st.markdown(f'<div class="cta {css_class}">', unsafe_allow_html=True)
        pressed = st.button(label, key=key, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return pressed

# --------------------------------------------------
# 5) DB HELPERS (for KNN samples)
# --------------------------------------------------
def load_db() -> Dict[str, List[List[float]]]:
    if GESTURE_DB_PATH.exists():
        try:
            with open(GESTURE_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_db(db: Dict[str, List[List[float]]]) -> None:
    with open(GESTURE_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)

def db_counts(db: Dict[str, List[List[float]]]) -> Dict[str, int]:
    return {k: len(v) for k, v in db.items()}

# --------------------------------------------------
# 6) MEDIAPIPE FEATURE EXTRACTION (optimized)
# --------------------------------------------------
def _require(pkgs: List[str]) -> bool:
    if not pkgs:
        return True
    missing = [p for p in pkgs if p in MISSING]
    if missing:
        st.error(
            "Missing dependencies:\n\n```\n" +
            "\n".join(f"pip install {p}" for p in missing) +
            "\n```",
            icon="⚠️",
        )
        return False
    return True

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
        self.last_init = 0
        self.drawing = None
        self.mp = None

    def get(self):
        if not _require(["mediapipe"]):
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
    handed = None
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
    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=object)
    k = min(5, len(X))
    clf = KNeighborsClassifier(n_neighbors=k, weights="distance", metric="euclidean")
    clf.fit(X, y)
    return clf, sorted(list(set(y.tolist())))

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

# --------------------------------------------------
# 8) LANDING (two colored, right-aligned big buttons)
# --------------------------------------------------
# --------------------------------------------------
# 8) LANDING (two centered buttons in one row)
# --------------------------------------------------
if not st.session_state.signalink_started:
    st.markdown(
        "<h1 style='text-align:center; margin-top:10px;'>🤟 SIGNALINK</h1>",
        unsafe_allow_html=True,
    )

    # Outer columns → left spacer | center content | right spacer
    left_spacer, center_col, right_spacer = st.columns([1, 2, 1])

    with center_col:
        # Inner columns → two buttons in a single centered row
        col_learn, col_trans = st.columns(2)

        with col_learn:
            st.markdown('<div class="cta learn">', unsafe_allow_html=True)
            if st.button("📚 Learn Signs", key="cta_learn", use_container_width=True):
                st.session_state.signalink_started = True
                st.session_state.signalink_route = "learn"
                _rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with col_trans:
            st.markdown('<div class="cta signtext">', unsafe_allow_html=True)
            if st.button("✋ Sign to Text Translator", key="cta_translator", use_container_width=True):
                st.session_state.signalink_started = True
                st.session_state.signalink_route = "translator"
                _rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


# --------------------------------------------------
# 9) ROUTES
# --------------------------------------------------
route = st.session_state.signalink_route or "learn"
st.title("🤟 SIGNALINK")

# -------------- LEARN ROUTE --------------
if route == "learn":
    # Tabs: Learn Signs | Practice | Progress
    tab_learn, tab_practice, tab_progress = st.tabs(["📚 Learn Signs", "🧪 Practice", "📊 Progress"])

    # LEARN SIGNS
    with tab_learn:
        st.subheader("📚 Learn Signs")
        st.caption("Browse sample signs and hints.")
        st.write("**Categories**")
        all_cats = ["All"] + CATEGORIES
        pill_cols = st.columns(len(all_cats))
        for i, cat_name in enumerate(all_cats):
            active = "active" if st.session_state.signalink_cat == cat_name else ""
            if pill_cols[i].button(cat_name, key=f"pill_{cat_name}"):
                st.session_state.signalink_cat = cat_name
            pill_cols[i].markdown(f"<span class='cat-pill {active}'>{cat_name}</span>", unsafe_allow_html=True)

        st.selectbox("Choose a category", all_cats, key="signalink_cat")

        cat = st.session_state.signalink_cat
        filtered = SIGN_DATA if cat == "All" else [s for s in SIGN_DATA if s["category"] == cat]
        cols = st.columns(3)
        for i, sign in enumerate(filtered):
            with cols[i % 3]:
                st.markdown("<div class='sign-card'>", unsafe_allow_html=True)
                img_path = sign["image"]
                st.image(img_path if (img_path and os.path.exists(img_path))
                         else "https://via.placeholder.com/300x180?text=SIGN", use_container_width=True)
                st.markdown(f"**{sign['word']}**")
                st.caption(f"Category: {sign['category']}")
                st.caption(f"Hint: {sign['hint']}")
                if st.button(f"Mark learned", key=f"learn_{sign['word']}"):
                    learned = st.session_state.learn_progress["learned"]
                    if sign["word"] not in learned:
                        learned.append(sign["word"])
                    st.success(f"Marked {sign['word']} as learned ✅")
                st.markdown("</div>", unsafe_allow_html=True)

    # PRACTICE
    with tab_practice:
        st.subheader("🧪 Practice")
        st.caption("We’ll show a sign image—type the correct word.")
        if "practice_idx" not in st.session_state:
            st.session_state.practice_idx = 0
            st.session_state.practice_order = list(range(len(SIGN_DATA)))

        idx = st.session_state.practice_order[st.session_state.practice_idx % len(SIGN_DATA)]
        item = SIGN_DATA[idx]
        st.image(item["image"] if os.path.exists(item["image"])
                 else "https://via.placeholder.com/420x240?text=SIGN", use_container_width=False)
        ans = st.text_input("Your answer (word):", key="practice_answer")
        col_a, col_b = st.columns(2)
        if col_a.button("Check"):
            if ans.strip().lower() == item["word"].lower():
                st.success("✅ Correct!")
                st.session_state.learn_progress["quiz_scores"].append({"word": item["word"], "correct": True})
            else:
                st.error(f"❌ Incorrect. It was **{item['word']}**")
                st.session_state.learn_progress["quiz_scores"].append({"word": item["word"], "correct": False})
        if col_b.button("Next"):
            st.session_state.practice_idx += 1
            _rerun()

    # PROGRESS
    with tab_progress:
        st.subheader("📊 Progress")
        learned = st.session_state.learn_progress["learned"]
        scores = st.session_state.learn_progress["quiz_scores"]
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
    tab_live, tab_samples, tab_help = st.tabs(["✋ Live Translator", "📸 Samples & Train", "ℹ️ Help"])

    # LIVE TRANSLATOR
    with tab_live:
        st.subheader("✋ Live Sign → Text")
        st.caption("Predicts one of your trained labels. Collect samples & train first if needed.")
        state = st.session_state[MODEL_STATE_KEY]
        if state["clf"] is None:
            st.warning("No trained model yet. Add samples and train in **📸 Samples & Train**.", icon="⚠️")
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
                return cv2.resize(img_bgr, (target_w, nh), interpolation=cv2.INTER_AREA)

            if WEBRTC_OK and _require(["mediapipe", "opencv-python"]):
                rtc_config = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

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
                    pred_text = "No hand"
                    conf_text = ""
                    if res and res.multi_hand_landmarks:
                        lms = res.multi_hand_landmarks[0]
                        handed = None
                        if res.multi_handedness:
                            handed = res.multi_handedness[0].classification[0].label

                        # Draw occasionally (cheaper)
                        if ((_last["n"] // FRAME_SKIP) % 2) == 0:
                            drawing.draw_landmarks(
                                small, lms, mp_mod.solutions.hands.HAND_CONNECTIONS,
                                drawing.DrawingSpec(color=(0,255,255), thickness=2, circle_radius=2),
                                drawing.DrawingSpec(color=(255,0,255), thickness=2)
                            )

                        vec = vector_from_landmarks(lms, handed)
                        label, prob = predict_vector(vec)
                        if label is not None:
                            pred_text = label
                            conf_text = f"{(prob or 0.0)*100:.1f}%"

                    out = cv2.resize(small, (img_bgr.shape[1], img_bgr.shape[0]), interpolation=cv2.INTER_LINEAR)
                    cv2.rectangle(out, (10, 10), (380, 70), (0, 0, 0), -1)
                    cv2.putText(out, f"Pred: {pred_text}", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2)
                    if conf_text:
                        cv2.putText(out, conf_text, (260, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
                    return out

                webrtc_streamer(
                    key="signalink-live",
                    mode=_webrtc_mode_any(),  # LIVE if available; else SENDRECV
                    rtc_configuration=rtc_config,
                    media_stream_constraints={
                        "video": {"width": {"ideal": 320}, "height": {"ideal": 240}, "frameRate": {"ideal": 12, "max": 12}},
                        "audio": False
                    },
                    video_frame_callback=video_frame_callback,
                    async_processing=True,
                )
            else:
                st.info("WebRTC not available; using **Snapshot Mode**.", icon="ℹ️")
                snap = st.camera_input("Take a snapshot for prediction")
                if snap is not None:
                    img = Image.open(snap)
                    vec, _ = extract_hand_vector_snapshot(img)
                    if vec is None:
                        st.error("No hand detected. Try again with better lighting and one hand in frame.")
                    else:
                        label, prob = predict_vector(vec)
                        if label is None:
                            st.error("Model not ready or could not predict.")
                        else:
                            st.success(f"Prediction: **{label}**" + (f"  ({prob*100:.1f}% conf.)" if prob else ""))

    # SAMPLES & TRAIN
    with tab_samples:
        st.subheader("📸 Samples & Train")
        st.caption("Capture labeled samples via webcam, then train the on-device classifier.")
        if not _require(["mediapipe", "opencv-python", "scikit-learn"]):
            st.info("Install missing packages shown above, then reload.", icon="ℹ️")
        else:
            db = load_db()
            with st.expander("Current dataset summary", expanded=True):
                counts = db_counts(db)
                st.write(counts if counts else "No samples yet.")

            label = st.selectbox("Choose a label to record", LABELS, index=0)
            st.write("1) Capture an image. 2) Click **Add sample**.")
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
                        st.error("No hand detected. Try better lighting and one hand in frame.")
                    else:
                        db.setdefault(label, []).append(vec.tolist())
                        save_db(db)
                        st.success(f"Added 1 sample to **{label}**. Total for {label}: {len(db[label])}")

            if clear_ok:
                if label in db:
                    db[label] = []
                    save_db(db)
                    st.warning(f"Cleared all samples for **{label}**")

            if train_ok:
                clf, class_labels = train_classifier(db)
                st.session_state[MODEL_STATE_KEY] = {"clf": clf, "labels": class_labels}
                if clf is None:
                    st.error("Need at least 2 samples total (ideally ≥10 per label) to train.")
                else:
                    st.success(f"Model trained on classes: {', '.join(class_labels)}")

    # HELP
    with tab_help:
        st.subheader("ℹ️ Help")
        st.markdown(
            """
            **Install once:**
            ```
            pip install mediapipe opencv-python scikit-learn
            pip install streamlit-webrtc
            ```
            **Workflow:**
            1. Go to **📸 Samples & Train**, pick a label (e.g., "Hello"), capture 10–30 snapshots, and **Train**.  
            2. Repeat for other labels (Thank you, Sorry, …).  
            3. Open **✋ Live Translator** and keep one hand in frame—predictions appear with confidence.
            """
        )
