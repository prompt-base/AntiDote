# ANTIDOTE/pages/Alzy--Beta.py
# ------------------------------------------------------------
# ALZY – Memory Assistant (Caregiver + Patient) with AI Chatbot
# ------------------------------------------------------------
import os
import json
import uuid
import random
import datetime
from pathlib import Path
from typing import Dict, Any, List

import streamlit as st
from PIL import Image
import requests
import streamlit.components.v1 as components

# ------------------------------------------------------------
# SAFE API KEY LOADING (works local + Streamlit Cloud)
# ------------------------------------------------------------
def _load_api_key() -> str:
    # 1) Streamlit Cloud Secrets
    try:
        key = st.secrets.get("OPENAI_API_KEY")
        if key:
            return key.strip()
    except Exception:
        pass

    # 2) Local .env using python-dotenv (optional)
    try:
        from dotenv import load_dotenv  # only if installed
        project_root = Path(r"C:\Users\Anurag\PycharmProjects\AntiDote")
        env_path = project_root / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
        else:
            load_dotenv(override=True)
    except Exception:
        # dotenv not installed or failed — ignore
        pass

    # 3) Plain env var
    return (os.getenv("OPENAI_API_KEY") or "").strip()

OPENAI_API_KEY = _load_api_key()

# ------------------------------------------------------------
# CONSTANT PATHS
# ------------------------------------------------------------
PROJECT_ROOT = Path(r"C:\Users\Anurag\PycharmProjects\AntiDote")
UPLOAD_DIR = PROJECT_ROOT / "uploads"           # faces / photos folder
DATA_FILE = PROJECT_ROOT / "data.json"          # storage for reminders etc.

# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
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

def default_data() -> Dict[str, Any]:
    return {
        "profile": {"name": "Friend"},
        "reminders": {},
        "people": {},
        "logs": [],
        "gps": {"home_address": "", "lat": "", "lon": ""},
    }

def load_data() -> Dict[str, Any]:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = default_data()
    else:
        data = default_data()
    # ensure keys
    data.setdefault("profile", {"name": "Friend"})
    data.setdefault("reminders", {})
    data.setdefault("people", {})
    data.setdefault("logs", [])
    data.setdefault("gps", {"home_address": "", "lat": "", "lon": ""})
    return data

def save_data(data: Dict[str, Any]) -> None:
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass
    st.session_state.data = data

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

# Spaced repetition
SR_INTERVALS = [1, 2, 4, 7, 14, 30]
def next_sr_due(stage: int) -> datetime.datetime:
    idx = min(stage, len(SR_INTERVALS)) - 1
    return now_local() + datetime.timedelta(days=SR_INTERVALS[idx])

