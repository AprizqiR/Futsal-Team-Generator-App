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
# KONFIGURASI HALAMAN & CUSTOM CSS
# ==========================================
st.set_page_config(
    page_title="⚽ Futsal Tim Generator",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan modern, bersih, dan adaptif Light/Dark mode
st.markdown("""
<style>
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
    }
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #666;
        margin-bottom: 1.5rem;
    }
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
        "karakter": "Sangat seimbang antara bertahan dan menyerang.",
        "sketsa": "[Pivot] [Flank] [Flank] [Anchor]",
        "positions": [{"label": "GK", "x": 8, "y": 50}, {"label": "A", "x": 28, "y": 50}, {"label": "F", "x": 52, "y": 22}, {"label": "F", "x": 52, "y": 78}, {"label": "P", "x": 78, "y": 50}],
    },
    "Pyramid / Wall (2-1-1)": {
        "pola": "2 Defender (belakang) • 1 Midfielder (tengah) • 1 Pivot (depan)",
        "karakter": "Fokus defensif kokoh. Efektif untuk meredam tim agresif.",
        "sketsa": "[Pivot] [Midfielder] [Def] [Def]",
        "positions": [{"label": "GK", "x": 8, "y": 50}, {"label": "A", "x": 28, "y": 32}, {"label": "A", "x": 28, "y": 68}, {"label": "F", "x": 55, "y": 50}, {"label": "P", "x": 80, "y": 50}],
    },
    "The Box / Square (2-2)": {
        "pola": "2 Pemain Belakang • 2 Pemain Depan",
        "karakter": "Fleksibel dan konvensional. Membagi lapangan menjadi dua area simetris.",
        "sketsa": "[Pivot] [Pivot] [Def] [Def]",
        "positions": [{"label": "GK", "x": 8, "y": 50}, {"label": "A", "x": 32, "y": 30}, {"label": "A", "x": 32, "y": 70}, {"label": "P", "x": 72, "y": 30}, {"label": "P", "x": 72, "y": 70}],
    },
    "Formasi Y (1-1-2)": {
        "pola": "1 Anchor • 1 Midfielder • 2 Pivot (depan sejajar)",
        "karakter": "Sangat agresif (offensive). Menekan pertahanan lawan sejak dini.",
        "sketsa": "[Pivot] [Pivot] [Midfielder] [Anchor]",
        "positions": [{"label": "GK", "x": 8, "y": 50}, {"label": "A", "x": 28, "y": 50}, {"label": "F", "x": 52, "y": 50}, {"label": "P", "x": 78, "y": 30}, {"label": "P", "x": 78, "y": 70}],
    },
    "Park the Bus (3-1)": {
        "pola": "3 Defender (belakang) • 1 Pivot (depan)",
        "karakter": "Defensif total untuk mempertahankan keunggulan.",
        "sketsa": "[Pivot] [Def][Def][Def]",
        "positions": [{"label": "GK", "x": 8, "y": 50}, {"label": "A", "x": 30, "y": 22}, {"label": "A", "x": 30, "y": 50}, {"label": "A", "x": 30, "y": 78}, {"label": "P", "x": 72, "y": 50}],
    },
    "Total / Flat (4-0)": {
        "pola": "4 Pemain Sejajar (rotasi dinamis)",
        "karakter": "Semua pemain wajib bisa bertahan dan menyerang sama baiknya.",
        "sketsa": "[P1] [P2] [P3] [P4] (Sejajar dinamis)",
        "positions": [{"label": "GK", "x": 8, "y": 50}, {"label": "F", "x": 48, "y": 18}, {"label": "F", "x": 48, "y": 40}, {"label": "F", "x": 48, "y": 60}, {"label": "F", "x": 48, "y": 82}],
    },
}

UNIFORM_OPTIONS = ["Biru", "Putih", "Merah", "Kuning", "Ungu", "Hitam", "Hijau"]
COLOR_MAP = {"Biru": "#1976d2", "Putih": "#ffffff", "Merah": "#d32f2f", "Kuning": "#fbc02d", "Ungu": "#7b1fa2", "Hitam": "#212121", "Hijau": "#388e3c", "Abu-abu": "#757575"}
DARK_UNIFORMS = ["Hitam", "Biru", "Merah", "Ungu", "Hijau"]
MAX_TEAMS = 6

# ==========================================
# HELPER & DATABASE FUNCTIONS
# ==========================================
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "players_db.json")
MAX_LOGIN_ATTEMPTS = 5
DEFAULT_ADMIN_PASSWORD = "admin123"
AVATAR_COLORS = ["#1976d2", "#388e3c", "#d32f2f", "#7b1fa2", "#f57c00", "#00838f", "#5d4037", "#455a64", "#c2185b", "#512da8"]

def _clamp_rating(v, default=5):
    try:
        v = int(round(float(v)))
    except (TypeError, ValueError, OverflowError):
        return default
    return max(1, min(10, v))

def _b(v):
    try:
        return bool(v) if v == v else False
    except Exception:
        return False

def seed_db():
    return [{"nama": p["nama"], "roles": list(p["roles"]), "rating": p["rating"]} for p in DATABASE_PLAYERS if p["status"] == "Active"]

def load_db():
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

# --- State Management ---
_defaults = {
    "db": None, "db_ver": 0, "extras": [], "extra_info": {}, "rules": [],
    "selected_players": None, "generated_result": None, "num_teams": 2,
    "team_uniforms": [], "payments": {}, "is_admin": False, "login_open": False,
    "login_attempts": 0, "step2_mode": "view"
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
    return (words[0][0] + words[1][0]).upper() if len(words) > 1 else words[0][:2].upper()

def avatar_html(name, size=40):
    color = AVATAR_COLORS[sum(ord(c) for c in name) % len(AVATAR_COLORS)]
    return (
        f"<div style='width:{size}px;height:{size}px;border-radius:50%;background:{color};color:#fff;"
        f"display:flex;align-items:center;justify-content:center;font-weight:700;"
        f"font-size:{int(size * 0.38)}px;flex-shrink:0'>{esc(initials(name))}</div>"
    )

def player_card_html(name, roles, is_extra=False):
    chips = "".join(
        f"<span style='display:inline-block;padding:2px 8px;margin:2px 2px 0 0;"
        f"border-radius:10px;font-size:11px;background:rgba(25,118,210,0.12);border:1px solid rgba(25,118,210,0.25)'>"
        f"{roles_data[r]['emoji']} {r}</span>"
        for r in ROLE_KEYS if r in roles
    )
    badge = " <span style='background:#ff9800;color:#fff;padding:1px 5px;border-radius:6px;font-size:10px'>LUAR</span>" if is_extra else ""
    return (
        f"<div style='display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:12px;"
        f"background:rgba(150,150,150,0.08);border:1px solid rgba(150,150,150,0.2)'>"
        f"{avatar_html(name)}"
        f"<div style='min-width:0'><div style='font-weight:600;font-size:14px;'>{esc(name)}{badge}</div>"
        f"<div>{chips}</div></div></div>"
    )

# ==========================================
# TIM GENERATOR LOGIC
# ==========================================
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
    
    def team_total_rating(i): return sum(get_rating(p) for p in teams[i])
    def team_size(i): return len(teams[i])
    def has_conflict_with_team(player, team_idx): return any(t in conflicts.get(player, set()) for t in teams[team_idx])
    def valid_teams_for(player):
        valid = [i for i in range(num_teams) if not has_conflict_with_team(player, i)]
        return valid if valid else list(range(num_teams))
    
    # Assign GK
    gks_sorted = sorted(gks, key=get_rating, reverse=True)
    random.shuffle(gks_sorted)
    gks_sorted = sorted(gks_sorted, key=get_rating, reverse=True)
    for gk in gks_sorted[:num_teams]:
        candidates = valid_teams_for(gk)
        best = min(candidates, key=lambda i: (team_total_rating(i), team_size(i)))
        teams[best].append(gk)
    
    remaining = non_gks + gks_sorted[num_teams:]
    random.shuffle(remaining)
    remaining.sort(key=lambda p: (get_rating(p), p in extras_set), reverse=True)
    
    # Assign sisanya
    for player in remaining:
        candidates = valid_teams_for(player)
        def score(i, player=player):
            team_roles = [r for p in teams[i] for r in roles.get(p, [])]
            role_need = sum(1 for r in roles.get(player, []) if team_roles.count(r) < 2)
            return (team_total_rating(i), team_size(i), -role_need)
        best = min(candidates, key=score)
        teams[best].append(player)
    
    formation_names = list(formations.keys())
    team_formations = {i: random.choice(formation_names) for i in range(num_teams)}
    team_uniforms = {i: team_uniforms_in[i] if i < len(team_uniforms_in) and team_uniforms_in[i] else UNIFORM_OPTIONS[i % len(UNIFORM_OPTIONS)] for i in range(num_teams)}
    
    return teams, team_formations, team_uniforms

def formation_svg(formation_name, width=320, height=180):
    form = formations.get(formation_name, {})
    positions = form.get("positions", [])
    W, H = 400, 250
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {W} {H}" style="border-radius:10px;display:block;margin:auto;">',
        f'<rect x="0" y="0" width="{W}" height="{H}" rx="14" fill="#1b5e20"/>',
        f'<rect x="12" y="12" width="{W-24}" height="{H-24}" rx="6" fill="#2e7d32"/>',
        f'<circle cx="{W/2}" cy="{H/2}" r="28" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="2"/>',
        f'<circle cx="{W/2}" cy="{H/2}" r="3" fill="rgba(255,255,255,0.8)"/>',
        f'<line x1="{W/2}" y1="12" x2="{W/2}" y2="{H-12}" stroke="rgba(255,255,255,0.6)" stroke-width="2"/>',
        f'<rect x="12" y="{H/2-45}" width="40" height="90" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1.5"/>',
        f'<rect x="{W-52}" y="{H/2-45}" width="40" height="90" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1.5"/>',
    ]
    for pos in positions:
        px = 12 + (pos["x"] / 100) * (W - 24)
        py = 12 + (pos["y"] / 100) * (H - 24)
        svg.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="14" fill="#d32f2f" stroke="white" stroke-width="2"/>')
        svg.append(f'<text x="{px:.1f}" y="{py+4:.1f}" text-anchor="middle" fill="white" font-size="10" font-weight="bold" font-family="Arial,sans-serif">{pos["label"]}</text>')
    svg.append("</svg>")
    return "".join(svg)

def render_teams_png(teams, team_formations, team_uniforms, roles_map, ratings, extras):
    extras_set = set(extras)
    def get_rating(p): return ratings.get(p, DEFAULT_RATINGS.get(p, 5))
    
    margin, col_w, row_h = 24, 540, 28
    header_block = 52 + 40 + 12
    card_heights = [header_block + (len(t) + 1) * row_h + 24 for t in teams]
    n = len(teams)
    cols = 1 if n == 1 else 2
    rows_cards = (n + cols - 1) // cols
    row_heights = [max([card_heights[r * cols + c] for c in range(cols) if r * cols + c < n] or [0]) for r in range(rows_cards)]
    
    top_banner, balance_h = 70, 50
    img_w = margin * 2 + cols * col_w + (cols - 1) * 20
    img_h = margin + top_banner + sum(row_heights) + (rows_cards - 1) * 20 + balance_h + margin
    img = Image.new("RGB", (img_w, img_h), "#f8f9fa")
    draw = ImageDraw.Draw(img)
    
    font_title = ImageFont.load_default()
    font_h = ImageFont.load_default()
    
    draw.rectangle([0, 0, img_w, top_banner], fill="#0d47a1")
    draw.text((margin, 20), "HASIL PEMBAGIAN TIM FUTSAL", fill="white", font=font_title)
    
    totals = []
    y_base = margin + top_banner + 10
    for idx, team in enumerate(teams):
        r, c = divmod(idx, cols)
        x0 = margin + c * (col_w + 20)
        y0 = y_base + sum(row_heights[:r]) + r * 20
        ch = card_heights[idx]
        uniform = team_uniforms[idx]
        team_rating = sum(get_rating(p) for p in team)
        totals.append(team_rating)
        bg = COLOR_MAP.get(uniform, "#757575")
        
        draw.rounded_rectangle([x0, y0, x0 + col_w, y0 + ch], radius=12, fill="white", outline=bg, width=2)
        draw.rounded_rectangle([x0, y0, x0 + col_w, y0 + 40], radius=12, fill=bg)
        draw.text((x0 + 14, y0 + 12), f"TEAM {idx+1} ({uniform}) - Rating Total: {team_rating}", fill="white", font=font_h)
        
        y = y0 + 50
        for j, player in enumerate(team, 1):
            pr = roles_map.get(player, [])
            tag = " *" if player in extras_set else ""
            draw.text((x0 + 18, y), f"{j}. {player}{tag} ({', '.join(pr)})", fill="#333", font=font_h)
            y += row_h

    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()

# ==========================================
# STREAMLIT UI (MODERNIZED)
# ==========================================
STEPS = [
    "1️⃣ Pilih Pemain",
    "2️⃣ Role & Rating",
    "3️⃣ Rules (Conflict)",
    "4️⃣ Konfigurasi Tim",
    "5️⃣ Generate Tim",
    "6️⃣ Hitung Biaya",
]

st.sidebar.title("⚽ Futsal Generator")
step = st.sidebar.radio("Navigasi Langkah:", STEPS)
st.sidebar.divider()
st.sidebar.caption(f"👥 Pemain terpilih: **{len(st.session_state.selected_players)} orang**")

if step != STEPS[1]:
    st.session_state.step2_mode = "view"
    st.session_state.login_open = False

all_players = master_names() + st.session_state.extras

# --- STEP 1: PILIH PEMAIN ---
if step == STEPS[0]:
    st.markdown("<div class='main-header'>📋 Step 1: Pilih Pemain</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Pilih pemain yang hadir dari database atau tambahkan pemain luar.</div>", unsafe_allow_html=True)

    if "ms_players" not in st.session_state:
        st.session_state.ms_players = list(st.session_state.selected_players)
    st.session_state.ms_players = [p for p in st.session_state.ms_players if p in all_players]

    selected = st.multiselect("Daftar Pemain Hadir:", options=all_players, key="ms_players")
    st.session_state.selected_players = list(selected)

    c1, c2, _ = st.columns([1, 1, 3])
    if c1.button("Select All", use_container_width=True):
        st.session_state.ms_players = all_players
        st.rerun()
    if c2.button("Clear All", use_container_width=True):
        st.session_state.ms_players = []
        st.rerun()

    with st.expander("➕ Tambah Pemain Luar (Sesi Ini)", expanded=False):
        with st.form("form_extra", clear_on_submit=True):
            ex_name = st.text_input("Nama Pemain", placeholder="Ketik nama...")
            col_a, col_b = st.columns(2)
            with col_a:
                ex_roles = st.pills("Role", ROLE_KEYS, default=["A", "F", "P"], selection_mode="multi")
            with col_b:
                ex_rating = st.slider("Rating (1-10)", 1, 10, 5)
            if st.form_submit_button("Tambah Pemain", type="primary"):
                if ex_name.strip():
                    name = ex_name.strip()
                    st.session_state.extras.append(name)
                    st.session_state.extra_info[name] = {"roles": ex_roles, "rating": ex_rating}
                    st.session_state.selected_players.append(name)
                    st.success(f"✅ {name} berhasil ditambahkan!")
                    st.rerun()

    st.divider()
    st.metric("Total Pemain Terpilih", len(st.session_state.selected_players))

# --- STEP 2: ROLE & RATING ---
elif step == STEPS[1]:
    st.markdown("<div class='main-header'>🎯 Step 2: Role & Rating Pemain</div>", unsafe_allow_html=True)
    
    if st.session_state.step2_mode == "view":
        c_left, c_right = st.columns([4, 1])
        c_left.caption("Daftar role & rating pemain yang terpilih.")
        if c_right.button("✏️ Mode Edit Data"):
            if st.session_state.is_admin:
                st.session_state.step2_mode = "edit"
                st.rerun()
            else:
                st.session_state.login_open = True

        if st.session_state.login_open and not st.session_state.is_admin:
            with st.form("login_form"):
                pw = st.text_input("Password Admin", type="password")
                if st.form_submit_button("Masuk"):
                    if hmac.compare_digest(pw.encode("utf-8"), get_admin_password().encode("utf-8")):
                        st.session_state.is_admin = True
                        st.session_state.step2_mode = "edit"
                        st.session_state.login_open = False
                        st.rerun()
                    else:
                        st.error("❌ Password salah!")

        show_all = st.toggle("Tampilkan semua pemain di database", value=False)
        names = all_players if show_all else st.session_state.selected_players

        cols = st.columns(3)
        for idx, p in enumerate(names):
            r, _ = defaults_for(p)
            with cols[idx % 3]:
                st.markdown(player_card_html(p, r, p in st.session_state.extras), unsafe_allow_html=True)

    else:
        st.subheader("📝 Mode Edit Data Pemain (Admin)")
        if st.button("🔒 Keluar Mode Edit"):
            st.session_state.step2_mode = "view"
            st.rerun()

        # Database Editor via Dataframe
        df_db = pd.DataFrame([
            {"Pemain": d["nama"], "GK": "GK" in d["roles"], "A": "A" in d["roles"], "F": "F" in d["roles"], "P": "P" in d["roles"], "Rating": d["rating"]}
            for d in st.session_state.db
        ])
        
        edited = st.data_editor(
            df_db,
            column_config={
                "Pemain": st.column_config.TextColumn("Nama Pemain", disabled=True),
                "Rating": st.column_config.NumberColumn("Rating", min_value=1, max_value=10)
            },
            hide_index=True,
            use_container_width=True
        )

        if st.button("💾 Simpan Perubahan Database", type="primary"):
            new_db = []
            for _, row in edited.iterrows():
                roles = [r for r in ROLE_KEYS if row[r]]
                new_db.append({"nama": row["Pemain"], "roles": roles, "rating": int(row["Rating"])})
            st.session_state.db = new_db
            save_db(new_db)
            st.success("✅ Database berhasil diperbarui!")

# --- STEP 3: RULES (CONFLICT) ---
elif step == STEPS[2]:
    st.markdown("<div class='main-header'>⚖️ Step 3: Rules Conflict</div>", unsafe_allow_html=True)
    st.caption("Tentukan pemain yang tidak boleh ditaruh dalam 1 tim yang sama.")

    sel = st.session_state.selected_players
    if not sel:
        st.warning("⚠️ Pilih pemain dulu di Step 1!")
        st.stop()

    c1, c2, c3 = st.columns([2, 2, 1])
    p1 = c1.selectbox("Pemain 1", sel, key="r_p1")
    p2 = c2.selectbox("Pemain 2", sel, key="r_p2")
    
    if c3.button("➕ Tambah Rule", use_container_width=True):
        if p1 != p2:
            pair = tuple(sorted([p1, p2]))
            if pair not in st.session_state.rules:
                st.session_state.rules.append(pair)
                st.rerun()
        else:
            st.error("Pemain tidak boleh sama!")

    st.divider()
    for i, (a, b) in enumerate(st.session_state.rules):
        col_rule, col_del = st.columns([4, 1])
        col_rule.warning(f"⚔️ **{a}** dan **{b}** dipisah")
        if col_del.button("🗑️ Hapus", key=f"del_{i}"):
            st.session_state.rules.remove((a, b))
            st.rerun()

# --- STEP 4: KONFIGURASI TIM ---
elif step == STEPS[3]:
    st.markdown("<div class='main-header'>⚙️ Step 4: Konfigurasi Tim</div>", unsafe_allow_html=True)
    
    sel = st.session_state.selected_players
    if not sel:
        st.warning("⚠️ Pilih pemain dulu di Step 1!")
        st.stop()

    num_teams = st.slider("Jumlah Tim yang Diinginkan:", 2, MAX_TEAMS, int(st.session_state.num_teams))
    st.session_state.num_teams = num_teams

    st.subheader("🎨 Seragam Tim")
    cols = st.columns(num_teams)
    team_uniforms = []
    for i in range(num_teams):
        with cols[i]:
            u = st.selectbox(f"Tim {i+1}", UNIFORM_OPTIONS, index=i % len(UNIFORM_OPTIONS), key=f"u_{i}")
            team_uniforms.append(u)
    st.session_state.team_uniforms = team_uniforms

    st.divider()
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total Pemain", len(sel))
    col_b.metric("Rata-rata / Tim", f"~{len(sel) // num_teams}")
    col_c.metric("Sisa Pemain", len(sel) % num_teams)

# --- STEP 5: GENERATE TIM ---
elif step == STEPS[4]:
    st.markdown("<div class='main-header'>🎲 Step 5: Hasil Pembagian Tim</div>", unsafe_allow_html=True)
    
    sel = st.session_state.selected_players
    if not sel:
        st.warning("⚠️ Pilih pemain dulu di Step 1!")
        st.stop()

    if st.button("🎲 GENERATE TIM SEKARANG", type="primary", use_container_width=True):
        roles_all, ratings_all = {}, {}
        for p in sel:
            r, rt = defaults_for(p)
            roles_all[p], ratings_all[p] = r, rt

        teams, team_formations, team_uniforms = generate_teams(
            sel, roles_all, ratings_all, st.session_state.rules,
            st.session_state.num_teams, st.session_state.team_uniforms, st.session_state.extras
        )
        st.session_state.generated_result = {
            "teams": teams, "formations": team_formations, "uniforms": team_uniforms,
            "roles": roles_all, "ratings": ratings_all,
            "png": render_teams_png(teams, team_formations, team_uniforms, roles_all, ratings_all, st.session_state.extras)
        }

    res = st.session_state.generated_result
    if res:
        teams = res["teams"]
        cols = st.columns(len(teams))
        
        for i, team in enumerate(teams):
            unif = res["uniforms"][i]
            form = res["formations"][i]
            t_rating = sum(res["ratings"].get(p, 5) for p in team)
            
            with cols[i]:
                with st.container(border=True):
                    st.subheader(f"🏅 TEAM {i+1}")
                    st.caption(f"Seragam: **{unif}** | Rating Total: **{t_rating}**")
                    st.write(f"📐 **{form}**")
                    
                    with st.popover("📐 Lihat Formasi Lapangan"):
                        st.markdown(formation_svg(form), unsafe_allow_html=True)

                    df_t = pd.DataFrame([
                        {"No": j+1, "Nama": p, "Role": ", ".join(res["roles"].get(p, []))}
                        for j, p in enumerate(team)
                    ])
                    st.dataframe(df_t, hide_index=True, use_container_width=True)

        st.divider()
        st.download_button(
            "⬇️ Download PNG Pembagian Tim",
            data=res["png"],
            file_name="pembagian_tim_futsal.png",
            mime="image/png",
            use_container_width=True
        )

# --- STEP 6: HITUNG BIAYA ---
elif step == STEPS[5]:
    st.markdown("<div class='main-header'>💰 Step 6: Hitung Biaya & Pembayaran</div>", unsafe_allow_html=True)
    
    sel = st.session_state.selected_players
    if not sel:
        st.warning("⚠️ Pilih pemain dulu di Step 1!")
        st.stop()

    total_cost = st.number_input("Total Biaya Lapangan (Rp)", min_value=0, value=0, step=50000)

    if total_cost > 0:
        per_player = total_cost / len(sel)
        
        col1, col2 = st.columns(2)
        col1.metric("Total Biaya", f"Rp {total_cost:,.0f}".replace(",", "."))
        col2.metric("Biaya per Pemain", f"Rp {per_player:,.0f}".replace(",", "."))

        st.subheader("📋 Tracking Pembayaran")

        # Inisialisasi/Sync DataFrame Pembayaran
        pay_df = pd.DataFrame([
            {"Pemain": p, "Status": st.session_state.payments.get(p, "Belum")}
            for p in sel
        ])

        edited_pay = st.data_editor(
            pay_df,
            column_config={
                "Pemain": st.column_config.TextColumn("Nama Pemain", disabled=True),
                "Status": st.column_config.SelectboxColumn(
                    "Status Pembayaran",
                    options=["Belum Bayar", "Cicil", "Done"],
                    required=True
                )
            },
            hide_index=True,
            use_container_width=True
        )

        # Update Session State
        for _, row in edited_pay.iterrows():
            st.session_state.payments[row["Pemain"]] = row["Status"]

        # Metric Status Ringkas
        c_done, c_cicil, c_belum = st.columns(3)
        c_done.metric("✅ Done", sum(1 for v in st.session_state.payments.values() if v == "Done"))
        c_cicil.metric("💳 Cicil", sum(1 for v in st.session_state.payments.values() if v == "Cicil"))
        c_belum.metric("⏳ Belum Bayar", sum(1 for v in st.session_state.payments.values() if v == "Belum"))

st.divider()
st.caption("⚽ Futsal Tim Generator v2.2 (Streamlit Native UI)")