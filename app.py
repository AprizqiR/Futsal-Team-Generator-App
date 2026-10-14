import streamlit as st
import pandas as pd
import random
import tempfile
import os
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
# STATE MANAGEMENT
# ==========================================
if "extras" not in st.session_state:
    st.session_state.extras = []
if "rules" not in st.session_state:
    st.session_state.rules = []
if "selected_players" not in st.session_state:
    st.session_state.selected_players = SAMPLE_PLAYERS[:10]
if "df_roles" not in st.session_state:
    st.session_state.df_roles = None
if "generated_result" not in st.session_state:
    st.session_state.generated_result = None

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def _clamp_rating(v, default=5):
    try:
        v = int(round(float(v)))
    except (TypeError, ValueError):
        return default
    return max(1, min(10, v))

def build_df(selected, extras):
    rows = []
    all_players = selected + [e for e in extras if e not in selected]
    for p in all_players:
        if st.session_state.df_roles is not None and p in st.session_state.df_roles["Pemain"].values:
            row = st.session_state.df_roles[st.session_state.df_roles["Pemain"] == p].iloc[0]
            rows.append([p, bool(row["GK"]), bool(row["A"]), bool(row["F"]), bool(row["P"]), _clamp_rating(row["Rating"])])
        else:
            default_roles = DEFAULT_ROLES.get(p, ["A", "F", "P"])
            rows.append([p, "GK" in default_roles, "A" in default_roles, "F" in default_roles, "P" in default_roles, DEFAULT_RATINGS.get(p, 5)])
    return pd.DataFrame(rows, columns=TABLE_HEADERS)

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
            html += f"<tr><td style='text-align:center'>{j}</td><td><b>{player}</b>{badge}</td><td>{role_str}</td></tr>"
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
    return html

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

def render_teams_png(teams, team_formations, team_uniforms, roles_map, ratings, extras, filepath=None):
    extras_set = set(extras)
    if filepath is None:
        filepath = os.path.join(tempfile.gettempdir(), "pembagian_tim_futsal.png")
    
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
    
    img.save(filepath, "PNG")
    return filepath

# ==========================================
# STREAMLIT UI
# ==========================================
st.title("⚽ Futsal Tim Generator")
st.markdown("Pilih pemain, atur role & rating, tentukan jumlah tim & seragam, lalu generate pembagian tim otomatis.")

all_players = SAMPLE_PLAYERS + st.session_state.extras

with st.sidebar:
    st.header("📋 Navigasi")
    step = st.radio("Pilih Tahapan:", ["1️⃣ Pilih Pemain", "2️⃣ Role & Rating", "3️⃣ Rules (Conflict)", "4️⃣ Konfigurasi Tim", "5️⃣ Generate Tim", "6️⃣ Hitung Biaya"])

# --- STEP 1: PILIH PEMAIN ---
if step == "1️⃣ Pilih Pemain":
    st.header("📋 Step 1: Pilih Pemain")
    
    # Filter out extras that might have been removed, keep valid ones
    valid_selected = [p for p in st.session_state.selected_players if p in all_players]
    
    selected = st.multiselect(
        "Pilih pemain dari database:",
        options=all_players,
        default=valid_selected,
        help="Tahan Ctrl/Cmd untuk memilih banyak"
    )
    
    st.session_state.selected_players = selected
    
    st.markdown("---")
    st.subheader("➕ Tambah Pemain Luar Database")
    col1, col2 = st.columns([3, 1])
    with col1:
        txt_extra = st.text_input("Nama pemain tambahan", placeholder="Ketik nama pemain...")
    with col2:
        st.write("")
        st.write("")
        if st.button("Tambah", use_container_width=True):
            name = (txt_extra or "").strip()
            if not name:
                st.error("⚠️ Nama tidak boleh kosong!")
            elif name in all_players:
                st.warning(f"⚠️ '{name}' sudah ada di daftar.")
            else:
                st.session_state.extras.append(name)
                DEFAULT_ROLES[name] = ["A", "F", "P"]
                DEFAULT_RATINGS[name] = 5
                if name not in st.session_state.selected_players:
                    st.session_state.selected_players.append(name)
                st.success(f"✅ '{name}' ditambahkan!")
                st.rerun()
    
    if st.session_state.extras:
        st.info(f"👥 Pemain tambahan: {', '.join(st.session_state.extras)}")
    
    st.markdown("---")
    st.metric("Total Pemain Terpilih", len(st.session_state.selected_players))

