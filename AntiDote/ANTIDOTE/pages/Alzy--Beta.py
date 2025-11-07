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
from typing import Dict, Any, List, Optional

import streamlit as st
from PIL import Image  # noqa: F401
import requests
import streamlit.components.v1 as components

# ------------------------------------------------------------
# PATHS (separate temp folders per feature)
# ------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent

# Base scratch area
UPLOAD_BASE = Path("/tmp/alzy_uploads")
UPLOAD_BASE.mkdir(parents=True, exist_ok=True)

# Activity / Medicine / MemoryBook specific
ACTIVITY_IMG_DIR = UPLOAD_BASE / "activity_images"
MEDICINE_IMG_DIR = UPLOAD_BASE / "medicine_images"
MBOOK_IMG_DIR    = UPLOAD_BASE / "memory_book_images"
AUDIO_DIR        = UPLOAD_BASE / "audio"

for p in (ACTIVITY_IMG_DIR, MEDICINE_IMG_DIR, MBOOK_IMG_DIR, AUDIO_DIR):
    p.mkdir(parents=True, exist_ok=True)

# Data file
DATA_FILE = PROJECT_ROOT / ".data_temp.json"
if not DATA_FILE.exists():
    DATA_FILE.write_text("{}", encoding="utf-8")

# ------------------------------------------------------------
# SAFE API KEY LOADING (works local + Streamlit Cloud)
# ------------------------------------------------------------
def _load_api_key() -> str:
    # 1) Streamlit Secrets
    try:
        k = st.secrets.get("OPENAI_API_KEY")
        if k:
            return k.strip()
    except Exception:
        pass
    # 2) .env (optional)
    try:
        from dotenv import load_dotenv
        env_path = PROJECT_ROOT / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
        else:
            load_dotenv(override=True)
    except Exception:
        pass
    # 3) Plain env
    return (os.getenv("OPENAI_API_KEY") or "").strip()

OPENAI_API_KEY = _load_api_key()

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
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            data = default_data()
    else:
        data = default_data()
    data.setdefault("profile", {"name": "Friend"})
    data.setdefault("reminders", {})
    data.setdefault("people", {})
    data.setdefault("logs", [])
    data.setdefault("gps", {"home_address": "", "lat": "", "lon": ""})
    return data

def save_data(data: Dict[str, Any]) -> None:
    st.session_state.data = data
    try:
        DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass

def save_upload_to(upload, folder: Path) -> str:
    if not upload:
        return ""
    folder.mkdir(parents=True, exist_ok=True)
    ext = Path(upload.name).suffix.lower()
    name = f"{uuid.uuid4().hex}{ext}"
    path = folder / name
    with open(path, "wb") as f:
        f.write(upload.read())
    return str(path)

# Spaced repetition
SR_INTERVALS = [1, 2, 4, 7, 14, 30]
def next_sr_due(stage: int) -> datetime.datetime:
    stage = max(1, stage)
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
    p["stage"] = p.get("stage", 1) + 1 if correct else 1
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

# IMPORTANT: we KEEP the original name, but make it read ONLY from Memory Book folder
def get_memory_book_images() -> List[Path]:
    if not MBOOK_IMG_DIR.exists():
        return []
    exts = ("*.jpg", "*.jpeg", "*.png", "*.gif", "*.webp")
    files: List[Path] = []
    for ext in exts:
        files.extend(MBOOK_IMG_DIR.rglob(ext))
    return sorted(files)

# Import Memory Book photos as People (for quiz). Kept separate helper.
def ensure_people_from_memory_book(data: Dict[str, Any], force_due: bool = False) -> int:
    imgs = get_memory_book_images()
    if not imgs:
        return 0
    existing_paths = {
        os.path.abspath(p.get("image_path", "")) for p in data["people"].values() if p.get("image_path")
    }
    added = 0
    for img_path in imgs:
        ap = os.path.abspath(str(img_path))
        if ap in existing_paths:
            continue
        name_guess = img_path.stem.replace("_", " ").title()
        pid = uuid.uuid4().hex
        person = {
            "id": pid,
            "name": name_guess or "Family",
            "relation": "Family",
            "image_path": ap,
            "stage": 1,
            "next_due_iso": to_iso(now_local() if force_due else next_sr_due(1)),
        }
        data["people"][pid] = person
        added += 1
    if added:
        save_data(data)
    return added

