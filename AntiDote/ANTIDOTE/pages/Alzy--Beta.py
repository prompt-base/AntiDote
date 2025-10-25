# Home.py
# -----------------------------
# Memory Assistant (Recognition > Recall)
# Colorful UI + User Greeting (fixed)
# -----------------------------

import os, json, uuid, random, datetime
from pathlib import Path
from typing import List, Dict, Any
import streamlit as st
from PIL import Image

# -----------------------------
# Storage setup
# -----------------------------
DATA_FILE = Path("data.json")
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def now_utc() -> datetime.datetime:
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

def parse_iso(ts: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(ts)

def to_iso(dt: datetime.datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.isoformat()

def load_data() -> Dict[str, Any]:
    if not DATA_FILE.exists():
        return {"profile": {"name": "Friend"}, "reminders": {}, "people": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data: Dict[str, Any]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

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

# -----------------------------
# Spaced-repetition helpers
# -----------------------------
SR_INTERVALS_DAYS = [1, 2, 4, 7, 14, 30]  # simple curve

def next_sr_due(stage: int) -> datetime.datetime:
    idx = min(stage, len(SR_INTERVALS_DAYS)) - 1
    return now_utc() + datetime.timedelta(days=SR_INTERVALS_DAYS[idx])

def human_time(dt_iso: str) -> str:
    try:
        dt = parse_iso(dt_iso).astimezone()
        return dt.strftime("%d %b %Y • %I:%M %p")
    except Exception:
        return dt_iso

# -----------------------------
# Reminder CRUD
# -----------------------------
def add_reminder(data, title, when_dt, image_path, audio_path, steps: List[str], repeat_rule: str):
    rid = uuid.uuid4().hex
    rec = {
        "id": rid,
        "title": title,
        "when_iso": to_iso(when_dt),
        "next_due_iso": to_iso(when_dt),
        "repeat_rule": repeat_rule,  # "once" | "daily" | "sr"
        "stage": 1,                  # for spaced repetition
        "image_path": image_path,
        "audio_path": audio_path,
        "steps": steps or []
    }
    data["reminders"][rid] = rec
    save_data(data)
    return rec

def advance_reminder(rec):
    rule = rec.get("repeat_rule", "once")
    if rule == "once":
        rec["next_due_iso"] = to_iso(now_utc() + datetime.timedelta(days=3650))  # far future
    elif rule == "daily":
        due = parse_iso(rec["next_due_iso"])
        rec["next_due_iso"] = to_iso(due + datetime.timedelta(days=1))
    elif rule == "sr":
        rec["stage"] = max(1, int(rec.get("stage", 1))) + 1
        rec["next_due_iso"] = to_iso(next_sr_due(rec["stage"]))
    else:
        rec["next_due_iso"] = to_iso(now_utc() + datetime.timedelta(days=1))

def snooze_reminder(rec, minutes=10):
    rec["next_due_iso"] = to_iso(now_utc() + datetime.timedelta(minutes=minutes))

def reminder_due(rec) -> bool:
    try:
        return parse_iso(rec["next_due_iso"]) <= now_utc()
    except Exception:
        return False

# -----------------------------
# People CRUD (for face quiz)
# -----------------------------
def add_person(data, name, relation, image_path):
    pid = uuid.uuid4().hex
    data["people"][pid] = {
        "id": pid,
        "name": name,
        "relation": relation,
        "image_path": image_path,
        "stage": 1,
        "next_due_iso": to_iso(next_sr_due(1))
    }
    save_data(data)

def get_due_people_for_quiz(data) -> List[Dict[str, Any]]:
    return [p for p in data["people"].values() if parse_iso(p["next_due_iso"]) <= now_utc()]

def mark_quiz_result(data, person_id: str, correct: bool):
    p = data["people"].get(person_id)
    if not p:
        return
    if correct:
        p["stage"] = p.get("stage", 1) + 1
    else:
        p["stage"] = 1
    p["next_due_iso"] = to_iso(next_sr_due(p["stage"]))
    save_data(data)

# -----------------------------
# Streamlit UI
# -----------------------------

# Colorful theme via CSS (triple quotes properly closed)
st.markdown("""
<style>
/* Page gradient */
.stApp {
  background: linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%);
}

/* Headings */
h1, h2, h3, h4 {
  color: #3A6FF7 !important;
}

/* Nice cards (containers/expanders) */
[data-testid="stContainer"], .st-expander {
  border-radius: 16px !important;
  background: linear-gradient(145deg, #ffffff, #f0f4ff) !important;
  box-shadow: 0 8px 22px rgba(58,111,247,0.14) !important;
  padding: 12px !important;
  margin-bottom: 14px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: 8px;
}
.stTabs [data-baseweb="tab"] {
  background: #000;
  border-radius: 12px;
  padding: 8px 14px;
  border: 1px solid #e8ecff;
}

/* Buttons */
div.stButton > button {
  background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
  color: #000;
  border-radius: 12px;
  padding: 10px 18px;
  font-weight: 600;
  border: none;
}
div.stButton > button:hover {
  background: linear-gradient(90deg, #2575fc 0%, #6a11cb 100%);
}

/* Chips */
.chip {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  background: #F0F4FF;
  color: #3A6FF7;
  font-size: 12px;
  margin-right: 6px;
  margin-bottom: 6px;
}

/* Tiny caption accent */
.small-muted {
  color: #6B6B6B;
  font-size: 12px;
}

/* Big success toast look */
.success-toast {
  background: #E8FFF3;
  padding: 10px 14px;
  border-radius: 12px;
  color: #1E824C;
  font-weight: 600;
}

/* Center helper */
.center {
  display: flex; align-items: center; justify-content: center;
}
</style>
""", unsafe_allow_html=True)

# Load / init data
if "data" not in st.session_state:
    st.session_state.data = load_data()
data = st.session_state.data

# Title + Greeting
st.title("🧠 Memory Assistant")
colA, colB = st.columns([2, 1])
with colA:
    name_default = data.get("profile", {}).get("name", "Friend")
    user_name = st.text_input("Your name", value=name_default, help="Used for greeting only.")
    if user_name.strip() == "":
        user_name = "Friend"
    # Persist name if changed
    if user_name != name_default:
        data.setdefault("profile", {})["name"] = user_name
        save_data(data)
with colB:
    st.markdown("<div class='center' style='height:100%;'><span style='font-size:32px;'>👋</span></div>", unsafe_allow_html=True)

st.markdown(f"### Hello, **{user_name}**!")
st.caption("Welcome back to your colorful Memory Assistant. Let’s make recognition easier than recall 💡")

# Tabs
tab_home, tab_reminders, tab_people, tab_quiz = st.tabs(["🏠 Home", "⏰ Reminders", "👨‍👩‍👧 People", "🧩 Quiz"])

# -----------------------------
# HOME — due reminders
# -----------------------------
with tab_home:
    st.subheader("Due now")
    due_rems = [r for r in data["reminders"].values() if reminder_due(r)]
    if not due_rems:
        st.info("No reminders due right now. Add some in the Reminders tab, or wait until they’re due.")
    else:
        for r in sorted(due_rems, key=lambda x: x["next_due_iso"]):
            with st.container():
                cols = st.columns([1, 2])
                # Image
                img_path = r.get("image_path", "")
                if img_path and os.path.exists(img_path):
                    try:
                        img = Image.open(img_path)
                        cols[0].image(img, use_column_width=True)
                    except Exception:
                        cols[0].warning("Image unavailable")
                else:
                    cols[0].write("📷 No image")

                # Content
                with cols[1]:
                    st.markdown(f"**{r['title']}**")
                    st.caption(f"Scheduled: {human_time(r['when_iso'])} • Next due: {human_time(r['next_due_iso'])}")

                    # Chips (example: repetition & stage)
                    chips = []
                    rule = r.get("repeat_rule", "once")
                    chips.append(f"<span class='chip'>🔁 {rule.upper()}</span>")
                    chips.append(f"<span class='chip'>🎯 Stage {r.get('stage',1)}</span>")
                    st.markdown(" ".join(chips), unsafe_allow_html=True)

                    # Steps
                    steps = r.get("steps", [])
                    if steps:
                        st.write("Steps:")
                        for i, s in enumerate(steps, 1):
                            st.write(f"{i}. {s}")

                    # Audio (play if uploaded)
                    audio_path = r.get("audio_path", "")
                    if audio_path and os.path.exists(audio_path):
                        st.audio(audio_path)
                    else:
                        st.caption("🔊 Optional: add a voice cue to make recognition easier.")

                    cols_btn = st.columns([1, 1, 1])
                    if cols_btn[0].button("✅ DONE", key=f"done_{r['id']}"):
                        advance_reminder(r)
                        save_data(data)
                        st.markdown("<div class='success-toast'>Nice! Marked as done.</div>", unsafe_allow_html=True)
                        st.rerun()
                    if cols_btn[1].button("⏰ Snooze 10 min", key=f"snooze_{r['id']}"):
                        snooze_reminder(r, minutes=10)
                        save_data(data)
                        st.info("Snoozed for 10 minutes.")
                        st.rerun()
                    if cols_btn[2].button("🗑️ Remove (one-time)", key=f"rm_{r['id']}"):
                        data["reminders"].pop(r["id"], None)
                        save_data(data)
                        st.warning("Reminder removed.")
                        st.rerun()

# -----------------------------
# REMINDERS — add/manage
# -----------------------------
with tab_reminders:
    st.subheader("Add recognition-first reminder")
    # (No border= param to avoid version issues)
    with st.form("add_reminder_form", clear_on_submit=True):
        title = st.text_input("Title (e.g., Take blue capsule)")
        date = st.date_input("Date", value=datetime.date.today())
        time = st.time_input("Time", value=datetime.time(hour=20, minute=0))
        st.caption("Tip: Use a **photo** and a **voice cue** for stronger recognition.")
        image_upload = st.file_uploader("Photo (pill bottle / object)", type=["png", "jpg", "jpeg"])
        audio_upload = st.file_uploader("Optional voice cue (mp3/wav/m4a)", type=["mp3", "wav", "m4a"])
        steps_text = st.text_area("Steps (one per line)", placeholder="Drink water\nTake capsule\nMark done")
        repeat_rule = st.selectbox("Repeat", ["once", "daily", "sr"], index=1, help="sr = spaced repetition")
        submitted = st.form_submit_button("➕ Add reminder")
        if submitted:
            if not title:
                st.error("Title is required.")
            else:
                when_dt = datetime.datetime.combine(date, time, tzinfo=datetime.timezone.utc)
                img_path = save_upload(image_upload, "images") if image_upload else ""
                aud_path = save_upload(audio_upload, "audio") if audio_upload else ""
                steps = [s.strip() for s in steps_text.splitlines() if s.strip()]
                rec = add_reminder(data, title, when_dt, img_path, aud_path, steps, repeat_rule)
                st.success(f"Added reminder for {human_time(rec['when_iso'])}")

    st.divider()
    st.subheader("All reminders")
    if not data["reminders"]:
        st.info("No reminders yet.")
    else:
        for r in sorted(data["reminders"].values(), key=lambda x: x["next_due_iso"]):
            with st.expander(f"{r['title']}  — next: {human_time(r['next_due_iso'])}"):
                st.json(r)

# -----------------------------
# PEOPLE — add/manage (for face quiz)
# -----------------------------
with tab_people:
    st.subheader("Add a person (for face recognition quiz)")
    with st.form("add_person_form", clear_on_submit=True):
        name = st.text_input("Name (e.g., Arjun)")
        relation = st.text_input("Relation (e.g., Son)")
        img_up = st.file_uploader("Photo", type=["png","jpg","jpeg"])
        ok = st.form_submit_button("💾 Save person")
        if ok:
            if not name or not img_up:
                st.error("Name and photo are required.")
            else:
                p_path = save_upload(img_up, "people")
                add_person(data, name, relation, p_path)
                st.success("Person saved for quizzes.")

    st.divider()
    if not data["people"]:
        st.info("No people added yet.")
    else:
        st.subheader("People")
        grid = st.columns(2)
        i = 0
        for p in data["people"].values():
            with grid[i % 2]:
                with st.container():
                    if os.path.exists(p["image_path"]):
                        st.image(p["image_path"], use_column_width=True)
                    st.markdown(f"**{p['name']}** — {p['relation']}")
                    st.caption(f"Next quiz: {human_time(p['next_due_iso'])} • Stage {p.get('stage',1)}")
            i += 1

# -----------------------------
# QUIZ — face recognition
# -----------------------------
with tab_quiz:
    st.subheader("Face recognition quiz")
    due_people = get_due_people_for_quiz(data)
    if not data["people"]:
        st.info("Add people first in the People tab.")
    elif not due_people:
        st.success("🎉 No one is due for quiz right now. Come back later!")
    else:
        target = random.choice(due_people)
        distractors = [p for p in data["people"].values() if p["id"] != target["id"]]
        random.shuffle(distractors)
        distractors = distractors[:2] if len(distractors) >= 2 else distractors

        st.write("**Who is this?**")
        if os.path.exists(target["image_path"]):
            st.image(target["image_path"], width=320)
        else:
            st.warning("Target image missing.")

        options = [target] + distractors
        random.shuffle(options)

        cols = st.columns(len(options)) if len(options) > 0 else [st]
        # Keep choice in session to allow feedback + rerun loop
        chosen_id = st.session_state.get("chosen_id", None)
        for i, person in enumerate(options):
            with cols[i]:
                with st.container():
                    if os.path.exists(person["image_path"]):
                        st.image(person["image_path"], use_column_width=True)
                    if st.button(f"{person['name']} — {person['relation']}", key=f"opt_{person['id']}"):
                        st.session_state["chosen_id"] = person["id"]
                        st.rerun()

        chosen_id = st.session_state.get("chosen_id", None)
        if chosen_id:
            correct = (chosen_id == target["id"])
            mark_quiz_result(data, target["id"], correct)
            if correct:
                st.markdown("<div class='success-toast'>✅ Correct! Next quiz scheduled.</div>", unsafe_allow_html=True)
            else:
                st.error("❌ Try again—look carefully at the face.")
            # reset choice after feedback
            st.session_state["chosen_id"] = None
            st.rerun()