# --- STEP 2: ROLE & RATING ---
elif step == "2️⃣ Role & Rating":
    st.header("🎯 Step 2: Atur Role & Rating per Pemain")
    if not st.session_state.selected_players:
        st.warning("⚠️ Pilih pemain dulu di Step 1!")
        st.stop()
    
    st.info("💡 Centang role yang bisa dimainkan, dan ubah angka Rating (1-10) sesuai kemampuan.")
    
    # Build or update dataframe
    if st.session_state.df_roles is None or len(st.session_state.df_roles) != len(st.session_state.selected_players):
        st.session_state.df_roles = build_df(st.session_state.selected_players, st.session_state.extras)
    
    # Column configuration for better UI
    column_config = {
        "Pemain": st.column_config.TextColumn("Pemain", disabled=True),
        "GK": st.column_config.CheckboxColumn("GK 🧤", default=False),
        "A": st.column_config.CheckboxColumn("A ⚓", default=False),
        "F": st.column_config.CheckboxColumn("F 🪽", default=False),
        "P": st.column_config.CheckboxColumn("P 🔥", default=False),
        "Rating": st.column_config.NumberColumn("Rating (1-10)", min_value=1, max_value=10, step=1),
    }
    
    edited_df = st.data_editor(
        st.session_state.df_roles,
        column_config=column_config,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True,
        key="role_editor"
    )
    
    # Save edits back to session state
    st.session_state.df_roles = edited_df
    
    # Validation
    gk_count = sum(1 for _, row in edited_df.iterrows() if row["GK"])
    no_role = []
    for _, row in edited_df.iterrows():
        if not (row["GK"] or row["A"] or row["F"] or row["P"]):
            no_role.append(row["Pemain"])
    
    if gk_count == 0:
        st.error("⚠️ Harus ada minimal 1 Kiper (GK)!")
    elif no_role:
        st.warning(f"⚠️ Pemain tanpa role: {', '.join(no_role)}")
    else:
        st.success("✅ Semua pemain sudah memiliki role yang valid!")

# --- STEP 3: RULES ---
elif step == "3️⃣ Rules (Conflict)":
    st.header("⚖️ Step 3: Aturan Conflict (Tidak Boleh Setim)")
    if not st.session_state.selected_players:
        st.warning("⚠️ Pilih pemain dulu di Step 1!")
        st.stop()
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        p1 = st.selectbox("Pemain 1", st.session_state.selected_players, key="rule_p1")
    with col2:
        p2 = st.selectbox("Pemain 2", st.session_state.selected_players, key="rule_p2")
    with col3:
        st.write("")
        st.write("")
        if st.button("➕ Tambah", use_container_width=True):
            if p1 == p2:
                st.error("⚠️ Pemain harus berbeda!")
            else:
                pair = tuple(sorted([p1, p2]))
                if pair not in st.session_state.rules:
                    st.session_state.rules.append(pair)
                    st.success(f"✅ Rule ditambahkan: {p1} ⚔️ {p2}")
                    st.rerun()
                else:
                    st.warning("⚠️ Rule sudah ada!")
    
    st.markdown("---")
    st.subheader(f"📜 Rules Aktif ({len(st.session_state.rules)})")
    if st.session_state.rules:
        for i, (a, b) in enumerate(st.session_state.rules):
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
elif step == "4️⃣ Konfigurasi Tim":
    st.header("⚙️ Step 4: Konfigurasi Jumlah Tim & Seragam")
    if not st.session_state.selected_players:
        st.warning("⚠️ Pilih pemain dulu di Step 1!")
        st.stop()
    
    num_teams = st.slider("Jumlah Tim", 2, MAX_TEAMS, 2, step=1)
    st.session_state.num_teams = num_teams
    
    st.markdown("**🎨 Pilih Seragam tiap Tim**")
    team_uniforms = []
    cols = st.columns(min(num_teams, 3))
    for i in range(num_teams):
        with cols[i % 3]:
            uniform = st.selectbox(
                f"Team {i+1}", 
                UNIFORM_OPTIONS, 
                index=i % len(UNIFORM_OPTIONS),
                key=f"uniform_{i}"
            )
            team_uniforms.append(uniform)
    st.session_state.team_uniforms = team_uniforms
    
    st.markdown("---")
    num_players = len(st.session_state.selected_players)
    per_team = num_players // num_teams
    sisa = num_players % num_teams
    st.info(f"📊 **Total Pemain:** {num_players} | **Rata-rata per Tim:** ~{per_team} pemain | **Sisa:** {sisa} pemain")