# Query param helper
def get_qp(name: str) -> Optional[str]:
    try:
        qp = st.query_params
        v = qp.get(name)
    except Exception:
        qp = st.experimental_get_query_params()
        v = qp.get(name)
    if isinstance(v, list):
        return v[0]
    return v

# ------------------------------------------------------------
# PAGE CONFIG + CSS (polished)
# ------------------------------------------------------------
st.set_page_config(page_title="ALZY – Memory Assistant", page_icon="🧠", layout="wide")

st.markdown(
    """
    <style>
    :root{
      --bg0:#0b1220; --bg1:#0f172a; --bg2:#111827; --card:#0b1020;
      --brand:#7c3aed; --brand-2:#22d3ee; --ok:#10b981; --warn:#f59e0b; --danger:#ef4444;
      --border:rgba(255,255,255,0.08); --muted:rgba(255,255,255,0.6);
    }
    .stApp { background: radial-gradient(1200px 600px at 10% -10%, #1e293b 0%, var(--bg0) 40%), linear-gradient(180deg, var(--bg0), var(--bg2)); color:#fff;}
    h1,h2,h3,h4 { color:#fff !important; letter-spacing:.2px }
    .role-badge {
      display:inline-flex; gap:.5rem; align-items:center;
      background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.03));
      border:1px solid var(--border); padding:6px 12px; border-radius:999px; font-size:.8rem;
    }
    /* Cards */
    .alzy-card {
      background: linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));
      border:1px solid var(--border);
      border-radius:16px; padding:14px 16px; box-shadow: 0 10px 30px rgba(0,0,0,.25);
    }
    .alzy-chip { display:inline-block; padding:3px 9px; font-size:.75rem; border-radius:999px; border:1px solid var(--border); color:var(--muted);}
    .due-panel {
      background: linear-gradient(135deg,#f97316 0%,#f43f5e 90%);
      border-radius: 16px; padding: 12px 14px; color: #fff; margin-bottom: 12px; border:1px solid rgba(255,255,255,.18);
    }
    .coming-panel {
      background: linear-gradient(135deg,#6366f1 0%,#06b6d4 90%);
      border-radius: 16px; padding: 10px 14px; margin-bottom: 10px; color:#fff; border:1px solid rgba(255,255,255,.18);
    }
    .stButton button {
      background-image: linear-gradient(90deg, var(--brand), var(--brand-2));
      color: #061018 !important; border-radius: 12px !important; padding: 10px 14px !important; font-weight: 700; border:none;
      box-shadow: 0 6px 16px rgba(124,58,237,.35);
      transition: transform .05s ease;
    }
    .stButton button:hover { transform: translateY(-1px); }
    .stButton button:active { transform: translateY(0); }
    .ghost-btn {
      background:transparent; border:1px solid var(--border); color:#fff; padding:8px 12px; border-radius:10px; cursor:pointer;
    }
    .grid-2 { display:grid; grid-template-columns: 1fr 1fr; gap:12px; }
    .mb-1{margin-bottom:.25rem} .mb-2{margin-bottom:.5rem} .mb-3{margin-bottom:1rem}
    img { border-radius: 12px; }
    .floating-gif {
      position: fixed; top:10px; left:10px; width:82px; height:82px; z-index: 9999; border-radius: 16px; overflow:hidden; border:1px solid var(--border);
      background: radial-gradient(120px 60px at 50% 0%, rgba(255,255,255,.1), rgba(255,255,255,0));
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
qp_role = get_qp("role")
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
            st.session_state.role = "patient"; st.rerun()
    with c2:
        if st.button("🧑‍⚕️ Caregiver", use_container_width=True, key="choose_caregiver"):
            st.session_state.role = "caretaker"; st.rerun()
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
            data["profile"]["name"] = new_nm.strip(); save_data(data)
    else:
        st.markdown(f"**Hello, {nm}!**")
with right:
    st.markdown(f"<span class='role-badge'>Current: {st.session_state.role.title()}</span>", unsafe_allow_html=True)
    if st.button("🔁 Change role"):
        st.session_state.role = None; st.rerun()

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
                    if ip and os.path.exists(ip): st.image(ip, use_container_width=True)
                    else: st.image("https://via.placeholder.com/512x320?text=Photo", use_container_width=True)
                with c2:
                    st.markdown(f"**{r['title']}**  <span class='alzy-chip'>{r.get('reminder_type','activity')}</span>", unsafe_allow_html=True)
                    st.caption(f"Next: {human_time(r['next_due_iso'])}")
                    for i, s in enumerate(r.get("steps", []), 1):
                        st.write(f"{i}. {s}")
                    b1, b2, b3 = st.columns(3)
                    if b1.button("✅ Done", key=f"cg_done_{r['id']}"):
                        advance_reminder(r); 
                        if r.get("reminder_type") == "medicine": add_log(data, r, "taken (caregiver)")
                        save_data(data); st.rerun()
                    if b2.button("⏰ Snooze", key=f"cg_snooze_{r['id']}"):
                        snooze_reminder(r); 
                        if r.get("reminder_type") == "medicine": add_log(data, r, "snoozed (caregiver)")
                        save_data(data); st.rerun()
                    if b3.button("🗑️ Remove", key=f"cg_rm_{r['id']}"):
                        data["reminders"].pop(r["id"], None); save_data(data); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.subheader("🟡 Coming soon (24h)")
        upcoming = []
        now_ = now_local()
        for r in data["reminders"].values():
            dt = parse_iso(r["next_due_iso"])
            if now_ < dt <= now_ + datetime.timedelta(hours=24): upcoming.append(r)
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

            # --- Time (5-min step) ---
            time_options = [f"{h:02d}:{m:02d}" for h in range(24) for m in range(0, 60, 5)]
            now_dt = now_local()
            default_time_str = f"{now_dt.hour:02d}:{(now_dt.minute//5)*5:02d}"
            if default_time_str not in time_options: default_time_str = "23:55"
            time_str = st.selectbox("Time", options=time_options, index=time_options.index(default_time_str))
            t = datetime.time(int(time_str[:2]), int(time_str[3:]))

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
                    # Save image in the correct folder
                    if img_up:
                        if rtype == "medicine":
                            img_path = save_upload_to(img_up, MEDICINE_IMG_DIR)
                        else:
                            img_path = save_upload_to(img_up, ACTIVITY_IMG_DIR)
                    else:
                        img_path = ""
                    aud_path = save_upload_to(aud_up, AUDIO_DIR) if aud_up else ""
                    steps = [s.strip() for s in steps_txt.splitlines() if s.strip()]
                    add_reminder(data, title, when_dt, img_path, aud_path, steps, rpt, reminder_type=rtype)
                    st.success("Reminder added")

        st.divider()
        st.subheader("All reminders")
        for r in sorted(data["reminders"].values(), key=lambda x: x["next_due_iso"]):
            with st.expander(f"{r['title']} — {human_time(r['next_due_iso'])}"):
                st.json(r)

    # PEOPLE (list only; add via Memory Book)
    with tab_people:
        st.subheader("People for Memory Book / Quiz")
        if not data["people"]:
            st.info("No people added yet. Use the Memory Book tab to add photos.")
        else:
            cols = st.columns(2)
            for i, p in enumerate(data["people"].values()):
                with cols[i % 2]:
                    ip = p.get("image_path", "")
                    if ip and os.path.exists(ip): st.image(ip, use_container_width=True)
                    st.markdown(f"**{p['name']}** — {p.get('relation','Family')}")

    # LOGS
    with tab_logs:
        st.subheader("📜 Medicine / action logs")
        logs = sorted(data.get("logs", []), key=lambda x: x["time"], reverse=True)
        if not logs:
            st.info("No logs yet.")
        else:
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

        components.html(
            """
            <button onclick="getGPS()" class="ghost-btn">📍 Get current location</button>
            <script>
            function getGPS(){
              if (!navigator.geolocation){ alert("Geolocation not supported"); return; }
              navigator.geolocation.getCurrentPosition(function(pos){
                const lat = pos.coords.latitude, lon = pos.coords.longitude;
                const u = new URL(window.parent.location.href);
                u.searchParams.set('lat', lat); u.searchParams.set('lon', lon);
                window.parent.location.href = u.toString();
              }, function(err){ alert(err.message); });
            }
            </script>
            """,
            height=60,
        )

        new_lat = get_qp("lat"); new_lon = get_qp("lon")
        if new_lat and new_lon:
            data["gps"]["lat"] = new_lat; data["gps"]["lon"] = new_lon; save_data(data)
            st.success(f"Saved location: {new_lat}, {new_lon}")

        with st.form("set_home_form"):
            addr = st.text_input("Home address", value=cur_home)
            lat_in = st.text_input("Latitude", value=cur_lat)
            lon_in = st.text_input("Longitude", value=cur_lon)
            ok = st.form_submit_button("💾 Save home")
            if ok:
                data["gps"]["home_address"] = addr; data["gps"]["lat"] = lat_in; data["gps"]["lon"] = lon_in
                save_data(data); st.success("Home saved")

        if cur_lat and cur_lon:
            try:
                la = float(cur_lat); lo = float(cur_lon)
                maps_url = f"https://www.google.com/maps?q={la},{lo}&z=15&output=embed"
                components.html(
                    f'<iframe src="{maps_url}" width="100%" height="260" style="border:0" loading="lazy"></iframe>',
                    height=270,
                )
            except Exception:
                pass

        if st.button("🧭 Show directions to home"):
            components.html(f"<script>window.open('{GO_HOME_URL}', '_blank');</script>", height=0)

    # MEMORY BOOK (uploads saved ONLY to MBOOK_IMG_DIR)
    with tab_mbook:
        st.subheader("📘 Memory Book")
        st.caption(f"Folder: {MBOOK_IMG_DIR.resolve()}")
        with st.form("add_person_form", clear_on_submit=True):
            name = st.text_input("Name")
            rel = st.text_input("Relation", value="Family")
            img_up = st.file_uploader("Photo", type=["png", "jpg", "jpeg"])
            ok = st.form_submit_button("💾 Save to Memory Book")
            if ok:
                if not img_up:
                    st.error("Please select a photo.")
                else:
                    pth = save_upload_to(img_up, MBOOK_IMG_DIR)
                    # If a name was given, store as a Person immediately (helps quiz)
                    if name.strip():
                        add_person(data, name.strip(), rel.strip() or "Family", pth)
                    st.success("Saved.")

        imgs = get_memory_book_images()
        if not imgs:
            st.info("No images found yet. Add photos above.")
        else:
            for img_path in imgs:
                c1, c2 = st.columns([1, 2])
                c1.image(str(img_path), use_container_width=True)
                name_guess = img_path.stem.replace("_", " ").title()
                c2.markdown(
                    f"""
<div class="alzy-card">
  <div class="mb-2"><strong>Name:</strong> {name_guess}</div>
  <div class="mb-1"><strong>Relation:</strong> Family</div>
  <div class="mb-1"><span class="alzy-chip">Memory Book</span></div>
</div>
""",
                    unsafe_allow_html=True,
                )
                st.divider()

# ------------------------------------------------------------
# PATIENT VIEW
# ------------------------------------------------------------
else:
    tab_act, tab_med, tab_quiz, tab_mbook, tab_gps, tab_ai = st.tabs(
        ["🧑‍🦽 Activity", "💊 Medicine", "🧩 Quiz", "📘 Memory Book", "📍 GPS", "🤖 AI Chatbot"]
    )

    # Activity / Medicine render
    def render_patient_tab(rem_type: str):
        st.subheader("🔔 Due now")
        due_rems = [r for r in data["reminders"].values() if reminder_due(r) and r.get("reminder_type","activity")==rem_type]
        if not due_rems:
            st.info("Nothing to do right now ✅")
        else:
            for r in sorted(due_rems, key=lambda x: x["next_due_iso"]):
                st.markdown("<div class='due-panel'>", unsafe_allow_html=True)
                c1, c2 = st.columns([1, 2])
                with c1:
                    ip = r.get("image_path", "")
                    if ip and os.path.exists(ip): st.image(ip, use_container_width=True)
                    else: st.image("https://via.placeholder.com/512x320?text=Photo", use_container_width=True)
                with c2:
                    st.markdown(f"**{r['title']}**")
                    st.caption(human_time(r["next_due_iso"]))
                    for i, s in enumerate(r.get("steps", []), 1):
                        st.write(f"{i}. {s}")
                    b1, b2 = st.columns(2)
                    if b1.button("✅ I did it", key=f"pt_done_{rem_type}_{r['id']}"):
                        advance_reminder(r); 
                        if rem_type == "medicine": add_log(data, r, "taken (patient)")
                        save_data(data); st.rerun()
                    if b2.button("⏰ Later", key=f"pt_snooze_{rem_type}_{r['id']}"):
                        snooze_reminder(r); 
                        if rem_type == "medicine": add_log(data, r, "snoozed (patient)")
                        save_data(data); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.subheader("🟡 Coming soon")
        upcoming = []
        now_ = now_local()
        for r in data["reminders"].values():
            if r.get("reminder_type","activity") != rem_type: continue
            dt = parse_iso(r["next_due_iso"])
            if now_ < dt <= now_ + datetime.timedelta(hours=24): upcoming.append(r)
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

    # Quiz (GENERATE ONLY FROM MEMORY BOOK)
    with tab_quiz:
        st.subheader("🧩 Face quiz")
        if "quiz_target_id" not in st.session_state:
            st.session_state.quiz_target_id = None
            st.session_state.quiz_option_ids = []

        # Ensure memory-book images are represented as People
        if not data["people"]:
            ensure_people_from_memory_book(data, force_due=True)
        due = get_due_people(data)

        # If nothing due, force newly imported to due-now
        if not due:
            added = ensure_people_from_memory_book(data, force_due=True)
            due = get_due_people(data)

        if not data["people"]:
            st.info("No Memory Book images found. Please add some in the Memory Book tab.")
        elif not due:
            st.success("All set! People exist, but nothing is due right now. We'll nudge you later.")
        else:
            if st.session_state.quiz_target_id is None:
                target = random.choice(due)
                others = [p for p in data["people"].values() if p["id"] != target["id"]]
                random.shuffle(others); others = others[:2]
                st.session_state.quiz_target_id = target["id"]
                st.session_state.quiz_option_ids = [target["id"]] + [o["id"] for o in others]

            if st.session_state.quiz_target_id:
                target = data["people"][st.session_state.quiz_target_id]
                st.write("Who is this?")
                ip = target.get("image_path", "")
                if ip and os.path.exists(ip): st.image(ip, use_container_width=True)
                else: st.image("https://via.placeholder.com/512x320?text=Photo", use_container_width=True)

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
                            st.success("✅ Correct!") if correct else st.error("❌ Not correct.")
                            st.session_state.quiz_target_id = None
                            st.session_state.quiz_option_ids = []
                            st.rerun()

    # Memory Book (patient view – read-only gallery)
    with tab_mbook:
        st.subheader("📘 Memory Book")
        st.caption(f"Folder: {MBOOK_IMG_DIR.resolve()}")
        imgs = get_memory_book_images()
        if not imgs:
            st.info("No images yet.")
        else:
            for img_path in imgs:
                c1, c2 = st.columns([1, 2])
                c1.image(str(img_path), use_container_width=True)
                name_guess = img_path.stem.replace("_", " ").title()
                c2.markdown(
                    f"""
<div class="alzy-card">
  <div class="mb-2"><strong>Name:</strong> {name_guess}</div>
  <div class="mb-1"><strong>Relation:</strong> Family</div>
  <div class="mb-1"><span class="alzy-chip">Memory Book</span></div>
</div>
""",
                    unsafe_allow_html=True,
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

        for msg in st.session_state.patient_ai_chat:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        st.markdown(
            """
            <div style="margin:8px 0 12px 0;">
              <button id="stt-btn" class="ghost-btn">🎤 Speak</button>
              <span id="stt-status" style="margin-left:8px;font-size:12px;color:#fff;"></span>
            </div>
            <script>
            (function(){
              const btn = document.getElementById("stt-btn"), status = document.getElementById("stt-status");
              if (!btn) return;
              btn.addEventListener("click", function(){
                const isLocal=(location.hostname==="localhost"||location.hostname==="127.0.0.1");
                if (!window.isSecureContext && !isLocal){ status.innerText="❌ Mic blocked: use https or localhost."; return; }
                const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
                if (!SR){ status.innerText="❌ SpeechRecognition not supported."; return; }
                const rec=new SR(); rec.lang="en-US";
                rec.onstart=()=>{ status.innerText="Listening..."; };
                rec.onerror=(e)=>{ status.innerText="❌ "+e.error; };
                rec.onresult=(e)=>{
                  const text=e.results[0][0].transcript;
                  const u=new URL(window.location.href); u.searchParams.set("say", text); window.location.href=u.toString();
                };
                rec.start();
              });
            })();
            </script>
            """,
            unsafe_allow_html=True,
        )

        spoken = get_qp("say")
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
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    msgs = [{"role": "system", "content": "You are a gentle assistant for an Alzheimer's patient. Reply in 2–3 short, simple sentences. Be friendly."}] + st.session_state.patient_ai_chat[-6:]
                    payload = {"model": "gpt-4o-mini", "messages": msgs, "max_tokens": 150, "temperature": 0.6}
                    resp = requests.post(url, headers=headers, json=payload, timeout=15)
                    if resp.status_code == 200:
                        j = resp.json()
                        reply_text = j.get("choices", [{}])[0].get("message", {}).get("content", "I’m here with you.")
                    else:
                        reply_text = f"⚠️ API error {resp.status_code}: {resp.text[:160]}"
                except Exception as e:
                    reply_text = f"⚠️ Request failed: {e}"
            else:
                reply_text = "❗ No OPENAI_API_KEY found.\nAdd it to your .env or Streamlit Secrets."

            with st.chat_message("assistant"):
                st.markdown(reply_text)

            st.session_state.patient_ai_chat.append({"role": "assistant", "content": reply_text})
            last_reply = reply_text
        else:
            for m in reversed(st.session_state.patient_ai_chat):
                if m["role"] == "assistant":
                    last_reply = m["content"]; break

        if last_reply:
            safe_last = json.dumps(last_reply)
            st.markdown(
                f"""
                <button id="tts-btn" class="ghost-btn" style="margin-top:10px;">🔊 Read aloud</button>
                <script>
                (function(){{
                  const btn=document.getElementById("tts-btn");
                  if(!btn) return;
                  btn.addEventListener("click", function(){{
                    if(!window.speechSynthesis){{ alert("Speech not supported here."); return; }}
                    const u=new SpeechSynthesisUtterance({safe_last}); u.lang="en-US"; u.rate=0.95; window.speechSynthesis.speak(u);
                  }});
                }})();
                </script>
                """,
                unsafe_allow_html=True,
            )
