# ANTIDOTE/pages/Alzy--Beta.py
# ------------------------------------------------------------
# ALZY – Memory Assistant (Caregiver + Patient) with AI Chatbot
# ------------------------------------------------------------
import os
import re
import json
import uuid
import random
import datetime as dt
from pathlib import Path
from typing import Dict, Any, List, Optional

import streamlit as st
from PIL import Image  # noqa: F401
import requests
import streamlit.components.v1 as components

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:
    ZoneInfo = None

# ------------------------------------------------------------
# CONSTANT PATHS
# ------------------------------------------------------------
PROJECT_DIR = Path(__file__).parent                   # ANTIDOTE/pages
APP_DIR = PROJECT_DIR.parent                          # ANTIDOTE
REPO_ROOT = APP_DIR                                   # project root (where data.json & uploads live)

# Base scratch area for runtime uploads
UPLOAD_BASE = Path("/tmp/alzy_uploads")
UPLOAD_BASE.mkdir(parents=True, exist_ok=True)

# Activity / Medicine / MemoryBook specific runtime dirs
ACTIVITY_IMG_DIR = UPLOAD_BASE / "activity_images"
MEDICINE_IMG_DIR = UPLOAD_BASE / "medicine_images"
MBOOK_IMG_DIR = UPLOAD_BASE / "memory_book_images"
AUDIO_DIR = UPLOAD_BASE / "audio"

for p in (ACTIVITY_IMG_DIR, MEDICINE_IMG_DIR, MBOOK_IMG_DIR, AUDIO_DIR):
    p.mkdir(parents=True, exist_ok=True)

# Baseline file (repo) + Runtime file (temp)
BASELINE_FILE_CANDIDATES = [
    REPO_ROOT / "data.json",
    APP_DIR / "data.json",
    PROJECT_DIR / "data.json",
]
RUNTIME_FILE = PROJECT_DIR / ".data_temp.json"
if not RUNTIME_FILE.exists():
    RUNTIME_FILE.write_text("{}", encoding="utf-8")

# Default timezone (IST)
IST = ZoneInfo("Asia/Kolkata") if ZoneInfo else None

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
        env_path = REPO_ROOT / ".env"
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
# TIME HELPERS (consistent IST)
# ------------------------------------------------------------
def now_local() -> dt.datetime:
    n = dt.datetime.now(tz=IST) if IST else dt.datetime.now()
    return n.replace(microsecond=0)


def parse_iso(ts: str) -> dt.datetime:
    """Treat stored ISO strings as IST wall-time if naive; convert to IST if aware."""
    try:
        v = dt.datetime.fromisoformat(ts)
        if v.tzinfo is None:
            return v.replace(tzinfo=IST) if IST else v
        return v.astimezone(IST) if IST else v
    except Exception:
        return now_local()


def to_iso(d: dt.datetime) -> str:
    if d.tzinfo is None and IST:
        d = d.replace(tzinfo=IST)
    return d.astimezone(IST).replace(microsecond=0).isoformat() if IST else d.replace(microsecond=0).isoformat()


def human_time(dt_iso: str) -> str:
    try:
        d = parse_iso(dt_iso)
        return d.strftime("%d %b %Y • %I:%M %p")
    except Exception:
        return dt_iso


# ------------------------------------------------------------
# PATH RESOLUTION HELPERS (baseline-relative media)
# ------------------------------------------------------------
def resolve_path(p: str) -> str:
    """Return absolute path for media:
    - absolute path => unchanged if exists
    - relative (e.g., 'uploads/images/...') => try REPO_ROOT, APP_DIR, PROJECT_DIR
    - otherwise return original
    """
    if not p:
        return ""
    # absolute and exists
    if os.path.isabs(p) and os.path.exists(p):
        return p
    # try common bases
    for base in (REPO_ROOT, APP_DIR, PROJECT_DIR):
        candidate = (base / p).resolve()
        if os.path.exists(candidate):
            return str(candidate)
    return p


def image_exists(path: str) -> bool:
    rp = resolve_path(path)
    return bool(rp and os.path.exists(rp))


# ------------------------------------------------------------
# DATA LOAD & MERGE
# ------------------------------------------------------------
def default_data() -> Dict[str, Any]:
    return {
        "profile": {"name": "Friend"},
        "reminders": {},
        "people": {},
        "logs": [],
        "gps": {
            "home_address": "",
            "lat": "",
            "lon": "",
            "pois": {
                "family_doctor": {"name": "Family Doctor", "lat": "", "lon": ""},
                "daily_market": {"name": "Daily Market", "lat": "", "lon": ""},
                "hospital": {"name": "Hospital", "lat": "", "lon": ""},
                "mothers_home": {"name": "Mother's Home", "lat": "", "lon": ""},
            },
        },
        "memory_book_images": [],
    }


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _find_baseline_file() -> Optional[Path]:
    for p in BASELINE_FILE_CANDIDATES:
        if p.exists():
            return p
    return None


def _merge_maps(baseline: Dict[str, Any], runtime: Dict[str, Any], key: str) -> Dict[str, Any]:
    """Merge dicts of objects by ID. Runtime overrides baseline."""
    out = dict(baseline.get(key, {}))
    out.update(runtime.get(key, {}))
    return out