# --- STEP 5: GENERATE TIM ---
elif step == "5️⃣ Generate Tim":
    st.header("🎲 Step 5: Generate Pembagian Tim")
    if not st.session_state.selected_players:
        st.warning("⚠️ Pilih pemain dulu di Step 1!")
        st.stop()
    if st.session_state.df_roles is None:
        st.warning("⚠️ Atur role dulu di Step 2!")
        st.stop()
    
    if st.button("🎲 GENERATE TIM SEKARANG", type="primary", use_container_width=True):
        with st.spinner("Sedang mengacak dan menyeimbangkan tim..."):
            roles_all = {}
            ratings_all = {}
            for _, row in st.session_state.df_roles.iterrows():
                name = str(row["Pemain"]).strip()
                chosen = [r for r in ROLE_KEYS if row[r]]
                roles_all[name] = chosen if chosen else ["A", "F", "P"]
                ratings_all[name] = _clamp_rating(row["Rating"], DEFAULT_RATINGS.get(name, 5))
            
            teams, team_formations, team_uniforms = generate_teams(
                st.session_state.selected_players,
                roles_all,
                ratings_all,
                st.session_state.rules,
                st.session_state.get("num_teams", 2),
                st.session_state.get("team_uniforms", ["Biru", "Putih"]),
                st.session_state.extras
            )
            
            html_result = display_teams(teams, team_formations, team_uniforms, roles_all, ratings_all, st.session_state.extras)
            
            # Generate PNG
            png_path = render_teams_png(teams, team_formations, team_uniforms, roles_all, ratings_all, st.session_state.extras)
            
            st.session_state.generated_result = {
                "html": html_result,
                "png_path": png_path,
                "teams": teams
            }
            st.rerun()
    
    if st.session_state.generated_result:
        st.markdown(st.session_state.generated_result["html"], unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("📥 Download Hasil sebagai Gambar")
        with open(st.session_state.generated_result["png_path"], "rb") as f:
            st.download_button(
                label="⬇️ Download PNG Pembagian Tim",
                data=f,
                file_name="pembagian_tim_futsal.png",
                mime="image/png",
                use_container_width=True
 are
            )

# --- STEP 6: HITUNG BIAYA ---
elif step == "6️⃣ Hitung Biaya":
    st.header("💰 Step 6: Hitung Biaya per Pemain")
    if not st.session_state.selected_players:
        st.warning("⚠️ Pilih pemain dulu di Step 1!")
        st.stop()
    
    num_players = len(st.session_state.selected_players)
    total_cost = st.number_input("Total Biaya Lapangan (Rp)", min_value=0, value=0, step=50000, format="%d")
    
    if total_cost > 0:
        per_player = total_cost / num_players
        fmt = lambda v: f"{v:,.0f}".replace(",", ".")
        
        st.markdown(f"""
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
        """, unsafe_allow_html=True)
        
        st.subheader("📋 Tracking Status Pembayaran")
        payment_data = []
        for player in st.session_state.selected_players:
            # Use session state to remember payment status per player
            key = f"pay_{player}"
            if key not in st.session_state:
                st.session_state[key] = "Belum"
            status = st.selectbox(player, ["Belum", "Cicil", "Done"], key=key)
            payment_data.append({"Pemain": player, "Status": status})
        
        df_pay = pd.DataFrame(payment_data)
        st.dataframe(df_pay, use_container_width=True, hide_index=True)
        
        done = sum(1 for p in payment_data if p["Status"] == "Done")
        cicil = sum(1 for p in payment_data if p["Status"] == "Cicil")
        belum = sum(1 for p in payment_data if p["Status"] == "Belum")
        
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("✅ Done", done)
        col_b.metric("💳 Cicil", cicil)
        col_c.metric("⏳ Belum", belum)

# Footer
st.markdown("---")
st.markdown("<div style='text-align:center;color:#666;font-size:12px'><p>⚽ Futsal Tim Generator v2.0 (Streamlit)</p></div>", unsafe_allow_html=True)