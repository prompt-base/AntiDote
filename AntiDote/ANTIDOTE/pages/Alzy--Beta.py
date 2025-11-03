import os
import json
import uuid
import random
import datetime
from pathlib import Path
from typing import List, Dict, Any

import streamlit as st
from PIL import Image
import streamlit.components.v1 as components

# =========================================================
# 1. CONSTANTS / PATHS
# =========================================================
# your real folder:
HARDCODED_UPLOAD_DIR = Path(r"C:\Users\Anurag\PycharmProjects\AntiDote\uploads")

# we still keep these JSONs (best-effort)
ROOT_UPLOADS_JSON = Path("uploads.json")
DATA_FILE = Path("data.json")

# fallback folder if real one doesn't exist
FALLBACK_UPLOAD_DIR = Path("uploads")


def pick_upload_dir() -> Path:
    """
    Use your real folder first. If it doesn't exist (first run),
    fall back to ./uploads so the app doesn't crash.
    """
    if HARDCODED_UPLOAD_DIR.exists():
        return HARDCODED_UPLOAD_DIR
    FALLBACK_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return FALLBACK_UPLOAD_DIR


UPLOAD_DIR = pick_upload_dir()

IMG_WIDTH = 220

GO_HOME_URL = (
    "https://www.google.com/maps/dir//Garia,+Kolkata,+West+Bengal/@22.4624833,88.3695706,14z/"
    "data=!4m18!1m8!3m7!1s0x3a0271a00d52ca53:0x84c91e76a182e37a!2sGaria,+Kolkata,+West+Bengal!"
    "3b1!8m2!3d22.4660129!4d88.3928446!16zL20vMGMwMnYx!4m8!1m0!1m5!1m1!1s0x3a0271a00d52ca53:"
    "0x84c91e76a182e37a!2m2!1d88.3928446!2d22.4660129!3e0?entry=ttu"
)

GPS_PRESETS = {
    "Therapist's House": "https://www.google.com/maps?q=Therapist+House+Kolkata",
    "Daughter's House": "https://www.google.com/maps?q=Daughters+House+Kolkata",
    "Family Doctor": "https://www.google.com/maps?q=Family+Doctor+Kolkata",
    "Nearby Pharmacy": "https://www.google.com/maps?q=pharmacy+near+me",
}

# =========================================================
# 2. TIME HELPERS
# =========================================================
def now_local() -> datetime.datetime:
    return datetime.datetime.now()


def parse_iso(ts: str) -> datetime.datetime:
    try:
        return datetime.datetime.fromisoformat(ts)
    except Exception:
        return now_local()