def _merge_lists_latest_first(b_list: List[str], r_list: List[str]) -> List[str]:
    """Concatenate runtime first (latest), then baseline; remove duplicates preserving order."""
    seen = set()
    out: List[str] = []
    for s in (r_list or []) + (b_list or []):
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def load_merged_data() -> Dict[str, Any]:
    baseline_path = _find_baseline_file()
    baseline = _read_json(baseline_path) if baseline_path else {}
    runtime = _read_json(RUNTIME_FILE)

    data = default_data()
    # shallow keys
    data["profile"] = baseline.get("profile") or runtime.get("profile") or data["profile"]
    data["gps"] = baseline.get("gps") or runtime.get("gps") or data["gps"]
    data["logs"] = baseline.get("logs") or runtime.get("logs") or data["logs"]

    # merged maps
    data["reminders"] = _merge_maps(baseline, runtime, "reminders")
    data["people"] = _merge_maps(baseline, runtime, "people")

    # merged memory book index (paths)
    data["memory_book_images"] = _merge_lists_latest_first(
        baseline.get("memory_book_images", []),
        runtime.get("memory_book_images", []),
    )

    # ensure gps.pois schema
    data.setdefault("gps", {})
    data["gps"].setdefault("home_address", "")
    data["gps"].setdefault("lat", "")
    data["gps"].setdefault("lon", "")
    data["gps"].setdefault(
        "pois",
        {
            "family_doctor": {"name": "Family Doctor", "lat": "", "lon": ""},
            "daily_market": {"name": "Daily Market", "lat": "", "lon": ""},
            "hospital": {"name": "Hospital", "lat": "", "lon": ""},
            "mothers_home": {"name": "Mother's Home", "lat": "", "lon": ""},
        },
    )

    return data


def save_runtime_data(data: Dict[str, Any]) -> None:
    # only persist dynamic keys (don't overwrite baseline)
    dyn = {
        "profile": data.get("profile", {}),
        "gps": data.get("gps", {}),
        "reminders": data.get("reminders", {}),
        "people": data.get("people", {}),
        "logs": data.get("logs", []),
        "memory_book_images": data.get("memory_book_images", []),
    }
    try:
        RUNTIME_FILE.write_text(json.dumps(dyn, indent=2), encoding="utf-8")
    except Exception:
        pass
    st.session_state.data = data


# ------------------------------------------------------------
# OTHER HELPERS
# ------------------------------------------------------------
def _slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "photo"


def save_upload_to(upload, folder: Path, name_hint: Optional[str] = None) -> str:
    if not upload:
        return ""
    folder.mkdir(parents=True, exist_ok=True)
    ext = Path(upload.name).suffix.lower()
    stem_hint = name_hint or Path(upload.name).stem
    stem = _slugify(stem_hint)
    fname = f"{stem}-{uuid.uuid4().hex[:8]}{ext}"
    path = folder / fname
    with open(path, "wb") as f:
        f.write(upload.read())
    return str(path)


# Spaced repetition
SR_INTERVALS = [1, 2, 4, 7, 14, 30]


def next_sr_due(stage: int) -> dt.datetime:
    stage = max(1, stage)
    idx = min(stage, len(SR_INTERVALS)) - 1
    return now_local() + dt.timedelta(days=SR_INTERVALS[idx])


