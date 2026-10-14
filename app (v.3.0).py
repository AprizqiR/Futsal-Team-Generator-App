import streamlit as st
import pandas as pd
import random
import io
import hmac
import json
import os
from html import escape as esc
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="⚽ Futsal Tim Generator",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# MODERN FUTSAL THEME
# ==========================================
# Background foto memakai URL publik agar aplikasi tetap satu file.
# Jika ingin hosting offline, simpan gambar lokal lalu ubah background-image di bawah.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root { --futsal-blue:#1388ff; --futsal-cyan:#20d9e8; --futsal-navy:#06162b; --futsal-green:#20c997; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
  background: linear-gradient(135deg, rgba(3,12,27,.96), rgba(5,31,57,.91)),
    url('https://images.unsplash.com/photo-1574629810360-7efbbe195018?auto=format&fit=crop&w=2000&q=85') center top / cover fixed;
  color: #f4f8ff;
}
[data-testid="stHeader"] { background: rgba(3,12,27,.72); }
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #06162b 0%, #08294a 100%);
  border-right: 1px solid rgba(32,217,232,.22);
}
[data-testid="stSidebar"] * { color: #eaf4ff; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1500px; }
h1, h2, h3 { letter-spacing: -.035em; }
h1 { color:#fff; font-weight:800 !important; }
h2, h3 { color:#f3f8ff; }
p, label, [data-testid="stCaptionContainer"] { color: #c8d8eb; }
[data-testid="stMetric"], [data-testid="stVerticalBlockBorderWrapper"] {
  background: rgba(8,29,53,.78); border: 1px solid rgba(85,166,255,.25);
  border-radius: 16px; padding: 12px 16px;
}
[data-testid="stMetricValue"] { color: #20d9e8; font-weight:800; }
.stButton > button, [data-testid="stDownloadButton"] button,
.stFormSubmitButton > button {
  border: 0; border-radius: 12px; font-weight:700;
  background: linear-gradient(110deg,#087cff,#11b8d7); color:#fff;
  box-shadow: 0 6px 18px rgba(0,130,255,.18); transition: transform .18s, filter .18s;
}
.stButton > button:hover, [data-testid="stDownloadButton"] button:hover,
.stFormSubmitButton > button:hover { transform: translateY(-2px); filter:brightness(1.08); color:#fff; }
[data-baseweb="select"] > div, [data-baseweb="input"] > div,
[data-baseweb="textarea"] > div { background:rgba(7,25,47,.92); border-color:#28527b; border-radius:10px; }
[data-testid="stDataFrame"] { border:1px solid rgba(85,166,255,.28); border-radius:12px; overflow:hidden; }
hr { border-color:rgba(91,160,220,.24); }
.futsal-hero {
  position:relative; overflow:hidden; padding:30px 32px; margin:0 0 22px 0;
  border-radius:22px; border:1px solid rgba(68,190,255,.35);
  background:linear-gradient(100deg,rgba(3,15,32,.97) 0%,rgba(5,35,65,.88) 55%,rgba(6,55,86,.45) 100%),
  url('https://images.unsplash.com/photo-1574629810360-7efbbe195018?auto=format&fit=crop&w=1600&q=85') center 55%/cover;
  box-shadow:0 18px 55px rgba(0,0,0,.24);
}
.futsal-kicker { color:#20d9e8; text-transform:uppercase; letter-spacing:.19em; font-size:.76rem; font-weight:800; }
.futsal-hero h1 { font-size:clamp(2rem,4vw,3.2rem); margin:.3rem 0 .5rem 0; line-height:1.08; }
.futsal-hero p { max-width:720px; font-size:1rem; margin:0; color:#d5e6f7; }
.futsal-pill { display:inline-block; margin-top:18px; padding:7px 12px; border-radius:999px;
  background:rgba(32,217,232,.12); border:1px solid rgba(32,217,232,.3); color:#b8f8ff; font-size:.8rem; font-weight:700; }
@media (max-width: 700px) { .futsal-hero { padding:22px 18px; } }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATABASE & KONSTANTA
# ==========================================
DATABASE_PLAYERS = [
    {"no": 1, "nama": "Aprizqi R", "alias": "", "status": "Active", "roles": ["GK", "A", "F", "P"], "rating": 10},
    {"no": 2, "nama": "Arby R", "alias": "", "status": "Active", "roles": ["GK", "A", "F", "P"], "rating": 10},
    {"no": 3, "nama": "Ibrahim", "alias": "", "status": "Active", "roles": ["A", "F", "P"], "rating": 9},
    {"no": 4, "nama": "Fadhli D. Ikram", "alias": "", "status": "Active", "roles": ["GK", "A", "F", "P"], "rating": 10},
    {"no": 5, "nama": "Geraldo H.", "alias": "", "status": "Active", "roles": ["GK", "A", "F"], "rating": 8},
    {"no": 6, "nama": "Rafif Kusuma", "alias": "", "status": "Active", "roles": ["A", "F", "P"], "rating": 7},
    {"no": 7, "nama": "Ade Suryadana", "alias": "", "status": "Active", "roles": ["GK", "A", "F", "P"], "rating": 10},
    {"no": 8, "nama": "Jehua Kusuma Dewa", "alias": "", "status": "Active", "roles": ["A", "F", "P"], "rating": 7},
    {"no": 9, "nama": "Hanz Seca", "alias": "", "status": "Active", "roles": ["GK"], "rating": 6},
    {"no": 10, "nama": "Martin Koko", "alias": "", "status": "Active", "roles": ["GK", "A", "F", "P"], "rating": 10},
    {"no": 11, "nama": "M. Zidan G.", "alias": "", "status": "Active", "roles": ["GK", "A", "F", "P"], "rating": 10},
    {"no": 12, "nama": "R. Hafis M.", "alias": "", "status": "Active", "roles": ["GK", "A", "F", "P"], "rating": 10},
    {"no": 13, "nama": "Musyaffa C. M.", "alias": "", "status": "Active", "roles": ["GK", "A", "F"], "rating": 8},
    {"no": 14, "nama": "Yadhit P.", "alias": "", "status": "Active", "roles": ["GK", "A", "F"], "rating": 8},
    {"no": 15, "nama": "M. Ardhana W. N.", "alias": "", "status": "Active", "roles": ["GK"], "rating": 6},
    {"no": 16, "nama": "Farhan I. A.", "alias": "", "status": "Active", "roles": ["A", "F", "P"], "rating": 7},
    {"no": 17, "nama": "Naufal Y.", "alias": "", "status": "Active", "roles": ["A", "F", "P"], "rating": 7},
    {"no": 18, "nama": "Aldo S.", "alias": "", "status": "Active", "roles": ["GK", "A", "F", "P"], "rating": 10},
    {"no": 19, "nama": "M. Daffa A.", "alias": "", "status": "Active", "roles": ["A", "F", "P"], "rating": 9},
    {"no": 20, "nama": "Mahardhyka P.", "alias": "", "status": "Active", "roles": ["A", "F", "P"], "rating": 9},
    {"no": 21, "nama": "Rafi M. A.", "alias": "", "status": "Active", "roles": ["A", "F", "P"], "rating": 8},
    {"no": 22, "nama": "Teguh A. R.", "alias": "", "status": "Active", "roles": ["GK", "A", "F"], "rating": 8},
    {"no": 23, "nama": "Nur Sahrul", "alias": "", "status": "Active", "roles": ["A", "F", "P"], "rating": 9},
]

SAMPLE_PLAYERS = [p["nama"] for p in DATABASE_PLAYERS if p["status"] == "Active"]
DEFAULT_ROLES = {p["nama"]: list(p["roles"]) for p in DATABASE_PLAYERS}
DEFAULT_RATINGS = {p["nama"]: p["rating"] for p in DATABASE_PLAYERS}
ROLE_KEYS = ["GK", "A", "F", "P"]

roles_data = {
    "GK": {"nama": "Kiper", "emoji": "🧤", "tugas": "Menjaga gawang dari kebobolan, membaca arah bola, dan mengawali serangan balik."},
    "A": {"nama": "Anchor", "emoji": "⚓", "tugas": "Jangkar di lini belakang, memotong serangan lawan, mengatur ritme build-up."},
    "F": {"nama": "Flank", "emoji": "🪽", "tugas": "Beroperasi di sisi lapangan, menghubungkan pertahanan dan penyerangan."},
    "P": {"nama": "Pivot", "emoji": "🔥", "tugas": "Ujung tombak di depan, hold-up play, membuka ruang, dan mencetak gol."},
}

formations = {
    "Diamond (1-2-1)": {
        "pola": "1 Anchor (belakang) • 2 Flank (kanan & kiri) • 1 Pivot (depan)",
        "karakter": "Sangat seimbang antara bertahan dan menyerang. Formasi paling populer yang mengandalkan lebar lapangan melalui flank dan penguasaan bola via pivot.",
        "sketsa": "[Pivot] [Flank] [Flank] [Anchor]",
        "positions": [{"label": "GK", "x": 8, "y": 50}, {"label": "A", "x": 28, "y": 50}, {"label": "F", "x": 52, "y": 22}, {"label": "F", "x": 52, "y": 78}, {"label": "P", "x": 78, "y": 50}],
    },
    "Pyramid / Wall (2-1-1)": {
        "pola": "2 Defender (sejajar di belakang) • 1 Midfielder (tengah) • 1 Pivot (depan)",
        "karakter": "Fokus defensif kokoh yang sangat rapat di area belakang. Efektif untuk meredam tim agresif dan mengincar counter attack cepat.",
        "sketsa": "[Pivot] [Midfielder] [Def] [Def]",
        "positions": [{"label": "GK", "x": 8, "y": 50}, {"label": "A", "x": 28, "y": 32}, {"label": "A", "x": 28, "y": 68}, {"label": "F", "x": 55, "y": 50}, {"label": "P", "x": 80, "y": 50}],
    },
    "The Box / Square (2-2)": {
        "pola": "2 Pemain Belakang (sejajar) • 2 Pemain Depan (sejajar)",
        "karakter": "Fleksibel dan konvensional. Membagi lapangan menjadi dua area simetris. Mudah dipahami pemula namun butuh komunikasi intens.",
        "sketsa": "[Pivot] [Pivot] [Def] [Def]",
        "positions": [{"label": "GK", "x": 8, "y": 50}, {"label": "A", "x": 32, "y": 30}, {"label": "A", "x": 32, "y": 70}, {"label": "P", "x": 72, "y": 30}, {"label": "P", "x": 72, "y": 70}],
    },
    "Formasi Y (1-1-2)": {
        "pola": "1 Anchor (belakang) • 1 Midfielder (tengah) • 2 Pivot/Striker (depan sejajar)",
        "karakter": "Sangat agresif (offensive). Dua penyerang di lini depan untuk menekan pertahanan lawan sejak dini (high pressing).",
        "sketsa": "[Pivot] [Pivot] [Midfielder] [Anchor]",
        "positions": [{"label": "GK", "x": 8, "y": 50}, {"label": "A", "x": 28, "y": 50}, {"label": "F", "x": 52, "y": 50}, {"label": "P", "x": 78, "y": 30}, {"label": "P", "x": 78, "y": 70}],
    },
    "Park the Bus (3-1)": {
        "pola": "3 Defender (sejajar / berdekatan di belakang) • 1 Pivot (depan)",
        "karakter": "Defensif total. Dipakai saat ingin mempertahankan keunggulan skor di menit-menit akhir.",
        "sketsa": "[Pivot] [Def][Def][Def]",
        "positions": [{"label": "GK", "x": 8, "y": 50}, {"label": "A", "x": 30, "y": 22}, {"label": "A", "x": 30, "y": 50}, {"label": "A", "x": 30, "y": 78}, {"label": "P", "x": 72, "y": 50}],
    },
    "Total / Flat (4-0)": {
        "pola": "4 Pemain Sejajar (bergerak dinamis tanpa posisi permanen)",
        "karakter": "Rotasi dinamis tanpa pivot murni. Semua pemain wajib bisa bertahan dan menyerang sama baiknya.",
        "sketsa": "[P1] [P2] [P3] [P4] (Sejajar dinamis)",
        "positions": [{"label": "GK", "x": 8, "y": 50}, {"label": "F", "x": 48, "y": 18}, {"label": "F", "x": 48, "y": 40}, {"label": "F", "x": 48, "y": 60}, {"label": "F", "x": 48, "y": 82}],
    },
}

UNIFORM_OPTIONS = ["Biru", "Putih", "Merah", "Kuning", "Ungu", "Hitam", "Hijau"]
COLOR_MAP = {"Biru": "#1976d2", "Putih": "#ffffff", "Merah": "#d32f2f", "Kuning": "#fbc02d", "Ungu": "#7b1fa2", "Hitam": "#212121", "Hijau": "#388e3c", "Abu-abu": "#757575"}
DARK_UNIFORMS = ["Hitam", "Biru", "Merah", "Ungu", "Hijau"]
MAX_TEAMS = 6
TABLE_HEADERS = ["Pemain", "GK", "A", "F", "P", "Rating"]

# ==========================================
# HELPER, DATABASE PEMAIN & STATE
# ==========================================
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "players_db.json")
MAX_LOGIN_ATTEMPTS = 5
DEFAULT_ADMIN_PASSWORD = "BIAFUTSAL"
AVATAR_COLORS = ["#1976d2", "#388e3c", "#d32f2f", "#7b1fa2", "#f57c00",
                 "#00838f", "#5d4037", "#455a64", "#c2185b", "#512da8"]


def _clamp_rating(v, default=5):
    try:
        v = int(round(float(v)))
    except (TypeError, ValueError, OverflowError):
        return default
    return max(1, min(10, v))


def _b(v):
    """Bool aman untuk nilai dari data_editor (NaN/None -> False)."""
    try:
        return bool(v) if v == v else False
    except Exception:
        return False


def flat_html(s):
    """Ratakan HTML ke satu baris. Baris berindentasi >=4 spasi dianggap code block oleh markdown."""
    return " ".join(line.strip() for line in s.splitlines() if line.strip())


def seed_db():
    return [
        {"nama": p["nama"], "roles": list(p["roles"]), "rating": p["rating"]}
        for p in DATABASE_PLAYERS if p["status"] == "Active"
    ]


def load_db():
    """Baca database pemain dari players_db.json; jika tidak ada/rusak pakai data awal."""
    try:
        with open(DB_FILE, encoding="utf-8") as f:
            data = json.load(f)
        clean, seen = [], set()
        for d in data:
            nama = str(d.get("nama", "")).strip()
            if not nama or nama in seen:
                continue
            seen.add(nama)
            roles = [r for r in ROLE_KEYS if r in d.get("roles", [])] or ["A", "F", "P"]
            clean.append({"nama": nama, "roles": roles, "rating": _clamp_rating(d.get("rating", 5))})
        if clean:
            return clean
    except (OSError, ValueError, AttributeError, TypeError):
        pass
    return seed_db()


def save_db(db):
    """Simpan ke file. Return True jika berhasil (di hosting bisa read-only / sementara)."""
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


def get_admin_password():
    try:
        pw = st.secrets["ADMIN_PASSWORD"]
    except Exception:
        pw = None
    return str(pw) if pw else (os.environ.get("ADMIN_PASSWORD") or DEFAULT_ADMIN_PASSWORD)


def using_default_password():
    return get_admin_password() == DEFAULT_ADMIN_PASSWORD


# --- state ---
_defaults = {
    "db": None,
    "db_ver": 0,
    "extras": [],
    "extra_info": {},        # {nama: {"roles": [...], "rating": n}} untuk pemain luar
    "rules": [],
    "selected_players": None,
    "generated_result": None,
    "num_teams": 2,
    "team_uniforms": [],
    "payments": {},
    "is_admin": False,
    "login_open": False,
    "login_attempts": 0,
    "step2_mode": "view",
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v
if st.session_state.db is None:
    st.session_state.db = load_db()
if st.session_state.selected_players is None:
    st.session_state.selected_players = [d["nama"] for d in st.session_state.db][:10]


def master_names():
    return [d["nama"] for d in st.session_state.db]


def defaults_for(name):
    """Role & rating sebuah pemain: database -> pemain luar -> default."""
    for d in st.session_state.db:
        if d["nama"] == name:
            return list(d["roles"]), d["rating"]
    ex = st.session_state.extra_info.get(name)
    if ex:
        return list(ex["roles"]), ex["rating"]
    return ["A", "F", "P"], 5


def initials(name):
    words = [w.strip(".") for w in name.replace("-", " ").split() if w.strip(".")]
    if not words:
        return "?"
    if len(words) == 1:
        return words[0][:2].upper()
    return (words[0][0] + words[1][0]).upper()


def avatar_html(name, size=48):
    color = AVATAR_COLORS[sum(ord(c) for c in name) % len(AVATAR_COLORS)]
    return (
        f"<div style='width:{size}px;height:{size}px;border-radius:50%;background:{color};color:#fff;"
        f"display:flex;align-items:center;justify-content:center;font-weight:700;"
        f"font-size:{int(size * 0.38)}px;flex-shrink:0'>{esc(initials(name))}</div>"
    )


def player_card_html(name, roles, is_extra=False, status="Dipilih"):
    status_color = "#20c997" if status == "Dipilih" else "#94a3b8"
    status_badge = f" <span style='background:{status_color}22;color:{status_color};border:1px solid {status_color}77;padding:2px 7px;border-radius:8px;font-size:10px'>{esc(status)}</span>"
    chips = "".join(
        f"<span title='{esc(roles_data[r]['nama'])}' style='display:inline-block;padding:2px 9px;margin:2px 4px 0 0;"
        f"border-radius:12px;font-size:12px;background:rgba(25,118,210,0.15);border:1px solid rgba(25,118,210,0.35)'>"
        f"{roles_data[r]['emoji']} {r}</span>"
        for r in ROLE_KEYS if r in roles
    )
    badge = (" <span style='background:#ff9800;color:#fff;padding:1px 6px;border-radius:8px;font-size:10px'>LUAR</span>"
             if is_extra else "")
    return (
        "<div style='display:flex;align-items:center;gap:12px;padding:10px 12px;border-radius:12px;"
        "background:rgba(128,128,128,0.08);border:1px solid rgba(128,128,128,0.25)'>"
        f"{avatar_html(name)}"
        f"<div style='min-width:0'><div style='font-weight:600;line-height:1.3'>{esc(name)}{badge}{status_badge}</div>"
        f"<div>{chips}</div></div></div>"
    )


def generate_teams(players, roles, ratings, rules, num_teams, team_uniforms_in, extras):
    players = players[:]
    extras_set = set(extras)
    
    def get_rating(p):
        return ratings.get(p, DEFAULT_RATINGS.get(p, 5))
    
    conflicts = defaultdict(set)
    for p1, p2 in rules:
        conflicts[p1].add(p2)
        conflicts[p2].add(p1)
    
    gks = [p for p in players if "GK" in roles.get(p, [])]
    non_gks = [p for p in players if "GK" not in roles.get(p, [])]
    teams = [[] for _ in range(num_teams)]
    
    def team_total_rating(i):
        return sum(get_rating(p) for p in teams[i])
    def team_size(i):
        return len(teams[i])
    def has_conflict_with_team(player, team_idx):
        return any(t in conflicts.get(player, set()) for t in teams[team_idx])
    def valid_teams_for(player):
        valid = [i for i in range(num_teams) if not has_conflict_with_team(player, i)]
        return valid if valid else list(range(num_teams))
    
    # 1) Assign GK
    gks_sorted = sorted(gks, key=get_rating, reverse=True)
    random.shuffle(gks_sorted)
    gks_sorted = sorted(gks_sorted, key=get_rating, reverse=True)
    for gk in gks_sorted[:num_teams]:
        candidates = valid_teams_for(gk)
        best = min(candidates, key=lambda i: (team_total_rating(i), team_size(i)))
        teams[best].append(gk)
    
    remaining_gks = gks_sorted[num_teams:]
    remaining = non_gks + remaining_gks
    random.shuffle(remaining)
    remaining.sort(key=lambda p: (get_rating(p), p in extras_set), reverse=True)
    
    # 2) Assign remaining
    for player in remaining:
        candidates = valid_teams_for(player)
        def score(i, player=player):
            team_roles = [r for p in teams[i] for r in roles.get(p, [])]
            plist = roles.get(player, [])
            role_need = sum(1 for r in plist if team_roles.count(r) < 2)
            return (team_total_rating(i), team_size(i), -role_need)
        best = min(candidates, key=score)
        teams[best].append(player)
    
    # 3) Micro-balance
    def try_balance_swaps(max_rounds=30):
        for _ in range(max_rounds):
            totals = [team_total_rating(i) for i in range(num_teams)]
            strongest = max(range(num_teams), key=lambda i: totals[i])
            weakest = min(range(num_teams), key=lambda i: totals[i])
            gap = totals[strongest] - totals[weakest]
            if gap <= 2:
                break
            improved = False
            for p_s in list(teams[strongest]):
                if has_conflict_with_team(p_s, weakest):
                    continue
                for p_w in list(teams[weakest]):
                    if has_conflict_with_team(p_w, strongest):
                        continue
                    new_strong = totals[strongest] - get_rating(p_s) + get_rating(p_w)
                    new_weak = totals[weakest] - get_rating(p_w) + get_rating(p_s)
                    if abs(new_strong - new_weak) < gap:
                        teams[strongest].remove(p_s)
                        teams[weakest].remove(p_w)
                        teams[strongest].append(p_w)
                        teams[weakest].append(p_s)
                        improved = True
                        break
                if improved:
                    break
            if not improved:
                break
    try_balance_swaps()
    
    formation_names = list(formations.keys())
    team_formations = {i: random.choice(formation_names) for i in range(num_teams)}
    team_uniforms = {i: team_uniforms_in[i] if i < len(team_uniforms_in) and team_uniforms_in[i] else UNIFORM_OPTIONS[i % len(UNIFORM_OPTIONS)] for i in range(num_teams)}
    
    return teams, team_formations, team_uniforms

def formation_svg(formation_name, width=320, height=200):
    form = formations.get(formation_name, {})
    positions = form.get("positions", [])
    W, H = 400, 250
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {W} {H}" style="border-radius:12px;display:block;margin:8px 0">',
        f'<rect x="0" y="0" width="{W}" height="{H}" rx="14" fill="#c62828"/>',
        f'<rect x="12" y="12" width="{W-24}" height="{H-24}" rx="6" fill="#1565c0"/>',
        f'<circle cx="{W/2}" cy="{H/2}" r="28" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="2"/>',
        f'<circle cx="{W/2}" cy="{H/2}" r="3" fill="rgba(255,255,255,0.8)"/>',
        f'<line x1="{W/2}" y1="12" x2="{W/2}" y2="{H-12}" stroke="rgba(255,255,255,0.6)" stroke-width="2"/>',
        f'<rect x="12" y="{H/2-45}" width="40" height="90" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1.5"/>',
        f'<rect x="{W-52}" y="{H/2-45}" width="40" height="90" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1.5"/>',
        f'<text x="{W/2}" y="32" text-anchor="middle" fill="white" font-size="14" font-weight="bold" font-family="Arial,sans-serif">{formation_name}</text>',
    ]
    for pos in positions:
        px = 12 + (pos["x"] / 100) * (W - 24)
        py = 12 + (pos["y"] / 100) * (H - 24)
        svg.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="14" fill="#c62828" stroke="white" stroke-width="2"/>')
        svg.append(f'<text x="{px:.1f}" y="{py+4:.1f}" text-anchor="middle" fill="white" font-size="10" font-weight="bold" font-family="Arial,sans-serif">{pos["label"]}</text>')
    svg.append("</svg>")
    return " ".join(svg)

def display_teams(teams, team_formations, team_uniforms, roles, ratings, extras):
    extras_set = set(extras)
    def get_rating(p):
        return ratings.get(p, DEFAULT_RATINGS.get(p, 5))
    
    html = "<h3 style='color:#1565c0'>🏆 HASIL PEMBAGIAN TIM</h3><hr>"
    totals = []
    for i, team in enumerate(teams):
        uniform = team_uniforms[i]
        formation = team_formations[i]
        form_info = formations[formation]
        team_rating = sum(get_rating(p) for p in team)
        totals.append(team_rating)
        pitch = formation_svg(formation)
        bg = COLOR_MAP.get(uniform, "#757575")
        txt = "white" if uniform in DARK_UNIFORMS else "black"
        
        html += f"""
        <div style='border:3px solid {bg};border-radius:12px;padding:15px;margin:12px 0;background:{bg}18'>
            <h3 style='color:{bg};margin:0 0 8px 0'>
                🏅 TEAM {i+1}
                <span style='background:{bg};color:{txt};padding:4px 14px;border-radius:20px;font-size:13px;margin-left:10px;border:1px solid #ccc'>{uniform}</span>
                <span style='background:#37474f;color:white;padding:4px 12px;border-radius:20px;font-size:13px;margin-left:8px'>Σ Rating: {team_rating}</span>
            </h3>
            <p style='margin:4px 0'><b>📐 Formasi:</b> {formation}</p>
            <p style='margin:4px 0'><i>{form_info['pola']}</i></p>
            <p style='margin:4px 0;font-size:13px;color:#555'><b>Karakter:</b> {form_info['karakter']}</p>
            <p style='margin:4px 0;font-family:monospace;font-size:12px;color:#666'>{form_info.get('sketsa','')}</p>
            <div style='margin:8px 0'>{pitch}</div>
            <table border='1' cellpadding='7' style='border-collapse:collapse;width:100%;margin-top:8px'>
                <tr style='background:{bg};color:{txt}'>
                    <th style='width:40px'>No</th><th>Nama Pemain</th><th>Role</th>
                </tr>
        """
        for j, player in enumerate(team, 1):
            pr = roles.get(player, [])
            role_str = ", ".join(f"{r} ({roles_data[r]['nama']})" for r in pr) if pr else "-"
            badge = " <small style='background:#ff9800;color:#fff;padding:1px 5px;border-radius:6px'>LUAR</small>" if player in extras_set else ""
            html += f"<tr><td style='text-align:center'>{j}</td><td><b>{esc(player)}</b>{badge}</td><td>{role_str}</td></tr>"
        html += "</table></div>"
    
    if totals:
        mx, mn = max(totals), min(totals)
        gap = mx - mn
        color = "#2e7d32" if gap <= 3 else ("#f57c00" if gap <= 6 else "#c62828")
        status = " ✅ Imbang" if gap <= 3 else (" ⚠️ Cukup imbang" if gap <= 6 else " ❌ Kurang imbang — coba Generate ulang")
        summary = " &nbsp;|&nbsp; ".join(f"Team {i+1}: <b>{t}</b>" for i, t in enumerate(totals))
        html += f"""
        <div style='margin-top:16px;padding:12px 16px;border-radius:10px;background:#f5f5f5;border-left:5px solid {color}'>
            <b>⚖️ Keseimbangan Rating Tim:</b> {summary} &nbsp;→&nbsp; Selisih: <b style='color:{color}'>{gap}</b>{status}
        </div>
        """
    return flat_html(html)

def _load_font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()

def render_teams_png(teams, team_formations, team_uniforms, roles_map, ratings, extras):
    """Mengembalikan PNG dalam bentuk bytes."""
    extras_set = set(extras)
    
    def get_rating(p):
        return ratings.get(p, DEFAULT_RATINGS.get(p, 5))
    
    def draw_formation_pitch(draw, x, y, w, h, formation_name):
        form = formations.get(formation_name, {})
        positions = form.get("positions", [])
        draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill="#c62828")
        pad = 8
        px0, py0 = x + pad, y + pad
        pw, ph = w - 2 * pad, h - 2 * pad
        draw.rounded_rectangle([px0, py0, px0 + pw, py0 + ph], radius=5, fill="#1565c0")
        cx, cy = px0 + pw // 2, py0 + ph // 2
        draw.line([(cx, py0), (cx, py0 + ph)], fill="#8fb3e0", width=2)
        r = max(10, min(pw, ph) // 7)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline="#b9d0ee", width=2)
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill="white")
        box_w, box_h = max(14, pw // 10), max(28, ph // 2)
        draw.rectangle([px0, cy - box_h // 2, px0 + box_w, cy + box_h // 2], outline="#8fb3e0", width=1)
        draw.rectangle([px0 + pw - box_w, cy - box_h // 2, px0 + pw, cy + box_h // 2], outline="#8fb3e0", width=1)
        gw, gh = 5, max(12, ph // 5)
        draw.rectangle([x + 2, cy - gh // 2, x + 2 + gw, cy + gh // 2], outline="white", width=2)
        draw.rectangle([x + w - 2 - gw, cy - gh // 2, x + w - 2, cy + gh // 2], outline="white", width=2)
        title_font = _load_font(11, bold=True)
        title = formation_name if len(formation_name) <= 22 else formation_name[:20] + ".."
        try:
            bbox = draw.textbbox((0, 0), title, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = len(title) * 6
        draw.text((cx - tw // 2, py0 + 4), title, fill="white", font=title_font)
        dot_r = max(8, min(pw, ph) // 14)
        label_font = _load_font(9, bold=True)
        for pos in positions:
            dx = px0 + int(pos["x"] / 100 * pw)
            dy = py0 + int(pos["y"] / 100 * ph)
            draw.ellipse([dx - dot_r, dy - dot_r, dx + dot_r, dy + dot_r], fill="#c62828", outline="white", width=2)
            lab = pos["label"]
            try:
                bb = draw.textbbox((0, 0), lab, font=label_font)
                lw = bb[2] - bb[0]
            except Exception:
                lw = len(lab) * 5
            draw.text((dx - lw // 2, dy - 5), lab, fill="white", font=label_font)

    margin, card_pad = 24, 16
    col_w, row_h, pitch_h = 540, 28, 150
    pitch_w = col_w - 28
    header_block = 52 + 40 + pitch_h + 12
    gap = 20
    card_heights = [header_block + (len(t) + 1) * row_h + card_pad + 8 for t in teams]
    n = len(teams)
    cols = 1 if n == 1 else 2
    rows_cards = (n + cols - 1) // cols
    row_heights = []
    for r in range(rows_cards):
        hs = [card_heights[r * cols + c] for c in range(cols) if r * cols + c < n]
        row_heights.append(max(hs) if hs else 0)
    
    top_banner, balance_h = 70, 50
    img_w = margin * 2 + cols * col_w + (cols - 1) * gap
    img_h = margin + top_banner + sum(row_heights) + (rows_cards - 1) * gap + balance_h + margin
    img = Image.new("RGB", (img_w, img_h), "#f5f7fa")
    draw = ImageDraw.Draw(img)
    
    font_title = _load_font(26, bold=True)
    font_h = _load_font(18, bold=True)
    font_sub = _load_font(13)
    font_row = _load_font(13)
    font_row_b = _load_font(13, bold=True)
    font_small = _load_font(11)
    
    draw.rectangle([0, 0, img_w, top_banner], fill="#0d47a1")
    draw.text((margin, 18), "HASIL PEMBAGIAN TIM FUTSAL", fill="white", font=font_title)
    
    totals = []
    y_base = margin + top_banner - 8
    for idx, team in enumerate(teams):
        r, c = divmod(idx, cols)
        x0 = margin + c * (col_w + gap)
        y0 = y_base + sum(row_heights[:r]) + r * gap
        ch = card_heights[idx]
        uniform = team_uniforms[idx]
        formation = team_formations[idx]
        form_info = formations.get(formation, {})
        team_rating = sum(get_rating(p) for p in team)
        totals.append(team_rating)
        bg = COLOR_MAP.get(uniform, "#757575")
        text_color = "white" if uniform in DARK_UNIFORMS else "black"
        
        draw.rounded_rectangle([x0, y0, x0 + col_w, y0 + ch], radius=12, fill="white", outline=bg, width=3)
        draw.rounded_rectangle([x0, y0, x0 + col_w, y0 + 44], radius=12, fill=bg)
        draw.rectangle([x0, y0 + 28, x0 + col_w, y0 + 44], fill=bg)
        draw.text((x0 + 14, y0 + 10), f"TEAM {idx+1}  ·  {uniform}", fill=text_color, font=font_h)
        
        badge = f"Σ {team_rating}"
        bw = 54
        draw.rounded_rectangle([x0 + col_w - bw - 12, y0 + 10, x0 + col_w - 12, y0 + 34], radius=10, fill="#37474f")
        draw.text((x0 + col_w - bw - 4, y0 + 13), badge, fill="white", font=font_small)
        
        y = y0 + 52
        draw.text((x0 + 14, y), f"Formasi: {formation}", fill="#222", font=font_row_b)
        y += 18
        pola = form_info.get("pola", "")
        if len(pola) > 72:
            pola = pola[:69] + "..."
        draw.text((x0 + 14, y), pola, fill="#555", font=font_small)
        y += 20
        draw_formation_pitch(draw, x0 + 14, y, pitch_w, pitch_h, formation)
        y += pitch_h + 10
        
        draw.rectangle([x0 + 10, y, x0 + col_w - 10, y + row_h], fill=bg)
        draw.text((x0 + 18, y + 6), "No", fill=text_color, font=font_small)
        draw.text((x0 + 50, y + 6), "Nama Pemain", fill=text_color, font=font_small)
        draw.text((x0 + 320, y + 6), "Role", fill=text_color, font=font_small)
        y += row_h
        
        for j, player in enumerate(team, 1):
            if j % 2 == 0:
                draw.rectangle([x0 + 10, y, x0 + col_w - 10, y + row_h], fill="#f0f4f8")
            pr = roles_map.get(player, [])
            role_str = ", ".join(pr) if pr else "-"
            if len(role_str) > 22:
                role_str = role_str[:20] + ".."
            tag = " *" if player in extras_set else ""
            draw.text((x0 + 18, y + 6), str(j), fill="#333", font=font_row)
            draw.text((x0 + 50, y + 6), f"{player}{tag}", fill="#111", font=font_row_b)
            draw.text((x0 + 320, y + 6), role_str, fill="#444", font=font_row)
            y += row_h

    if totals:
        mx, mn = max(totals), min(totals)
        gap_v = mx - mn
        if gap_v <= 3:
            status, color = "Imbang", "#2e7d32"
        elif gap_v <= 6:
            status, color = "Cukup imbang", "#f57c00"
        else:
            status, color = "Kurang imbang", "#c62828"
        summary = "  |  ".join(f"Team {i+1}: {t}" for i, t in enumerate(totals))
        fy = img_h - margin - 36
        draw.rounded_rectangle([margin, fy, img_w - margin, fy + 36], radius=8, fill="#eceff1")
        draw.rectangle([margin, fy, margin + 6, fy + 36], fill=color)
        draw.text((margin + 16, fy + 9), f"Keseimbangan: {summary}   →  Selisih {gap_v}  ({status})", fill="#222", font=font_sub)
    
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()

def render_teams_svg(teams, team_formations, team_uniforms, roles_map, extras):
    """Buat hasil pembagian tim sebagai SVG vektor yang bisa diperbesar tanpa pecah."""
    width = 1100
    row_h = 31
    team_heights = [115 + max(1, len(team)) * row_h for team in teams]
    height = 90 + sum(team_heights) + 24 * max(0, len(teams) - 1)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="#07172b"/>',
             '<text x="42" y="52" font-family="Arial,sans-serif" font-size="30" font-weight="700" fill="#ffffff">HASIL PEMBAGIAN TIM FUTSAL</text>']
    y = 80
    for i, team in enumerate(teams):
        color = COLOR_MAP.get(team_uniforms[i], '#1388ff')
        h = team_heights[i]
        parts.append(f'<rect x="30" y="{y}" width="1040" height="{h}" rx="18" fill="#102943" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<text x="52" y="{y+35}" font-family="Arial,sans-serif" font-size="24" font-weight="700" fill="{color}">TEAM {i+1} · {esc(str(team_uniforms[i]))}</text>')
        parts.append(f'<text x="52" y="{y+63}" font-family="Arial,sans-serif" font-size="15" fill="#dbeafe">Formasi: {esc(str(team_formations[i]))}</text>')
        parts.append(f'<text x="52" y="{y+91}" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#9fe8ff">NO.   NAMA PEMAIN                                      POSISI</text>')
        for j, player in enumerate(team, 1):
            yy = y + 116 + (j-1)*row_h
            role_txt = ', '.join(roles_map.get(player, [])) or '-'
            extra_txt = ' (LUAR)' if player in extras else ''
            parts.append(f'<text x="55" y="{yy}" font-family="Arial,sans-serif" font-size="15" fill="#ffffff">{j}.</text>')
            parts.append(f'<text x="105" y="{yy}" font-family="Arial,sans-serif" font-size="15" fill="#ffffff">{esc(str(player + extra_txt))}</text>')
            parts.append(f'<text x="690" y="{yy}" font-family="Arial,sans-serif" font-size="15" fill="#b9d7f5">{esc(role_txt)}</text>')
        y += h + 24
    parts.append('</svg>')
    return ''.join(parts).encode('utf-8')


# ==========================================
# STREAMLIT UI
# ==========================================
STEPS = [
    "1️⃣ Pilih Pemain",
    "2️⃣ Role & Rating",
    "3️⃣ Rules (Conflict)",
    "4️⃣ Konfigurasi Tim",
    "5️⃣ Generate Tim",
    "6️⃣ Hitung Biaya",
]
PAY_OPTIONS = ["Belum", "Cicil", "Done"]


def role_label(r):
    return f"{roles_data[r]['emoji']} {r} — {roles_data[r]['nama']}"


st.markdown("""
<div class="futsal-hero">
  <div class="futsal-kicker">Play • Build • Win</div>
  <h1>⚽ Futsal Tim Generator</h1>
  <p>Bangun tim yang seimbang, tentukan peran pemain, pilih formasi, dan siapkan pertandingan dengan lebih mudah.</p>
  <span class="futsal-pill">TEAMWORK STARTS HERE · MATCHDAY READY</span>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("📋 Navigasi")
    step = st.radio("Pilih Tahapan:", STEPS)
    st.caption(f"👥 Pemain terpilih: {len(st.session_state.selected_players)}")

# keluar dari Step 2 -> kembali ke tampilan baca-saja
if step != STEPS[1]:
    st.session_state.step2_mode = "view"
    st.session_state.login_open = False

all_players = master_names() + st.session_state.extras


# ------------------------------------------
# Callbacks Step 1
# ------------------------------------------
def _add_extra():
    """Dipanggil oleh tombol submit form pemain luar."""
    name = (st.session_state.get("ex_name") or "").strip()
    roles = [r for r in ROLE_KEYS if r in (st.session_state.get("ex_roles") or [])]
    rating = _clamp_rating(st.session_state.get("ex_rating", 5))
    taken = {n.lower() for n in master_names() + st.session_state.extras}
    if not name:
        st.session_state.extra_msg = ("error", "⚠️ Nama tidak boleh kosong!")
    elif name.lower() in taken:
        st.session_state.extra_msg = ("warning", f"⚠️ '{name}' sudah ada di daftar.")
    elif not roles:
        st.session_state.extra_msg = ("error", "⚠️ Pilih minimal 1 role untuk pemain ini!")
    else:
        st.session_state.extras.append(name)
        st.session_state.extra_info[name] = {"roles": roles, "rating": rating}
        new_sel = list(st.session_state.get("ms_players", st.session_state.selected_players)) + [name]
        st.session_state.selected_players = new_sel
        st.session_state.ms_players = new_sel
        st.session_state.extra_msg = ("success", f"✅ '{name}' ditambahkan ({', '.join(roles)} • rating {rating}).")


def _select_all():
    st.session_state.ms_players = master_names() + st.session_state.extras


def _clear_all():
    st.session_state.ms_players = []


# ------------------------------------------
# Step 2: tampilan baca-saja & mode edit
# ------------------------------------------
def commit_db(new_db, removed=()):
    """Terapkan perubahan database pemain (dan bersihkan referensi pemain yang dihapus)."""
    removed = set(removed)
    st.session_state.db = new_db
    st.session_state.db_ver += 1
    sel = [p for p in st.session_state.selected_players if p not in removed]
    st.session_state.selected_players = sel
    if "ms_players" in st.session_state:
        st.session_state.ms_players = [p for p in st.session_state.ms_players if p not in removed]
    st.session_state.rules = [r for r in st.session_state.rules if not (set(r) & removed)]
    ok = save_db(new_db)
    if ok:
        st.session_state.flash = ("success", "✅ Perubahan tersimpan.")
    else:
        st.session_state.flash = ("warning", "⚠️ Perubahan berlaku selama sesi ini, tetapi file database tidak bisa ditulis di server.")


def render_login():
    st.markdown("##### 🔐 Masukkan password untuk masuk ke halaman edit")
    if st.session_state.login_attempts >= MAX_LOGIN_ATTEMPTS:
        st.error("⛔ Terlalu banyak percobaan salah. Muat ulang halaman untuk mencoba lagi.")
        return
    with st.form("form_login", clear_on_submit=True):
        pw = st.text_input("Password admin", type="password")
        c1, c2, _ = st.columns([1, 1, 4])
        ok = c1.form_submit_button("Masuk", type="primary")
        cancel = c2.form_submit_button("Batal")
    if cancel:
        st.session_state.login_open = False
        st.rerun()
    if ok:
        if hmac.compare_digest(pw.encode("utf-8"), get_admin_password().encode("utf-8")):
            st.session_state.is_admin = True
            st.session_state.login_attempts = 0
            st.session_state.login_open = False
            st.session_state.step2_mode = "edit"
            st.rerun()
        else:
            st.session_state.login_attempts += 1
            left = MAX_LOGIN_ATTEMPTS - st.session_state.login_attempts
            st.error(f"❌ Password salah. Sisa percobaan: {left}")


def render_view_page():
    st.header("🎯 Step 2: Role Pemain")
    st.caption("Daftar pemain menampilkan nama, posisi yang bisa dimainkan, dan status. Rating hanya terlihat di mode edit. "
               "Untuk mengubah nama, posisi, rating, atau menambah/menghapus pemain, masukkan password admin.")

    show_all = st.toggle("Tampilkan semua pemain database", value=False, key="show_all_players")
    names = (master_names() + st.session_state.extras) if show_all else list(st.session_state.selected_players)

    if not names:
        st.warning("⚠️ Pilih pemain dulu di Step 1!")
    else:
        cards = "".join(
            player_card_html(p, defaults_for(p)[0], p in st.session_state.extras,
                             "Dipilih" if p in st.session_state.selected_players else "Belum dipilih") for p in names
        )
        st.markdown(
            flat_html(
                "<div style='display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px'>"
                + cards + "</div>"
            ),
            unsafe_allow_html=True,
        )
        st.caption("  ".join(f"{roles_data[r]['emoji']} **{r}** = {roles_data[r]['nama']}" for r in ROLE_KEYS))

    st.markdown("---")
    st.subheader("🔐 Edit Data Pemain")
    st.write("Tambah pemain, ubah role & rating, atau hapus pemain dari database. Perlu password.")
    if st.button("🔐 Edit nama, posisi, rating & pemain"):
        if st.session_state.is_admin:
            st.session_state.step2_mode = "edit"
            st.rerun()
        else:
            st.session_state.login_open = True

    if st.session_state.login_open and not st.session_state.is_admin:
        render_login()


def db_editor_df():
    rows = [
        [d["nama"]] + [r in d["roles"] for r in ROLE_KEYS] + [d["rating"], False]
        for d in st.session_state.db
    ]
    return pd.DataFrame(rows, columns=["Pemain"] + ROLE_KEYS + ["Rating", "Hapus"])


def render_edit_page():
    top_l, top_r = st.columns([5, 1])
    top_l.header("✏️ Edit Data Pemain")
    if top_r.button("🔒 Keluar", help="Kunci kembali & kembali ke tampilan biasa"):
        st.session_state.is_admin = False
        st.session_state.step2_mode = "view"
        st.rerun()
    if st.button("← Kembali ke daftar pemain"):
        st.session_state.step2_mode = "view"
        st.rerun()

    if using_default_password():
        st.warning("⚠️ Password default masih dipakai. Atur `ADMIN_PASSWORD` di Secrets agar lebih aman.")

    flash = st.session_state.pop("flash", None)
    if flash:
        getattr(st, flash[0])(flash[1])

    tab_edit, tab_add = st.tabs(["📝 Edit role & rating", "➕ Tambah pemain baru"])

    with tab_edit:
        st.caption("Edit nama, posisi yang bisa dimainkan, dan rating. Centang **Hapus** untuk menghapus pemain, lalu simpan perubahan.")
        column_config = {
            "Pemain": st.column_config.TextColumn("Nama pemain", required=True),
            "GK": st.column_config.CheckboxColumn("GK 🧤", default=False),
            "A": st.column_config.CheckboxColumn("A ⚓", default=False),
            "F": st.column_config.CheckboxColumn("F 🪽", default=False),
            "P": st.column_config.CheckboxColumn("P 🔥", default=False),
            "Rating": st.column_config.NumberColumn("Rating (1-10)", min_value=1, max_value=10, step=1),
            "Hapus": st.column_config.CheckboxColumn("Hapus 🗑️", default=False),
        }
        edited = st.data_editor(
            db_editor_df(),
            column_config=column_config,
            width="stretch",
            num_rows="fixed",
            hide_index=True,
            key=f"db_editor_{st.session_state.db_ver}",
        )
        if st.button("💾 Simpan Perubahan", type="primary"):
            new_db, removed, no_role = [], [], []
            seen_names = set()
            invalid_names = []
            for _, row in edited.iterrows():
                old_name = str(row["Pemain"]).strip()
                if _b(row["Hapus"]):
                    removed.append(old_name)
                    continue
                name = old_name
                if not name:
                    invalid_names.append("(nama kosong)")
                    continue
                if name.casefold() in seen_names:
                    invalid_names.append(name)
                    continue
                seen_names.add(name.casefold())
                roles = [r for r in ROLE_KEYS if _b(row[r])]
                if not roles:
                    no_role.append(name)
                    roles = ["A", "F", "P"]
                new_db.append({"nama": name, "roles": roles, "rating": _clamp_rating(row["Rating"], 5)})
            if invalid_names:
                st.error("Nama pemain harus terisi dan tidak boleh duplikat: " + ", ".join(invalid_names))
            elif not new_db:
                st.error("⚠️ Database tidak boleh kosong.")
            else:
                # Sinkronkan referensi jika nama pemain berubah
                rename_map = {}
                for old_name in master_names():
                    match = next((d["nama"] for d in new_db if d["nama"].casefold() == old_name.casefold()), None)
                    if match and match != old_name:
                        rename_map[old_name] = match
                for old_name, new_name in rename_map.items():
                    st.session_state.selected_players = [new_name if x == old_name else x for x in st.session_state.selected_players]
                    if "ms_players" in st.session_state:
                        st.session_state.ms_players = [new_name if x == old_name else x for x in st.session_state.ms_players]
                    if old_name in st.session_state.payments:
                        st.session_state.payments[new_name] = st.session_state.payments.pop(old_name)
                commit_db(new_db, removed)
                if no_role:
                    st.session_state.flash = (
                        "info", f"ℹ️ Tersimpan. Pemain tanpa posisi diberi A/F/P otomatis: {', '.join(no_role)}")
                st.rerun()

    with tab_add:
        with st.form("form_add_db", clear_on_submit=True):
            new_name = st.text_input("Nama pemain", placeholder="Ketik nama pemain...")
            new_roles = st.multiselect("Role yang dapat dimainkan", ROLE_KEYS,
                                       default=["A", "F", "P"], format_func=role_label)
            new_rating = st.slider("Rating", 1, 10, 5)
            add_ok = st.form_submit_button("➕ Tambah ke database", type="primary")
        if add_ok:
            name = new_name.strip()
            taken = {n.lower() for n in master_names() + st.session_state.extras}
            if not name:
                st.error("⚠️ Nama tidak boleh kosong!")
            elif name.lower() in taken:
                st.warning(f"⚠️ '{name}' sudah ada.")
            elif not new_roles:
                st.error("⚠️ Pilih minimal 1 role!")
            else:
                roles = [r for r in ROLE_KEYS if r in new_roles]
                commit_db(st.session_state.db + [{"nama": name, "roles": roles, "rating": new_rating}])
                st.session_state.flash = (
                    st.session_state.flash[0],
                    f"✅ '{name}' ditambahkan ke database. " + st.session_state.flash[1],
                )
                st.rerun()


# --- STEP 1: PILIH PEMAIN ---
if step == STEPS[0]:
    st.header("📋 Step 1: Pilih Pemain")

    # key widget dihapus Streamlit saat step lain tampil, jadi diisi ulang dari selected_players
    if "ms_players" not in st.session_state:
        st.session_state.ms_players = list(st.session_state.selected_players)
    st.session_state.ms_players = [p for p in st.session_state.ms_players if p in all_players]

    selected = st.multiselect("Pilih pemain dari database:", options=all_players, key="ms_players")
    st.session_state.selected_players = list(selected)

    c1, c2, _ = st.columns([1, 1, 4])
    c1.button("Pilih semua", on_click=_select_all)
    c2.button("Kosongkan", on_click=_clear_all)

    st.markdown("---")
    st.subheader("➕ Tambah Pemain Luar Database")
    st.caption("Pemain luar hanya berlaku selama sesi ini dan tidak masuk database. Penambahan pemain juga dilindungi password.")
    if st.session_state.is_admin:
        with st.form("form_extra", clear_on_submit=True):
            st.text_input("Nama pemain tambahan", placeholder="Ketik nama pemain...", key="ex_name")
            f1, f2 = st.columns([3, 2])
            with f1:
                st.multiselect("Posisi yang bisa dimainkan", ROLE_KEYS, default=["A", "F", "P"],
                               format_func=role_label, key="ex_roles")
            with f2:
                st.slider("Rating (1-10)", 1, 10, 5, key="ex_rating")
            st.form_submit_button("➕ Tambah Pemain Luar", on_click=_add_extra, type="primary")
    else:
        if st.button("🔐 Masukkan password untuk menambah pemain"):
            st.session_state.login_open = True
            st.session_state.step2_mode = "view"
        if st.session_state.login_open:
            render_login()

    msg = st.session_state.pop("extra_msg", None)
    if msg:
        getattr(st, msg[0])(msg[1])

    if st.session_state.extras:
        st.markdown("**👥 Pemain luar (sesi ini):**")
        st.dataframe(
            pd.DataFrame(
                [
                    {"Nama": n,
                     "Posisi": ", ".join(st.session_state.extra_info[n]["roles"]),
                     "Status": "Dipilih" if n in st.session_state.selected_players else "Belum dipilih"}
                    for n in st.session_state.extras
                ]
            ),
            width="stretch",
            hide_index=True,
        )

    st.markdown("---")
    st.metric("Total Pemain Terpilih", len(st.session_state.selected_players))

# --- STEP 2: ROLE PEMAIN (view) / EDIT (password) ---
elif step == STEPS[1]:
    if st.session_state.step2_mode == "edit" and st.session_state.is_admin:
        render_edit_page()
    else:
        render_view_page()

# --- STEP 3: RULES ---
elif step == STEPS[2]:
    st.header("⚖️ Step 3: Aturan Conflict (Tidak Boleh Setim)")
    sel = st.session_state.selected_players
    if not sel:
        st.warning("⚠️ Pilih pemain dulu di Step 1!")
        st.stop()

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        p1 = st.selectbox("Pemain 1", sel, key="rule_p1")
    with col2:
        p2 = st.selectbox("Pemain 2", sel, key="rule_p2")
    with col3:
        st.write("")
        st.write("")
        if st.button("➕ Tambah", width="stretch"):
            if p1 == p2:
                st.error("⚠️ Pemain harus berbeda!")
            else:
                pair = tuple(sorted([p1, p2]))
                if pair not in st.session_state.rules:
                    st.session_state.rules.append(pair)
                    st.rerun()
                else:
                    st.warning("⚠️ Rule sudah ada!")

    st.markdown("---")
    st.subheader(f"📜 Rules Aktif ({len(st.session_state.rules)})")
    if st.session_state.rules:
        for i, (a, b) in enumerate(list(st.session_state.rules)):
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"**{i+1}.** {a} ⚔️ {b}")
            with col_b:
                if st.button("🗑️ Hapus", key=f"del_{i}"):
                    st.session_state.rules.remove((a, b))
                    st.rerun()
    else:
        st.info("Belum ada aturan conflict.")

# --- STEP 4: KONFIGURASI TIM ---
elif step == STEPS[3]:
    st.header("⚙️ Step 4: Konfigurasi Jumlah Tim & Seragam")
    if not st.session_state.selected_players:
        st.warning("⚠️ Pilih pemain dulu di Step 1!")
        st.stop()

    num_teams = st.slider("Jumlah Tim", 2, MAX_TEAMS, int(st.session_state.num_teams), step=1)
    st.session_state.num_teams = num_teams

    st.markdown("**🎨 Pilih Seragam tiap Tim**")
    saved = st.session_state.team_uniforms
    team_uniforms = []
    cols = st.columns(min(num_teams, 3))
    for i in range(num_teams):
        default = saved[i] if i < len(saved) and saved[i] in UNIFORM_OPTIONS else UNIFORM_OPTIONS[i % len(UNIFORM_OPTIONS)]
        with cols[i % len(cols)]:
            uniform = st.selectbox(
                f"Team {i+1}",
                UNIFORM_OPTIONS,
                index=UNIFORM_OPTIONS.index(default),
                key=f"uniform_{i}",
            )
            team_uniforms.append(uniform)
    st.session_state.team_uniforms = team_uniforms

    if len(set(team_uniforms)) < len(team_uniforms):
        st.warning("⚠️ Ada tim dengan warna seragam yang sama.")

    st.markdown("---")
    num_players = len(st.session_state.selected_players)
    per_team = num_players // num_teams
    sisa = num_players % num_teams
    st.info(f"📊 **Total Pemain:** {num_players} | **Rata-rata per Tim:** ~{per_team} pemain | **Sisa:** {sisa} pemain")

# --- STEP 5: GENERATE TIM ---
elif step == STEPS[4]:
    st.header("🎲 Step 5: Generate Pembagian Tim")
    sel = st.session_state.selected_players
    if not sel:
        st.warning("⚠️ Pilih pemain dulu di Step 1!")
        st.stop()

    n_teams = int(st.session_state.num_teams)
    if len(sel) < n_teams:
        st.error(f"⚠️ Jumlah pemain ({len(sel)}) lebih sedikit dari jumlah tim ({n_teams}). Ubah di Step 4.")
        st.stop()

    roles_all, ratings_all = {}, {}
    for p in sel:
        r, rt = defaults_for(p)
        roles_all[p], ratings_all[p] = r, rt

    gk_capable = sum(1 for p in sel if "GK" in roles_all[p])
    if gk_capable == 0:
        st.warning("⚠️ Belum ada pemain berole GK di daftar terpilih.")
    elif gk_capable < n_teams:
        st.info(f"ℹ️ Pemain berole GK ({gk_capable}) lebih sedikit dari jumlah tim ({n_teams}); sebagian tim tanpa kiper khusus.")

    if st.button("🎲 GENERATE TIM SEKARANG", type="primary", width="stretch"):
        with st.spinner("Sedang mengacak dan menyeimbangkan tim..."):
            teams, team_formations, team_uniforms = generate_teams(
                sel,
                roles_all,
                ratings_all,
                st.session_state.rules,
                n_teams,
                st.session_state.team_uniforms,
                st.session_state.extras,
            )
            st.session_state.generated_result = {
                "html": display_teams(teams, team_formations, team_uniforms, roles_all, ratings_all, st.session_state.extras),
                "png": render_teams_png(teams, team_formations, team_uniforms, roles_all, ratings_all, st.session_state.extras),
                "svg": render_teams_svg(teams, team_formations, team_uniforms, roles_all, st.session_state.extras),
            }

    if st.session_state.generated_result:
        st.markdown(st.session_state.generated_result["html"], unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📥 Download Hasil sebagai Gambar")
        dl_png, dl_svg = st.columns(2)
        with dl_png:
            st.download_button(
                label="⬇️ Download PNG Pembagian Tim",
                data=st.session_state.generated_result["png"],
                file_name="pembagian_tim_futsal.png",
                mime="image/png",
                width="stretch",
            )
        with dl_svg:
            st.download_button(
                label="⬇️ Download SVG (vektor)",
                data=st.session_state.generated_result["svg"],
                file_name="pembagian_tim_futsal.svg",
                mime="image/svg+xml",
                width="stretch",
            )

# --- STEP 6: HITUNG BIAYA ---
elif step == STEPS[5]:
    st.header("💰 Step 6: Hitung Biaya per Pemain")
    sel = st.session_state.selected_players
    if not sel:
        st.warning("⚠️ Pilih pemain dulu di Step 1!")
        st.stop()

    num_players = len(sel)
    total_cost = st.number_input("Total Biaya Lapangan (Rp)", min_value=0, value=0, step=50000, format="%d")

    if total_cost > 0:
        per_player = total_cost / num_players
        fmt = lambda v: f"{v:,.0f}".replace(",", ".")

        st.markdown(flat_html(f"""
        <div style='background:#fff3e0;padding:20px;border-radius:12px;border:2px solid #ff9800;color:#222;margin:20px 0'>
            <h3 style='color:#e65100;margin-top:0'>💰 RINCIAN BIAYA</h3>
            <table cellpadding='10' style='width:100%'>
                <tr><td><b>Total Biaya Lapangan:</b></td><td style='text-align:right'><b>Rp {fmt(total_cost)}</b></td></tr>
                <tr><td><b>Jumlah Pemain:</b></td><td style='text-align:right'><b>{num_players} orang</b></td></tr>
                <tr style='border-top:2px solid #ff9800'>
                    <td><b style='font-size:18px'>💵 Biaya per Pemain:</b></td>
                    <td style='text-align:right'><b style='font-size:22px;color:#e65100'>Rp {fmt(per_player)}</b></td>
                </tr>
            </table>
        </div>
        """), unsafe_allow_html=True)

        st.subheader("📋 Tracking Status Pembayaran")
        payments = st.session_state.payments
        payment_data = []
        for player in sel:
            current = payments.get(player, "Belum")
            status = st.selectbox(player, PAY_OPTIONS, index=PAY_OPTIONS.index(current), key=f"pay_{player}")
            payments[player] = status
            payment_data.append({"Pemain": player, "Status": status})

        st.dataframe(pd.DataFrame(payment_data), width="stretch", hide_index=True)

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("✅ Done", sum(1 for p in payment_data if p["Status"] == "Done"))
        col_b.metric("💳 Cicil", sum(1 for p in payment_data if p["Status"] == "Cicil"))
        col_c.metric("⏳ Belum", sum(1 for p in payment_data if p["Status"] == "Belum"))

# Footer
st.markdown("---")
st.markdown("<div style='text-align:center;color:#666;font-size:12px'><p>⚽ Futsal Tim Generator v2.1 (Streamlit)</p></div>", unsafe_allow_html=True)
