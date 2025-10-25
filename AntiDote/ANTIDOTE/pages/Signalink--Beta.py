# ANTIDOTE/pages/2_ ASL Sign.py
import queue
from collections import deque, defaultdict

import numpy as np
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration, VideoProcessorBase
import mediapipe as mp
from sklearn.neighbors import KNeighborsClassifier
from PIL import Image, ImageDraw, ImageFont


st.title("🤟 ANTIDOTE — ASL Sign (MediaPipe + k-NN, no OpenCV)")

def extract_xy_features(hand_landmarks, frame_w, frame_h):
    """42-D: (x,y) of 21 points, centered on wrist & scale-normalized."""
    xs = [lm.x * frame_w for lm in hand_landmarks.landmark]
    ys = [lm.y * frame_h for lm in hand_landmarks.landmark]
    xs, ys = np.array(xs), np.array(ys)
    x0, y0 = xs[0], ys[0]
    xs -= x0; ys -= y0
    scale = float(np.max(np.sqrt(xs**2 + ys**2)) + 1e-6)
    xs /= scale; ys /= scale
    return np.stack([xs, ys], axis=1).reshape(-1).astype("float32")

def pil_draw_text(draw, text, x, y, color=(0, 200, 0)):
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    draw.text((x, y), text, fill=color, font=font)

def pil_draw_landmarks(draw, hand_landmarks, w, h,
                       color_pts=(30,220,30), color_conn=(100,180,255)):
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks.landmark]
    for i, j in mp.solutions.hands.HAND_CONNECTIONS:
        draw.line([pts[i], pts[j]], fill=color_conn, width=3)
    for (x, y) in pts:
        r = 4
        draw.ellipse((x-r, y-r, x+r, y+r), outline=color_pts, width=2)

class ASLProcessor(VideoProcessorBase):
    def __init__(self):
        self.hands = mp.solutions.hands.Hands(
            max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.6
        )
        self.samples_X, self.samples_y = [], []
        self.class_counts = defaultdict(int)
        self.clf, self.model_ready = None, False

        self.collecting, self.collect_label, self.collect_frames_left = False, None, 0

        self.pred_buffer = deque(maxlen=8)
        self.current_pred, self.current_conf = None, 0.0

        self.compose_enabled, self.compose_min_stable = True, 6
        self.text_out, self._last_committed_pred = "", None

        self.info_queue = queue.Queue()

    # --- dataset/model ---
    def set_collect(self, label, n_frames):
        self.collecting, self.collect_label, self.collect_frames_left = True, str(label), int(n_frames)

    def stop_collect(self):
        self.collecting, self.collect_label, self.collect_frames_left = False, None, 0

    def fit_model(self, k=5):
        if len(self.samples_y) >= 2 and len(set(self.samples_y)) >= 2:
            self.clf = KNeighborsClassifier(n_neighbors=int(k), weights="distance", metric="euclidean")
            self.clf.fit(np.array(self.samples_X), np.array(self.samples_y))
            self.model_ready = True
            self.info_queue.put(("model", "trained"))
        else:
            self.model_ready = False
            self.info_queue.put(("model", "not_enough_data"))

    # --- compose text ---
    def set_compose(self, enabled=True, min_stable=6):
        self.compose_enabled, self.compose_min_stable = bool(enabled), int(min_stable)

    def clear_text(self):
        self.text_out, self._last_committed_pred = "", None

    # --- video callback ---
    def recv(self, frame):
        rgb = frame.to_ndarray(format="rgb24")
        h, w, _ = rgb.shape
        result = self.hands.process(rgb)

        pil_img = Image.fromarray(rgb)
        draw = ImageDraw.Draw(pil_img)

        features, bbox = None, None

        if result.multi_hand_landmarks:
            hand = result.multi_hand_landmarks[0]
            pil_draw_landmarks(draw, hand, w, h)

            xs = [lm.x for lm in hand.landmark]
            ys = [lm.y for lm in hand.landmark]
            x1, x2 = int(min(xs) * w), int(max(xs) * w)
            y1, y2 = int(min(ys) * h), int(max(ys) * h)
            bbox = (x1, y1, x2, y2)
            draw.rectangle([x1, y1, x2, y2], outline=(100, 100, 255), width=2)

            features = extract_xy_features(hand, w, h)

            if self.collecting and self.collect_frames_left > 0:
                self.samples_X.append(features)
                self.samples_y.append(self.collect_label)
                self.class_counts[self.collect_label] += 1
                self.collect_frames_left -= 1
                pil_draw_text(draw, f"Collecting [{self.collect_label}] left: {self.collect_frames_left}",
                              x1, max(10, y1 - 20), (255, 165, 0))
                if self.collect_frames_left == 0:
                    self.stop_collect()
                    self.info_queue.put(("collect", "done"))

        if self.model_ready and features is not None:
            try:
                proba = self.clf.predict_proba([features])[0]
                idx = int(np.argmax(proba))
                pred_label = self.clf.classes_[idx]
                pred_conf = float(proba[idx])
            except Exception:
                pred_label = self.clf.predict([features])[0]
                pred_conf = 1.0

            self.pred_buffer.append(pred_label)
            if len(self.pred_buffer) == self.pred_buffer.maxlen:
                mode = max(set(self.pred_buffer), key=self.pred_buffer.count)
                self.current_pred, self.current_conf = mode, pred_conf

                if self.compose_enabled and self._last_committed_pred != self.current_pred \
                   and self.pred_buffer.count(self.current_pred) >= self.compose_min_stable:
                    self.text_out += str(self.current_pred)
                    self._last_committed_pred = self.current_pred
            else:
                self.current_pred, self.current_conf = pred_label, pred_conf

            if bbox and self.current_pred:
                x1, y1, x2, y2 = bbox
                pil_draw_text(draw, f"Pred: {self.current_pred} ({self.current_conf:.2f})",
                              x1, min(h - 30, y2 + 10), (0, 220, 0))
        elif self.collecting:
            pil_draw_text(draw, "Place your hand in the box to collect samples.", 10, 10, (0, 200, 255))

        # bottom text bar
        draw.rectangle([0, h - 50, w, h], fill=(0, 0, 0))
        pil_draw_text(draw, self.text_out[-60:] if self.text_out else " ", 10, h - 35, (255, 255, 255))

        out_rgb = np.asarray(pil_img)
        out_bgr = out_rgb[:, :, ::-1]  # RGB->BGR (what webrtc expects)
        return out_bgr


