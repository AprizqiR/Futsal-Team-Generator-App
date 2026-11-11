"""
============================================================
BIAENERGI FUTSAL ACADEMY — v5.6
============================================================
Menu : Home | Team | Team Generator | Match History | About
Data : JSON lokal (mudah migrasi ke Google Sheets)

Update v5.6:
  - Implementasi Palet Warna baru (Navy, Oranye, Emas)
  - UI Player Card: Mini Radar Chart
  - UI Team Card: Header konsisten, Radar Tim diperjelas, Tabel Rapi
  - Generate PNG: Layout baru (Header Navy, Radar Tim + Label, Mini Radar per pemain, Badge OVR)
  - Algoritma generate tim: Multi-Objective (Overall Rating + Stamina)
"""
import streamlit as st
import pandas as pd
import json
import os
import io
import math
import random
import base64
from pathlib import Path
from html import escape as esc
from collections import defaultdict
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="BIAENERGI Futsal Academy",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# 🎨 CSS BIAENERGI THEME (v5.6)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Orbitron:wght@700;900&display=swap');

:root {
  /* Palet Warna Baru */
  --bng-navy:#0B1B38;
  --bng-navy-sec:#10264D;
  --bng-blue:#1769C2;
  --bng-yellow:#FBBF24;
  --bng-gray-light:#EDF3F9;
  --bng-orange:#DC4B14;
  
  --bng-text-main:#f8fafc;
  --bng-text-dim:#94a3b8;
  --bng-glass:rgba(16,38,77,.6);
  --bng-glass-border:rgba(23,105,194,.3);
}

html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
}