def to_iso(dt: datetime.datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


def human_time(dt_iso: str) -> str:
    try:
        dt = parse_iso(dt_iso)
        return dt.strftime("%d %b %Y • %I:%M %p")
    except Exception:
        return dt_iso

# =========================================================
# 3. DATA LOAD / SAVE
# =========================================================
def default_data() -> Dict[str, Any]:
    return {
        "profile": {"name": "Friend"},
        "reminders": {},
        "people": {},
        "logs": [],
        "gps": {"home_address": "", "lat": "", "lon": ""},
    }


def _try_load_json(path: Path) -> Dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def load_data() -> Dict[str, Any]:
    data = _try_load_json(ROOT_UPLOADS_JSON) or _try_load_json(DATA_FILE)
    if not data:
        data = default_data()

    data.setdefault("profile", {"name": "Friend"})
    data.setdefault("reminders", {})
    data.setdefault("people", {})
    data.setdefault("logs", [])
    data.setdefault("gps", {"home_address": "", "lat": "", "lon": ""})
    return data


def save_data(data: Dict[str, Any]) -> None:
    for p in [ROOT_UPLOADS_JSON, DATA_FILE]:
        try:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
    st.session_state.data = data

# =========================================================
# 4. MEMORY BOOK — read from your folder
# =========================================================
def get_memory_book_images() -> List[Path]:
    """
    Read ONLY from the hardcoded / chosen UPLOAD_DIR.
    No flip, no JSON — just list images.
    """
    imgs: List[Path] = []
    if UPLOAD_DIR.exists():
        for f in UPLOAD_DIR.iterdir():
            if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                imgs.append(f)
    return sorted(imgs)

# =========================================================
# 5. REMINDERS
# =========================================================
SR_INTERVALS_DAYS = [1, 2, 4, 7, 14, 30]


def next_sr_due(stage: int) -> datetime.datetime:
    idx = min(stage, len(SR_INTERVALS_DAYS)) - 1
    return now_local() + datetime.timedelta(days=SR_INTERVALS_DAYS[idx])


def add_reminder(
    data,
    title,
    when_dt: datetime.datetime,
    image_path: str,
    audio_path: str,
    steps: List[str],
    repeat_rule: str,
    reminder_type: str = "activity",
):
    rid = uuid.uuid4().hex
    data["reminders"][rid] = {
        "id": rid,
        "title": title,
        "when_iso": to_iso(when_dt),
        "next_due_iso": to_iso(when_dt),
        "repeat_rule": repeat_rule,
        "stage": 1,
        "image_path": image_path,
        "audio_path": audio_path,
        "steps": steps or [],
        "reminder_type": reminder_type,
    }
    save_data(data)


def reminder_due(rec: dict) -> bool:
    try:
        return parse_iso(rec["next_due_iso"]) <= now_local() + datetime.timedelta(minutes=2)
    except Exception:
        return False


def advance_reminder(rec: dict):
    rule = rec.get("repeat_rule", "once")
    if rule == "once":
        rec["next_due_iso"] = to_iso(now_local() + datetime.timedelta(days=3650))
    elif rule == "daily":
        rec["next_due_iso"] = to_iso(parse_iso(rec["next_due_iso"]) + datetime.timedelta(days=1))
    elif rule == "sr":
        rec["stage"] = rec.get("stage", 1) + 1
        rec["next_due_iso"] = to_iso(next_sr_due(rec["stage"]))
    else:
        rec["next_due_iso"] = to_iso(now_local() + datetime.timedelta(days=1))


def snooze_reminder(rec: dict, minutes=10):
    rec["next_due_iso"] = to_iso(now_local() + datetime.timedelta(minutes=minutes))

# =========================================================
# 6. PEOPLE (for quiz) — optional
# =========================================================
def add_person(data, name, relation, image_path):
    pid = uuid.uuid4().hex
    data["people"][pid] = {
        "id": pid,
        "name": name,
        "relation": relation,
        "image_path": image_path,
        "stage": 1,
        "next_due_iso": to_iso(next_sr_due(1)),
    }
    save_data(data)


def get_due_people_for_quiz(data) -> List[Dict[str, Any]]:
    return [p for p in data["people"].values() if parse_iso(p["next_due_iso"]) <= now_local()]


def mark_quiz_result(data, person_id: str, correct: bool):
    p = data["people"].get(person_id)
    if not p:
        return
    p["stage"] = p.get("stage", 1) + 1 if correct else 1
    p["next_due_iso"] = to_iso(next_sr_due(p["stage"]))
    save_data(data)

# =========================================================
# 7. LOGS
# =========================================================
def add_log(data, reminder, action: str):
    data.setdefault("logs", [])
    data["logs"].append(
        {
            "time": to_iso(now_local()),
            "reminder_id": reminder.get("id"),
            "title": reminder.get("title"),
            "type": reminder.get("reminder_type", "activity"),
            "action": action,
        }
    )
    save_data(data)

# =========================================================
# 8. SOUND
# =========================================================
def inject_due_alarm():
    st.markdown(
        """
    <script>
    (function(){
      try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const o = ctx.createOscillator();
        const g = ctx.createGain();
        o.connect(g); g.connect(ctx.destination);
        o.frequency.value = 820;
        o.start();
        g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.4);
      } catch(e) {}
    })();
    </script>
    """,
        unsafe_allow_html=True,
    )


def play_beep_done():
    st.markdown(
        """
    <script>
    (function(){
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.type = "sine";
      o.connect(g);
      g.connect(ctx.destination);
      o.frequency.value = 620;
      o.start();
      g.gain.exponentialRampToValueAtTime(0.00001, ctx.currentTime + 0.25);
    })();
    </script>
    """,
        unsafe_allow_html=True,
    )

# =========================================================
# 9. IMAGE SAVE
# =========================================================
def save_upload(upload, subdir: str) -> str:
    if not upload:
        return ""
    folder = UPLOAD_DIR / subdir
    folder.mkdir(parents=True, exist_ok=True)
    ext = Path(upload.name).suffix.lower()
    fname = f"{uuid.uuid4().hex}{ext}"
    path = folder / fname
    with open(path, "wb") as f:
        f.write(upload.read())
    return str(path)

# =========================================================
# 10. GLOBAL CSS
# =========================================================
st.markdown(
    """
<style>
.stApp {
  background: radial-gradient(circle at top, #1f2937 0%, #0f172a 100%);
  color: #ffffff;
}
h1,h2,h3,h4 { color: #ffffff !important; }

[data-testid="stContainer"], .st-expander {
  background: #ffffff !important;
  color: #111827 !important;
  border-radius: 16px !important;
  box-shadow: 0 10px 25px rgba(0,0,0,0.12) !important;
  margin-bottom: 14px !important;
  padding: 12px !important;
}

/* BIG LANDING BUTTONS */
div.stButton > button {
  background: linear-gradient(120deg, #0ea5e9 0%, #6366f1 80%);
  border: none;
  color: #fff;
  border-radius: 20px;
  padding: 20px 14px;
  font-size: 1.45rem;
  font-weight: 800;
  box-shadow: 0 10px 24px rgba(14,165,233,0.35);
}
div.stButton:nth-of-type(2) > button {
  background: linear-gradient(120deg, #f97316 0%, #fb7185 80%);
}

/* panels */
.due-panel {
  background: linear-gradient(135deg, #f97316 0%, #f43f5e 65%);
  border-radius: 16px;
  padding: 12px 14px;
  margin-bottom: 12px;
  color: #fff;
}
.coming-panel {
  background: linear-gradient(135deg, #6366f1 0%, #0ea5e9 65%);
  border-radius: 16px;
  padding: 12px 14px;
  margin-bottom: 12px;
  color: #fff;
}

/* floating gif */
.floating-gif {
  position: fixed;
  top: 10px;
  left: 10px;
  width: 90px;
  height: 90px;
  z-index: 9999;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 6px 18px rgba(0,0,0,0.25);
}
.floating-gif img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.role-badge {
  background: rgba(255,255,255,0.18);
  border: 1px solid rgba(255,255,255,0.4);
  border-radius: 999px;
  padding: 6px 12px;
  text-align: center;
  margin-bottom: 8px;
  font-weight: 600;
}
</style>
<div class="floating-gif">
  <img src="https://i.pinimg.com/originals/e9/f7/bf/e9f7bf6cd7b5f1f6b954ed7be35d8aac.gif" />
</div>
""",
    unsafe_allow_html=True,
)

# =========================================================
# 11. SESSION INIT
# =========================================================
if "data" not in st.session_state:
    st.session_state.data = load_data()
data = st.session_state.data

if "role" not in st.session_state:
    st.session_state.role = None
if "play_sound" not in st.session_state:
    st.session_state.play_sound = False
if "played_due_alarm" not in st.session_state:
    st.session_state.played_due_alarm = False

# support ?role=patient or ?role=caretaker
qp = st.query_params
qp_role = qp.get("role", None)
if qp_role:
    if isinstance(qp_role, list):
        qp_role = qp_role[0]
    if qp_role in ("patient", "caretaker"):
        st.session_state.role = qp_role

# =========================================================
# 12. LANDING PAGE
# =========================================================
if st.session_state.role is None:
    st.markdown("<h1 style='text-align:center;margin-top:1rem;'>🧠 Memory Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;font-size:1.1rem;color:#e2e8f0;'>Who are you?</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧑‍🦽 Patient", use_container_width=True):
            st.session_state.role = "patient"
            st.rerun()
    with c2:
        if st.button("🧑‍⚕️ Caregiver", use_container_width=True):
            st.session_state.role = "caretaker"
            st.rerun()
    st.stop()

# =========================================================
# 13. COMMON HEADER
# =========================================================
st.title("🧠 Memory Assistant")

lc, rc = st.columns([3, 1])
with lc:
    nm = data["profile"].get("name", "Friend")
    if st.session_state.role == "caretaker":
        new_nm = st.text_input("Your name", value=nm)
        if new_nm.strip() and new_nm != nm:
            data["profile"]["name"] = new_nm.strip()
            save_data(data)
    else:
        st.markdown(f"**Hello, {nm}!**")
with rc:
    st.markdown(f"<div class='role-badge'>Current: {st.session_state.role.title()}</div>", unsafe_allow_html=True)
    if st.button("🔁 Change role"):
        st.session_state.role = None
        st.rerun()

# =========================================================
# 14. CAREGIVER VIEW
# =========================================================
if st.session_state.role == "caretaker":
    tab_home, tab_rem, tab_people, tab_logs, tab_gps, tab_membook = st.tabs(
        ["🏠 Home", "⏰ Reminders", "👨‍👩‍👧 People", "📜 Logs", "📍 GPS / Home", "📘 Memory Book"]
    )

    # HOME
    with tab_home:
        st.subheader("🔔 Due now")
        due_rems = [r for r in data["reminders"].values() if reminder_due(r)]
        if due_rems and not st.session_state.played_due_alarm:
            inject_due_alarm()
            st.session_state.played_due_alarm = True

        if not due_rems:
            st.info("No reminders due.")
        else:
            for r in sorted(due_rems, key=lambda x: x["next_due_iso"]):
                st.markdown("<div class='due-panel'>", unsafe_allow_html=True)
                c1, c2 = st.columns([1, 2])
                with c1:
                    imgp = r.get("image_path", "")
                    if imgp and os.path.exists(imgp):
                        st.image(imgp, use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/200x160?text=Photo", use_container_width=True)
                with c2:
                    st.markdown(f"**{r['title']}**  ({r.get('reminder_type','activity')})")
                    st.caption(f"Next: {human_time(r['next_due_iso'])}")
                    steps = r.get("steps", [])
                    for i, s in enumerate(steps, 1):
                        st.write(f"{i}. {s}")
                    b1, b2, b3 = st.columns(3)
                    if b1.button("✅ Done", key=f"ct_done_{r['id']}"):
                        advance_reminder(r)
                        save_data(data)
                        if r.get("reminder_type") == "medicine":
                            add_log(data, r, "taken (caregiver)")
                        st.rerun()
                    if b2.button("⏰ Snooze", key=f"ct_snooze_{r['id']}"):
                        snooze_reminder(r)
                        save_data(data)
                        if r.get("reminder_type") == "medicine":
                            add_log(data, r, "snoozed (caregiver)")
                        st.rerun()
                    if b3.button("🗑️ Remove", key=f"ct_rm_{r['id']}"):
                        data["reminders"].pop(r["id"], None)
                        save_data(data)
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.subheader("🟡 Coming soon")
        upcoming = []
        now_ = now_local()
        for r in data["reminders"].values():
            dt = parse_iso(r["next_due_iso"])
            if now_ < dt <= now_ + datetime.timedelta(hours=24):
                upcoming.append(r)
        if not upcoming:
            st.caption("No upcoming reminders.")
        else:
            for r in sorted(upcoming, key=lambda x: x["next_due_iso"]):
                st.markdown(
                    f"<div class='coming-panel'>🕒 <strong>{r['title']}</strong> — {human_time(r['next_due_iso'])}</div>",
                    unsafe_allow_html=True,
                )

    # REMINDERS
    with tab_rem:
        st.subheader("Add reminder")
        with st.form("add_rem_form", clear_on_submit=True):
            title = st.text_input("Title")
            d = st.date_input("Date", value=now_local().date())
            t = st.time_input("Time", value=datetime.time(20, 0))
            img_up = st.file_uploader("Photo (optional)", type=["png", "jpg", "jpeg"])
            aud_up = st.file_uploader("Voice (optional)", type=["mp3", "wav", "m4a"])
            steps_txt = st.text_area("Steps", placeholder="Open kit\nTake capsule\nDrink water")
            rtype = st.selectbox("Reminder type", ["activity", "medicine"])
            rpt = st.selectbox("Repeat", ["once", "daily", "sr"], index=1)
            ok = st.form_submit_button("➕ Add")
            if ok:
                if not title:
                    st.error("Title is required")
                else:
                    when_dt = datetime.datetime.combine(d, t)
                    img_path = save_upload(img_up, "images") if img_up else ""
                    aud_path = save_upload(aud_up, "audio") if aud_up else ""
                    steps = [s.strip() for s in steps_txt.splitlines() if s.strip()]
                    add_reminder(data, title, when_dt, img_path, aud_path, steps, rpt, reminder_type=rtype)
                    st.success("Reminder added")

        st.divider()
        st.subheader("All reminders")
        for r in sorted(data["reminders"].values(), key=lambda x: x["next_due_iso"]):
            with st.expander(f"{r['title']} — {human_time(r['next_due_iso'])}"):
                st.json(r)

    # PEOPLE
    with tab_people:
        st.subheader("People")
        if not data["people"]:
            st.info("No people saved. You can add manually or just drop images in the uploads folder.")
        else:
            cols = st.columns(2)
            for i, p in enumerate(data["people"].values()):
                with cols[i % 2]:
                    ip = p.get("image_path", "")
                    if ip and os.path.exists(ip):
                        st.image(ip, use_container_width=True)
                    st.markdown(f"**{p['name']}** — {p.get('relation','Family')}")

        st.divider()
        st.caption("Add person manually")
        with st.form("add_person_form", clear_on_submit=True):
            name = st.text_input("Name")
            rel = st.text_input("Relation")
            img_up = st.file_uploader("Photo", type=["png", "jpg", "jpeg"])
            ok = st.form_submit_button("💾 Save")
            if ok:
                if not name or not img_up:
                    st.error("Name + photo required")
                else:
                    pth = save_upload(img_up, "people")
                    add_person(data, name, rel, pth)
                    st.success("Person added")

    # LOGS
    with tab_logs:
        st.subheader("📜 Medicine logs")
        logs = data.get("logs", [])
        if not logs:
            st.info("No logs yet.")
        else:
            logs = sorted(logs, key=lambda x: x["time"], reverse=True)
            for lg in logs:
                st.write(f"{human_time(lg['time'])} — {lg['title']} — {lg['action']} — ({lg['type']})")

    # GPS
    with tab_gps:
        st.subheader("📍 GPS / Home")

        # read from query params if browser sent location
        qp = st.query_params
        new_lat = qp.get("lat", None)
        new_lon = qp.get("lon", None)
        if isinstance(new_lat, list):
            new_lat = new_lat[0]
        if isinstance(new_lon, list):
            new_lon = new_lon[0]
        if new_lat and new_lon:
            data["gps"]["lat"] = new_lat
            data["gps"]["lon"] = new_lon
            save_data(data)
            st.success(f"Got location: {new_lat}, {new_lon}")

        cur_home = data["gps"].get("home_address", "")
        cur_lat = data["gps"].get("lat", "")
        cur_lon = data["gps"].get("lon", "")

        st.write(f"**Current saved location:** {cur_lat or '-'}, {cur_lon or '-'}")

        components.html(
            """
            <button onclick="getGPS()" style="padding:8px 14px;border:none;background:#0ea5e9;color:white;border-radius:8px;cursor:pointer;">
              📍 Get current location
            </button>
            <script>
            function getGPS(){
              if (!navigator.geolocation){ alert("Geolocation not supported"); return; }
              navigator.geolocation.getCurrentPosition(function(pos){
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;
                const u = new URL(window.parent.location.href);
                u.searchParams.set('lat', lat);
                u.searchParams.set('lon', lon);
                window.parent.location.href = u.toString();
              }, function(err){
                alert(err.message);
              });
            }
            </script>
            """,
            height=80,
        )

        st.divider()
        st.write(f"Home address: **{cur_home or 'Not set'}**")
        if st.button("🧭 Show directions to home"):
            components.html(f"<script>window.open('{GO_HOME_URL}', '_blank');</script>", height=0)

        with st.form("home_form"):
            home_addr = st.text_input("Update home address", value=cur_home)
            lat_in = st.text_input("Home lat", value=cur_lat)
            lon_in = st.text_input("Home lon", value=cur_lon)
            ok = st.form_submit_button("💾 Save home")
            if ok:
                data["gps"]["home_address"] = home_addr
                data["gps"]["lat"] = lat_in
                data["gps"]["lon"] = lon_in
                save_data(data)
                st.success("Home saved")

        # show map iframe if lat/lon present
        if cur_lat and cur_lon:
            try:
                latf = float(cur_lat)
                lonf = float(cur_lon)
                maps_url = f"https://www.google.com/maps?q={latf},{lonf}&z=16&output=embed"
                components.html(
                    f'<iframe src="{maps_url}" width="100%" height="260" style="border:0" loading="lazy"></iframe>',
                    height=270,
                )
            except Exception:
                st.caption("Invalid lat/lon")

        st.divider()
        st.markdown("### 3️⃣ Where to go?")
        choice = st.selectbox("Choose place", list(GPS_PRESETS.keys()))
        if st.button("📍 Show"):
            link = GPS_PRESETS.get(choice)
            components.html(f"<script>window.open('{link}', '_blank');</script>", height=0)

    # MEMORY BOOK (CAREGIVER)
    with tab_membook:
        st.subheader("📘 Memory Book (Caregiver view)")
        st.caption(f"📁 Looking in: {UPLOAD_DIR.resolve()}")
        imgs = get_memory_book_images()
        if not imgs:
            st.info("No images found. Put .jpg/.png in that folder.")
        else:
            for img_path in imgs:
                col1, col2 = st.columns([1, 2])
                col1.image(str(img_path), use_container_width=True)
                name_guess = img_path.stem.replace("_", " ").title()
                col2.markdown(
                    f"""
**Name:** {name_guess}  
**Relation:** Family member  
**Age:** (dummy)  
**Note:** This is dummy info, edit later.
"""
                )
                st.divider()

# =========================================================
# 15. PATIENT VIEW
# =========================================================
else:
    # we add AI tab here
    tab_act, tab_med, tab_quiz, tab_membook, tab_gps, tab_ai = st.tabs(
        ["🧑‍🦽 Activity", "💊 Medicine", "🧩 Quiz", "📘 Memory Book", "📍 GPS", "🤖 AI Chatbot"]
    )

    def render_patient_tab(rem_type: str):
        st.subheader("🔔 Due now")
        due_rems = [
            r for r in data["reminders"].values() if reminder_due(r) and r.get("reminder_type", "activity") == rem_type
        ]
        if due_rems and not st.session_state.played_due_alarm:
            inject_due_alarm()
            st.session_state.played_due_alarm = True

        if not due_rems:
            st.info("Nothing to do right now ✅")
        else:
            for r in sorted(due_rems, key=lambda x: x["next_due_iso"]):
                st.markdown("<div class='due-panel'>", unsafe_allow_html=True)
                c1, c2 = st.columns([1, 2])
                with c1:
                    ip = r.get("image_path", "")
                    if ip and os.path.exists(ip):
                        st.image(ip, use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/200x160?text=Photo", use_container_width=True)
                with c2:
                    st.markdown(f"**{r['title']}**")
                    st.caption(human_time(r["next_due_iso"]))
                    steps = r.get("steps", [])
                    for i, s in enumerate(steps, 1):
                        st.write(f"{i}. {s}")
                    b1, b2 = st.columns(2)
                    if b1.button("✅ I did it", key=f"pt_done_{rem_type}_{r['id']}"):
                        advance_reminder(r)
                        save_data(data)
                        if r.get("reminder_type") == "medicine":
                            add_log(data, r, "taken (patient)")
                        st.session_state.play_sound = True
                        st.rerun()
                    if b2.button("⏰ Later", key=f"pt_snooze_{rem_type}_{r['id']}"):
                        snooze_reminder(r)
                        save_data(data)
                        if r.get("reminder_type") == "medicine":
                            add_log(data, r, "snoozed (patient)")
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.subheader("🟡 Activities Coming Soon")
        upcoming = []
        now_ = now_local()
        for r in data["reminders"].values():
            if r.get("reminder_type", "activity") != rem_type:
                continue
            dt = parse_iso(r["next_due_iso"])
            if now_ < dt <= now_ + datetime.timedelta(hours=24):
                upcoming.append(r)
        if not upcoming:
            st.caption("No upcoming reminders.")
        else:
            for r in sorted(upcoming, key=lambda x: x["next_due_iso"]):
                st.markdown(
                    f"<div class='coming-panel'>🕒 <strong>{r['title']}</strong> — {human_time(r['next_due_iso'])}</div>",
                    unsafe_allow_html=True,
                )

    # Activity tab
    with tab_act:
        render_patient_tab("activity")

    # Medicine tab
    with tab_med:
        render_patient_tab("medicine")

    # Quiz tab
    with tab_quiz:
        st.subheader("🧩 Face quiz")
        if "quiz_target_id" not in st.session_state:
            st.session_state.quiz_target_id = None
            st.session_state.quiz_option_ids = []
        if not data["people"]:
            st.info("No faces yet. Caregiver must add or drop images.")
        else:
            if st.session_state.quiz_target_id is None:
                due_people = get_due_people_for_quiz(data)
                if not due_people:
                    st.success("🎉 No one is due right now.")
                else:
                    target = random.choice(due_people)
                    others = [p for p in data["people"].values() if p["id"] != target["id"]]
                    random.shuffle(others)
                    others = others[:2]
                    st.session_state.quiz_target_id = target["id"]
                    st.session_state.quiz_option_ids = [target["id"]] + [o["id"] for o in others]
            if st.session_state.quiz_target_id:
                target = data["people"][st.session_state.quiz_target_id]
                st.write("**Who is this?**")
                ip = target.get("image_path", "")
                if ip and os.path.exists(ip):
                    st.image(ip, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/200x160?text=Photo", use_container_width=True)
                opts = [data["people"][pid] for pid in st.session_state.quiz_option_ids if pid in data["people"]]
                random.shuffle(opts)
                cols = st.columns(len(opts))
                for i, p in enumerate(opts):
                    with cols[i]:
                        if p.get("image_path") and os.path.exists(p["image_path"]):
                            st.image(p["image_path"], use_container_width=True)
                        if st.button(f"{p['name']} — {p['relation']}", key=f"qopt_{p['id']}"):
                            correct = p["id"] == target["id"]
                            mark_quiz_result(data, target["id"], correct)
                            if correct:
                                st.success("✅ Correct! ")
                            else:
                                st.error("❌ Not correct, try again later.")
                            st.session_state.quiz_target_id = None
                            st.session_state.quiz_option_ids = []
                            st.rerun()

    # Memory Book (PATIENT)
    with tab_membook:
        st.subheader("📘 Memory Book")
        st.caption(f"📁 Looking in: {UPLOAD_DIR.resolve()}")
        imgs = get_memory_book_images()
        if not imgs:
            st.info("No images found. Ask caregiver to put images in that folder.")
        else:
            for img_path in imgs:
                c1, c2 = st.columns([1, 2])
                c1.image(str(img_path), use_container_width=True)
                name_guess = img_path.stem.replace("_", " ").title()
                c2.markdown(
                    f"""
**Name:** {name_guess}  
**Relation:** Family  
**Message:** Hi 👋 remember me?
"""
                )
                st.divider()

    # GPS (PATIENT)
    with tab_gps:
        st.subheader("📍 GPS (Patient)")
        gps = data.get("gps", {})
        home_addr = gps.get("home_address", "")
        st.write(f"Home address: **{home_addr or 'Not set'}**")
        if st.button("🧭 Show directions to home"):
            components.html(f"<script>window.open('{GO_HOME_URL}', '_blank');</script>", height=0)

        st.divider()
        st.markdown("### Where to go?")
        choice = st.selectbox("Choose place", list(GPS_PRESETS.keys()))
        if st.button("📍 Show this place"):
            link = GPS_PRESETS.get(choice)
            components.html(f"<script>window.open('{link}', '_blank');</script>", height=0)

    # 🤖 AI CHATBOT TAB (PATIENT) — final checked
    with tab_ai:
        import os, json, requests
        from pathlib import Path
        from dotenv import load_dotenv
        import streamlit as st  # if you're in same file, you already have st

        st.subheader("🤖 AI Chatbot")
        st.caption("Type or speak. I will answer in short, simple sentences.")

        # 1) load .env from your real root
        PROJECT_ROOT = Path(r"C:\Users\Anurag\PycharmProjects\AntiDote")
        ENV_PATH = PROJECT_ROOT / ".env"
        if ENV_PATH.exists():
            load_dotenv(ENV_PATH, override=True)
        else:
            # fallback to current dir
            load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY", "").strip()

        # 2) small debug
        with st.expander("⚙️ Chatbot diagnostic"):
            st.write("Looking for .env at:", str(ENV_PATH))
            st.write(".env exists:", ENV_PATH.exists())
            st.write("API key present:", bool(api_key))
            if api_key:
                st.write("API key (first 8):", api_key[:8] + "•••")

        # 3) keep chat history
        if "patient_ai_chat" not in st.session_state:
            st.session_state.patient_ai_chat = [
                {
                    "role": "assistant",
                    "content": "Hello 👋 I'm your Memory Assistant. How can I help you today?"
                }
            ]

        # 4) show history
        for msg in st.session_state.patient_ai_chat:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # 5) SPEECH-TO-TEXT (top-level, not iframe)
        st.markdown(
            """
            <div style="margin:8px 0 14px 0;">
              <button id="stt-btn"
                      style="padding:6px 14px;border:none;background:#f97316;color:white;border-radius:8px;cursor:pointer;">
                🎤 Speak
              </button>
              <span id="stt-status" style="color:#fff;margin-left:8px;font-size:12px;"></span>
            </div>
            <script>
            (function(){
              const btn = document.getElementById("stt-btn");
              const status = document.getElementById("stt-status");
              if (!btn) return;
              btn.addEventListener("click", function(){
                const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
                if (!SR) {
                  status.innerText = "Speech API not supported. Use Chrome on localhost.";
                  return;
                }
                const rec = new SR();
                rec.lang = "en-US";
                rec.onstart = function(){ status.innerText = "Listening..."; };
                rec.onerror = function(e){ status.innerText = "Error: " + e.error; };
                rec.onresult = function(e){
                  const text = e.results[0][0].transcript;
                  const u = new URL(window.location.href);
                  u.searchParams.set("say", text);
                  window.location.href = u.toString();
                };
                rec.start();
              });
            })();
            </script>
            """,
            unsafe_allow_html=True,
        )

        # 6) get spoken text (if any)
        spoken = st.query_params.get("say")
        if isinstance(spoken, list):
            spoken = spoken[0]

        if spoken:
            user_input = spoken
        else:
            user_input = st.chat_input("Type your message")

        last_reply = None

        # 7) handle user message
        if user_input:
            # add user
            st.session_state.patient_ai_chat.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # default fallback
            reply_text = (
                    "I heard you say: " + user_input +
                    "\n\nI couldn't reach the AI right now. (Check internet / model / firewall.)"
            )

            # try real OpenAI
            if api_key:
                try:
                    url = "https://api.openai.com/v1/chat/completions"
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    }

                    # take last 6 messages from history
                    last_msgs = st.session_state.patient_ai_chat[-6:]
                    messages = [
                                   {
                                       "role": "system",
                                       "content": "You are a very gentle assistant for an Alzheimer's patient. Reply in 2-3 short, friendly sentences, no code."
                                   }
                               ] + last_msgs

                    payload = {
                        "model": "gpt-4o-mini",  # change if your key doesn't have this
                        "messages": messages,
                        "max_tokens": 150,
                        "temperature": 0.6,
                    }

                    resp = requests.post(url, headers=headers, json=payload, timeout=15)
                    if resp.status_code == 200:
                        data_json = resp.json()
                        reply_text = data_json["choices"][0]["message"]["content"]
                    else:
                        reply_text = f"⚠️ API error {resp.status_code}: {resp.text[:250]}"
                except Exception as e:
                    reply_text = f"⚠️ Request failed: {e}\n\n(I heard: {user_input})"
            else:
                reply_text = (
                    "❗ No OPENAI_API_KEY found in C:\\Users\\Anurag\\PycharmProjects\\AntiDote\\.env\n"
                    "Add: OPENAI_API_KEY=sk-xxxx"
                )

            # show bot
            with st.chat_message("assistant"):
                st.markdown(reply_text)

            # store
            st.session_state.patient_ai_chat.append({"role": "assistant", "content": reply_text})
            last_reply = reply_text
        else:
            # no new user msg → fetch last assistant for TTS
            for m in reversed(st.session_state.patient_ai_chat):
                if m["role"] == "assistant":
                    last_reply = m["content"]
                    break

        # 8) READ ALOUD (TTS) – escape safely
        if last_reply:
            # json.dumps makes it safe for JS
            js_text = json.dumps(last_reply)
            st.markdown(
                f"""
                <button id="tts-btn"
                        style="padding:6px 14px;border:none;background:#0ea5e9;color:white;border-radius:8px;cursor:pointer;margin-top:10px;">
                  🔊 Read aloud
                </button>
                <script>
                (function(){{
                  const btn = document.getElementById("tts-btn");
                  if (!btn) return;
                  btn.addEventListener("click", function(){{
                    if (!window.speechSynthesis) {{
                      alert("Speech not supported here.");
                      return;
                    }}
                    const txt = {js_text};
                    const u = new SpeechSynthesisUtterance(txt);
                    u.lang = "en-US";
                    u.rate = 0.95;
                    window.speechSynthesis.speak(u);
                  }});
                }})();
                </script>
                """,
                unsafe_allow_html=True,
            )

    # play sound once for patient
    if st.session_state.play_sound:
        play_beep_done()
        st.session_state.play_sound = False