# ---------- Sidebar ----------
with st.sidebar:
    st.header("Settings")
    rtc_conf = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

    st.subheader("Collect")
    label = st.text_input("Label (e.g., A, HELLO)", value="A")
    n_frames = st.slider("Frames", 10, 200, 50, 10)

    st.subheader("Train")
    k = st.slider("k (neighbors)", 1, 15, 5, 1)

    st.subheader("Compose")
    compose_enabled = st.toggle("Auto-append stable prediction", True)
    min_stable = st.slider("Stability (out of 8)", 1, 8, 6)

    clear_text = st.button("Clear composed text")

# ---------- Main ----------
left, right = st.columns([2, 1])

with left:
    ctx = webrtc_streamer(
        key="asl-page",
        mode=WebRtcMode.SENDRECV,          # <-- enum, not string
        rtc_configuration=rtc_conf,
        video_processor_factory=ASLProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

with right:
    st.subheader("Live status")

    if ctx and ctx.state.playing and ctx.video_processor:
        vp: ASLProcessor = ctx.video_processor
        vp.set_compose(compose_enabled, min_stable)
        if clear_text:
            vp.clear_text()

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Start collecting"):
                vp.set_collect(label, n_frames)
        with c2:
            if st.button("Stop"):
                vp.stop_collect()

        if st.button("Train model"):
            vp.fit_model(k)

        # drain messages
        try:
            while True:
                t, m = vp.info_queue.get_nowait()
                if t == "model" and m == "trained":
                    st.success("Model trained ✔️")
                if t == "model" and m == "not_enough_data":
                    st.warning("Need ≥ 2 different labels.")
                if t == "collect" and m == "done":
                    st.info("Collection finished for this label.")
        except queue.Empty:
            pass

        st.markdown("### Samples per class")
        if vp.class_counts:
            st.table({"Class": list(vp.class_counts.keys()), "Samples": list(vp.class_counts.values())})
        else:
            st.caption("No samples yet.")
    else:
        st.info("Start the webcam and allow camera permission.")