def add_reminder(
    data: Dict[str, Any],
    title: str,
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

def reminder_due(rec: Dict[str, Any]) -> bool:
    try:
        return parse_iso(rec["next_due_iso"]) <= (now_local() + datetime.timedelta(minutes=1))
    except Exception:
        return False

def advance_reminder(rec: Dict[str, Any]):
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

def snooze_reminder(rec: Dict[str, Any], minutes: int = 10):
    rec["next_due_iso"] = to_iso(now_local() + datetime.timedelta(minutes=minutes))

def add_person(data: Dict[str, Any], name: str, relation: str, image_path: str):
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

def get_due_people(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [p for p in data["people"].values() if parse_iso(p["next_due_iso"]) <= now_local()]

def mark_quiz_result(data: Dict[str, Any], person_id: str, correct: bool):
    p = data["people"].get(person_id)
    if not p:
        return
    if correct:
        p["stage"] = p.get("stage", 1) + 1
    else:
        p["stage"] = 1
    p["next_due_iso"] = to_iso(next_sr_due(p["stage"]))
    save_data(data)

def add_log(data: Dict[str, Any], reminder: Dict[str, Any], action: str):
    data.setdefault("logs", [])
    data["logs"].append(
        {
            "time": to_iso(now_local()),
            "title": reminder.get("title"),
            "id": reminder.get("id"),
            "type": reminder.get("reminder_type", "activity"),
            "action": action,
        }
    )
    save_data(data)

def get_memory_book_images() -> List[Path]:
    imgs = []
    if UPLOAD_DIR.exists():
        for f in UPLOAD_DIR.iterdir():
            if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                imgs.append(f)
    return sorted(imgs)

# ------------------------------------------------------------
# PAGE CONFIG + CSS
# ------------------------------------------------------------
st.set_page_config(page_title="ALZY – Memory Assistant", page_icon="🧠", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
      background: radial-gradient(circle at top, #0f172a 0%, #020617 100%);
      color: #fff;
    }
    h1,h2,h3,h4 { color:#fff !important; }
    [data-testid="stContainer"], .st-expander {
      background: rgba(15,23,42,0.25) !important;
      border: 1px solid rgba(255,255,255,0.04);
      border-radius: 16px !important;
      padding: 10px 14px !important;
      margin-bottom: 12px !important;
    }
    .due-panel {
      background: linear-gradient(135deg,#f97316 0%,#f43f5e 80%);
      border-radius: 16px;
      padding: 12px 14px;
      color: #fff;
      margin-bottom: 12px;
    }
    .coming-panel {
      background: linear-gradient(135deg,#6366f1 0%,#0ea5e9 80%);
      border-radius: 16px;
      padding: 10px 14px;
      margin-bottom: 10px;
      color:#fff;
    }
    .role-badge {
      background: rgba(255,255,255,0.12);
      border-radius: 999px;
      padding: 4px 10px;
      text-align:center;
      font-size: 0.75rem;
      border: 1px solid rgba(255,255,255,0.25);
    }
    .stButton button {
    background-color: #6366f1 !important;  /* your desired button color */
    color: #fff !important;                 /* button text color */
    border-radius: 12px !important;
    padding: 10px 14px !important;
    font-weight: bold;
    }

    /* Hover effect */
    .stButton button:hover {
    background-color: #4f46e5 !important;  /* slightly darker on hover */
    color: #fff !important;
    }
    .floating-gif {
      position: fixed; top:10px; left:10px; width:90px; height:90px;
      z-index: 9999; border-radius: 16px; overflow:hidden;
    }
    .floating-gif img { width:100%; height:100%; object-fit:cover; }
    </style>
    <div class="floating-gif">
      <img src="https://i.pinimg.com/originals/e9/f7/bf/e9f7bf6cd7b5f1f6b954ed7be35d8aac.gif">
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# SESSION INIT
# ------------------------------------------------------------
if "data" not in st.session_state:
    st.session_state.data = load_data()
data = st.session_state.data

if "role" not in st.session_state:
    st.session_state.role = None

if "patient_ai_chat" not in st.session_state:
    st.session_state.patient_ai_chat = [
        {"role": "assistant", "content": "Hello 👋 I'm your Memory Assistant. How can I help you today?"}
    ]

# support ?role=patient or ?role=caretaker
qp_role = st.query_params.get("role")
if isinstance(qp_role, list):
    qp_role = qp_role[0]
if qp_role in ("patient", "caretaker"):
    st.session_state.role = qp_role

# ------------------------------------------------------------
# LANDING (choose role)
# ------------------------------------------------------------
if st.session_state.role is None:
    st.markdown("<h1 style='text-align:center;'>🧠 ALZY – Memory Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Who are you?</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧑‍🦽 Patient", use_container_width=True, key="choose_patient"):
            st.session_state.role = "patient"
            st.rerun()
    with c2:
        if st.button("🧑‍⚕️ Caregiver", use_container_width=True, key="choose_caregiver"):
            st.session_state.role = "caretaker"
            st.rerun()
    st.stop()

# ------------------------------------------------------------
# COMMON HEADER
# ------------------------------------------------------------
st.title("🧠 ALZY – Memory Assistant")

left, right = st.columns([4, 1])
with left:
    nm = data["profile"].get("name", "Friend")
    if st.session_state.role == "caretaker":
        new_nm = st.text_input("Patient / User name", value=nm)
        if new_nm.strip() and new_nm != nm:
            data["profile"]["name"] = new_nm.strip()
            save_data(data)
    else:
        st.markdown(f"**Hello, {nm}!**")
with right:
    st.markdown(f"<div class='role-badge'>Current: {st.session_state.role.title()}</div>", unsafe_allow_html=True)
    if st.button("🔁 Change role"):
        st.session_state.role = None
        st.rerun()

# ------------------------------------------------------------
# CAREGIVER VIEW
# ------------------------------------------------------------
GO_HOME_URL = (
    "https://www.google.com/maps/dir//Garia,+Kolkata,+West+Bengal/@22.4624833,88.3695706,14z/"
    "data=!4m18!1m8!3m7!1s0x3a0271a00d52ca53:0x84c91e76a182e37a!2sGaria,+Kolkata,+West+Bengal!"
    "3b1!8m2!3d22.4660129!4d88.3928446!16zL20vMGMwMnYx!4m8!1m0!1m5!1m1!1s0x3a0271a00d52ca53:"
    "0x84c91e76a182e37a!2m2!1d88.3928446!2d22.4660129!3e0?entry=ttu"
)

if st.session_state.role == "caretaker":
    tab_home, tab_rem, tab_people, tab_logs, tab_gps, tab_mbook = st.tabs(
        ["🏠 Home", "⏰ Reminders", "👨‍👩‍👧 People", "📜 Logs", "📍 GPS / Home", "📘 Memory Book"]
    )

    # HOME
    with tab_home:
        st.subheader("🔔 Due now")
        due_rems = [r for r in data["reminders"].values() if reminder_due(r)]
        if not due_rems:
            st.info("No reminders due.")
        else:
            for r in sorted(due_rems, key=lambda x: x["next_due_iso"]):
                st.markdown("<div class='due-panel'>", unsafe_allow_html=True)
                c1, c2 = st.columns([1, 2])
                with c1:
                    ip = r.get("image_path", "")
                    if ip and os.path.exists(ip):
                        st.image(ip, use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/200x150?text=Photo", use_container_width=True)
                with c2:
                    st.markdown(f"**{r['title']}**  ({r.get('reminder_type','activity')})")
                    st.caption(f"Next: {human_time(r['next_due_iso'])}")
                    steps = r.get("steps", [])
                    for i, s in enumerate(steps, 1):
                        st.write(f"{i}. {s}")
                    b1, b2, b3 = st.columns(3)
                    if b1.button("✅ Done", key=f"cg_done_{r['id']}"):
                        advance_reminder(r)
                        if r.get("reminder_type") == "medicine":
                            add_log(data, r, "taken (caregiver)")
                        save_data(data)
                        st.rerun()
                    if b2.button("⏰ Snooze", key=f"cg_snooze_{r['id']}"):
                        snooze_reminder(r)
                        if r.get("reminder_type") == "medicine":
                            add_log(data, r, "snoozed (caregiver)")
                        save_data(data)
                        st.rerun()
                    if b3.button("🗑️ Remove", key=f"cg_rm_{r['id']}"):
                        data["reminders"].pop(r["id"], None)
                        save_data(data)
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.subheader("🟡 Coming soon (24h)")
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
            img_up = st.file_uploader("Photo", type=["png", "jpg", "jpeg"])
            aud_up = st.file_uploader("Voice cue", type=["mp3", "wav", "m4a"])
            steps_txt = st.text_area("Steps (one per line)")
            rtype = st.selectbox("Reminder type", ["activity", "medicine"])
            rpt = st.selectbox("Repeat", ["once", "daily", "sr"], index=1)
            ok = st.form_submit_button("➕ Add")
            if ok:
                if not title:
                    st.error("Title required")
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
        st.subheader("People for Memory Book / Quiz")
        if not data["people"]:
            st.info("No people added yet.")
        else:
            cols = st.columns(2)
            for i, p in enumerate(data["people"].values()):
                with cols[i % 2]:
                    ip = p.get("image_path", "")
                    if ip and os.path.exists(ip):
                        st.image(ip, use_container_width=True)
                    st.markdown(f"**{p['name']}** — {p.get('relation','Family')}")

        st.divider()
        with st.form("add_person_form", clear_on_submit=True):
            name = st.text_input("Name")
            rel = st.text_input("Relation")
            img_up = st.file_uploader("Photo", type=["png", "jpg", "jpeg"])
            ok = st.form_submit_button("💾 Save")
            if ok:
                if not name or not img_up:
                    st.error("Name + Photo needed")
                else:
                    pth = save_upload(img_up, "people")
                    add_person(data, name, rel, pth)
                    st.success("Person added")

    # LOGS
    with tab_logs:
        st.subheader("📜 Medicine / action logs")
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
        cur = data.get("gps", {})
        cur_home = cur.get("home_address", "")
        cur_lat = cur.get("lat", "")
        cur_lon = cur.get("lon", "")

        st.write(f"Current saved home: **{cur_home or 'Not set'}**")
        st.write(f"Lat/Lon: {cur_lat or '-'}, {cur_lon or '-'}")

        # try to get browser location (writes back into URL as ?lat=...&lon=...)
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

        new_lat = st.query_params.get("lat")
        new_lon = st.query_params.get("lon")
        if isinstance(new_lat, list):
            new_lat = new_lat[0]
        if isinstance(new_lon, list):
            new_lon = new_lon[0]
        if new_lat and new_lon:
            data["gps"]["lat"] = new_lat
            data["gps"]["lon"] = new_lon
            save_data(data)
            st.success(f"Saved location: {new_lat}, {new_lon}")

        with st.form("set_home_form"):
            addr = st.text_input("Home address", value=cur_home)
            lat_in = st.text_input("Latitude", value=cur_lat)
            lon_in = st.text_input("Longitude", value=cur_lon)
            ok = st.form_submit_button("💾 Save home")
            if ok:
                data["gps"]["home_address"] = addr
                data["gps"]["lat"] = lat_in
                data["gps"]["lon"] = lon_in
                save_data(data)
                st.success("Home saved")

        if cur_lat and cur_lon:
            try:
                la = float(cur_lat)
                lo = float(cur_lon)
                maps_url = f"https://www.google.com/maps?q={la},{lo}&z=15&output=embed"
                components.html(
                    f'<iframe src="{maps_url}" width="100%" height="260" style="border:0" loading="lazy"></iframe>',
                    height=270,
                )
            except Exception:
                pass

        if st.button("🧭 Show directions to home"):
            components.html(f"<script>window.open('{GO_HOME_URL}', '_blank');</script>", height=0)

    # MEMORY BOOK
    with tab_mbook:
        st.subheader("📘 Memory Book")
        st.caption(f"Looking in: {UPLOAD_DIR.resolve()}")
        imgs = get_memory_book_images()
        if not imgs:
            st.info("No images found. Put .jpg/.png in uploads.")
        else:
            for img_path in imgs:
                c1, c2 = st.columns([1, 2])
                c1.image(str(img_path), use_container_width=True)
                name_guess = img_path.stem.replace("_", " ").title()
                c2.markdown(
                    f"""
**Name:** {name_guess}  
**Relation:** Family  
**Note:** Dummy info. Edit later.
"""
                )
                st.divider()

# ------------------------------------------------------------
# PATIENT VIEW
# ------------------------------------------------------------
else:
    tab_act, tab_med, tab_quiz, tab_mbook, tab_gps, tab_ai = st.tabs(
        ["🧑‍🦽 Activity", "💊 Medicine", "🧩 Quiz", "📘 Memory Book", "📍 GPS", "🤖 AI Chatbot"]
    )

    # function to render both activity & medicine
    def render_patient_tab(rem_type: str):
        st.subheader("🔔 Due now")
        due_rems = [
            r for r in data["reminders"].values() if reminder_due(r) and r.get("reminder_type", "activity") == rem_type
        ]
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
                        st.image("https://via.placeholder.com/200x150?text=Photo", use_container_width=True)
                with c2:
                    st.markdown(f"**{r['title']}**")
                    st.caption(human_time(r["next_due_iso"]))
                    steps = r.get("steps", [])
                    for i, s in enumerate(steps, 1):
                        st.write(f"{i}. {s}")
                    b1, b2 = st.columns(2)
                    if b1.button("✅ I did it", key=f"pt_done_{rem_type}_{r['id']}"):
                        advance_reminder(r)
                        if rem_type == "medicine":
                            add_log(data, r, "taken (patient)")
                        save_data(data)
                        st.rerun()
                    if b2.button("⏰ Later", key=f"pt_snooze_{rem_type}_{r['id']}"):
                        snooze_reminder(r)
                        if rem_type == "medicine":
                            add_log(data, r, "snoozed (patient)")
                        save_data(data)
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.subheader("🟡 Coming soon")
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

    # Activity
    with tab_act:
        render_patient_tab("activity")

    # Medicine
    with tab_med:
        render_patient_tab("medicine")

    # Quiz
    with tab_quiz:
        st.subheader("🧩 Face quiz")
        if "quiz_target_id" not in st.session_state:
            st.session_state.quiz_target_id = None
            st.session_state.quiz_option_ids = []

        if not data["people"]:
            st.info("No people added yet.")
        else:
            if st.session_state.quiz_target_id is None:
                due = get_due_people(data)
                if not due:
                    st.success("No one due for quiz right now.")
                else:
                    target = random.choice(due)
                    others = [p for p in data["people"].values() if p["id"] != target["id"]]
                    random.shuffle(others)
                    others = others[:2]
                    st.session_state.quiz_target_id = target["id"]
                    st.session_state.quiz_option_ids = [target["id"]] + [o["id"] for o in others]

            if st.session_state.quiz_target_id:
                target = data["people"][st.session_state.quiz_target_id]
                st.write("Who is this?")
                ip = target.get("image_path", "")
                if ip and os.path.exists(ip):
                    st.image(ip, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/200x150?text=Photo", use_container_width=True)
                opts = [data["people"][pid] for pid in st.session_state.quiz_option_ids if pid in data["people"]]
                random.shuffle(opts)
                cols = st.columns(len(opts))
                for i, p in enumerate(opts):
                    with cols[i]:
                        if p.get("image_path") and os.path.exists(p["image_path"]):
                            st.image(p["image_path"], use_container_width=True)
                        if st.button(f"{p['name']} — {p['relation']}", key=f"ans_{p['id']}"):
                            correct = p["id"] == target["id"]
                            mark_quiz_result(data, target["id"], correct)
                            if correct:
                                st.success("✅ Correct!")
                            else:
                                st.error("❌ Not correct.")
                            st.session_state.quiz_target_id = None
                            st.session_state.quiz_option_ids = []
                            st.rerun()

    # Memory Book
    with tab_mbook:
        st.subheader("📘 Memory Book")
        st.caption(f"Looking in: {UPLOAD_DIR.resolve()}")
        imgs = get_memory_book_images()
        if not imgs:
            st.info("No images found.")
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

    # GPS
    with tab_gps:
        st.subheader("📍 GPS (Patient)")
        gps = data.get("gps", {})
        home_addr = gps.get("home_address", "")
        st.write(f"Home: **{home_addr or 'Not set'}**")
        if st.button("🧭 Go home"):
            components.html(f"<script>window.open('{GO_HOME_URL}', '_blank');</script>", height=0)

    # AI Chatbot
    with tab_ai:
        st.subheader("🤖 AI Chatbot")
        st.caption("Speak (mic) or type. Short, friendly answers.")

        # show history
        for msg in st.session_state.patient_ai_chat:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # speech-to-text button (no unsupported args)
        st.markdown(
            """
            <div style="margin:8px 0 12px 0;">
              <button id="stt-btn"
                      style="padding:6px 14px;border:none;background:#f97316;color:white;border-radius:8px;cursor:pointer;">
                🎤 Speak
              </button>
              <span id="stt-status" style="margin-left:8px;font-size:12px;color:#fff;"></span>
            </div>
            <script>
            (function(){
              const btn = document.getElementById("stt-btn");
              const status = document.getElementById("stt-status");
              if (!btn) return;
              btn.addEventListener("click", function(){
                const isLocal = (location.hostname === "localhost" || location.hostname === "127.0.0.1");
                if (!window.isSecureContext && !isLocal){
                  status.innerText = "❌ Mic blocked: use https or localhost.";
                  return;
                }
                const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
                if (!SR){
                  status.innerText = "❌ SpeechRecognition not supported.";
                  return;
                }
                const rec = new SR();
                rec.lang = "en-US";
                rec.onstart = ()=>{ status.innerText = "Listening..."; };
                rec.onerror = (e)=>{ status.innerText = "❌ " + e.error; };
                rec.onresult = (e)=>{
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

        # get spoken text (from URL param)
        spoken = st.query_params.get("say")
        if isinstance(spoken, list):
            spoken = spoken[0]

        # chat input (no 'value' kw — not supported)
        typed = st.chat_input("Type your message")
        user_input = spoken if spoken else typed

        last_reply = None
        if user_input:
            st.session_state.patient_ai_chat.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            reply_text = f"I heard: {user_input}. I couldn't reach AI right now."
            api_key = OPENAI_API_KEY

            if api_key:
                try:
                    url = "https://api.openai.com/v1/chat/completions"
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    }
                    msgs = [
                        {
                            "role": "system",
                            "content": "You are a gentle assistant for an Alzheimer's patient. Reply in 2–3 short, simple sentences. Be friendly.",
                        }
                    ] + st.session_state.patient_ai_chat[-6:]
                    payload = {
                        "model": "gpt-4o-mini",
                        "messages": msgs,
                        "max_tokens": 150,
                        "temperature": 0.6,
                    }
                    resp = requests.post(url, headers=headers, json=payload, timeout=20)
                    if resp.status_code == 200:
                        data_json = resp.json()
                        reply_text = data_json["choices"][0]["message"]["content"]
                    else:
                        reply_text = f"⚠️ API error {resp.status_code}: {resp.text[:160]}"
                except Exception as e:
                    reply_text = f"⚠️ Request failed: {e}"
            else:
                reply_text = (
                    "❗ No OPENAI_API_KEY found.\n"
                    "Add it to C:\\Users\\Anurag\\PycharmProjects\\AntiDote\\.env or Streamlit Secrets."
                )

            with st.chat_message("assistant"):
                st.markdown(reply_text)

            st.session_state.patient_ai_chat.append({"role": "assistant", "content": reply_text})
            last_reply = reply_text
        else:
            for m in reversed(st.session_state.patient_ai_chat):
                if m["role"] == "assistant":
                    last_reply = m["content"]
                    break

        # read aloud last reply
        if last_reply:
            safe_last = json.dumps(last_reply)
            st.markdown(
                f"""
                <button id="tts-btn"
                        style="margin-top:10px;padding:6px 14px;border:none;background:#0ea5e9;color:white;border-radius:8px;cursor:pointer;">
                  🔊 Read aloud
                </button>
                <script>
                (function(){{
                  const btn = document.getElementById("tts-btn");
                  if (!btn) return;
                  btn.addEventListener("click", function(){{
                    if (!window.speechSynthesis){{ alert("Speech not supported here."); return; }}
                    const txt = {safe_last};
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