def add_reminder(
    data: Dict[str, Any],
    title: str,
    when_dt: dt.datetime,
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
    save_runtime_data(data)


def reminder_due(rec: Dict[str, Any]) -> bool:
    try:
        return parse_iso(rec["next_due_iso"]) <= (now_local() + dt.timedelta(minutes=1))
    except Exception:
        return False


def advance_reminder(rec: Dict[str, Any]):
    rule = rec.get("repeat_rule", "once")
    if rule == "once":
        rec["next_due_iso"] = to_iso(now_local() + dt.timedelta(days=3650))
    elif rule == "daily":
        rec["next_due_iso"] = to_iso(parse_iso(rec["next_due_iso"]) + dt.timedelta(days=1))
    elif rule == "sr":
        rec["stage"] = rec.get("stage", 1) + 1
        rec["next_due_iso"] = to_iso(next_sr_due(rec["stage"]))
    else:
        rec["next_due_iso"] = to_iso(now_local() + dt.timedelta(days=1))


def snooze_reminder(rec: Dict[str, Any], minutes: int = 10):
    rec["next_due_iso"] = to_iso(now_local() + dt.timedelta(minutes=minutes))


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
    save_runtime_data(data)


def mark_quiz_result(data: Dict[str, Any], person_id: str, correct: bool):
    p = data["people"].get(person_id)
    if not p:
        return
    p["stage"] = p.get("stage", 1) + 1 if correct else 1
    p["next_due_iso"] = to_iso(next_sr_due(p["stage"]))
    save_runtime_data(data)


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
    save_runtime_data(data)


# Memory Book helpers
def _file_mtime_or_zero(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except Exception:
        return 0.0


def get_memory_book_images() -> List[Path]:
    """
    Combine baseline memory_book_images plus runtime folder images.
    Return list of Paths (existing), newest first.
    """
    imgs: List[Path] = []

    baseline_paths = st.session_state.data.get("memory_book_images", [])
    for rel in baseline_paths:
        p = Path(resolve_path(rel)).resolve()
        if p.exists():
            imgs.append(p)

    if MBOOK_IMG_DIR.exists():
        for f in MBOOK_IMG_DIR.iterdir():
            if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
                imgs.append(f.resolve())

    uniq = {}
    for p in sorted(imgs, key=_file_mtime_or_zero, reverse=True):
        uniq[str(p)] = p
    return list(uniq.values())


def ensure_people_from_memory_book(data: Dict[str, Any]) -> int:
    """Ensure every Memory Book image has a Person entry. Do not force due dates."""
    imgs = get_memory_book_images()
    if not imgs:
        return 0

    existing_by_path = {
        os.path.abspath(resolve_path(p.get("image_path", ""))): pid
        for pid, p in data["people"].items()
        if p.get("image_path")
    }

    added = 0
    for img_path in imgs:
        ap = os.path.abspath(resolve_path(str(img_path)))
        if ap in existing_by_path:
            continue

        stem = Path(img_path).stem
        base = stem.split("-", 1)[0]
        nice = base.replace("-", " ").replace("_", " ").title() or "Family"

        pid = uuid.uuid4().hex
        data["people"][pid] = {
            "id": pid,
            "name": nice,
            "relation": "Family",
            "image_path": ap,
            "stage": 1,
            "next_due_iso": to_iso(next_sr_due(1)),
        }
        added += 1

    if added:
        save_runtime_data(data)
    return added


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


def read_audio_bytes(path: str) -> Optional[bytes]:
    try:
        with open(path, "rb") as f:
            return f.read()
    except Exception:
        return None


# --- GPS helpers (build Google Maps directions & open in new tab) ---
def _open_external(url: str) -> None:
    """Open a URL in a new browser tab from Streamlit."""
    components.html(f"<script>window.open('{url}', '_blank');</script>", height=0)


def _build_dir_url(origin_lat=None, origin_lon=None, dest_lat=None, dest_lon=None, mode: str = "driving") -> str:
    """
    Build Google Maps directions URL. If origin is None, Google Maps uses device GPS.
    """
    base = "https://www.google.com/maps/dir/?api=1"
    params = []
    if origin_lat and origin_lon:
        params.append(f"origin={origin_lat},{origin_lon}")
    if dest_lat and dest_lon:
        params.append(f"destination={dest_lat},{dest_lon}")
    params.append(f"travelmode={mode}")
    return base + "&" + "&".join(params)


def _offset_point(lat: float, lon: float, km_north: float = 0.0, km_east: float = 0.0) -> tuple[float, float]:
    """
    Roughly offset a lat/lon by km. 1 deg lat ~111km, 1 deg lon ~111km*cos(lat).
    Good enough to synthesize a ~5km sample point.
    """
    import math

    dlat = km_north / 111.0
    dlon = km_east / (111.0 * max(0.1, abs(math.cos(math.radians(lat)))))
    return lat + dlat, lon + dlon


# --- Local date/time answers for AI ---
def maybe_local_answer(user_input: str) -> Optional[str]:
    """Answer simple date/time questions locally in IST."""
    if not user_input:
        return None
    q = user_input.strip().lower()

    now = now_local()  # IST
    if "today" in q and "date" in q:
        return now.strftime("Today is %d %B %Y.")
    if "what day is today" in q or "which day is today" in q:
        return now.strftime("Today is %A.")
    if "what is the time" in q or "current time" in q or "time now" in q:
        return now.strftime("The time now is %I:%M %p.")
    return None


# ------------------------------------------------------------
# PAGE CONFIG + CSS
# ------------------------------------------------------------
st.set_page_config(page_title="ALZY – Memory Assistant", page_icon="🧠", layout="wide")

st.markdown(
    """
    <style>
    :root{
      --bg0:#0b1220; --bg1:#0f172a; --bg2:#111827; --card:#0b1020;
      --brand:#7c3aed; --brand-2:#22d3ee; --ok:#10b981; --warn:#f59e0b; --danger:#ef4444;
      --border:rgba(255,255,255,0.10); --muted:rgba(255,255,255,0.70);
    }
    .stApp {
      background: radial-gradient(1200px 600px at 10% -10%, #1e293b 0%, var(--bg0) 40%),
                  linear-gradient(180deg, var(--bg0), var(--bg2));
      color:#fff;
    }
    h1,h2,h3,h4 { color:#fff !important; letter-spacing:.2px }
    .role-badge {
      display:inline-flex; gap:.5rem; align-items:center;
      background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.03));
      border:1px solid var(--border); padding:6px 12px; border-radius:999px; font-size:.8rem;
    }
    .alzy-card {
      background: linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.025));
      border:1px solid var(--border); border-radius:14px; padding:12px 14px;
      box-shadow: 0 12px 28px rgba(0,0,0,.25); margin-bottom:10px;
    }
    .alzy-thumb {
      width: 170px; height: 130px; border-radius:12px; overflow:hidden; border:1px solid var(--border); flex: 0 0 auto;
    }
    .alzy-thumb img { width:100%; height:100%; object-fit:cover; display:block; }

    @media (max-width: 640px) {
      .alzy-thumb { width: 150px; height: 116px; }
    }
    @media (min-width: 1400px) {
      .alzy-thumb { width: 190px; height: 144px; }
    }

    .alzy-meta { flex: 1 1 auto; min-width: 0; }
    .alzy-actions { display:flex; gap:8px; flex-wrap:wrap; margin-top:8px; }
    .chip { display:inline-block; padding:2px 8px; font-size:.75rem; border-radius:999px; border:1px solid var(--border); color:var(--muted); }
    .grid-2 { display:grid; grid-template-columns: 1fr 1fr; gap:12px; }
    .mb-0{margin-bottom:0} .mb-1{margin-bottom:.25rem} .mb-2{margin-bottom:.5rem} .mb-3{margin-bottom:1rem}
    .stButton > button {
      background-image: linear-gradient(90deg, var(--brand), var(--brand-2));
      color: #061018 !important; border-radius: 10px !important; padding: 8px 12px !important; font-weight: 700; border:none;
      box-shadow: 0 6px 16px rgba(124,58,237,.35);
    }
    .btn-ghost button { background:transparent !important; color:#fff !important; border:1px solid var(--border) !important; }
    .btn-danger button { background:#ef4444 !important; color:#fff !important; }
    .btn-warn button { background:#f59e0b !important; color:#111 !important; }
    .noimg {
      width: 170px; height: 150px; display:flex; align-items:center; justify-content:center; border-radius:12px; border:1px dashed var(--border); color:var(--muted);
      font-size:.8rem; background:rgba(255,255,255,.03);
    }
    .mbook-thumb {
      width: 100%;
      aspect-ratio: 4 / 3;
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid var(--border);
      background: rgba(255,255,255,.03);
    }
    .mbook-thumb img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transition: transform .25s ease;
    }
    .mbook-thumb:hover img {
      transform: scale(1.08);
    }
    .mbook-row-sep {
      height: 14px;
      border-top: 1px solid var(--border);
      margin: 8px 0 16px 0;
    }
    .mbook-name {
      margin-top: 6px;
    }
    audio { width: 100%; max-width: 260px; }
    hr.thick {
      border: 0;
      height: 3px;
      background: linear-gradient(
        90deg,
        rgba(255,255,255,0.12),
        rgba(255,255,255,0.22),
        rgba(255,255,255,0.12)
      );
      margin: 10px 0 14px 0;
      border-radius: 2px;
    }

    /* ===== Tabs text color tweaks ===== */
    /* All tab labels (active + inactive) */
    div.stTabs [data-baseweb="tab"] {
      color: #ffffff !important;           /* make inactive text white */
      font-weight: 500;
    }

    /* Active tab label accent */
    div.stTabs [data-baseweb="tab"][aria-selected="true"] {
      color: #ff4b4b !important;
    #   border-bottom: 3px solid #22d3ee !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# SESSION INIT (baseline + runtime merged)
# ------------------------------------------------------------
if "data" not in st.session_state:
    st.session_state.data = load_merged_data()
data = st.session_state.data

if "role" not in st.session_state:
    st.session_state.role = None

if "patient_ai_chat" not in st.session_state:
    st.session_state.patient_ai_chat = [
        {"role": "assistant", "content": "Hello 👋 I'm your Memory Assistant. How can I help you today?"}
    ]

if "patient_ai_questions" not in st.session_state:
    st.session_state.patient_ai_questions = []

# Support ?role=patient or ?role=caretaker
qp_role = get_qp("role")
if qp_role in ("patient", "caretaker"):
    st.session_state.role = qp_role


# ------------------------------------------------------------
# SHARED RENDER HELPERS
# ------------------------------------------------------------
def _render_thumb(path: str) -> None:
    """Render a small thumbnail with a fixed target height (cropped/resized via PIL)."""
    rp = resolve_path(path)
    if image_exists(path):
        try:
            img = Image.open(rp).convert("RGB")
            target_h = 190
            scale = target_h / float(img.height if img.height else 1)
            target_w = max(1, int(img.width * scale))
            img = img.resize((target_w, target_h), Image.LANCZOS)
            st.image(img, use_container_width=False)
        except Exception:
            st.image(rp, width=220)
    else:
        st.markdown('<div class="noimg" style="height: 170px;">No image</div>', unsafe_allow_html=True)


def _render_audio(audio_path: str):
    if not audio_path:
        return
    rp = resolve_path(audio_path)
    b = read_audio_bytes(rp)
    if b:
        st.audio(b)


def _reminders_by_type(rem_type: str) -> List[Dict[str, Any]]:
    items = [r for r in data["reminders"].values() if r.get("reminder_type", "activity") == rem_type]
    return sorted(items, key=lambda x: parse_iso(x.get("when_iso", "1970-01-01T00:00:00")), reverse=True)


def _render_reminder_card(
    rec: Dict[str, Any],
    slno: int,
    is_caregiver: bool,
    key_prefix: str,
    show_actions: bool = True,
) -> None:
    with st.container():
        col_img, col_meta = st.columns([0.6, 1.4])

        with col_img:
            _render_thumb(rec.get("image_path", ""))

        with col_meta:
            st.markdown(f"**SL No:** {slno}")
            st.markdown(f"**Title:** {rec.get('title', '(Untitled)')}")
            st.caption(human_time(rec.get("next_due_iso", "")))

            steps = rec.get("steps", [])
            if steps:
                st.markdown("**Steps:**")
                for i, s in enumerate(steps, 1):
                    st.write(f"{i}. {s}")

            audio_path = rec.get("audio_path")
            if audio_path:
                st.markdown("**Audio:**")
                _render_audio(audio_path)

            if show_actions:
                c1, c2, c3 = st.columns(3)

                # ✅ Done – base style from .stButton > button
                with c1:
                    if st.button("✅ Done", key=f"{key_prefix}_done_{rec['id']}"):
                        advance_reminder(rec)
                        if rec.get("reminder_type") == "medicine":
                            add_log(
                                data,
                                rec,
                                "taken (caregiver)" if is_caregiver else "taken (patient)",
                            )
                        save_runtime_data(data)
                        st.rerun()

                # ⏰ Snooze – EXACT same styling as Done (same st.button)
                with c2:
                    if st.button(
                        "⏰ Snooze",
                        key=f"{key_prefix}_snooze_{rec['id']}",
                        help="Snooze by 10 minutes",
                    ):
                        snooze_reminder(rec, 10)
                        if rec.get("reminder_type") == "medicine":
                            add_log(
                                data,
                                rec,
                                "snoozed (caregiver)" if is_caregiver else "snoozed (patient)",
                            )
                        save_runtime_data(data)
                        st.rerun()

                # 🗑️ Remove – same base style unless you later override with .btn-danger
                with c3:
                    if st.button("🗑️ Remove", key=f"{key_prefix}_remove_{rec['id']}"):
                        data["reminders"].pop(rec["id"], None)
                        save_runtime_data(data)
                        st.rerun()

        st.markdown("<hr class='thick' />", unsafe_allow_html=True)


def _render_due_and_coming(
    is_caregiver: bool,
    types: tuple = ("activity", "medicine"),
    scope: str = "scope",
) -> None:
    now_ = now_local()
    sections = [(t.title(), t) for t in types]

    st.subheader("🔔 Due now")
    for _, t in sections:
        due = [r for r in _reminders_by_type(t) if reminder_due(r)]
        if not due:
            st.info("Nothing due.")
        else:
            due = sorted(due, key=lambda x: parse_iso(x["next_due_iso"]))
            for i, r in enumerate(due, 1):
                _render_reminder_card(r, i, is_caregiver, key_prefix=f"{scope}_due_{t}", show_actions=True)

    st.subheader("🟡 Coming soon")
    horizon = now_ + dt.timedelta(hours=24)
    for _, t in sections:
        upcoming = []
        for r in _reminders_by_type(t):
            d = parse_iso(r["next_due_iso"])
            if now_ < d <= horizon:
                upcoming.append(r)
        if not upcoming:
            st.caption("No upcoming reminders.")
        else:
            upcoming = sorted(upcoming, key=lambda x: parse_iso(x["next_due_iso"]))
            for i, r in enumerate(upcoming, 1):
                _render_reminder_card(r, i, is_caregiver, key_prefix=f"{scope}_soon_{t}", show_actions=False)


# --- QUIZ (simple & calm for ALZY) ---
def _render_quiz_simple():
    st.subheader("🧩 Face quiz")

    if "quiz_target_id" not in st.session_state:
        st.session_state.quiz_target_id = None
        st.session_state.quiz_option_ids = []
        st.session_state.quiz_feedback = None
        st.session_state.quiz_is_correct = None

    ensure_people_from_memory_book(data)

    due = [
        p
        for p in data["people"].values()
        if parse_iso(p.get("next_due_iso", "2099-01-01T00:00:00")) <= now_local()
    ]
    pool = due if due else list(data["people"].values())

    if not pool:
        st.info("No Memory Book images found. Please add some in the Memory Book tab.")
        return

    if st.session_state.quiz_target_id is None:
        target = random.choice(pool)
        others = [p for p in data["people"].values() if p["id"] != target["id"]]
        random.shuffle(others)
        others = others[:2]
        st.session_state.quiz_target_id = target["id"]
        st.session_state.quiz_option_ids = [target["id"]] + [o["id"] for o in others]
        st.session_state.quiz_feedback = None
        st.session_state.quiz_is_correct = None

    target = data["people"][st.session_state.quiz_target_id]

    st.write("Who is this?")
    _c1, _c2, _c3 = st.columns([1, 1.2, 1])
    with _c2:
        ip = target.get("image_path", "")
        rp = resolve_path(ip)
        if image_exists(ip):
            st.image(rp, width=240)
        else:
            st.markdown('<div class="noimg">No image</div>', unsafe_allow_html=True)

    option_people = [data["people"][pid] for pid in st.session_state.quiz_option_ids if pid in data["people"]]
    random.shuffle(option_people)

    st.markdown(" ")
    colA, colB, colC = st.columns(3)
    cols = [colA, colB, colC]

    for i, p in enumerate(option_people):
        label = f"{p['name']} — {p.get('relation', 'Family')}"
        with cols[i]:
            if st.button(label, key=f"quiz_ans_{p['id']}"):
                is_correct = p["id"] == target["id"]
                mark_quiz_result(data, target["id"], is_correct)
                st.session_state.quiz_is_correct = is_correct
                st.session_state.quiz_feedback = "✅ Correct!" if is_correct else "❌ Not correct."

    if st.session_state.quiz_feedback:
        if st.session_state.quiz_is_correct:
            st.success(st.session_state.quiz_feedback)
        else:
            st.error(st.session_state.quiz_feedback)

        if st.button("➡️ Next face", key="quiz_next_face"):
            st.session_state.quiz_target_id = None
            st.session_state.quiz_option_ids = []
            st.session_state.quiz_feedback = None
            st.session_state.quiz_is_correct = None
            st.rerun()


def _display_memory_book_gallery():
    imgs = get_memory_book_images()
    if not imgs:
        st.info("No images found yet.")
        return

    def _chunks(seq, n):
        for i in range(0, len(seq), n):
            yield seq[i : i + n]

    for row in _chunks(imgs, 4):
        cols = st.columns(4, gap="small")
        for idx, img_path in enumerate(row):
            with cols[idx]:
                _render_thumb(str(img_path))

                ap = os.path.abspath(resolve_path(str(img_path)))
                person = next(
                    (
                        p
                        for p in data["people"].values()
                        if os.path.abspath(resolve_path(p.get("image_path", ""))) == ap
                    ),
                    None,
                )
                if person:
                    display_name = person.get("name") or "Family"
                    display_rel = person.get("relation") or "Family"
                else:
                    stem = Path(img_path).stem
                    base = stem.split("-", 1)[0]
                    display_name = base.replace("-", " ").replace("_", " ").title() or "Family"
                    display_rel = "Family"

                st.markdown(
                    f'<div class="mbook-name"><strong>{display_name}</strong><br/>'
                    f'<span class="chip">{display_rel}</span></div>',
                    unsafe_allow_html=True,
                )

        st.markdown('<div class="mbook-row-sep"></div>', unsafe_allow_html=True)


# ------------------------------------------------------------
# LANDING (choose role)
# ------------------------------------------------------------
if st.session_state.role is None:
    st.markdown("<h1 style='text-align:center;'>🧠 ALZY – Memory Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Who are you?</h3>", unsafe_allow_html=True)
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 3 columns: left spacer, center content, right spacer
    left_spacer, center_col, right_spacer = st.columns([1, 2, 1])

    with center_col:
        # inner columns for the two buttons, centered within the middle column
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🧑‍🦽 Patient", key="choose_patient", use_container_width=True):
                st.session_state.role = "patient"
                st.rerun()
        with c2:
            if st.button("🧑‍⚕️ Caregiver", key="choose_caregiver", use_container_width=True):
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
            save_runtime_data(data)
    else:
        st.markdown(f"**Hello, {nm}!**")
with right:
    st.markdown(f"<span class='role-badge'>Current: {st.session_state.role.title()}</span>", unsafe_allow_html=True)
    if st.button("🔁 Change role"):
        st.session_state.role = None
        st.rerun()


# ------------------------------------------------------------
# CAREGIVER VIEW
# ------------------------------------------------------------
if st.session_state.role == "caretaker":
    tab_home, tab_rem, tab_people, tab_logs, tab_gps, tab_mbook = st.tabs(
        ["🏠 Home", "⏰ Reminders", "👨‍👩‍👧 People", "📜 Logs", "📍 GPS / Home", "📘 Memory Book"]
    )

    with tab_home:
        _render_due_and_coming(is_caregiver=True, types=("activity", "medicine"), scope="cg_home")

    with tab_rem:
        st.subheader("Add reminder")
        with st.form("add_rem_form", clear_on_submit=True):
            title = st.text_input("Title")
            d = st.date_input("Date", value=now_local().date())

            time_options = [f"{h:02d}:{m:02d}" for h in range(24) for m in range(0, 60, 5)]
            now_dt = now_local()
            default_time_str = f"{now_dt.hour:02d}:{(now_dt.minute // 5) * 5:02d}"
            if default_time_str not in time_options:
                default_time_str = "23:55"
            time_str = st.selectbox("Time", options=time_options, index=time_options.index(default_time_str))
            t = dt.time(int(time_str[:2]), int(time_str[3:]))

            img_up = st.file_uploader("Photo", type=["png", "jpg", "jpeg", "webp"])
            aud_up = st.file_uploader("Audio (mp3/wav/m4a)", type=["mp3", "wav", "m4a"])
            steps_txt = st.text_area("Steps (one per line)")
            rtype = st.selectbox("Reminder type", ["activity", "medicine"])
            rpt = st.selectbox("Repeat", ["once", "daily", "sr"], index=1)
            ok = st.form_submit_button("➕ Add")
            if ok:
                if not title:
                    st.error("Title required")
                else:
                    when_dt = dt.datetime.combine(d, t, tzinfo=IST) if IST else dt.datetime.combine(d, t)
                    if img_up:
                        img_path = save_upload_to(
                            img_up, MEDICINE_IMG_DIR if rtype == "medicine" else ACTIVITY_IMG_DIR
                        )
                    else:
                        img_path = ""
                    aud_path = save_upload_to(aud_up, AUDIO_DIR) if aud_up else ""
                    steps = [s.strip() for s in steps_txt.splitlines() if s.strip()]
                    add_reminder(data, title, when_dt, img_path, aud_path, steps, rpt, reminder_type=rtype)
                    st.success("Reminder added")

        st.divider()
        st.subheader("All reminders (latest first)")
        all_rems = sorted(
            list(data["reminders"].values()),
            key=lambda x: parse_iso(x.get("when_iso", "1970-01-01T00:00:00")),
            reverse=True,
        )
        for i, r in enumerate(all_rems, 1):
            with st.expander(f"{i}. {r['title']} — {human_time(r['next_due_iso'])}"):
                st.json(r)

    with tab_people:
        st.subheader("People for Memory Book / Quiz")
        ensure_people_from_memory_book(data)
        ppl = list(data["people"].values())
        if not ppl:
            st.info("No people added yet. Use the Memory Book tab to add photos.")
        else:
            ppl_sorted = sorted(
                ppl,
                key=lambda p: _file_mtime_or_zero(Path(resolve_path(p.get("image_path", "")))) * -1,
            )
            cols = st.columns(2)
            for i, p in enumerate(ppl_sorted):
                with cols[i % 2]:
                    st.markdown('<div class="alzy-card">', unsafe_allow_html=True)
                    _render_thumb(p.get("image_path", ""))
                    st.markdown(f"**{p['name']}** — {p.get('relation', 'Family')}")
                    st.markdown("</div>", unsafe_allow_html=True)

    with tab_logs:
        st.subheader("📜 Medicine / action logs")
        logs = sorted(data.get("logs", []), key=lambda x: x["time"], reverse=True)
        if not logs:
            st.info("No logs yet.")
        else:
            for lg in logs:
                st.write(f"{human_time(lg['time'])} — {lg['title']} — {lg['action']} — ({lg['type']})")

    with tab_gps:
        st.subheader("📍 GPS / Home (IST time shown across app)")

        cur = data.get("gps", {})
        cur_home = cur.get("home_address", "")
        cur_lat = cur.get("lat", "")
        cur_lon = cur.get("lon", "")

        st.write(f"Current saved home: **{cur_home or 'Not set'}**")
        st.write(f"Lat/Lon: {cur_lat or '-'}, {cur_lon or '-'}")

        components.html(
            """
            <button onclick="getGPS()" style="padding:8px 14px;border:none;background:#0ea5e9;color:white;border-radius:8px;cursor:pointer;">
              📍 Get current location
            </button>
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
            height=70,
        )

        new_lat = get_qp("lat")
        new_lon = get_qp("lon")
        if new_lat and new_lon:
            data["gps"]["lat"] = new_lat
            data["gps"]["lon"] = new_lon
            save_runtime_data(data)
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
                save_runtime_data(data)
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
            if cur_lat and cur_lon:
                url = _build_dir_url(dest_lat=cur_lat, dest_lon=cur_lon, mode="driving")
                _open_external(url)
            else:
                st.error("Please save Home first.")

        st.divider()
        st.subheader("⭐ Favorite Places (POIs)")

        poi_keys = [
            ("family_doctor", "Family Doctor"),
            ("daily_market", "Daily Market"),
            ("hospital", "Hospital"),
            ("mothers_home", "Mother's Home"),
        ]
        pois = data["gps"].get("pois", {})

        with st.form("save_pois_form", clear_on_submit=False):
            cols_hdr = st.columns([2, 1, 1])
            with cols_hdr[0]:
                st.markdown("**Place name**")
            with cols_hdr[1]:
                st.markdown("**Latitude**")
            with cols_hdr[2]:
                st.markdown("**Longitude**")

            new_pois = {}
            for key, label in poi_keys:
                curp = pois.get(key, {"name": label, "lat": "", "lon": ""})
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1:
                    name_val = st.text_input(
                        f"{label} name",
                        value=curp.get("name", ""),
                        key=f"poi_name_{key}",
                    )
                with c2:
                    lat_val = st.text_input(
                        f"{label} lat",
                        value=str(curp.get("lat", "")),
                        key=f"poi_lat_{key}",
                    )
                with c3:
                    lon_val = st.text_input(
                        f"{label} lon",
                        value=str(curp.get("lon", "")),
                        key=f"poi_lon_{key}",
                    )
                new_pois[key] = {
                    "name": (name_val or label).strip(),
                    "lat": lat_val.strip(),
                    "lon": lon_val.strip(),
                }

            if st.form_submit_button("💾 Save POIs"):
                data["gps"]["pois"] = new_pois
                save_runtime_data(data)
                st.success("Favorite places saved.")

        st.caption("Quick test: open driving directions Home → selected place")
        home_lat = data["gps"].get("lat") or ""
        home_lon = data["gps"].get("lon") or ""
        cA, cB, cC, cD = st.columns(4)
        for (key, label), col in zip(poi_keys, [cA, cB, cC, cD]):
            with col:
                if st.button(f"➡️ {label}", key=f"poi_go_{key}"):
                    poi = data["gps"]["pois"].get(key, {})
                    p_lat = poi.get("lat") or ""
                    p_lon = poi.get("lon") or ""
                    try:
                        if (not p_lat or not p_lon) and home_lat and home_lon:
                            hlat = float(home_lat)
                            hlon = float(home_lon)
                            off_lat, off_lon = _offset_point(hlat, hlon, km_north=3.5, km_east=3.5)
                            p_lat, p_lon = f"{off_lat:.6f}", f"{off_lon:.6f}"
                        url = _build_dir_url(
                            origin_lat=home_lat if home_lat else None,
                            origin_lon=home_lon if home_lon else None,
                            dest_lat=p_lat if p_lat else None,
                            dest_lon=p_lon if p_lon else None,
                            mode="driving",
                        )
                        _open_external(url)
                    except Exception:
                        st.error("Invalid coordinates. Please check Home and POI lat/lon.")

    with tab_mbook:
        st.subheader("📘 Memory Book")
        st.caption(f"Runtime folder: {MBOOK_IMG_DIR.resolve()}")
        with st.form("add_person_form", clear_on_submit=True):
            name = st.text_input("Name")
            rel = st.text_input("Relation", value="Family")
            img_up = st.file_uploader("Photo", type=["png", "jpg", "jpeg", "webp"])
            ok = st.form_submit_button("💾 Save to Memory Book")
            if ok:
                if not img_up:
                    st.error("Please select a photo.")
                else:
                    pth = save_upload_to(img_up, MBOOK_IMG_DIR, name_hint=(name or rel or "Family"))
                    display_name = (
                        name
                        or Path(pth)
                        .stem.split("-", 1)[0]
                        .replace("-", " ")
                        .replace("_", " ")
                        .title()
                    ).strip()
                    display_rel = (rel or "Family").strip() or "Family"
                    add_person(data, display_name, display_rel, pth)
                    data.setdefault("memory_book_images", [])
                    if pth not in data["memory_book_images"]:
                        data["memory_book_images"].insert(0, pth)
                    save_runtime_data(data)
                    st.success(f"Saved '{display_name}' to Memory Book.")

        _display_memory_book_gallery()

# ------------------------------------------------------------
# PATIENT VIEW
# ------------------------------------------------------------
else:
    tab_act, tab_med, tab_quiz, tab_mbook, tab_gps, tab_ai = st.tabs(
        ["🧑‍🦽 Activity", "💊 Medicine", "🧩 Quiz", "📘 Memory Book", "📍 GPS", "🤖 AI Chatbot"]
    )

    with tab_act:
        _render_due_and_coming(is_caregiver=False, types=("activity",), scope="pt_act")

    with tab_med:
        _render_due_and_coming(is_caregiver=False, types=("medicine",), scope="pt_med")

    with tab_quiz:
        _render_quiz_simple()

    with tab_mbook:
        st.subheader("📘 Memory Book")
        _display_memory_book_gallery()

    with tab_gps:
        st.subheader("📍 GPS (Patient)")

        gps = data.get("gps", {})
        home_addr = gps.get("home_address", "")
        home_lat = gps.get("lat") or ""
        home_lon = gps.get("lon") or ""
        pois = gps.get("pois", {})

        st.write(f"Home: **{home_addr or 'Not set'}**")
        st.caption("Tap a button to open Google Maps with directions.")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("🏠 Back to Home"):
                url = _build_dir_url(
                    origin_lat=None,
                    origin_lon=None,
                    dest_lat=home_lat if home_lat else None,
                    dest_lon=home_lon if home_lon else None,
                    mode="driving",
                )
                if "destination=" in url:
                    _open_external(url)
                else:
                    st.error("Home is not set. Ask the caregiver to save Home in GPS / Home tab.")

        row = st.columns(4)
        for (key, label), col in zip(
            [
                ("family_doctor", "Family Doctor"),
                ("daily_market", "Daily Market"),
                ("hospital", "Hospital"),
                ("mothers_home", "Mother's Home"),
            ],
            row,
        ):
            with col:
                if st.button(label, key=f"pt_go_{key}"):
                    poi = pois.get(key, {})
                    p_lat = poi.get("lat") or ""
                    p_lon = poi.get("lon") or ""
                    try:
                        if (not p_lat or not p_lon) and home_lat and home_lon:
                            hlat = float(home_lat)
                            hlon = float(home_lon)
                            off_lat, off_lon = _offset_point(hlat, hlon, km_north=3.5, km_east=3.5)
                            p_lat, p_lon = f"{off_lat:.6f}", f"{off_lon:.6f}"
                        url = _build_dir_url(
                            origin_lat=home_lat if home_lat else None,
                            origin_lon=home_lon if home_lon else None,
                            dest_lat=p_lat if p_lat else None,
                            dest_lon=p_lon if p_lon else None,
                            mode="driving",
                        )
                        _open_external(url)
                    except Exception:
                        st.error("Please ask the caregiver to set this place in GPS / Home tab.")

    # ---------------- AI Chatbot (Patient) ----------------
    with tab_ai:
        st.subheader("🤖 AI Chatbot")
        st.caption("Speak (mic) or type. Short, friendly answers.")

        # Clear previous button
        col_clear, _ = st.columns([1, 3])
        with col_clear:
            if st.button("🧹 Clear previous"):
                st.session_state.patient_ai_chat = [
                    {
                        "role": "assistant",
                        "content": "Hello 👋 I'm your Memory Assistant. How can I help you today?",
                    }
                ]
                st.rerun()

        # Show chat history
        for msg in st.session_state.patient_ai_chat:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Previous questions (last 5 user messages)
        past_questions = [m["content"] for m in st.session_state.patient_ai_chat if m["role"] == "user"]
        if past_questions:
            st.markdown("**Previous questions:**")
            for q in reversed(past_questions[-5:]):
                st.markdown(f"- {q}")

        # Speak button – just listens and shows what it heard (no URL navigation)
        components.html(
            """
            <div style="margin:8px 0 12px 0;">
              <button id="stt-btn"
                style="padding:6px 14px;border:none;background:#f97316;color:white;border-radius:8px;cursor:pointer;">
                🎤 Speak
              </button>
              <span id="stt-status"
                style="margin-left:8px;font-size:12px;color:#fff;"></span>
            </div>

            <script>
            (function(){
              const btn    = document.getElementById("stt-btn");
              const status = document.getElementById("stt-status");
              if (!btn) return;

              btn.addEventListener("click", function(){
                status.textContent = "";

                const isLocal =
                  (location.hostname === "localhost" || location.hostname === "127.0.0.1");
                if (!window.isSecureContext && !isLocal){
                  status.textContent = "❌ Mic blocked: use https or localhost.";
                  return;
                }

                const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
                if (!SR){
                  status.textContent = "❌ SpeechRecognition not supported.";
                  return;
                }

                const rec = new SR();
                rec.lang = "en-US";

                rec.onstart = function(){
                  status.textContent = "Listening...";
                };
                rec.onerror = function(e){
                  status.textContent = "❌ " + (e.error || "Error");
                };
                rec.onend = function(){
                  if (status.textContent === "Listening...") {
                    status.textContent = "";
                  }
                };

                rec.onresult = function(e){
                  const text = e.results[0][0].transcript;
                  // Just show what was heard; user can type it below
                  status.textContent = "Heard: " + text;
                };

                rec.start();
              });
            })();
            </script>
            """,
            height=110,
        )

        # Only typed input is used as user message (chat_input works normally)
        user_input = st.chat_input("Type your message")
        last_reply: Optional[str] = None

        if user_input:
            # Log user message
            st.session_state.patient_ai_chat.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # Local date/time answers first (IST-aware)
            local_ans = maybe_local_answer(user_input)
            if local_ans:
                reply_text = local_ans
            else:
                reply_text = "I couldn't reach AI right now, but I'm here with you."
                api_key = OPENAI_API_KEY

                today_str = now_local().strftime("%d %B %Y")
                system_msg = (
                    "You are a gentle assistant for an Alzheimer's patient. "
                    "Reply in 2–3 short, simple sentences. Be friendly. "
                    f"Today's date (IST) is {today_str}. If the user asks about today's date or time, "
                    f"use {today_str} as the current date."
                )

                if api_key:
                    try:
                        url = "https://api.openai.com/v1/chat/completions"
                        headers = {
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                        }
                        msgs = [{"role": "system", "content": system_msg}] + st.session_state.patient_ai_chat[-6:]
                        payload = {
                            "model": "gpt-4o-mini",
                            "messages": msgs,
                            "max_tokens": 150,
                            "temperature": 0.6,
                        }
                        resp = requests.post(url, headers=headers, json=payload, timeout=15)
                        if resp.status_code == 200:
                            j = resp.json()
                            reply_text = (
                                j.get("choices", [{}])[0]
                                 .get("message", {})
                                 .get("content", "I’m here with you.")
                            )
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
            # No new input – use last assistant message for "Read aloud"
            for m in reversed(st.session_state.patient_ai_chat):
                if m["role"] == "assistant":
                    last_reply = m["content"]
                    break

        # Read aloud last answer
        if last_reply:
            safe_last = json.dumps(last_reply)
            components.html(
                f"""
                <button id="tts-btn"
                  style="margin-top:10px;padding:6px 14px;border:none;background:#0ea5e9;color:white;border-radius:8px;cursor:pointer;">
                  🔊 Read aloud last answer
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
                    const u = new SpeechSynthesisUtterance({safe_last});
                    u.lang = "en-US";
                    u.rate = 0.95;
                    window.speechSynthesis.cancel();
                    window.speechSynthesis.speak(u);
                  }});
                }})();
                </script>
                """,
                height=60,
            )