.stApp {
  background:
    radial-gradient(circle at 10% 10%, rgba(23,105,194,.15), transparent 45%),
    radial-gradient(circle at 90% 90%, rgba(251,191,36,.08), transparent 50%),
    linear-gradient(160deg, #0B1B38 0%, #10264D 55%, #0B1B38 100%);
  background-attachment: fixed;
  min-height: 100vh;
  color: var(--bng-text-main);
}
.stApp::before {
  content:'';
  position:fixed; inset:0; pointer-events:none; z-index:0;
  background-image:
    linear-gradient(rgba(23,105,194,.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(23,105,194,.04) 1px, transparent 1px);
  background-size: 60px 60px;
  mask-image: radial-gradient(ellipse at center, black 30%, transparent 85%);
  -webkit-mask-image: radial-gradient(ellipse at center, black 30%, transparent 85%);
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { display: none; }

.block-container {
  padding-top: 1rem !important;
  padding-bottom: 3rem;
  max-width: 1400px;
  position: relative; z-index: 1;
}

h1, h2, h3 { letter-spacing: -.03em; font-weight: 800; color: #fff; }
p, li { color: #d1dce8; }
label { color: #cbd5e1 !important; }

/* ============ NAVBAR ============ */
.bng-navbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 24px;
  background: linear-gradient(90deg, rgba(16,38,77,.95), rgba(11,27,56,.9));
  border-radius: 20px;
  border: 1px solid rgba(23,105,194,.25);
  backdrop-filter: blur(14px);
  box-shadow: 0 10px 40px rgba(0,0,0,.35);
  margin-bottom: 22px;
}
.bng-logo { display: flex; align-items: center; gap: 14px; }
.bng-logo-badge {
  width: 52px; height: 52px; border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #ffffff, #dbeafe 60%, #93c5fd);
  display: flex; align-items: center; justify-content: center;
  font-size: 30px;
  box-shadow: 0 0 0 3px rgba(251,191,36,.35), 0 8px 20px rgba(0,0,0,.4);
  position: relative;
}
.bng-logo-badge::after {
  content: '👑'; position: absolute; top: -12px; font-size: 16px;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,.4));
}
.bng-logo-text { display: flex; flex-direction: column; line-height: 1.05; }
.bng-logo-title {
  font-weight: 900; font-size: 22px; letter-spacing: .02em; color: #ffffff;
  font-family: 'Orbitron', sans-serif;
}
.bng-logo-sub {
  font-weight: 800; font-size: 12px; letter-spacing: .32em;
  color: var(--bng-yellow); text-transform: uppercase;
}
.bng-slogan {
  text-align: right; font-style: italic;
  font-family: 'Orbitron', sans-serif;
  font-size: 14px; font-weight: 700;
  color: var(--bng-yellow);
  line-height: 1.1;
  text-shadow: 0 2px 8px rgba(251,191,36,.4);
}
.bng-slogan small {
  display: block; font-size: 9px; letter-spacing: .3em;
  color: #cbd5e1; margin-top: 4px; font-style: normal;
}

/* ============ HERO ============ */
.bng-hero {
  position: relative; overflow: hidden;
  border-radius: 26px;
  padding: 46px 50px;
  margin-bottom: 26px;
  min-height: 380px;
  border: 1px solid rgba(23,105,194,.3);
  background:
    linear-gradient(120deg, rgba(11,27,56,.92) 0%, rgba(16,38,77,.7) 60%, rgba(23,105,194,.5) 100%);
  box-shadow: 0 24px 60px rgba(0,0,0,.45);
}
.bng-hero-img {
  position: absolute; inset: 0;
  background-size: cover; background-position: center right;
  opacity: .35; z-index: 0;
}
.bng-hero-content { position: relative; z-index: 2; max-width: 580px; }
.bng-hero-kicker {
  display: inline-block; padding: 6px 16px;
  background: var(--bng-yellow); color: var(--bng-navy);
  font-weight: 900; font-size: 13px; font-style: italic;
  letter-spacing: .04em; transform: rotate(-2deg);
  border-radius: 4px; margin-bottom: 18px;
  box-shadow: 0 4px 14px rgba(251,191,36,.35);
}
.bng-hero h1 {
  font-family: 'Orbitron', sans-serif;
  font-size: clamp(2.2rem, 4.5vw, 3.6rem);
  font-weight: 900; line-height: 1.02; color: #fff;
  margin: 0 0 16px 0;
  text-shadow: 0 6px 24px rgba(0,0,0,.5);
  letter-spacing: -.02em;
}
.bng-hero h1 .hl { color: var(--bng-yellow); display: block; }
.bng-hero-quote {
  font-style: italic; font-size: 1.05rem; color: #e0ecf8;
  border-left: 4px solid var(--bng-yellow);
  padding-left: 14px; margin: 16px 0; line-height: 1.5;
}
.bng-hero-sub { font-size: .88rem; color: #b8c8dd; margin-top: 12px; }
.bng-hero-tag {
  position: absolute; right: 40px; top: 50%;
  transform: translateY(-50%); z-index: 2;
  text-align: center; font-family: 'Orbitron', sans-serif;
}
.bng-hero-tag .t1, .bng-hero-tag .t2, .bng-hero-tag .t3 {
  display: block; font-style: italic; font-weight: 900;
  color: var(--bng-yellow); line-height: 1.1;
  text-shadow: 0 4px 16px rgba(0,0,0,.6);
  font-size: 42px;
}

/* ============ SECTION ============ */
.bng-section {
  display: flex; align-items: center; gap: 12px;
  margin: 28px 0 16px 0;
}
.bng-section .icon { font-size: 24px; }
.bng-section h2 { margin: 0; font-size: 1.3rem; font-weight: 800; color: #fff; }
.bng-section .sub { color: var(--bng-text-dim); font-size: .85rem; margin-top: 2px; }

/* ============ STAT CARDS ============ */
.bng-stat-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px;
}
.bng-stat-card {
  background: var(--bng-glass);
  border: 1px solid var(--bng-glass-border);
  border-radius: 18px; padding: 20px 18px;
  backdrop-filter: blur(12px);
  transition: transform .2s, border-color .2s, box-shadow .2s;
  position: relative; overflow: hidden;
}
.bng-stat-card::before {
  content:''; position: absolute; top: 0; left: 0;
  width: 100%; height: 3px;
  background: linear-gradient(90deg, var(--bng-blue), var(--bng-yellow));
  opacity: .8;
}
.bng-stat-card:hover {
  transform: translateY(-4px);
  border-color: rgba(251,191,36,.5);
  box-shadow: 0 14px 34px rgba(251,191,36,.15);
}
.bng-stat-icon { font-size: 28px; margin-bottom: 10px; display: inline-block; }
.bng-stat-value {
  font-family: 'Orbitron', sans-serif;
  font-size: 34px; font-weight: 900;
  color: var(--bng-yellow);
  line-height: 1; margin: 6px 0 4px 0;
}
.bng-stat-label {
  font-size: .82rem; color: #cbd5e1; font-weight: 600;
  text-transform: uppercase; letter-spacing: .05em;
}

/* ============ ATTR BARS ============ */
.bng-attr-grid {
  display: grid; grid-template-columns: repeat(6, 1fr);
  gap: 12px; margin-top: 10px;
}
.bng-attr-card {
  background: var(--bng-glass);
  border: 1px solid var(--bng-glass-border);
  border-radius: 14px; padding: 14px;
  text-align: center; backdrop-filter: blur(12px);
}
.bng-attr-icon { font-size: 22px; margin-bottom: 6px; display: inline-block; }
.bng-attr-name {
  font-size: .78rem; font-weight: 700;
  color: #cbd5e1; margin-bottom: 6px;
  text-transform: uppercase; letter-spacing: .04em;
}
.bng-attr-value {
  font-family: 'Orbitron', sans-serif;
  font-size: 22px; font-weight: 900;
  color: #fff; margin-bottom: 8px;
}
.bng-attr-bar {
  height: 5px; border-radius: 3px;
  background: rgba(255,255,255,.08); overflow: hidden;
}
.bng-attr-bar-fill {
  height: 100%; border-radius: 3px;
  transition: width .8s cubic-bezier(.2,.8,.2,1);
}

/* ============ MORE BOX ============ */
.bng-more-box {
  background:
    radial-gradient(circle at 100% 0%, rgba(251,191,36,.15), transparent 55%),
    linear-gradient(135deg, rgba(16,38,77,.85), rgba(11,27,56,.9));
  border: 1px solid rgba(251,191,36,.35);
  border-radius: 22px; padding: 26px 24px;
  backdrop-filter: blur(14px);
  position: relative; overflow: hidden;
}
.bng-more-title {
  font-family: 'Orbitron', sans-serif;
  font-style: italic; font-size: 24px; font-weight: 900;
  color: var(--bng-yellow); line-height: 1.1;
  margin-bottom: 20px;
  text-shadow: 0 4px 14px rgba(251,191,36,.3);
}
.bng-more-title small {
  display: block; font-size: 12px; font-style: normal;
  letter-spacing: .3em; color: #cbd5e1;
  margin-top: 6px; font-family: 'Inter', sans-serif; font-weight: 700;
}
.bng-more-item {
  display: flex; align-items: flex-start; gap: 14px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(23,105,194,.15);
}
.bng-more-item:last-child { border-bottom: none; }
.bng-more-item .icon {
  width: 40px; height: 40px; border-radius: 50%;
  background: rgba(251,191,36,.15);
  border: 1px solid rgba(251,191,36,.4);
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; flex-shrink: 0;
}
.bng-more-item .txt strong {
  display: block; color: #fff; font-size: .95rem;
  font-weight: 700; margin-bottom: 2px;
}
.bng-more-item .txt span { color: #94a3b8; font-size: .8rem; }
.bng-more-tag {
  margin-top: 18px; display: inline-block;
  padding: 8px 18px;
  background: linear-gradient(90deg, var(--bng-yellow), #fde68a);
  color: var(--bng-navy);
  font-family: 'Orbitron', sans-serif;
  font-weight: 900; font-size: 13px;
  letter-spacing: .08em; border-radius: 6px;
  transform: skewX(-8deg);
  box-shadow: 0 4px 14px rgba(251,191,36,.4);
}
.bng-more-tag span { display: inline-block; transform: skewX(8deg); }

/* ============ PLAYER CARD ============ */
.bng-player-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 14px;
}
.bng-player-card {
  background: var(--bng-glass);
  border: 1px solid var(--bng-glass-border);
  border-radius: 16px; padding: 14px;
  backdrop-filter: blur(12px);
  display: flex; gap: 12px; align-items: center;
  transition: transform .22s cubic-bezier(.2,.8,.2,1), border-color .22s, box-shadow .22s;
  position: relative; overflow: hidden;
}
.bng-player-card::before {
  content:''; position: absolute; left: 0; top: 0;
  width: 3px; height: 100%;
  background: linear-gradient(180deg, var(--bng-yellow), #fde68a);
  opacity: 0; transition: opacity .2s;
}
.bng-player-card:hover {
  transform: translateY(-4px);
  border-color: rgba(251,191,36,.6);
  box-shadow: 0 14px 34px rgba(251,191,36,.15);
}
.bng-player-card:hover::before { opacity: 1; }

.bng-player-card svg {
  transition: transform 0.3s ease;
}
.bng-player-card:hover svg {
  transform: scale(1.1) rotate(5deg);
}

.bng-avatar {
  width: 56px; height: 56px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 900; font-size: 18px; color: #fff;
  flex-shrink: 0;
  border: 2px solid rgba(255,255,255,.2);
  box-shadow: 0 4px 12px rgba(0,0,0,.3);
  overflow: hidden; position: relative;
}
.bng-avatar img { width: 100%; height: 100%; object-fit: cover; }

.bng-player-info { min-width: 0; flex: 1; }
.bng-player-name {
  font-weight: 700; color: #fff;
  font-size: .95rem; line-height: 1.2;
  margin-bottom: 3px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.bng-player-alias {
  font-size: .72rem; color: var(--bng-text-dim);
  margin-bottom: 6px;
}
.bng-player-roles { display: flex; gap: 4px; flex-wrap: wrap; }
.bng-role-chip {
  display: inline-block; padding: 2px 8px;
  border-radius: 6px;
  font-size: 10px; font-weight: 800;
  letter-spacing: .04em;
}
.bng-role-chip.gk { background: rgba(251,191,36,.2); border: 1px solid rgba(251,191,36,.5); color: #fde68a; }
.bng-role-chip.a  { background: rgba(23,105,194,.25); border: 1px solid rgba(23,105,194,.5); color: #bfdbfe; }
.bng-role-chip.f  { background: rgba(34,197,94,.2); border: 1px solid rgba(34,197,94,.5); color: #bbf7d0; }
.bng-role-chip.p  { background: rgba(220,75,20,.2); border: 1px solid rgba(220,75,20,.5); color: #fecaca; }

.bng-ovr-badge {
  position: absolute; top: 10px; right: 10px;
  background: linear-gradient(135deg, var(--bng-yellow), #fde68a);
  color: var(--bng-navy);
  font-family: 'Orbitron', sans-serif;
  font-weight: 900; font-size: 13px;
  padding: 3px 9px; border-radius: 8px;
  box-shadow: 0 4px 10px rgba(251,191,36,.4);
}

/* ============ BUTTONS ============ */
.stButton > button {
  border: 1px solid rgba(251,191,36,.4) !important;
  border-radius: 12px !important;
  font-weight: 800 !important;
  background: linear-gradient(110deg, var(--bng-yellow), #fde68a) !important;
  color: var(--bng-navy) !important;
  box-shadow: 0 6px 18px rgba(251,191,36,.3) !important;
  transition: transform .16s, filter .16s, box-shadow .16s !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  filter: brightness(1.1) !important;
  box-shadow: 0 10px 24px rgba(251,191,36,.5) !important;
}
.stButton > button * { color: var(--bng-navy) !important; font-weight: 800 !important; }

.stButton > button[kind="secondary"] {
  background: linear-gradient(110deg, rgba(16,38,77,.8), rgba(23,105,194,.8)) !important;
  color: #fff !important;
  border-color: rgba(23,105,194,.6) !important;
}
.stButton > button[kind="secondary"] * { color: #fff !important; }

[data-testid="stDownloadButton"] button {
  background: linear-gradient(110deg, #16a34a, #22c55e) !important;
  color: #fff !important;
  border-color: rgba(34,197,94,.5) !important;
}
[data-testid="stDownloadButton"] button * { color: #fff !important; }

/* ============ FORM INPUTS ============ */
[data-baseweb="input"] > div,
[data-baseweb="select"] > div,
[data-baseweb="textarea"] > div {
  background: rgba(16,38,77,.85) !important;
  border-color: rgba(23,105,194,.3) !important;
  border-radius: 10px !important;
  color: #fff !important;
}
[data-baseweb="input"] input,
[data-baseweb="select"] span,
[data-baseweb="textarea"] textarea { color: #fff !important; }

[data-baseweb="tag"] {
  background: linear-gradient(110deg, var(--bng-yellow), #fde68a) !important;
  color: var(--bng-navy) !important;
  font-weight: 700 !important;
  border-radius: 6px !important;
}
[data-baseweb="tag"] * { color: var(--bng-navy) !important; }

/* ============ TABS ============ */
[data-baseweb="tab-list"] {
  background: rgba(16,38,77,.5);
  border-radius: 12px;
  padding: 5px;
  border: 1px solid rgba(23,105,194,.2);
}
[data-baseweb="tab"] {
  font-weight: 700 !important;
  border-radius: 8px !important;
  color: #94a3b8 !important;
  padding: 8px 18px !important;
}
[data-baseweb="tab"][aria-selected="true"] {
  background: linear-gradient(110deg, var(--bng-yellow), #fde68a) !important;
  color: var(--bng-navy) !important;
}
[data-baseweb="tab"][aria-selected="true"] * { color: var(--bng-navy) !important; }

/* ============ METRIC ============ */
[data-testid="stMetric"] {
  background: var(--bng-glass);
  border: 1px solid var(--bng-glass-border);
  border-radius: 14px;
  padding: 14px 18px;
  backdrop-filter: blur(12px);
}
[data-testid="stMetricValue"] {
  color: var(--bng-yellow) !important;
  font-family: 'Orbitron', sans-serif !important;
  font-weight: 900 !important;
}
[data-testid="stMetricLabel"] { color: #cbd5e1 !important; }

/* ============ PLACEHOLDER ============ */
.bng-placeholder {
  text-align: center; padding: 60px 30px;
  border-radius: 22px;
  background: var(--bng-glass);
  border: 2px dashed rgba(23,105,194,.3);
  backdrop-filter: blur(12px);
  margin: 16px 0;
}
.bng-placeholder .emoji {
  font-size: 64px; margin-bottom: 16px;
  filter: drop-shadow(0 6px 20px rgba(251,191,36,.3));
}
.bng-placeholder h3 { color: var(--bng-yellow); margin: 0 0 8px 0; }
.bng-placeholder p { color: #94a3b8; margin: 0; }

/* ============ RESULT TEAM CARD (v5.6 Update) ============ */
.bng-result-card {
  background: linear-gradient(135deg, rgba(16,38,77,.85), rgba(11,27,56,.95));
  border: 2px solid rgba(23,105,194,.35);
  border-radius: 20px;
  padding: 0;
  margin: 18px 0;
  backdrop-filter: blur(14px);
  box-shadow: 0 16px 40px rgba(0,0,0,.4);
  overflow: hidden;
}
.bng-result-header {
  padding: 16px 22px;
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 10px;
  border-bottom: 2px solid rgba(255,255,255,.08);
  background: var(--bng-navy-sec); /* Warna Navy Konsisten */
}
.bng-result-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 22px; font-weight: 900;
  color: #fff;
  display: flex; align-items: center; gap: 12px;
}
.bng-result-uniform {
  padding: 4px 14px;
  border-radius: 16px;
  font-size: 12px; font-weight: 800;
  border: 2px solid rgba(255,255,255,.35);
  letter-spacing: .04em;
}
.bng-result-rating {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px; font-weight: 900;
  background: linear-gradient(110deg, var(--bng-blue), var(--bng-yellow));
  color: #fff;
  font-family: 'Orbitron', sans-serif;
  box-shadow: 0 4px 12px rgba(251,191,36,.3);
}
.bng-result-body {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 0;
}
.bng-result-left { padding: 20px 22px; }
.bng-result-right {
  padding: 20px 18px;
  background: rgba(0,0,0,.2);
  border-left: 1px solid rgba(255,255,255,.06);
}
.bng-result-pitch {
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 12px;
}
.bng-result-form-info {
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.6;
  padding: 12px 14px;
  background: rgba(0,0,0,.25);
  border-radius: 10px;
  border-left: 3px solid var(--bng-yellow);
}
.bng-result-form-info b {
  color: var(--bng-yellow);
  display: block;
  margin-bottom: 4px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: .06em;
}

/* Roster list */
.bng-roster { margin-top: 14px; }
.bng-roster-title {
  font-size: 11px; font-weight: 800;
  color: var(--bng-yellow);
  text-transform: uppercase;
  letter-spacing: .1em;
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(251,191,36,.25);
}
.bng-roster-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 10px;
  margin-bottom: 6px;
  background: rgba(255,255,255,.03);
  border-left: 3px solid transparent;
  transition: all .18s;
}
.bng-roster-row:hover {
  background: rgba(251,191,36,.08);
  border-left-color: var(--bng-yellow);
  transform: translateX(3px);
}
.bng-roster-num {
  width: 26px; height: 26px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--bng-yellow), #fde68a);
  color: var(--bng-navy);
  font-weight: 900; font-size: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  font-family: 'Orbitron', sans-serif;
}
.bng-roster-avatar {
  width: 34px; height: 34px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 900; font-size: 11px;
  color: #fff;
  flex-shrink: 0;
  border: 2px solid rgba(255,255,255,.2);
  overflow: hidden;
}
.bng-roster-avatar img { width: 100%; height: 100%; object-fit: cover; }
.bng-roster-info { flex: 1; min-width: 0; }
.bng-roster-name {
  font-weight: 700; color: #fff; font-size: 13px;
  margin-bottom: 3px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.bng-roster-roles { display: flex; gap: 3px; flex-wrap: wrap; }
.bng-roster-role-chip {
  display: inline-block;
  padding: 1px 7px;
  border-radius: 5px;
  font-size: 9px;
  font-weight: 800;
  letter-spacing: .04em;
}
.bng-roster-role-chip.gk { background: rgba(251,191,36,.2); color: #fde68a; }
.bng-roster-role-chip.a  { background: rgba(23,105,194,.25); color: #bfdbfe; }
.bng-roster-role-chip.f  { background: rgba(34,197,94,.2); color: #bbf7d0; }
.bng-roster-role-chip.p  { background: rgba(220,75,20,.2); color: #fecaca; }
.bng-roster-ovr {
  font-family: 'Orbitron', sans-serif;
  font-weight: 900; font-size: 14px;
  color: var(--bng-yellow);
  flex-shrink: 0;
  min-width: 36px;
  text-align: right;
}

/* Balance bar */
.bng-balance-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 22px;
  border-radius: 16px;
  margin-top: 20px;
  background: linear-gradient(135deg, rgba(16,38,77,.9), rgba(11,27,56,.95));
  border: 2px solid rgba(23,105,194,.25);
  backdrop-filter: blur(12px);
  flex-wrap: wrap; gap: 12px;
}
.bng-balance-bar .label {
  font-size: 12px; color: #94a3b8;
  text-transform: uppercase; letter-spacing: .08em;
  font-weight: 700;
}
.bng-balance-bar .value {
  font-family: 'Orbitron', sans-serif;
  font-size: 22px; font-weight: 900;
}
.bng-balance-teams { display: flex; gap: 10px; flex-wrap: wrap; }
.bng-balance-team {
  padding: 6px 14px;
  border-radius: 10px;
  background: rgba(255,255,255,.05);
  border: 1px solid rgba(23,105,194,.2);
  font-size: 12px; color: #e0ecf8; font-weight: 700;
}
.bng-balance-team b { color: var(--bng-yellow); }

/* ============ MATCH CARD ============ */
.bng-match-card {
  background: var(--bng-glass);
  border: 1px solid var(--bng-glass-border);
  border-radius: 16px;
  padding: 18px;
  margin: 12px 0;
  backdrop-filter: blur(12px);
}
.bng-match-header {
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 10px;
  margin-bottom: 12px;
}
.bng-match-id {
  font-family: 'Orbitron', sans-serif;
  font-weight: 900; color: var(--bng-yellow);
  font-size: 14px;
}
.bng-match-date { font-size: 12px; color: #94a3b8; }
.bng-match-score {
  display: flex; align-items: center; justify-content: center;
  gap: 20px; margin: 12px 0;
}
.bng-match-team { flex: 1; text-align: center; }
.bng-match-team .name {
  font-weight: 800; color: #fff;
  font-size: 15px; margin-bottom: 4px;
}
.bng-match-team .uniform { font-size: 11px; color: #94a3b8; }
.bng-match-score-num {
  font-family: 'Orbitron', sans-serif;
  font-size: 36px; font-weight: 900;
  color: var(--bng-yellow);
  min-width: 90px; text-align: center;
}

/* ============ RADAR SECTION ============ */
.bng-radar-section {
  margin: 30px 0 20px 0;
  padding: 24px;
  background: linear-gradient(135deg, rgba(16,38,77,.75), rgba(11,27,56,.85));
  border: 1px solid rgba(23,105,194,.3);
  border-radius: 22px;
  backdrop-filter: blur(14px);
}
.bng-radar-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 18px; font-weight: 900;
  color: var(--bng-yellow);
  letter-spacing: .04em;
  margin-bottom: 4px;
}
.bng-radar-sub {
  font-size: 12px; color: #94a3b8;
  margin-bottom: 16px;
}

/* ============ TIPS BOX (regenerate) ============ */
.bng-tip-box {
  background: rgba(23,105,194,.1);
  border: 1px solid rgba(23,105,194,.4);
  border-radius: 12px;
  padding: 14px 18px;
  margin-bottom: 16px;
}
.bng-tip-box .title {
  font-weight: 800; color: #60a5fa; margin-bottom: 4px;
}
.bng-tip-box .desc { font-size: 12px; color: #94a3b8; }

/* ============ SAVE BOX ============ */
.bng-save-box {
  background: linear-gradient(135deg, rgba(251,191,36,.12), rgba(245,158,11,.06));
  border: 2px solid rgba(251,191,36,.4);
  border-radius: 16px;
  padding: 20px 24px;
  margin: 20px 0 8px 0;
}

/* Stats bar (counter + gap history) */
.bng-stats-bar {
  display: flex; gap: 12px; flex-wrap: wrap;
  padding: 12px 16px;
  background: rgba(16,38,77,.5);
  border: 1px solid rgba(23,105,194,.2);
  border-radius: 12px;
  margin-bottom: 14px;
  font-size: 12px;
}
.bng-stats-bar .item {
  display: flex; align-items: center; gap: 6px;
  color: #cbd5e1;
}
.bng-stats-bar .item b { color: var(--bng-yellow); font-weight: 800; }

/* ============ FOOTER ============ */
.bng-footer {
  margin-top: 40px; padding: 24px;
  border-radius: 18px;
  background: var(--bng-glass);
  border: 1px solid var(--bng-glass-border);
  text-align: center;
  backdrop-filter: blur(12px);
}
.bng-footer .brand {
  font-family: 'Orbitron', sans-serif;
  font-weight: 900;
  background: linear-gradient(110deg, var(--bng-yellow), #fde68a);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: .06em;
}
.bng-footer small { color: #64748b; }

/* ============ ANIMATION ============ */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}
.bng-animate { animation: fadeInUp .5s cubic-bezier(.2,.8,.2,1) both; }

/* ============ RESPONSIVE ============ */
@media (max-width: 900px) {
  .bng-stat-grid { grid-template-columns: repeat(2, 1fr); }
  .bng-attr-grid { grid-template-columns: repeat(3, 1fr); }
  .bng-hero-tag { display: none; }
  .bng-hero { padding: 30px 24px; }
  .bng-result-body { grid-template-columns: 1fr; }
  .bng-result-right { border-left: none; border-top: 1px solid rgba(255,255,255,.06); }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# PATH & KONSTANTA
# ==========================================
BASE_DIR = Path(__file__).parent.resolve()
PLAYERS_DB = BASE_DIR / "players_db.json"
MATCH_HISTORY = BASE_DIR / "match_history.json"
LAST_GENERATE = BASE_DIR / "last_generate.json"
AVATARS_DIR = BASE_DIR / "assets" / "avatars"
HERO_IMG = BASE_DIR / "assets" / "hero.png"

ROLE_INFO = {
    "GK": {"nama": "Kiper",  "emoji": "🧤", "css": "gk"},
    "A":  {"nama": "Anchor", "emoji": "⚓", "css": "a"},
    "F":  {"nama": "Flank",  "emoji": "🪽", "css": "f"},
    "P":  {"nama": "Pivot",  "emoji": "🔥", "css": "p"},
}
ROLE_KEYS = ["GK", "A", "F", "P"]

PHY_COLS = ["STA", "AKS", "SPR", "AGI", "BAL", "STR"]
TEC_COLS = ["CON", "DRI", "PAS", "SHA", "SHP", "TAC"]
MTC_COLS = ["VIS", "OFB", "COM", "AGR", "TMW"]
GKS_COLS = ["DEC", "REF", "POS", "THR", "KIC", "BRV"]
ALL_ATTRS = PHY_COLS + TEC_COLS + MTC_COLS + GKS_COLS

ATTR_CATEGORIES = {
    "Speed":    {"emoji": "🏃", "cols": ["STA", "AKS", "SPR", "AGI"], "color": "#1769C2"},
    "Shooting": {"emoji": "🎯", "cols": ["SHA", "SHP"],               "color": "#DC4B14"},
    "Defense":  {"emoji": "🛡️", "cols": ["TAC", "STR", "BAL"],        "color": "#22c55e"},
    "Tactics":  {"emoji": "🧠", "cols": ["VIS", "OFB", "DEC"],        "color": "#a855f7"},
    "Teamwork": {"emoji": "🤝", "cols": ["TMW", "COM"],               "color": "#FBBF24"},
    "Mood":     {"emoji": "😊", "cols": ["BRV", "AGR"],               "color": "#ef4444"},
}

UNIFORM_OPTIONS = ["Biru", "Putih", "Merah", "Kuning", "Ungu", "Hitam", "Hijau"]
COLOR_MAP = {
    "Biru": "#1769C2", "Putih": "#ffffff", "Merah": "#d32f2f",
    "Kuning": "#FBBF24", "Ungu": "#7b1fa2", "Hitam": "#212121",
    "Hijau": "#388e3c", "Abu-abu": "#757575",
}
DARK_UNIFORMS = ["Hitam", "Biru", "Merah", "Ungu", "Hijau"]

FORMATIONS = {
    "Diamond (1-2-1)": {
        "pola": "1 Anchor • 2 Flank • 1 Pivot",
        "karakter": "Seimbang antara bertahan & menyerang. Formasi paling populer.",
        "sketsa": "[Pivot] [Flank] [Flank] [Anchor]",
        "positions": [{"label": "GK", "x": 8, "y": 50}, {"label": "A", "x": 28, "y": 50},
                      {"label": "F", "x": 52, "y": 22}, {"label": "F", "x": 52, "y": 78},
                      {"label": "P", "x": 78, "y": 50}],
    },
    "Pyramid / Wall (2-1-1)": {
        "pola": "2 Defender • 1 Midfielder • 1 Pivot",
        "karakter": "Defensif kokoh. Cocok untuk counter attack.",
        "sketsa": "[Pivot] [Midfielder] [Def] [Def]",
        "positions": [{"label": "GK", "x": 8, "y": 50}, {"label": "A", "x": 28, "y": 32},
                      {"label": "A", "x": 28, "y": 68}, {"label": "F", "x": 55, "y": 50},
                      {"label": "P", "x": 80, "y": 50}],
    },
    "The Box / Square (2-2)": {
        "pola": "2 Belakang • 2 Depan (sejajar)",
        "karakter": "Fleksibel & simetris. Butuh komunikasi intens.",
        "sketsa": "[Pivot] [Pivot] [Def] [Def]",
        "positions": [{"label": "GK", "x": 8, "y": 50}, {"label": "A", "x": 32, "y": 30},
                      {"label": "A", "x": 32, "y": 70}, {"label": "P", "x": 72, "y": 30},
                      {"label": "P", "x": 72, "y": 70}],
    },
    "Formasi Y (1-1-2)": {
        "pola": "1 Anchor • 1 Midfielder • 2 Pivot",
        "karakter": "Agresif. High pressing dengan 2 penyerang.",
        "sketsa": "[Pivot] [Pivot] [Midfielder] [Anchor]",
        "positions": [{"label": "GK", "x": 8, "y": 50}, {"label": "A", "x": 28, "y": 50},
                      {"label": "F", "x": 52, "y": 50}, {"label": "P", "x": 78, "y": 30},
                      {"label": "P", "x": 78, "y": 70}],
    },
    "Park the Bus (3-1)": {
        "pola": "3 Defender • 1 Pivot",
        "karakter": "Defensif total. Untuk mempertahankan skor.",
        "sketsa": "[Pivot] [Def][Def][Def]",
        "positions": [{"label": "GK", "x": 8, "y": 50}, {"label": "A", "x": 30, "y": 22},
                      {"label": "A", "x": 30, "y": 50}, {"label": "A", "x": 30, "y": 78},
                      {"label": "P", "x": 72, "y": 50}],
    },
    "Total / Flat (4-0)": {
        "pola": "4 Pemain Sejajar (dinamis)",
        "karakter": "Rotasi dinamis tanpa pivot murni.",
        "sketsa": "[P1] [P2] [P3] [P4] (Sejajar)",
        "positions": [{"label": "GK", "x": 8, "y": 50}, {"label": "F", "x": 48, "y": 18},
                      {"label": "F", "x": 48, "y": 40}, {"label": "F", "x": 48, "y": 60},
                      {"label": "F", "x": 48, "y": 82}],
    },
}

AVATAR_COLORS = ["#1769C2", "#22c55e", "#DC4B14", "#a855f7",
                 "#FBBF24", "#06b6d4", "#ec4899", "#6366f1"]

MAX_LOGIN_ATTEMPTS = 5
DEFAULT_ADMIN_PASSWORD = "BIAFUTSAL"

# ==========================================
# SEED DATA
# ==========================================
SEED_PLAYERS = [
    {"id": "P001", "nama": "Ade Suryadana",     "alias": "Ade",     "overall": 100, "positions": ["F", "GK", "P", "A"], "attributes": {"STA": 95, "AKS": 99, "SPR": 98, "AGI": 99, "BAL": 94, "STR": 96, "CON": 95, "DRI": 98, "PAS": 94, "SHA": 99, "SHP": 99, "TAC": 88, "VIS": 90, "OFB": 93, "COM": 91, "AGR": 94, "TMW": 92, "DEC": 78, "REF": 76, "POS": 77, "THR": 74, "KIC": 76, "BRV": 79}},
    {"id": "P002", "nama": "Aldo S.",           "alias": "Aldo",    "overall": 95,  "positions": ["A", "P", "GK", "F"], "attributes": {"STA": 65, "AKS": 90, "SPR": 88, "AGI": 94, "BAL": 96, "STR": 93, "CON": 91, "DRI": 93, "PAS": 95, "SHA": 89, "SHP": 90, "TAC": 97, "VIS": 96, "OFB": 95, "COM": 94, "AGR": 92, "TMW": 93, "DEC": 85, "REF": 82, "POS": 84, "THR": 80, "KIC": 83, "BRV": 86}},
    {"id": "P003", "nama": "Aprizqi R",         "alias": "AP",      "overall": 95,  "positions": ["A", "P", "F", "GK"], "attributes": {"STA": 80, "AKS": 90, "SPR": 88, "AGI": 94, "BAL": 96, "STR": 93, "CON": 91, "DRI": 93, "PAS": 95, "SHA": 89, "SHP": 90, "TAC": 97, "VIS": 96, "OFB": 95, "COM": 94, "AGR": 92, "TMW": 93, "DEC": 85, "REF": 82, "POS": 84, "THR": 80, "KIC": 83, "BRV": 86}},
    {"id": "P004", "nama": "Arby R",            "alias": "Byrus",   "overall": 100, "positions": ["A", "P", "F", "GK"], "attributes": {"STA": 95, "AKS": 95, "SPR": 93, "AGI": 99, "BAL": 99, "STR": 98, "CON": 96, "DRI": 98, "PAS": 99, "SHA": 94, "SHP": 95, "TAC": 99, "VIS": 99, "OFB": 99, "COM": 98, "AGR": 97, "TMW": 98, "DEC": 90, "REF": 87, "POS": 89, "THR": 85, "KIC": 88, "BRV": 91}},
    {"id": "P005", "nama": "Fadhli D. Ikram",   "alias": "Dzil",    "overall": 95,  "positions": ["A", "P", "GK", "F"], "attributes": {"STA": 65, "AKS": 90, "SPR": 88, "AGI": 94, "BAL": 96, "STR": 93, "CON": 91, "DRI": 93, "PAS": 95, "SHA": 89, "SHP": 90, "TAC": 97, "VIS": 96, "OFB": 95, "COM": 94, "AGR": 92, "TMW": 93, "DEC": 85, "REF": 82, "POS": 84, "THR": 80, "KIC": 83, "BRV": 86}},
    {"id": "P006", "nama": "Farhan I. A.",      "alias": "Han",     "overall": 70,  "positions": ["P", "A", "F", "GK"], "attributes": {"STA": 65, "AKS": 73, "SPR": 70, "AGI": 74, "BAL": 78, "STR": 76, "CON": 74, "DRI": 76, "PAS": 73, "SHA": 79, "SHP": 80, "TAC": 71, "VIS": 72, "OFB": 74, "COM": 72, "AGR": 75, "TMW": 73, "DEC": 64, "REF": 62, "POS": 63, "THR": 60, "KIC": 62, "BRV": 65}},
    {"id": "P007", "nama": "Geraldo H.",        "alias": "Geraldo", "overall": 80,  "positions": ["A", "GK", "P", "F"], "attributes": {"STA": 65, "AKS": 80, "SPR": 78, "AGI": 84, "BAL": 86, "STR": 83, "CON": 81, "DRI": 83, "PAS": 85, "SHA": 79, "SHP": 80, "TAC": 87, "VIS": 86, "OFB": 85, "COM": 84, "AGR": 82, "TMW": 83, "DEC": 75, "REF": 72, "POS": 74, "THR": 70, "KIC": 73, "BRV": 76}},
    {"id": "P008", "nama": "Hanz Seca",         "alias": "Hanz",    "overall": 60,  "positions": ["GK", "A", "P", "F"], "attributes": {"STA": 65, "AKS": 59, "SPR": 57, "AGI": 60, "BAL": 62, "STR": 63, "CON": 58, "DRI": 60, "PAS": 58, "SHA": 56, "SHP": 57, "TAC": 62, "VIS": 65, "OFB": 68, "COM": 67, "AGR": 66, "TMW": 68, "DEC": 70, "REF": 72, "POS": 71, "THR": 69, "KIC": 70, "BRV": 73}},
    {"id": "P009", "nama": "Ibrahim",           "alias": "Bacing",  "overall": 90,  "positions": ["F", "P", "A", "GK"], "attributes": {"STA": 60, "AKS": 85, "SPR": 92, "AGI": 87, "BAL": 89, "STR": 86, "CON": 85, "DRI": 88, "PAS": 84, "SHA": 90, "SHP": 91, "TAC": 82, "VIS": 84, "OFB": 86, "COM": 83, "AGR": 87, "TMW": 85, "DEC": 72, "REF": 70, "POS": 71, "THR": 68, "KIC": 70, "BRV": 73}},
    {"id": "P010", "nama": "Jehua Kusuma Dewa", "alias": "Jeje",    "overall": 70,  "positions": ["A", "F", "P", "GK"], "attributes": {"STA": 75, "AKS": 70, "SPR": 68, "AGI": 74, "BAL": 76, "STR": 73, "CON": 71, "DRI": 73, "PAS": 75, "SHA": 69, "SHP": 70, "TAC": 77, "VIS": 76, "OFB": 75, "COM": 74, "AGR": 72, "TMW": 73, "DEC": 65, "REF": 62, "POS": 64, "THR": 60, "KIC": 63, "BRV": 66}},
    {"id": "P011", "nama": "M. Ardhana W. N.",  "alias": "Ardha",   "overall": 60,  "positions": ["GK", "A", "P", "F"], "attributes": {"STA": 70, "AKS": 59, "SPR": 57, "AGI": 60, "BAL": 62, "STR": 63, "CON": 58, "DRI": 60, "PAS": 58, "SHA": 56, "SHP": 57, "TAC": 62, "VIS": 65, "OFB": 68, "COM": 67, "AGR": 66, "TMW": 68, "DEC": 70, "REF": 72, "POS": 71, "THR": 69, "KIC": 70, "BRV": 73}},
    {"id": "P012", "nama": "M. Daffa A.",       "alias": "Daffa",   "overall": 95,  "positions": ["F", "A", "P", "GK"], "attributes": {"STA": 70, "AKS": 92, "SPR": 96, "AGI": 92, "BAL": 94, "STR": 91, "CON": 90, "DRI": 93, "PAS": 89, "SHA": 95, "SHP": 96, "TAC": 87, "VIS": 88, "OFB": 90, "COM": 88, "AGR": 91, "TMW": 89, "DEC": 72, "REF": 70, "POS": 71, "THR": 68, "KIC": 70, "BRV": 73}},
    {"id": "P013", "nama": "M. Zidan G.",       "alias": "Zidan",   "overall": 100, "positions": ["F", "P", "A", "GK"], "attributes": {"STA": 95, "AKS": 95, "SPR": 98, "AGI": 99, "BAL": 97, "STR": 99, "CON": 96, "DRI": 98, "PAS": 95, "SHA": 99, "SHP": 99, "TAC": 89, "VIS": 90, "OFB": 92, "COM": 90, "AGR": 93, "TMW": 91, "DEC": 74, "REF": 72, "POS": 73, "THR": 70, "KIC": 72, "BRV": 75}},
    {"id": "P014", "nama": "Mahardhyka P.",     "alias": "Dhyka",   "overall": 90,  "positions": ["P", "F", "A", "GK"], "attributes": {"STA": 80, "AKS": 90, "SPR": 88, "AGI": 89, "BAL": 94, "STR": 91, "CON": 90, "DRI": 92, "PAS": 94, "SHA": 88, "SHP": 89, "TAC": 96, "VIS": 95, "OFB": 94, "COM": 93, "AGR": 91, "TMW": 92, "DEC": 72, "REF": 70, "POS": 71, "THR": 68, "KIC": 70, "BRV": 73}},
    {"id": "P015", "nama": "Martin Koko",       "alias": "Martin",  "overall": 90,  "positions": ["A", "GK", "P", "F"], "attributes": {"STA": 95, "AKS": 85, "SPR": 82, "AGI": 89, "BAL": 91, "STR": 88, "CON": 86, "DRI": 88, "PAS": 90, "SHA": 84, "SHP": 85, "TAC": 92, "VIS": 91, "OFB": 90, "COM": 89, "AGR": 87, "TMW": 88, "DEC": 80, "REF": 77, "POS": 79, "THR": 75, "KIC": 78, "BRV": 81}},
    {"id": "P016", "nama": "Musyaffa C. M.",    "alias": "Mus",     "overall": 75,  "positions": ["A", "P", "F", "GK"], "attributes": {"STA": 80, "AKS": 75, "SPR": 73, "AGI": 79, "BAL": 81, "STR": 78, "CON": 76, "DRI": 78, "PAS": 80, "SHA": 74, "SHP": 75, "TAC": 82, "VIS": 81, "OFB": 80, "COM": 79, "AGR": 77, "TMW": 78, "DEC": 70, "REF": 67, "POS": 69, "THR": 65, "KIC": 68, "BRV": 71}},
    {"id": "P017", "nama": "Naufal Y.",         "alias": "Naufal",  "overall": 70,  "positions": ["A", "P", "F", "GK"], "attributes": {"STA": 90, "AKS": 70, "SPR": 68, "AGI": 74, "BAL": 76, "STR": 73, "CON": 71, "DRI": 73, "PAS": 75, "SHA": 69, "SHP": 70, "TAC": 77, "VIS": 76, "OFB": 75, "COM": 74, "AGR": 72, "TMW": 73, "DEC": 65, "REF": 62, "POS": 64, "THR": 60, "KIC": 63, "BRV": 66}},
    {"id": "P018", "nama": "Nur Sahrul",        "alias": "Aloenk",  "overall": 95,  "positions": ["F", "P", "A", "GK"], "attributes": {"STA": 70, "AKS": 92, "SPR": 96, "AGI": 92, "BAL": 94, "STR": 91, "CON": 90, "DRI": 93, "PAS": 89, "SHA": 95, "SHP": 96, "TAC": 87, "VIS": 88, "OFB": 90, "COM": 88, "AGR": 91, "TMW": 89, "DEC": 72, "REF": 70, "POS": 71, "THR": 68, "KIC": 70, "BRV": 73}},
    {"id": "P019", "nama": "R. Hafis M.",       "alias": "Fis",     "overall": 90,  "positions": ["F", "GK", "A", "P"], "attributes": {"STA": 75, "AKS": 85, "SPR": 92, "AGI": 87, "BAL": 89, "STR": 86, "CON": 85, "DRI": 88, "PAS": 84, "SHA": 90, "SHP": 91, "TAC": 82, "VIS": 84, "OFB": 86, "COM": 83, "AGR": 87, "TMW": 85, "DEC": 78, "REF": 80, "POS": 79, "THR": 77, "KIC": 78, "BRV": 81}},
    {"id": "P020", "nama": "Rafi M. A.",        "alias": "Rafi",    "overall": 80,  "positions": ["A", "P", "F", "GK"], "attributes": {"STA": 65, "AKS": 80, "SPR": 78, "AGI": 84, "BAL": 86, "STR": 83, "CON": 81, "DRI": 83, "PAS": 85, "SHA": 79, "SHP": 80, "TAC": 87, "VIS": 86, "OFB": 85, "COM": 84, "AGR": 82, "TMW": 83, "DEC": 75, "REF": 72, "POS": 74, "THR": 70, "KIC": 73, "BRV": 76}},
    {"id": "P021", "nama": "Rafif Kusuma",      "alias": "RaKus",   "overall": 70,  "positions": ["A", "P", "F", "GK"], "attributes": {"STA": 95, "AKS": 70, "SPR": 68, "AGI": 74, "BAL": 76, "STR": 73, "CON": 71, "DRI": 73, "PAS": 75, "SHA": 69, "SHP": 70, "TAC": 77, "VIS": 76, "OFB": 75, "COM": 74, "AGR": 72, "TMW": 73, "DEC": 65, "REF": 62, "POS": 64, "THR": 60, "KIC": 63, "BRV": 66}},
    {"id": "P022", "nama": "Teguh A. R.",       "alias": "PapiKai", "overall": 80,  "positions": ["GK", "A", "P", "F"], "attributes": {"STA": 65, "AKS": 80, "SPR": 78, "AGI": 84, "BAL": 86, "STR": 83, "CON": 81, "DRI": 83, "PAS": 85, "SHA": 79, "SHP": 80, "TAC": 87, "VIS": 86, "OFB": 85, "COM": 84, "AGR": 82, "TMW": 83, "DEC": 78, "REF": 80, "POS": 79, "THR": 77, "KIC": 78, "BRV": 81}},
    {"id": "P023", "nama": "Yadhit P.",         "alias": "Yadhit",  "overall": 75,  "positions": ["A", "GK", "P", "F"], "attributes": {"STA": 70, "AKS": 75, "SPR": 73, "AGI": 79, "BAL": 81, "STR": 78, "CON": 76, "DRI": 78, "PAS": 80, "SHA": 74, "SHP": 75, "TAC": 82, "VIS": 81, "OFB": 80, "COM": 79, "AGR": 77, "TMW": 78, "DEC": 73, "REF": 75, "POS": 74, "THR": 72, "KIC": 73, "BRV": 76}},
]


def seed_players():
    result = []
    for p in SEED_PLAYERS:
        roles = list(dict.fromkeys(p["positions"]))
        result.append({
            "id": p["id"],
            "nama": p["nama"],
            "alias": p["alias"],
            "overall": p["overall"],
            "roles": roles,
            "main_position": p["positions"][0],
            "positions": {
                "1st": p["positions"][0],
                "2nd": p["positions"][1],
                "3rd": p["positions"][2],
                "4th": p["positions"][3],
            },
            "attributes": p["attributes"],
            "photo_url": "",
        })
    return result


# ==========================================
# DATA STORE LAYER
# ==========================================
class JSONStore:
    def __init__(self, players_path: Path, match_path: Path):
        self.players_path = players_path
        self.match_path = match_path

    def get_players(self) -> list:
        if not self.players_path.exists():
            data = seed_players()
            self._write_json(self.players_path, data)
            return data
        try:
            with open(self.players_path, encoding="utf-8") as f:
                data = json.load(f)
            if not data:
                data = seed_players()
                self._write_json(self.players_path, data)
            return data
        except (OSError, ValueError):
            data = seed_players()
            self._write_json(self.players_path, data)
            return data

    def save_players(self, players: list) -> bool:
        return self._write_json(self.players_path, players)

    def get_match_history(self) -> list:
        if not self.match_path.exists():
            self._write_json(self.match_path, [])
            return []
        try:
            with open(self.match_path, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return []

    def save_match_history(self, matches: list) -> bool:
        return self._write_json(self.match_path, matches)

    @staticmethod
    def _write_json(path: Path, data) -> bool:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except OSError:
            return False


store = JSONStore(PLAYERS_DB, MATCH_HISTORY)


# ==========================================
# PERSISTENSI HASIL GENERATE
# ==========================================
def save_last_generate(res: dict) -> bool:
    try:
        data = {
            "teams": res["teams"],
            "formations": res["formations"],
            "uniforms": res["uniforms"],
            "roles_map": res["roles_map"],
            "ratings_map": res["ratings_map"],
            "timestamp": res["timestamp"],
        }
        with open(LAST_GENERATE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def load_last_generate():
    try:
        if not LAST_GENERATE.exists():
            return None
        with open(LAST_GENERATE, encoding="utf-8") as f:
            data = json.load(f)
        # Need team names: load players to get uniforms
        players = load_players()
        uniforms = [p.get("uniform", "Putih") for p in players if p.get("uniform")]
        # Generate names from uniforms if not present
        generated_names = generate_team_names(uniforms)
        data["teams"] = data.get("teams", [])
        data["uniforms"] = data.get("uniforms", [])
        if data["teams"] and data["uniforms"]:
            data["team_names"] = generated_names[:len(data["teams"])]
        data["png"] = render_teams_png(
            data["teams"], data["formations"], data["uniforms"],
            data["roles_map"], data["ratings_map"], data.get("team_names"), load_players()
        )
        return data
    except Exception:
        return None


def clear_last_generate():
    try:
        if LAST_GENERATE.exists():
            LAST_GENERATE.unlink()
    except Exception:
        pass


# ==========================================
# UTILITAS
# ==========================================
def get_admin_password() -> str:
    try:
        pw = st.secrets.get("ADMIN_PASSWORD")
    except Exception:
        pw = None
    return str(pw) if pw else os.environ.get("ADMIN_PASSWORD") or DEFAULT_ADMIN_PASSWORD


def initials(name: str) -> str:
    words = [w.strip(".") for w in name.replace("-", " ").split() if w.strip(".")]
    if not words:
        return "?"
    if len(words) == 1:
        return words[0][:2].upper()
    return (words[0][0] + words[1][0]).upper()


def color_for(name: str) -> str:
    return AVATAR_COLORS[sum(ord(c) for c in name) % len(AVATAR_COLORS)]


def image_to_base64(path: Path) -> str | None:
    try:
        if not path.exists():
            return None
        with open(path, "rb") as f:
            data = f.read()
        ext = path.suffix.lower().lstrip(".")
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                "gif": "image/gif", "webp": "image/webp"}.get(ext, "image/png")
        return f"data:{mime};base64,{base64.b64encode(data).decode()}"
    except Exception:
        return None


def resolve_avatar(player: dict, size: int = 56, css_class: str = "bng-avatar") -> str:
    pid = player.get("id", "")
    for ext in ("png", "jpg", "jpeg", "webp"):
        img_path = AVATARS_DIR / f"{pid}.{ext}"
        b64 = image_to_base64(img_path)
        if b64:
            return (f"<div class='{css_class}' style='background:{color_for(player['nama'])};"
                    f"width:{size}px;height:{size}px'>"
                    f"<img src='{b64}' alt='{esc(player['nama'])}'></div>")
    url = (player.get("photo_url") or "").strip()
    if url:
        return (f"<div class='{css_class}' style='background:{color_for(player['nama'])};"
                f"width:{size}px;height:{size}px'>"
                f"<img src='{esc(url)}' alt='{esc(player['nama'])}' "
                f"onerror=\"this.style.display='none'\"></div>")
    return (f"<div class='{css_class}' style='background:{color_for(player['nama'])};"
            f"width:{size}px;height:{size}px'>{esc(initials(player['nama']))}</div>")


def role_chip_html(role: str) -> str:
    info = ROLE_INFO.get(role, {})
    return f"<span class='bng-role-chip {info.get('css', '')}'>{role}</span>"


def hero_background_css() -> str:
    b64 = image_to_base64(HERO_IMG)
    return f"background-image: url('{b64}');" if b64 else ""


def flat_html(s: str) -> str:
    return " ".join(line.strip() for line in s.splitlines() if line.strip())


# ==========================================
# SESSION STATE
# ==========================================
_defaults = {
    "page": "Home",
    "is_admin": False,
    "login_open": False,
    "login_attempts": 0,
    "players_cache": None,
    "flash": None,
    "gen_selected": None,
    "gen_rules": [],
    "gen_uniform_rules": {},
    "gen_num_teams": 2,
    "gen_team_uniforms": [],
    "gen_result": None,
    "gen_result_loaded": False,
    "show_save_form": False,
    "gen_count": 0,
    "gen_history": [],
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if not st.session_state.gen_result_loaded:
    loaded = load_last_generate()
    if loaded:
        st.session_state.gen_result = loaded
    st.session_state.gen_result_loaded = True


def load_players(force: bool = False) -> list:
    if st.session_state.players_cache is None or force:
        st.session_state.players_cache = store.get_players()
    return st.session_state.players_cache


def refresh_players():
    st.session_state.players_cache = store.get_players()


# ==========================================
# CALLBACKS
# ==========================================
def do_login():
    pw = st.session_state.get("login_pw", "")
    if pw == get_admin_password():
        st.session_state.is_admin = True
        st.session_state.login_attempts = 0
        st.session_state.login_open = False
        st.session_state.flash = ("success", "✅ Login berhasil. Mode admin aktif.")
    else:
        st.session_state.login_attempts += 1
        left = MAX_LOGIN_ATTEMPTS - st.session_state.login_attempts
        if left <= 0:
            st.session_state.flash = ("error", "⛔ Terlalu banyak percobaan salah.")
            st.session_state.login_open = False
        else:
            st.session_state.flash = ("error", f"❌ Password salah. Sisa: {left}")


def do_logout():
    st.session_state.is_admin = False
    st.session_state.flash = ("info", "🔒 Logout. Mode admin nonaktif.")


# ==========================================
# TEAM GENERATOR ENGINE (MULTI-OBJECTIVE)
# ==========================================
def generate_teams_v2(players, roles_map, ratings, stamina_map, rules, num_teams, team_uniforms_in, uniform_rules):
    players = players[:]

    def get_rating(p): return ratings.get(p, 50)
    def get_stamina(p): return stamina_map.get(p, 50)

    conflicts = defaultdict(set)
    for p1, p2 in rules:
        conflicts[p1].add(p2)
        conflicts[p2].add(p1)

    gks = [p for p in players if "GK" in roles_map.get(p, [])]
    non_gks = [p for p in players if "GK" not in roles_map.get(p, [])]
    teams = [[] for _ in range(num_teams)]

    def team_ovr(i): return sum(get_rating(p) for p in teams[i])
    def team_sta(i): return sum(get_stamina(p) for p in teams[i])
    def team_size(i): return len(teams[i])
    
    def conflict_with_team(player, tidx):
        return any(t in conflicts.get(player, set()) for t in teams[tidx])
    def valid_teams(player):
        v = [i for i in range(num_teams) if not conflict_with_team(player, i)]
        return v if v else list(range(num_teams))

    gks_sorted = sorted(gks, key=get_rating, reverse=True)
    random.shuffle(gks_sorted)
    gks_sorted = sorted(gks_sorted, key=get_rating, reverse=True)
    
    for gk in gks_sorted[:num_teams]:
        candidates = valid_teams(gk)
        best = min(candidates, key=lambda i: (team_ovr(i), team_sta(i), team_size(i)))
        teams[best].append(gk)

    remaining_gks = gks_sorted[num_teams:]
    remaining = non_gks + remaining_gks
    random.shuffle(remaining)
    remaining.sort(key=lambda p: (get_rating(p), get_stamina(p)), reverse=True)

    for player in remaining:
        candidates = valid_teams(player)
        def score(i, player=player):
            team_roles = [r for p in teams[i] for r in roles_map.get(p, [])]
            plist = roles_map.get(player, [])
            role_need = sum(1 for r in plist if team_roles.count(r) < 2)
            return (team_ovr(i), team_sta(i), team_size(i), -role_need)
        best = min(candidates, key=score)
        teams[best].append(player)

    def try_balance(max_rounds=60):
        for _ in range(max_rounds):
            totals_ovr = [team_ovr(i) for i in range(num_teams)]
            totals_sta = [team_sta(i) for i in range(num_teams)]
            
            strong_ovr = max(range(num_teams), key=lambda i: totals_ovr[i])
            weak_ovr = min(range(num_teams), key=lambda i: totals_ovr[i])
            gap_ovr = totals_ovr[strong_ovr] - totals_ovr[weak_ovr]
            
            strong_sta = max(range(num_teams), key=lambda i: totals_sta[i])
            weak_sta = min(range(num_teams), key=lambda i: totals_sta[i])
            gap_sta = totals_sta[strong_sta] - totals_sta[weak_sta]
            
            if gap_ovr <= 3 and gap_sta <= 5:
                break
                
            improved = False
            t_a = strong_ovr if gap_ovr > 3 else strong_sta
            t_b = weak_ovr if gap_ovr > 3 else weak_sta
            
            for p_a in list(teams[t_a]):
                if conflict_with_team(p_a, t_b): continue
                for p_b in list(teams[t_b]):
                    if conflict_with_team(p_b, t_a): continue
                    
                    new_ovr_a = totals_ovr[t_a] - get_rating(p_a) + get_rating(p_b)
                    new_ovr_b = totals_ovr[t_b] - get_rating(p_b) + get_rating(p_a)
                    new_gap_ovr = abs(new_ovr_a - new_ovr_b)
                    
                    new_sta_a = totals_sta[t_a] - get_stamina(p_a) + get_stamina(p_b)
                    new_sta_b = totals_sta[t_b] - get_stamina(p_b) + get_stamina(p_a)
                    new_gap_sta = abs(new_sta_a - new_sta_b)
                    
                    old_cost = (max(0, gap_ovr - 3) * 10) + (max(0, gap_sta - 5) * 5) + gap_ovr + gap_sta
                    new_cost = (max(0, new_gap_ovr - 3) * 10) + (max(0, new_gap_sta - 5) * 5) + new_gap_ovr + new_gap_sta
                    
                    if new_cost < old_cost:
                        teams[t_a].remove(p_a)
                        teams[t_b].remove(p_b)
                        teams[t_a].append(p_b)
                        teams[t_b].append(p_a)
                        improved = True
                        break
                if improved: break
            if not improved: break
                
    try_balance()

    formation_names = list(FORMATIONS.keys())
    team_formations = {i: random.choice(formation_names) for i in range(num_teams)}
    team_uniforms = {
        i: (team_uniforms_in[i] if i < len(team_uniforms_in) and team_uniforms_in[i]
            else UNIFORM_OPTIONS[i % len(UNIFORM_OPTIONS)])
        for i in range(num_teams)
    }

    if uniform_rules:
        for _ in range(60):
            broken = []
            for tidx, team in enumerate(teams):
                for player in team:
                    allowed = uniform_rules.get(player)
                    if allowed and team_uniforms[tidx] not in allowed:
                        broken.append((tidx, player, allowed))
            if not broken: break
            fixed = False
            for tidx, player, allowed in broken:
                candidates = [j for j in range(num_teams)
                              if j != tidx and team_uniforms[j] in allowed]
                def safety(j):
                    new_uni = team_uniforms[tidx]
                    old_uni = team_uniforms[j]
                    for p in teams[j]:
                        a = uniform_rules.get(p)
                        if a and new_uni not in a: return 1
                    for p in teams[tidx]:
                        if p == player: continue
                        a = uniform_rules.get(p)
                        if a and old_uni not in a: return 1
                    return 0
                candidates.sort(key=safety)
                if candidates and safety(candidates[0]) == 0:
                    j = candidates[0]
                    team_uniforms[tidx], team_uniforms[j] = team_uniforms[j], team_uniforms[tidx]
                    fixed = True
                    break
            if not fixed: break

    return teams, team_formations, team_uniforms


# ==========================================
# RADAR CHART HELPERS
# ==========================================
def mini_radar_svg(attributes, size=50):
    if not attributes: return ""
    categories = list(ATTR_CATEGORIES.keys())
    n = len(categories)
    angles = [-math.pi / 2 + 2 * math.pi * i / n for i in range(n)]
    cx, cy = size / 2, size / 2
    R = size / 2 - 4
    
    def point(value, angle):
        r = (max(1, min(100, value)) / 100.0) * R
        return (cx + r * math.cos(angle), cy + r * math.sin(angle))
        
    values = []
    for cat in categories:
        cols = ATTR_CATEGORIES[cat]["cols"]
        total, count = 0, 0
        for c in cols:
            if c in attributes:
                total += attributes[c]
                count += 1
        values.append(total / count if count else 0)
        
    parts = [f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" style="display:block">']
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="rgba(16,38,77,.4)" stroke="rgba(23,105,194,.2)" stroke-width="1"/>')
    
    for pct in [0.5, 1.0]:
        r = R * pct
        pts = " ".join(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}" for a in angles)
        parts.append(f'<polygon points="{pts}" fill="none" stroke="rgba(23,105,194,.4)" stroke-width="1"/>')

    for a in angles:
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + R * math.cos(a):.1f}" y2="{cy + R * math.sin(a):.1f}" stroke="rgba(23,105,194,.3)" stroke-width="1"/>')

    pts = []
    for v, a in zip(values, angles):
        x, y = point(v, a)
        pts.append(f"{x:.1f},{y:.1f}")
    polygon_pts = " ".join(pts)
    parts.append(f'<polygon points="{polygon_pts}" fill="rgba(220,75,20,0.2)" stroke="#DC4B14" stroke-width="2" stroke-linejoin="round"/>')
    
    for v, a in zip(values, angles):
        x, y = point(v, a)
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="#DC4B14"/>')
        
    parts.append('</svg>')
    return "".join(parts)


def compute_team_attributes(team_players, players_db):
    result = {}
    for cat, info in ATTR_CATEGORIES.items():
        total, count = 0, 0
        for name in team_players:
            pl = next((p for p in players_db if p["nama"] == name), None)
            if not pl: continue
            for c in info["cols"]:
                v = pl.get("attributes", {}).get(c)
                if isinstance(v, (int, float)):
                    total += v
                    count += 1
        result[cat] = total / count if count else 0
    return result


def radar_chart_svg(categories, datasets, width=340, height=320):
    W, H = width, height
    cx, cy = W / 2, H / 2 + 6
    R = min(W, H) / 2 - 46
    n = len(categories)
    if n < 3: return ""
    angles = [-math.pi / 2 + 2 * math.pi * i / n for i in range(n)]
    def point(value, angle):
        r = (value / 100.0) * R
        return (cx + r * math.cos(angle), cy + r * math.sin(angle))
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="display:block;margin:0 auto">']
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="rgba(16,38,77,.4)" stroke="rgba(23,105,194,.2)" stroke-width="1"/>')
    for pct in [0.25, 0.5, 0.75, 1.0]:
        r = R * pct
        pts = " ".join(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}" for a in angles)
        parts.append(f'<polygon points="{pts}" fill="none" stroke="rgba(23,105,194,{0.08 + 0.04 * pct:.2f})" stroke-width="1"/>')
    for cat, ang in zip(categories, angles):
        x_end = cx + R * math.cos(ang)
        y_end = cy + R * math.sin(ang)
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x_end:.1f}" y2="{y_end:.1f}" stroke="rgba(23,105,194,.35)" stroke-width="1"/>')
        lx = cx + (R + 20) * math.cos(ang)
        ly = cy + (R + 20) * math.sin(ang)
        anchor = "middle" if lx > cx - 8 and lx < cx + 8 else ("end" if lx < cx - 8 else "start")
        parts.append(f'<text x="{lx:.1f}" y="{ly + 4:.1f}" text-anchor="{anchor}" fill="#94a3b8" font-size="10" font-weight="700" font-family="Inter, sans-serif">{cat.upper()}</text>')
    for ds in datasets:
        pts = [f"{point(v, a)[0]:.1f},{point(v, a)[1]:.1f}" for v, a in zip(ds["values"], angles)]
        parts.append(f'<polygon points="{" ".join(pts)}" fill="{ds["color"]}" fill-opacity="0.18" stroke="{ds["color"]}" stroke-width="2.2" stroke-linejoin="round"/>')
        for v, a in zip(ds["values"], angles):
            x, y = point(v, a)
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{ds["color"]}" stroke="#0B1B38" stroke-width="1.6"/>')
    legend_y = H - 12
    total_legend_width = sum(90 for _ in datasets)
    lx_start = (W - total_legend_width) / 2 + 12
    for i, ds in enumerate(datasets):
        x = lx_start + i * 90
        parts.append(f'<circle cx="{x:.1f}" cy="{legend_y}" r="5" fill="{ds["color"]}"/>')
        parts.append(f'<text x="{x + 10:.1f}" y="{legend_y + 4}" fill="#e0ecf8" font-size="11" font-weight="700" font-family="Inter, sans-serif">{ds.get("label", "")}</text>')
    parts.append("</svg>")
    return " ".join(parts)


def render_radar_section(teams, team_uniforms, players_db):
    teams_data = []
    for i, team in enumerate(teams):
        attrs = compute_team_attributes(team, players_db)
        teams_data.append({
            "idx": i,
            "uniform": team_uniforms[i],
            "color": COLOR_MAP.get(team_uniforms[i], "#1769C2"),
            "attrs": attrs,
        })
    if not teams_data: return
    categories = list(teams_data[0]["attrs"].keys())

    st.markdown(flat_html("""
    <div class='bng-radar-section bng-animate'>
      <div class='bng-radar-title'>📊 TEAM ATTRIBUTE RADAR</div>
      <div class='bng-radar-sub'>Perbandingan 6 kategori atribut rata-rata per tim</div>
    </div>
    """), unsafe_allow_html=True)

    tab_overlay, tab_perteam = st.tabs(["🔀 Overlay (Semua Tim)", "🎯 Per Tim"])

    with tab_overlay:
        datasets = []
        for td in teams_data:
            values = [td["attrs"][c] for c in categories]
            datasets.append({"label": f"Team {td['idx']+1}", "values": values, "color": td["color"]})
        svg = radar_chart_svg(categories, datasets, width=460, height=420)
        st.markdown(f"<div style='display:flex;justify-content:center'>{svg}</div>", unsafe_allow_html=True)
        rows = []
        for td in teams_data:
            row = {"Tim": f"Team {td['idx']+1} ({td['uniform']})"}
            for c in categories: row[c] = int(round(td["attrs"][c]))
            rows.append(row)
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

    with tab_perteam:
        cols = st.columns(min(len(teams_data), 3))
        for i, td in enumerate(teams_data):
            with cols[i % len(cols)]:
                values = [td["attrs"][c] for c in categories]
                svg = radar_chart_svg(categories, [{"label": f"Team {td['idx']+1}", "values": values, "color": td["color"]}], width=320, height=320)
                st.markdown(flat_html(f"""
                <div style='text-align:center;margin-top:8px'>
                  <div style='display:inline-block;padding:5px 14px;background:{td["color"]};color:white;border-radius:14px;font-weight:800;font-size:13px'>Team {td['idx']+1} · {td['uniform']}</div>
                </div>
                """), unsafe_allow_html=True)
                st.markdown(f"<div style='display:flex;justify-content:center'>{svg}</div>", unsafe_allow_html=True)


# ==========================================
# TEAM NAME GENERATOR
# ==========================================
def generate_team_names(uniforms):
    """Generate team names based on uniform color."""
    name_map = {
        "Biru": "Biru FC",
        "Putih": "Putih United",
        "Merah": "Merah Storm",
        "Kuning": "Kuning Rose",
        "Unggu": "Unggul FC",
        "Hitam": "Hitam Shadow",
        "Hijau": "Hijau Forest",
        "Abu-abu": "Abu-abu Neutral",
    }
    return [name_map.get(u, f"Tim {u}") for u in uniforms]


# ==========================================
# SVG PITCH
# ==========================================
def formation_svg(formation_name, width=320, height=200):
    form = FORMATIONS.get(formation_name, {})
    positions = form.get("positions", [])
    W, H = 400, 250
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {W} {H}" style="border-radius:12px;display:block;margin:8px 0">',
        f'<rect x="0" y="0" width="{W}" height="{H}" rx="14" fill="#c62828"/>',
        f'<rect x="12" y="12" width="{W-24}" height="{H-24}" rx="6" fill="#1769C2"/>',
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
        parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="14" fill="#c62828" stroke="white" stroke-width="2"/>')
        parts.append(f'<text x="{px:.1f}" y="{py+4:.1f}" text-anchor="middle" fill="white" font-size="10" font-weight="bold" font-family="Arial,sans-serif">{pos["label"]}</text>')
    parts.append("</svg>")
    return " ".join(parts)


# ==========================================
# PNG RENDERER (v5.6 Update)
# ==========================================
def _load_font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "arial.ttf",
    ]
    for path in candidates:
        try: return ImageFont.truetype(path, size)
        except Exception: continue
    try: return ImageFont.load_default(size)
    except TypeError: return ImageFont.load_default()


def draw_png_player_radar(draw, x, y, size, attributes):
    """Mini radar chart pemain dengan grid lembut dan data kontras."""
    categories = list(ATTR_CATEGORIES.keys())
    n = len(categories)
    if n < 3 or not attributes:
        return

    cx, cy = x + size / 2, y + size / 2
    R = max(1, size / 2 - 3)
    angles = [-math.pi / 2 + 2 * math.pi * i / n for i in range(n)]

    def point(value, angle):
        r = max(0, min(100, float(value))) / 100.0 * R
        return (cx + r * math.cos(angle), cy + r * math.sin(angle))

    values = []
    for cat in categories:
        cols = ATTR_CATEGORIES[cat]["cols"]
        valid = [float(attributes[c]) for c in cols if c in attributes and attributes[c] is not None]
        values.append(sum(valid) / len(valid) if valid else 0)

    poly_pts = [point(v, a) for v, a in zip(values, angles)]

    # 1. Area data
    if len(poly_pts) >= 3:
        draw.polygon(poly_pts, fill=(255, 237, 213))

    # 2. Grid
    grid_color = (226, 232, 240)
    axis_color = (203, 213, 225)

    for pct in (0.25, 0.50, 0.75, 1.0):
        r = R * pct
        pts = [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in angles]
        draw.polygon(pts, outline=grid_color, width=1)

    for a in angles:
        draw.line([(cx, cy), (cx + R * math.cos(a), cy + R * math.sin(a))], fill=axis_color, width=1)

    # 3. Garis nilai
    data_color = (220, 75, 20)
    draw.polygon(poly_pts, fill=None, outline=data_color, width=2)

    # 4. Titik nilai
    dot_r = max(2, min(3, size // 12))
    for px, py in poly_pts:
        draw.ellipse((px - dot_r, py - dot_r, px + dot_r, py + dot_r), fill=data_color, outline=(255, 255, 255), width=1)


def draw_png_radar(draw, x, y, w, h, attributes):
    """Radar chart tim dengan grid, label, dan garis data terpisah."""
    categories = list(ATTR_CATEGORIES.keys())
    n = len(categories)
    if n < 3:
        return

    cx, cy = x + w / 2, y + h / 2
    R = max(1, min(w, h) / 2 - 20) # Ruang untuk label
    angles = [-math.pi / 2 + 2 * math.pi * i / n for i in range(n)]

    def point(value, angle):
        r = max(0, min(100, float(value))) / 100.0 * R
        return (cx + r * math.cos(angle), cy + r * math.sin(angle))

    values = []
    for cat in categories:
        cols = ATTR_CATEGORIES[cat]["cols"]
        valid = [float(attributes[c]) for c in cols if c in attributes and attributes[c] is not None]
        values.append(sum(valid) / len(valid) if valid else 0)

    poly_pts = [point(v, a) for v, a in zip(values, angles)]

    # 1. Fill lembut
    if len(poly_pts) >= 3:
        draw.polygon(poly_pts, fill=(255, 237, 213))

    # 2. Grid
    grid_color = (226, 232, 240)
    axis_color = (203, 213, 225)

    for pct in (0.25, 0.50, 0.75, 1.0):
        r = R * pct
        pts = [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in angles]
        draw.polygon(pts, outline=grid_color, width=1)

    for a in angles:
        draw.line([(cx, cy), (cx + R * math.cos(a), cy + R * math.sin(a))], fill=axis_color, width=1)

    # 3. Label Teks (PHY, TEC, MTC, GKS)
    font_label = _load_font(9, bold=True)
    for cat, a in zip(categories, angles):
        lx = cx + (R + 12) * math.cos(a)
        ly = cy + (R + 12) * math.sin(a)
        lbl = cat[:3].upper()
        try:
            bb = draw.textbbox((0, 0), lbl, font=font_label)
            lw, lh = bb[2] - bb[0], bb[3] - bb[1]
        except Exception:
            lw, lh = 20, 10
        draw.text((lx - lw/2, ly - lh/2), lbl, fill=(100, 100, 100), font=font_label)

    # 4. Outline data
    data_color = (220, 75, 20)
    draw.polygon(poly_pts, fill=None, outline=data_color, width=3)

    # 5. Titik data
    dot_r = max(3, min(4, int(R / 12)))
    for px, py in poly_pts:
        draw.ellipse((px - dot_r, py - dot_r, px + dot_r, py + dot_r), fill=data_color, outline=(255, 255, 255), width=1)


def render_teams_png(teams, team_formations, team_uniforms, roles_map, ratings, team_names=None, players_db=None):
    def get_rating(p): return ratings.get(p, 50)
    
    def draw_pitch(draw, x, y, w, h, formation_name):
        form = FORMATIONS.get(formation_name, {})
        positions = form.get("positions", [])
        draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill="#c62828")
        pad = 8
        px0, py0 = x + pad, y + pad
        pw, ph = w - 2 * pad, h - 2 * pad
        draw.rounded_rectangle([px0, py0, px0 + pw, py0 + ph], radius=5, fill="#1769C2")
        cx, cy = px0 + pw // 2, py0 + ph // 2
        draw.line([(cx, py0), (cx, py0 + ph)], fill="#8fb3e0", width=2)
        r = max(10, min(pw, ph) // 7)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline="#b9d0ee", width=2)
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill="white")
        bw, bh = max(14, pw // 10), max(28, ph // 2)
        draw.rectangle([px0, cy - bh // 2, px0 + bw, cy + bh // 2], outline="#8fb3e0", width=1)
        draw.rectangle([px0 + pw - bw, cy - bh // 2, px0 + pw, cy + bh // 2], outline="#8fb3e0", width=1)
        gw, gh = 5, max(12, ph // 5)
        draw.rectangle([x + 2, cy - gh // 2, x + 2 + gw, cy + gh // 2], outline="white", width=2)
        draw.rectangle([x + w - 2 - gw, cy - gh // 2, x + w - 2, cy + gh // 2], outline="white", width=2)
        title_font = _load_font(11, bold=True)
        title = formation_name if len(formation_name) <= 22 else formation_name[:20] + ".."
        try:
            bbox = draw.textbbox((0, 0), title, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception: tw = len(title) * 6
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
            except Exception: lw = len(lab) * 5
            draw.text((dx - lw // 2, dy - 5), lab, fill="white", font=label_font)

    margin, card_pad = 24, 16
    row_h, pitch_h = 39, 150  # Update tinggi baris
    col_w = 560               # Update lebar card
    pitch_w = col_w - 28
    
    header_block = 52 + 40 + pitch_h + 10 
    gap = 20
    card_heights = [header_block + (len(t) + 1) * row_h + card_pad + 8 for t in teams]
    n = len(teams)
    cols = 1 if n == 1 else 2
    rows_cards = (n + cols - 1) // cols
    row_heights = []
    for r in range(rows_cards):
        hs = [card_heights[r * cols + c] for c in range(cols) if r * cols + c < n]
        row_heights.append(max(hs) if hs else 0)

    top_banner, balance_h = 80, 50
    img_w = margin * 2 + cols * col_w + (cols - 1) * gap
    img_h = margin + top_banner + sum(row_heights) + (rows_cards - 1) * gap + balance_h + margin
    img = Image.new("RGB", (img_w, img_h), "#0B1B38")
    draw = ImageDraw.Draw(img)

    font_title = _load_font(26, bold=True)
    font_sub = _load_font(13)
    font_h = _load_font(18, bold=True)
    font_row = _load_font(13)
    font_row_b = _load_font(13, bold=True)
    font_small = _load_font(11)

    draw.rectangle([0, 0, img_w, top_banner], fill="#10264D")
    draw.rectangle([0, 0, img_w, 4], fill="#FBBF24")
    draw.text((margin, 16), "BIAENERGI FUTSAL ACADEMY", fill="#FBBF24", font=font_title)
    draw.text((margin, 50), "Hasil Pembagian Tim", fill="#94a3b8", font=font_sub)

    totals = []
    y_base = margin + top_banner - 8
    for idx, team in enumerate(teams):
        r, c = divmod(idx, cols)
        x0 = margin + c * (col_w + gap)
        y0 = y_base + sum(row_heights[:r]) + r * gap
        ch = card_heights[idx]
        uniform = team_uniforms[idx]
        formation = team_formations[idx]
        form_info = FORMATIONS.get(formation, {})
        team_rating = sum(get_rating(p) for p in team)
        totals.append(team_rating)
        bg = COLOR_MAP.get(uniform, "#757575")
        text_color = "white" if uniform in DARK_UNIFORMS else "black"

        draw.rounded_rectangle([x0, y0, x0 + col_w, y0 + ch], radius=12, fill="white", outline="#10264D", width=3)
        draw.rounded_rectangle([x0, y0, x0 + col_w, y0 + 44], radius=12, fill="#10264D")
        draw.rectangle([x0, y0 + 28, x0 + col_w, y0 + 44], fill="#10264D")
        
        # Header Text
        draw.text((x0 + 14, y0 + 10), f"TEAM {idx+1}", fill="white", font=font_h)
        
        # Uniform Badge
        ub_x = x0 + 120
        draw.rounded_rectangle([ub_x, y0 + 10, ub_x + 70, y0 + 34], radius=10, fill=bg)
        draw.text((ub_x + 12, y0 + 13), uniform, fill=text_color, font=font_small)

        # OVR Badge
        badge = f"Total OVR: {team_rating}"
        bw = 110
        draw.rounded_rectangle([x0 + col_w - bw - 12, y0 + 10, x0 + col_w - 12, y0 + 34], radius=10, fill="#1769C2")
        draw.text((x0 + col_w - bw + 4, y0 + 13), badge, fill="white", font=font_small)

        y = y0 + 52
        draw.text((x0 + 14, y), f"Formasi: {formation}", fill="#222", font=font_row_b)
        y += 18
        pola = form_info.get("pola", "")
        if len(pola) > 72: pola = pola[:69] + "..."
        draw.text((x0 + 14, y), pola, fill="#555", font=font_small)
        y += 22
        
        draw_pitch(draw, x0 + 14, y, pitch_w - 150, pitch_h, formation)
        
        # Hapus radar chart, ganti dengan nama tim di sisi kanan
        if players_db and team:
            team_attrs = compute_team_attributes(team, players_db)
            pass
        
        team_name = (team_names[idx] if team_names and idx < len(team_names) else f"Team {idx+1}")
        name_font = _load_font(18, bold=True)
        try:
            bbox = draw.textbbox((0, 0), team_name, font=name_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = len(team_name) * 9
        radar_x = x0 + 14 + (pitch_w - 150) + 10
        radar_y = y + (pitch_h - 40) // 2
        draw.text((radar_x + (140 - tw) // 2, radar_y), team_name, fill=text_color, font=name_font)
        
        y += pitch_h + 10

        col_no_w = 40
        col_name_w = 230
        radar_size = 34 # Update ukuran radar
        col_radar_w = 40
        col_role_w = col_w - 20 - col_no_w - col_name_w - col_radar_w
        
        draw.rectangle([x0 + 10, y, x0 + col_w - 10, y + row_h], fill="#10264D")
        draw.text((x0 + 18, y + 10), "No", fill="white", font=font_small)
        draw.text((x0 + 18 + col_no_w, y + 10), "Nama Pemain", fill="white", font=font_small)
        draw.text((x0 + 18 + col_no_w + col_name_w, y + 10), "Role / Posisi", fill="white", font=font_small)
        draw.text((x0 + 18 + col_no_w + col_name_w + col_role_w, y + 10), "Attr", fill="white", font=font_small)
        y += row_h

        for j, player in enumerate(team, 1):
            if j % 2 == 0:
                draw.rectangle([x0 + 10, y, x0 + col_w - 10, y + row_h], fill="#EDF3F9")
            
            pr = roles_map.get(player, [])
            role_str = ", ".join(pr) if pr else "-"
            
            text_y = y + (row_h - 14) // 2
            draw.text((x0 + 18, text_y), str(j), fill="#333", font=font_row)
            draw.text((x0 + 18 + col_no_w, text_y), player, fill="#111", font=font_row_b)
            draw.text((x0 + 18 + col_no_w + col_name_w, text_y), role_str, fill="#444", font=font_row)
            
            if players_db:
                pl_obj = next((p for p in players_db if p["nama"] == player), None)
                if pl_obj and "attributes" in pl_obj:
                    radar_x = x0 + 18 + col_no_w + col_name_w + col_role_w
                    radar_y = y + (row_h - radar_size) // 2
                    draw_png_player_radar(draw, radar_x, radar_y, radar_size, pl_obj["attributes"])
            
            y += row_h

    if totals:
        mx, mn = max(totals), min(totals)
        gap_v = mx - mn
        if gap_v <= 3: status, color, bg_color = "IMBANG", "#22c55e", "#dcfce7"
        elif gap_v <= 6: status, color, bg_color = "CUKUP IMBANG", "#f59e0b", "#fef3c7"
        else: status, color, bg_color = "KURANG IMBANG", "#ef4444", "#fee2e2"
        
        summary = "  |  ".join(f"Team {i+1}: {t}" for i, t in enumerate(totals))
        fy = img_h - margin - 36
        
        # Footer Background
        draw.rounded_rectangle([margin, fy, img_w - margin, fy + 36], radius=8, fill="#10264D")
        draw.rectangle([margin, fy, margin + 6, fy + 36], fill=color)
        
        # Teks Summary
        draw.text((margin + 16, fy + 9), f"Keseimbangan: {summary}   |   Selisih {gap_v}", fill="#f8fafc", font=font_sub)
        
        # Badge Status
        st_badge = f" {status} "
        bw_st = 120
        draw.rounded_rectangle([img_w - margin - bw_st - 16, fy + 6, img_w - margin - 16, fy + 30], radius=6, fill=bg_color)
        draw.text((img_w - margin - bw_st - 4, fy + 9), st_badge, fill=color, font=font_small)

    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


# ==========================================
# UI COMPONENTS
# ==========================================
def render_navbar():
    st.markdown(flat_html("""
    <div class='bng-navbar bng-animate'>
      <div class='bng-logo'>
        <div class='bng-logo-badge'>⚽</div>
        <div class='bng-logo-text'>
          <div class='bng-logo-title'>BIAENERGI</div>
          <div class='bng-logo-sub'>Futsal Academy</div>
        </div>
      </div>
      <div class='bng-slogan'>
        "One Team<br>One Spirit"
        <small>✦ PLAY · LEARN · GROW ✦</small>
      </div>
    </div>
    """), unsafe_allow_html=True)


def render_footer():
    st.markdown(flat_html("""
    <div class='bng-footer bng-animate'>
      <div class='brand'>BIAENERGI FUTSAL ACADEMY</div>
      <p style='margin:8px 0 0 0;color:#94a3b8;font-size:.82rem'>
        Pantang menyerah meski skor tidak berpihak — <i>Never give up, even when the score isn't on our side.</i>
      </p>
      <small>© 2026 BIAENERGI Futsal Academy · v5.6</small>
    </div>
    """), unsafe_allow_html=True)


def render_hero():
    bg = hero_background_css()
    bg_div = f"<div class='bng-hero-img' style='{bg}'></div>" if bg else ""
    st.markdown(flat_html(f"""
    <div class='bng-hero bng-animate'>
      {bg_div}
      <div class='bng-hero-content'>
        <div class='bng-hero-kicker'>Welcome to the</div>
        <h1>BIAENERGI<span class='hl'>Futsal Academy</span></h1>
        <div class='bng-hero-quote'>"Pantang menyerah meski skor tidak berpihak."</div>
        <div class='bng-hero-sub'>Never give up, even when the score isn't on our side.</div>
      </div>
      <div class='bng-hero-tag'>
        <span class='t1'>Play</span>
        <span class='t2'>Learn</span>
        <span class='t3'>Grow</span>
      </div>
    </div>
    """), unsafe_allow_html=True)


def section_header(icon, title, subtitle=""):
    sub = f"<div class='sub'>{subtitle}</div>" if subtitle else ""
    st.markdown(flat_html(f"""
    <div class='bng-section'>
      <span class='icon'>{icon}</span>
      <div><h2>{title}</h2>{sub}</div>
    </div>
    """), unsafe_allow_html=True)


def stat_card(icon, value, label):
    return flat_html(f"""
    <div class='bng-stat-card'>
      <div class='bng-stat-icon'>{icon}</div>
      <div class='bng-stat-value'>{value}</div>
      <div class='bng-stat-label'>{label}</div>
    </div>
    """)


def attribute_card(icon, name, value, color):
    pct = max(0, min(100, value))
    return flat_html(f"""
    <div class='bng-attr-card'>
      <div class='bng-attr-icon'>{icon}</div>
      <div class='bng-attr-name'>{name}</div>
      <div class='bng-attr-value'>{int(round(value))}</div>
      <div class='bng-attr-bar'>
        <div class='bng-attr-bar-fill' style='width:{pct}%;background:{color}'></div>
      </div>
    </div>
    """)


def player_card(player):
    avatar = resolve_avatar(player, size=56, css_class="bng-avatar")
    roles_html = "".join(role_chip_html(r) for r in player.get("roles", [])[:4])
    alias = player.get("alias", "")
    alias_html = f"<div class='bng-player-alias'>“{esc(alias)}”</div>" if alias else ""
    ovr = player.get("overall", 0)
    radar_html = mini_radar_svg(player.get("attributes", {}), size=54)
    return flat_html(f"""
    <div class='bng-player-card'>
      <div class='bng-ovr-badge'>{ovr}</div>
      {avatar}
      <div class='bng-player-info'>
        <div class='bng-player-name'>{esc(player['nama'])}</div>
        {alias_html}
        <div class='bng-player-roles'>{roles_html}</div>
      </div>
      <div style='margin-left: auto; display: flex; align-items: center; justify-content: center; opacity: 0.85;'>
        {radar_html}
      </div>
    </div>
    """)


def placeholder_box(emoji, title, desc):
    st.markdown(flat_html(f"""
    <div class='bng-placeholder bng-animate'>
      <div class='emoji'>{emoji}</div>
      <h3>{title}</h3>
      <p>{desc}</p>
    </div>
    """), unsafe_allow_html=True)


def render_team_result_card(team_idx, team_players, uniform, formation,
                             roles_map, ratings_map, stamina_map, players_db):
    bg = COLOR_MAP.get(uniform, "#757575")
    txt = "white" if uniform in DARK_UNIFORMS else "black"
    
    team_rating = sum(ratings_map.get(p, 50) for p in team_players)
    team_stamina = sum(stamina_map.get(p, 50) for p in team_players)
    
    form_info = FORMATIONS.get(formation, {})
    pitch = formation_svg(formation, width=380, height=240)

    roster_rows = []
    for j, pl_name in enumerate(team_players, 1):
        pl_obj = next((p for p in players_db if p["nama"] == pl_name), None)
        if pl_obj:
            avatar_str = resolve_avatar(pl_obj, size=34, css_class="bng-roster-avatar")
        else:
            c = color_for(pl_name)
            avatar_str = (f"<div class='bng-roster-avatar' style='background:{c};width:34px;height:34px'>{esc(initials(pl_name))}</div>")

        pr = roles_map.get(pl_name, [])
        roles_html = "".join(f"<span class='bng-roster-role-chip {ROLE_INFO[r]['css']}'>{r}</span>" for r in pr)
        ovr = ratings_map.get(pl_name, 50)

        roster_rows.append(flat_html(f"""
        <div class='bng-roster-row'>
          <div class='bng-roster-num'>{j}</div>
          {avatar_str}
          <div class='bng-roster-info'>
            <div class='bng-roster-name'>{esc(pl_name)}</div>
            <div class='bng-roster-roles'>{roles_html}</div>
          </div>
          <div class='bng-roster-ovr'>{ovr}</div>
        </div>
        """))

    roster_html = "".join(roster_rows)

    return flat_html(f"""
    <div class='bng-result-card'>
      <div class='bng-result-header'>
        <div class='bng-result-title'>
          🏅 TEAM {team_idx + 1}
          <span class='bng-result-uniform' style='background:{bg};color:{txt}'>{uniform}</span>
        </div>
        <div style='display:flex;gap:8px;flex-wrap:wrap'>
            <span class='bng-result-rating'>Total OVR: {team_rating}</span>
            <span class='bng-result-rating' style='background:linear-gradient(110deg,#DC4B14,#f97316)'>Total STA: {team_stamina}</span>
        </div>
      </div>
      <div class='bng-result-body'>
        <div class='bng-result-left'>
          <div class='bng-result-pitch'>{pitch}</div>
          <div class='bng-result-form-info'>
            <b>📐 {formation}</b>
            {esc(form_info.get('pola', ''))}<br>
            <span style='color:#64748b'>{esc(form_info.get('karakter', ''))}</span>
          </div>
        </div>
        <div class='bng-result-right'>
          <div class='bng-roster'>
            <div class='bng-roster-title'>👥 Roster ({len(team_players)} pemain)</div>
            {roster_html}
          </div>
        </div>
      </div>
    </div>
    """)


# ==========================================
# PAGE: HOME
# ==========================================
def page_home():
    render_hero()
    players = load_players()
    total_players = len(players)
    highest_ovr = max((p.get("overall", 0) for p in players), default=0)
    matches = store.get_match_history()
    total_matches = len(matches)

    section_header("👥", "Our Team at a Glance", "Statistik singkat tim BIAENERGI")
    stats = [
        stat_card("👥", total_players, "Total Players"),
        stat_card("🎯", "GK·A·F·P", "Player Positions"),
        stat_card("⭐", highest_ovr, "Highest Overall Rating"),
        stat_card("🏆", total_matches, "Match Played"),
    ]
    st.markdown(flat_html(f"<div class='bng-stat-grid bng-animate'>{''.join(stats)}</div>"), unsafe_allow_html=True)

    section_header("📊", "Player Attributes", f"Average Team Stats — Berdasarkan {total_players} pemain")
    if players:
        def avg_of(cols):
            total, count = 0, 0
            for p in players:
                for c in cols:
                    v = p.get("attributes", {}).get(c)
                    if isinstance(v, (int, float)):
                        total += v
                        count += 1
            return total / count if count else 0

        attr_groups = [
            ("Speed",    "🏃", ["STA", "AKS", "SPR", "AGI"], "#1769C2"),
            ("Shooting", "🎯", ["SHA", "SHP"],               "#DC4B14"),
            ("Defense",  "🛡️", ["TAC", "STR", "BAL"],        "#22c55e"),
            ("Tactics",  "🧠", ["VIS", "OFB", "DEC"],        "#a855f7"),
            ("Teamwork", "🤝", ["TMW", "COM"],               "#FBBF24"),
            ("Mood",     "😊", ["BRV", "AGR"],               "#ef4444"),
        ]
        cards = [attribute_card(icon, name, avg_of(cols), color) for name, icon, cols, color in attr_groups]
        st.markdown(flat_html(f"<div class='bng-attr-grid bng-animate'>{''.join(cards)}</div>"), unsafe_allow_html=True)
        st.caption(f"Berdasarkan {total_players} pemain  •  Player attributes are from our team data.")
    else:
        placeholder_box("📊", "Belum Ada Data Pemain", "Tambahkan pemain di menu Team untuk melihat statistik.")


# ==========================================
# PAGE: TEAM
# ==========================================
def page_team():
    players = load_players()
    is_admin = st.session_state.is_admin

    section_header("👥", "Team Roster", f"{len(players)} pemain terdaftar di database BIAENERGI")

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search = st.text_input("🔍 Cari pemain", placeholder="Ketik nama atau alias...", label_visibility="collapsed")
    with col2:
        if is_admin:
            if st.button("➕ Tambah Pemain", width="stretch", key="btn_add_player"):
                st.session_state.show_add_player = True
        else:
            if st.button("🔐 Login Admin", width="stretch", key="btn_open_login"):
                st.session_state.login_open = True
    with col3:
        if is_admin:
            if st.button("🔒 Logout", width="stretch", key="btn_logout"):
                do_logout()
                st.rerun()

    if st.session_state.login_open and not is_admin:
        with st.container(border=True):
            st.markdown("#### 🔐 Login Admin")
            if st.session_state.login_attempts >= MAX_LOGIN_ATTEMPTS:
                st.error("⛔ Terlalu banyak percobaan. Refresh halaman.")
            else:
                st.text_input("Password", type="password", key="login_pw")
                c1, c2, _ = st.columns([1, 1, 3])
                if c1.button("Masuk", key="btn_do_login", type="primary", width="stretch"):
                    do_login()
                    st.rerun()
                if c2.button("Batal", key="btn_cancel_login", width="stretch"):
                    st.session_state.login_open = False
                    st.rerun()

    shown = players
    if search:
        s = search.lower()
        shown = [p for p in players if s in p["nama"].lower() or s in p.get("alias", "").lower()]

    if shown:
        cards_html = "".join(player_card(p) for p in shown)
        st.markdown(flat_html(f"<div class='bng-player-grid bng-animate'>{cards_html}</div>"), unsafe_allow_html=True)
    else:
        placeholder_box("🔍", "Tidak Ada Pemain Ditemukan", "Coba ubah kata kunci pencarian.")

    if is_admin:
        st.markdown("---")
        section_header("✏️", "Kelola Database Pemain", "Edit atribut, tambah pemain baru, atau hapus pemain")
        tab_edit, tab_add = st.tabs(["📝 Edit Pemain", "➕ Tambah Pemain"])

        with tab_edit:
            if not players:
                st.info("Belum ada pemain.")
            else:
                options = {f"{p['id']} — {p['nama']}": p["id"] for p in players}
                selected_label = st.selectbox("Pilih pemain", list(options.keys()), key="edit_select")
                pid = options[selected_label]
                player = next((p for p in players if p["id"] == pid), None)

                if player:
                    with st.form(f"form_edit_{pid}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            new_nama = st.text_input("Nama", value=player["nama"])
                            new_alias = st.text_input("Alias", value=player.get("alias", ""))
                        with c2:
                            new_overall = st.slider("Overall Rating (1-100)", 1, 100, int(player.get("overall", 50)))
                            new_photo = st.text_input("Photo URL (opsional)", value=player.get("photo_url", ""))

                        st.markdown("**Roles**")
                        role_cols = st.columns(4)
                        new_roles = []
                        for i, r in enumerate(ROLE_KEYS):
                            if role_cols[i].checkbox(f"{ROLE_INFO[r]['emoji']} {r} ({ROLE_INFO[r]['nama']})", value=(r in player.get("roles", [])), key=f"edit_role_{pid}_{r}"):
                                new_roles.append(r)

                        st.markdown("**Attributes (1-99)**")
                        attr_cols = st.columns(6)
                        new_attrs = {}
                        for i, attr in enumerate(ALL_ATTRS):
                            with attr_cols[i % 6]:
                                new_attrs[attr] = st.number_input(attr, 1, 99, int(player.get("attributes", {}).get(attr, 50)), key=f"edit_attr_{pid}_{attr}")

                        cbtn1, cbtn2 = st.columns([1, 1])
                        save = cbtn1.form_submit_button("💾 Simpan", type="primary", width="stretch")
                        delete = cbtn2.form_submit_button("🗑️ Hapus", width="stretch")

                        if save:
                            if not new_roles:
                                st.error("⚠️ Pilih minimal 1 role!")
                            else:
                                for p in players:
                                    if p["id"] == pid:
                                        p["nama"] = new_nama.strip() or p["nama"]
                                        p["alias"] = new_alias.strip()
                                        p["overall"] = int(new_overall)
                                        p["roles"] = new_roles
                                        p["photo_url"] = new_photo.strip()
                                        p["attributes"] = new_attrs
                                        p["main_position"] = new_roles[0]
                                        break
                                if store.save_players(players):
                                    refresh_players()
                                    st.session_state.flash = ("success", f"✅ Data '{new_nama}' tersimpan.")
                                    st.rerun()
                                else:
                                    st.error("⚠️ Gagal menyimpan ke file.")

                        if delete:
                            players = [p for p in players if p["id"] != pid]
                            if store.save_players(players):
                                refresh_players()
                                st.session_state.flash = ("warning", f"🗑️ '{player['nama']}' dihapus.")
                                st.rerun()

        with tab_add:
            with st.form("form_add_player", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    new_nama = st.text_input("Nama *", placeholder="Nama lengkap")
                    new_alias = st.text_input("Alias", placeholder="Nama panggilan")
                with c2:
                    new_overall = st.slider("Overall Rating (1-100)", 1, 100, 50)
                    new_photo = st.text_input("Photo URL (opsional)", placeholder="https://...")

                st.markdown("**Roles**")
                role_cols = st.columns(4)
                new_roles = []
                for i, r in enumerate(ROLE_KEYS):
                    if role_cols[i].checkbox(f"{ROLE_INFO[r]['emoji']} {r}", value=(r == "A"), key=f"add_role_{r}"):
                        new_roles.append(r)

                st.markdown("**Attributes (default 50)**")
                attr_cols = st.columns(6)
                new_attrs = {}
                for i, attr in enumerate(ALL_ATTRS):
                    with attr_cols[i % 6]:
                        new_attrs[attr] = st.number_input(attr, 1, 99, 50, key=f"add_attr_{attr}")

                submitted = st.form_submit_button("➕ Tambah Pemain", type="primary", width="stretch")
                if submitted:
                    if not new_nama.strip():
                        st.error("⚠️ Nama wajib diisi!")
                    elif not new_roles:
                        st.error("⚠️ Pilih minimal 1 role!")
                    else:
                        existing_ids = [p["id"] for p in players]
                        nums = [int(i[1:]) for i in existing_ids if i.startswith("P") and i[1:].isdigit()]
                        next_num = (max(nums) + 1) if nums else 1
                        new_id = f"P{next_num:03d}"
                        new_player = {
                            "id": new_id, "nama": new_nama.strip(), "alias": new_alias.strip(),
                            "overall": int(new_overall), "roles": new_roles, "main_position": new_roles[0],
                            "positions": {"1st": new_roles[0], "2nd": new_roles[1] if len(new_roles) > 1 else "", "3rd": new_roles[2] if len(new_roles) > 2 else "", "4th": new_roles[3] if len(new_roles) > 3 else ""},
                            "attributes": new_attrs, "photo_url": new_photo.strip(),
                        }
                        players.append(new_player)
                        if store.save_players(players):
                            refresh_players()
                            st.session_state.flash = ("success", f"✅ '{new_player['nama']}' ditambahkan.")
                            st.rerun()
                        else:
                            st.error("⚠️ Gagal menyimpan.")


# ==========================================
# PAGE: TEAM GENERATOR
# ==========================================
def page_team_generator():
    section_header("⚽", "Team Generator", "Bagi tim secara otomatis dengan keseimbangan Overall Rating, Stamina & aturan.")

    players = load_players()
    if not players:
        placeholder_box("👥", "Belum Ada Pemain", "Tambahkan pemain di menu Team terlebih dahulu.")
        return

    if st.session_state.gen_selected is None:
        st.session_state.gen_selected = [p["nama"] for p in players]

    all_names = [p["nama"] for p in players]
    st.session_state.gen_selected = [n for n in st.session_state.gen_selected if n in all_names]

    tab1, tab2, tab3, tab4 = st.tabs(["1️⃣ Pemain", "2️⃣ Rules", "3️⃣ Konfigurasi", "4️⃣ Generate & Simpan"])

    # ---------- TAB 1 ----------
    with tab1:
        section_header("📋", "Player Selection", "Pilih pemain dari database atau tambahkan pemain luar untuk sesi ini")
        col_a, col_b = st.columns([4, 1])
        with col_a:
            selected = st.multiselect("Pilih pemain yang akan dibagi:", options=all_names, default=st.session_state.gen_selected, key="gen_ms_players")
            st.session_state.gen_selected = list(selected)
        with col_b:
            st.write(""); st.write("")
            if st.button("Pilih Semua", width="stretch", key="gen_sel_all"):
                st.session_state.gen_selected = all_names[:]
                st.rerun()

        st.metric("Total Pemain Terpilih", len(st.session_state.gen_selected))

        if st.session_state.gen_selected:
            sel_players = [p for p in players if p["nama"] in st.session_state.gen_selected]
            cards_html = "".join(player_card(p) for p in sel_players)
            st.markdown(flat_html(f"<div class='bng-player-grid bng-animate'>{cards_html}</div>"), unsafe_allow_html=True)

    # ---------- TAB 2 ----------
    with tab2:
        section_header("⚖️", "Rules", "Aturan Conflict & Uniform yang harus dipatuhi saat generate")
        rtab1, rtab2 = st.tabs(["⚔️ Separating Players", "👕 Uniform"])

        with rtab1:
            st.caption("Tentukan pasangan pemain yang **tidak boleh** berada di tim yang sama.")
            sel_names = st.session_state.gen_selected or all_names
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1: p1 = st.selectbox("Pemain 1", sel_names, key="gen_rule_p1")
            with c2: p2 = st.selectbox("Pemain 2", sel_names, key="gen_rule_p2")
            with c3:
                st.write(""); st.write("")
                if st.button("➕ Tambah", key="gen_add_rule", width="stretch"):
                    if p1 == p2: st.error("⚠️ Pemain harus berbeda!")
                    else:
                        pair = tuple(sorted([p1, p2]))
                        if pair not in st.session_state.gen_rules:
                            st.session_state.gen_rules.append(pair)
                            st.rerun()
                        else: st.warning("Rule sudah ada!")

            st.markdown(f"**Rules Conflict Aktif ({len(st.session_state.gen_rules)})**")
            if st.session_state.gen_rules:
                for i, (a, b) in enumerate(list(st.session_state.gen_rules)):
                    c1, c2 = st.columns([5, 1])
                    c1.markdown(f"**{i+1}.** {a} ⚔️ {b}")
                    if c2.button("🗑️", key=f"gen_del_rule_{i}"):
                        st.session_state.gen_rules.remove((a, b))
                        st.rerun()
            else: st.info("Belum ada aturan conflict.")

        with rtab2:
            st.caption("Tentukan pemain yang **hanya boleh** memakai uniform tertentu.")
            sel_names = st.session_state.gen_selected or all_names
            c1, c2 = st.columns([3, 2])
            with c1: sel_player = st.selectbox("Pemain", sel_names, key="gen_uni_player")
            with c2:
                current = st.session_state.gen_uniform_rules.get(sel_player, [])
                allowed = st.multiselect("Uniform yang diizinkan", UNIFORM_OPTIONS, default=current, key="gen_uni_allowed")
            cbtn1, cbtn2 = st.columns([1, 1])
            with cbtn1:
                if st.button("💾 Simpan Aturan", width="stretch", key="gen_save_uni"):
                    if allowed:
                        st.session_state.gen_uniform_rules[sel_player] = list(allowed)
                        st.success(f"✅ Aturan uniform untuk {sel_player} disimpan.")
                    else:
                        st.session_state.gen_uniform_rules.pop(sel_player, None)
                        st.info(f"ℹ️ Aturan {sel_player} dihapus (bebas).")
                    st.rerun()
            with cbtn2:
                if st.button("🗑️ Hapus Aturan", width="stretch", key="gen_del_uni"):
                    if sel_player in st.session_state.gen_uniform_rules:
                        del st.session_state.gen_uniform_rules[sel_player]
                        st.success(f"✅ Aturan {sel_player} dihapus.")
                        st.rerun()
                    else: st.warning("Tidak ada aturan untuk pemain ini.")

            st.markdown(f"**Aturan Uniform Aktif ({len(st.session_state.gen_uniform_rules)})**")
            if st.session_state.gen_uniform_rules:
                for player, unis in list(st.session_state.gen_uniform_rules.items()):
                    c1, c2, c3 = st.columns([3, 4, 1])
                    c1.markdown(f"**{player}**")
                    badges = " ".join(f"<span style='display:inline-block;padding:2px 10px;margin:2px;border-radius:6px;font-size:11px;font-weight:700;background:{COLOR_MAP.get(u, '#757575')};color:{'white' if u in DARK_UNIFORMS else 'black'}'>{u}</span>" for u in unis)
                    c2.markdown(badges, unsafe_allow_html=True)
                    if c3.button("🗑️", key=f"gen_del_uni_{player}"):
                        del st.session_state.gen_uniform_rules[player]
                        st.rerun()
            else: st.info("Belum ada aturan uniform.")

    # ---------- TAB 3 ----------
    with tab3:
        section_header("⚙️", "Team Configuration", "Atur jumlah tim dan warna seragam tiap tim")
        num_teams = st.slider("Jumlah Tim", 2, 6, int(st.session_state.gen_num_teams), step=1)
        st.session_state.gen_num_teams = num_teams
        st.markdown("**🎨 Pilih Seragam tiap Tim**")
        saved = st.session_state.gen_team_uniforms
        new_uniforms = []
        cols = st.columns(min(num_teams, 3))
        for i in range(num_teams):
            default = (saved[i] if i < len(saved) and saved[i] in UNIFORM_OPTIONS else UNIFORM_OPTIONS[i % len(UNIFORM_OPTIONS)])
            with cols[i % len(cols)]:
                uni = st.selectbox(f"Team {i+1}", UNIFORM_OPTIONS, index=UNIFORM_OPTIONS.index(default), key=f"gen_uni_{i}")
                new_uniforms.append(uni)
        st.session_state.gen_team_uniforms = new_uniforms
        if len(set(new_uniforms)) < len(new_uniforms): st.warning("⚠️ Ada tim dengan warna seragam yang sama.")
        
        uni_rules = st.session_state.gen_uniform_rules
        if uni_rules:
            conflicts = [player for player, allowed in uni_rules.items() if player in (st.session_state.gen_selected or []) and not any(u in allowed for u in new_uniforms)]
            if conflicts: st.error(f"⚠️ **Aturan Uniform Tidak Terpenuhi:** {', '.join(conflicts)}.")
            else: st.success("✅ Semua aturan uniform dapat dipenuhi.")

        num_sel = len(st.session_state.gen_selected or [])
        per_team = num_sel // num_teams if num_teams else 0
        sisa = num_sel % num_teams if num_teams else 0
        st.info(f"📊 **Total Pemain:** {num_sel} | **Rata-rata per Tim:** ~{per_team} | **Sisa:** {sisa}")

    # ---------- TAB 4: GENERATE & SIMPAN ----------
    with tab4:
        section_header("🎲", "Generate Team", "Bagi tim otomatis — bisa generate berkali-kali sampai komposisi adil, lalu simpan hasil terbaik.")
        sel = st.session_state.gen_selected or []
        
        if not sel:
            placeholder_box("👥", "Belum Ada Pemain Terpilih", "Pilih pemain di tab 1 terlebih dahulu.")
        elif len(sel) < st.session_state.gen_num_teams:
            st.error(f"⚠️ Jumlah pemain ({len(sel)}) kurang dari jumlah tim ({st.session_state.gen_num_teams}).")
        else:
            roles_map = {}
            ratings_map = {}
            stamina_map = {}
            for p in players:
                if p["nama"] in sel:
                    roles_map[p["nama"]] = p["roles"]
                    ratings_map[p["nama"]] = p["overall"]
                    stamina_map[p["nama"]] = p.get("attributes", {}).get("STA", 50)

            gk_count = sum(1 for p in players if p["nama"] in sel and "GK" in p["roles"])
            if gk_count == 0: st.warning("⚠️ Belum ada pemain berole GK di daftar terpilih.")
            elif gk_count < st.session_state.gen_num_teams: st.info(f"ℹ️ GK ({gk_count}) lebih sedikit dari jumlah tim.")

            st.markdown(flat_html("""
            <div class='bng-tip-box'>
              <div class='title'>💡 Tips: Generate Berkali-kali Sampai Adil</div>
              <div class='desc'>Klik <b>Generate</b> untuk mengacak tim. Kalau komposisi belum adil (Overall & Stamina), klik <b>Generate Ulang</b>. Kalau sudah pas, klik <b>Simpan Match Ini</b>.</div>
            </div>
            """), unsafe_allow_html=True)

            if st.session_state.gen_count > 0 or st.session_state.gen_history:
                gap_text = " · ".join(str(g) for g in st.session_state.gen_history[-5:]) or "-"
                st.markdown(flat_html(f"""
                <div class='bng-stats-bar'>
                  <div class='item'>🎲 Sudah generate: <b>{st.session_state.gen_count}x</b></div>
                  <div class='item'>📊 OVR Gap 5 terakhir: <b>{gap_text}</b></div>
                </div>
                """), unsafe_allow_html=True)

            if not st.session_state.gen_result:
                if st.button("🎲 GENERATE TIM SEKARANG", type="primary", width="stretch", key="gen_do_first"):
                    with st.spinner("Sedang mengacak & menyeimbangkan tim..."):
                        teams, team_formations, team_uniforms = generate_teams_v2(
                            sel, roles_map, ratings_map, stamina_map,
                            st.session_state.gen_rules, st.session_state.gen_num_teams,
                            st.session_state.gen_team_uniforms, st.session_state.gen_uniform_rules,
                        )
                        team_names = generate_team_names(list(team_uniforms.values()))
                        png_bytes = render_teams_png(teams, team_formations, team_uniforms, roles_map, ratings_map, team_names, players)
                        st.session_state.gen_result = {
                            "teams": teams, "formations": team_formations, "uniforms": team_uniforms,
                            "roles_map": roles_map, "ratings_map": ratings_map, "png": png_bytes,
                            "timestamp": datetime.now().isoformat(),
                        }
                        save_last_generate(st.session_state.gen_result)
                        st.session_state.gen_count += 1
                        totals = [sum(ratings_map.get(p, 50) for p in t) for t in teams]
                        gap_v = max(totals) - min(totals)
                        st.session_state.gen_history.append(gap_v)
                        st.session_state.gen_history = st.session_state.gen_history[-5:]
                        st.session_state.show_save_form = False
                    st.balloons()
                    st.toast("✅ Tim berhasil dibagi!", icon="🏆")
                    st.rerun()
            else:
                c_regen, c_dl = st.columns([1, 1])
                with c_regen:
                    if st.button("🔄 GENERATE ULANG", type="primary", width="stretch", key="gen_do_again"):
                        with st.spinner("Mengacak ulang tim..."):
                            teams, team_formations, team_uniforms = generate_teams_v2(
                                sel, roles_map, ratings_map, stamina_map,
                                st.session_state.gen_rules, st.session_state.gen_num_teams,
                                st.session_state.gen_team_uniforms, st.session_state.gen_uniform_rules,
                            )
                            team_names = generate_team_names(list(team_uniforms.values()))
                            png_bytes = render_teams_png(teams, team_formations, team_uniforms, roles_map, ratings_map, team_names, players)
                            st.session_state.gen_result = {
                                "teams": teams, "formations": team_formations, "uniforms": team_uniforms,
                                "roles_map": roles_map, "ratings_map": ratings_map, "png": png_bytes,
                                "timestamp": datetime.now().isoformat(),
                            }
                            save_last_generate(st.session_state.gen_result)
                            st.session_state.gen_count += 1
                            totals = [sum(ratings_map.get(p, 50) for p in t) for t in teams]
                            gap_v = max(totals) - min(totals)
                            st.session_state.gen_history.append(gap_v)
                            st.session_state.gen_history = st.session_state.gen_history[-5:]
                            st.session_state.show_save_form = False
                        st.toast("🔄 Tim diacak ulang! Cek hasil di bawah.", icon="🎲")
                        st.rerun()
                with c_dl:
                    st.download_button(label="⬇️ Download PNG", data=st.session_state.gen_result["png"], file_name=f"pembagian_tim_{datetime.now().strftime('%Y%m%d_%H%M')}.png", mime="image/png", width="stretch", key="gen_dl_png")

            if st.session_state.gen_result:
                res = st.session_state.gen_result
                players_db = load_players()

                st.markdown(flat_html(f"""
                <div style='margin:24px 0 12px 0;padding-bottom:8px;border-bottom:2px solid rgba(251,191,36,.3)'>
                  <div style='font-family:Orbitron,sans-serif;font-size:20px;font-weight:900;color:#FBBF24;letter-spacing:.04em'>🏆 HASIL PEMBAGIAN TIM</div>
                  <div style='font-size:12px;color:#94a3b8;margin-top:4px'>Dibuat pada {datetime.fromisoformat(res['timestamp']).strftime('%d %b %Y · %H:%M:%S')}</div>
                </div>
                """), unsafe_allow_html=True)

                for i, team in enumerate(res["teams"]):
                    card_html = render_team_result_card(
                        team_idx=i, team_players=team, uniform=res["uniforms"][i],
                        formation=res["formations"][i], roles_map=res["roles_map"],
                        ratings_map=res["ratings_map"], stamina_map=stamina_map, players_db=players_db
                    )
                    st.markdown(card_html, unsafe_allow_html=True)

                sta_lookup = {p["nama"]: p.get("attributes", {}).get("STA", 50) for p in players_db}
                totals_ovr = [sum(res["ratings_map"].get(p, 50) for p in t) for t in res["teams"]]
                totals_sta = [sum(sta_lookup.get(p, 50) for p in t) for t in res["teams"]]
                
                mx_ovr, mn_ovr = max(totals_ovr), min(totals_ovr)
                gap_ovr = mx_ovr - mn_ovr
                mx_sta, mn_sta = max(totals_sta), min(totals_sta)
                gap_sta = mx_sta - mn_sta

                if gap_ovr <= 3 and gap_sta <= 5:
                    color, status, icon = "#22c55e", "Sangat Seimbang", "✅"
                elif gap_ovr <= 6 and gap_sta <= 10:
                    color, status, icon = "#f59e0b", "Cukup Seimbang", "⚠️"
                else:
                    color, status, icon = "#ef4444", "Kurang Seimbang", "❌"

                teams_summary = "".join(
                    f"<div class='bng-balance-team'>Team {i+1}: OVR <b>{t_ovr}</b> | STA <b>{t_sta}</b></div>"
                    for i, (t_ovr, t_sta) in enumerate(zip(totals_ovr, totals_sta))
                )

                st.markdown(flat_html(f"""
                <div class='bng-balance-bar' style='border-left:6px solid {color}'>
                  <div>
                    <div class='label'>⚖️ Keseimbangan Tim (Overall & Stamina)</div>
                    <div class='value' style='color:{color}'>OVR Gap: {gap_ovr} | STA Gap: {gap_sta} {icon}</div>
                    <div style='font-size:12px;color:#94a3b8;margin-top:2px'>Status: {status}</div>
                  </div>
                  <div class='bng-balance-teams'>{teams_summary}</div>
                </div>
                """), unsafe_allow_html=True)

                st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
                render_radar_section(res["teams"], res["uniforms"], players_db)

                st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
                st.markdown(flat_html("""
                <div class='bng-save-box'>
                  <div style='display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:14px'>
                    <div>
                      <div style='font-family:Orbitron,sans-serif;font-size:18px;font-weight:900;color:#FBBF24;letter-spacing:.04em'>💾 Sudah Puas Dengan Pembagian Ini?</div>
                      <div style='font-size:13px;color:#cbd5e1;margin-top:4px'>Simpan hasil generate ini sebagai Match History, atau generate ulang untuk coba komposisi lain.</div>
                    </div>
                  </div>
                </div>
                """), unsafe_allow_html=True)

                if st.session_state.show_save_form:
                    c_btn1, c_btn2 = st.columns([1, 1])
                    with c_btn2:
                        if st.button("✖️ Tutup Form Simpan", width="stretch", key="btn_hide_save"):
                            st.session_state.show_save_form = False
                            st.rerun()
                else:
                    if st.button("💾 Simpan Match Ini", type="primary", width="stretch", key="btn_show_save"):
                        st.session_state.show_save_form = True
                        st.rerun()

                if st.session_state.show_save_form:
                    with st.form("form_save_match", clear_on_submit=False):
                        st.markdown("##### 📅 Info Match")
                        c1, c2 = st.columns(2)
                        with c1:
                            tanggal = st.date_input("Tanggal Match", value=datetime.now().date())
                            lokasi = st.text_input("Lokasi", placeholder="Contoh: Lapangan XYZ")
                        with c2:
                            waktu = st.time_input("Waktu", value=datetime.now().time())
                            catatan = st.text_input("Catatan (opsional)", placeholder="Contoh: Friendly match")

                        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                        submitted = st.form_submit_button("💾 Simpan ke Match History", type="primary", width="stretch")
                        if submitted:
                            matches = store.get_match_history()
                            mid = f"M{datetime.now().strftime('%Y%m%d%H%M%S')}"
                            match_record = {
                                "match_id": mid, "tanggal": tanggal.isoformat(),
                                "waktu": waktu.strftime("%H:%M"), "lokasi": lokasi, "catatan": catatan,
                                "teams": [
                                    {
                                        "nama": f"Team {i+1}", "uniform": res["uniforms"][i],
                                        "formasi": res["formations"][i], "players": list(res["teams"][i]),
                                        "rating_total": sum(res["ratings_map"].get(p, 50) for p in res["teams"][i]),
                                    } for i in range(len(res["teams"]))
                                ],
                                "skor": {f"team{i+1}": 0 for i in range(len(res["teams"]))},
                                "created_at": datetime.now().isoformat(),
                            }
                            matches.append(match_record)
                            if store.save_match_history(matches):
                                st.session_state.gen_result = None
                                st.session_state.show_save_form = False
                                clear_last_generate()
                                st.session_state.flash = ("success", f"✅ Match {mid} tersimpan! Cek tab Match History untuk input skor.")
                                st.rerun()
                            else: st.error("⚠️ Gagal menyimpan match.")


# ==========================================
# PAGE: MATCH HISTORY
# ==========================================
def page_match_history():
    section_header("📜", "Match History", "Riwayat pertandingan yang sudah digenerate & disimpan")
    matches = store.get_match_history()
    if not matches:
        placeholder_box("📭", "Belum Ada Riwayat Match", "Generate tim di menu Team Generator, lalu simpan hasilnya ke Match History.")
        return

    st.metric("Total Match Tersimpan", len(matches))
    matches_sorted = sorted(matches, key=lambda m: m.get("created_at", ""), reverse=True)

    for idx, match in enumerate(matches_sorted):
        mid = match["match_id"]
        tanggal = match.get("tanggal", "-")
        waktu = match.get("waktu", "")
        lokasi = match.get("lokasi", "-")
        catatan = match.get("catatan", "")
        teams = match.get("teams", [])
        skor = match.get("skor", {})

        st.markdown(flat_html(f"""
        <div class='bng-match-card bng-animate'>
          <div class='bng-match-header'>
            <div>
              <span class='bng-match-id'>🏆 {mid}</span>
              <span class='bng-match-date' style='margin-left:10px'>📅 {tanggal} {waktu} · 📍 {lokasi}</span>
            </div>
            <span style='color:#94a3b8;font-size:12px'>{catatan}</span>
          </div>
        """), unsafe_allow_html=True)

        if len(teams) >= 2:
            t1, t2 = teams[0], teams[1]
            s1, s2 = skor.get("team1", 0), skor.get("team2", 0)
            bg1, bg2 = COLOR_MAP.get(t1["uniform"], "#757575"), COLOR_MAP.get(t2["uniform"], "#757575")
            st.markdown(flat_html(f"""
            <div class='bng-match-score'>
              <div class='bng-match-team'>
                <div class='name'>{t1['nama']}</div>
                <div class='uniform'><span style='display:inline-block;width:12px;height:12px;border-radius:50%;background:{bg1};vertical-align:middle;margin-right:4px'></span>{t1['uniform']} · {t1['formasi']}</div>
              </div>
              <div class='bng-match-score-num'>{s1} — {s2}</div>
              <div class='bng-match-team'>
                <div class='name'>{t2['nama']}</div>
                <div class='uniform'><span style='display:inline-block;width:12px;height:12px;border-radius:50%;background:{bg2};vertical-align:middle;margin-right:4px'></span>{t2['uniform']} · {t2['formasi']}</div>
              </div>
            </div>
            """), unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander(f"📝 Input Skor & Detail — {mid}", expanded=False):
            with st.form(f"form_match_{mid}"):
                st.markdown("**Input Skor:**")
                score_cols = st.columns(len(teams))
                new_skor = {}
                for i, team in enumerate(teams):
                    with score_cols[i]:
                        val = st.number_input(f"{team['nama']} ({team['uniform']})", min_value=0, max_value=99, value=int(skor.get(f"team{i+1}", 0)), key=f"score_{mid}_t{i+1}")
                        new_skor[f"team{i+1}"] = val

                st.markdown("**Info Match:**")
                c1, c2 = st.columns(2)
                with c1:
                    try: default_date = datetime.fromisoformat(match["tanggal"]).date()
                    except Exception: default_date = datetime.now().date()
                    new_tanggal = st.date_input("Tanggal", value=default_date, key=f"date_{mid}")
                    new_lokasi = st.text_input("Lokasi", value=lokasi, key=f"lok_{mid}")
                with c2:
                    try: default_time = datetime.strptime(waktu, "%H:%M").time()
                    except Exception: default_time = datetime.now().time()
                    new_waktu = st.time_input("Waktu", value=default_time, key=f"time_{mid}")
                    new_catatan = st.text_input("Catatan", value=catatan, key=f"cat_{mid}")

                cbtn1, cbtn2 = st.columns([1, 1])
                save_score = cbtn1.form_submit_button("💾 Simpan Skor", type="primary", width="stretch")
                delete_match = cbtn2.form_submit_button("🗑️ Hapus Match", width="stretch")

                if save_score:
                    for m in matches:
                        if m["match_id"] == mid:
                            m["skor"] = new_skor
                            m["tanggal"] = new_tanggal.isoformat()
                            m["waktu"] = new_waktu.strftime("%H:%M")
                            m["lokasi"] = new_lokasi
                            m["catatan"] = new_catatan
                            break
                    if store.save_match_history(matches):
                        st.success("✅ Skor & info match diperbarui.")
                        st.rerun()

                if delete_match:
                    matches = [m for m in matches if m["match_id"] != mid]
                    if store.save_match_history(matches):
                        st.warning(f"🗑️ Match {mid} dihapus.")
                        st.rerun()

            st.markdown("**Detail Tim:**")
            players_db = load_players()
            for i, team in enumerate(teams):
                bg = COLOR_MAP.get(team["uniform"], "#757575")
                txt = "white" if team["uniform"] in DARK_UNIFORMS else "black"
                roster_rows = []
                for j, pl_name in enumerate(team.get("players", []), 1):
                    pl_obj = next((p for p in players_db if p["nama"] == pl_name), None)
                    if pl_obj: avatar_str = resolve_avatar(pl_obj, size=34, css_class="bng-roster-avatar")
                    else:
                        c = color_for(pl_name)
                        avatar_str = f"<div class='bng-roster-avatar' style='background:{c};width:34px;height:34px'>{esc(initials(pl_name))}</div>"
                    pr = pl_obj["roles"] if pl_obj else []
                    roles_html = "".join(f"<span class='bng-roster-role-chip {ROLE_INFO[r]['css']}'>{r}</span>" for r in pr)
                    ovr = pl_obj["overall"] if pl_obj else 50
                    roster_rows.append(flat_html(f"""
                    <div class='bng-roster-row'>
                      <div class='bng-roster-num'>{j}</div>{avatar_str}
                      <div class='bng-roster-info'>
                        <div class='bng-roster-name'>{esc(pl_name)}</div>
                        <div class='bng-roster-roles'>{roles_html}</div>
                      </div>
                      <div class='bng-roster-ovr'>{ovr}</div>
                    </div>
                    """))

                st.markdown(flat_html(f"""
                <div style='background:rgba(16,38,77,.5);border-radius:14px;padding:14px 16px;margin:10px 0;border-left:4px solid {bg}'>
                  <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px'>
                    <div style='font-family:Orbitron,sans-serif;font-size:15px;font-weight:900;color:#fff'>
                      {team['nama']}
                      <span style='background:{bg};color:{txt};padding:3px 12px;border-radius:14px;font-size:11px;margin-left:8px'>{team['uniform']}</span>
                    </div>
                    <span style='font-size:12px;color:#94a3b8'>{team['formasi']} · OVR {team.get('rating_total', 0)}</span>
                  </div>
                  <div style='display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:6px'>{''.join(roster_rows)}</div>
                </div>
                """), unsafe_allow_html=True)


# ==========================================
# PAGE: ABOUT
# ==========================================
def page_about():
    section_header("ℹ️", "Tentang BIAENERGI Futsal Academy", "One Team, One Spirit — Play, Learn, Grow Together")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(flat_html("""
        <div class='bng-more-box bng-animate'>
          <div class='bng-more-title'>More Than<br>Just a Game<small>MORE THAN JUST A GAME</small></div>
          <div class='bng-more-item'><div class='icon'>👥</div><div class='txt'><strong>Friendship</strong><span>Builds Stronger Team</span></div></div>
          <div class='bng-more-item'><div class='icon'>🏆</div><div class='txt'><strong>Effort</strong><span>Brings Progress</span></div></div>
          <div class='bng-more-item'><div class='icon'>🤍</div><div class='txt'><strong>Together</strong><span>We Are Stronger</span></div></div>
          <div class='bng-more-tag'><span>BIAENERGI FUTSAL ACADEMY 👑</span></div>
        </div>
        """), unsafe_allow_html=True)
    with col2:
        st.markdown("""
        ### 🎯 Visi
        Menjadi akademi futsal yang membangun karakter, sportivitas, dan skill pemain melalui pendekatan seimbang antara **Play, Learn, Grow**.

        ### 🧭 Misi
        - Mengembangkan skill teknis & taktik setiap pemain
        - Membangun kekompakan tim melalui latihan rutin
        - Menjunjung tinggi sportivitas di setiap pertandingan
        - Menciptakan lingkungan positif & menyenangkan

        ### 💬 Filosofi
        > *"Pantang menyerah meski skor tidak berpihak."*
        >
        > — Never give up, even when the score isn't on our side.
        """)


# ==========================================
# MAIN
# ==========================================
def main():
    render_navbar()
    if st.session_state.get("flash"):
        kind, msg = st.session_state.flash
        getattr(st, kind)(msg)
        st.session_state.flash = None

    tabs = st.tabs(["🏠 Home", "👥 Team", "⚽ Team Generator", "📜 Match History", "ℹ️ About"])
    with tabs[0]: page_home()
    with tabs[1]: page_team()
    with tabs[2]: page_team_generator()
    with tabs[3]: page_match_history()
    with tabs[4]: page_about()
    render_footer()


if __name__ == "__main__":
    main()
