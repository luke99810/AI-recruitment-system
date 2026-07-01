"""
Streamlit 统一前端：AI 智能招聘系统 v2.1
专业级 UI 设计 — 简历分析 → AI面试 → 评估报告
"""
import streamlit as st
import streamlit.components.v1 as components
import json, os, sys, time, hashlib, random
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.parser import parse_uploaded_file

import nest_asyncio
nest_asyncio.apply()

# ── Page Config ─────────────────────────────────────
st.set_page_config(
    page_title="AI 招聘系统",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="auto",
)

# ── Professional CSS (Theme-Responsive) ──────────────
st.markdown("""
<style>
    /* ========== Global ========== */
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; }
    
    /* Use Streamlit native theme variables */
    :root {
        --accent: #06b6d4;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --radius: 12px;
        --radius-sm: 8px;
        --radius-lg: 16px;
        --shadow: 0 1px 3px rgba(0,0,0,0.08);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.1);
        --shadow-lg: 0 8px 32px rgba(0,0,0,0.12);
    }
    
    .main .block-container { padding: 1.5rem 2rem; max-width: 1400px; }
    
    /* ========== Header (always dark gradient - brand identity) ========== */
    .app-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 30%, #4338ca 70%, #0e7490 100%);
        border-radius: var(--radius-lg);
        padding: 22px 36px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(99,102,241,0.3);
    }
    .app-header::before {
        content: '';
        position: absolute; top: -50%; right: -20%;
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(99,102,241,0.3) 0%, transparent 70%);
        border-radius: 50%;
    }
    .app-header::after {
        content: '';
        position: absolute; bottom: -40%; left: 10%;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(6,182,212,0.2) 0%, transparent 70%);
        border-radius: 50%;
    }
    .app-header h1 {
        font-size: 28px; font-weight: 800; color: #fff;
        margin: 0; position: relative; z-index: 1; letter-spacing: -0.5px;
    }
    .app-header p {
        font-size: 14px; color: rgba(255,255,255,0.7);
        margin: 6px 0 0; position: relative; z-index: 1;
    }

    
    /* ========== Tabs (theme-responsive) ========== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: var(--st-color-background-secondary, #f0f2f6);
        border-radius: var(--radius);
        padding: 4px;
        border: 1px solid var(--st-color-border, #e0e0e0);
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 24px; border-radius: 8px;
        font-size: 14px; font-weight: 500;
        color: var(--st-color-text-secondary, #555);
        border: none; transition: all 0.2s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--st-color-text-primary, #111);
        background: rgba(99,102,241,0.08);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #4f46e5, #6366f1);
        color: #fff; font-weight: 600;
    }
    
    /* ========== Cards (theme-responsive) ========== */
    .card {
        background: var(--st-color-background-secondary, #f8f9fa);
        border: 1px solid var(--st-color-border, #e0e0e0);
        border-radius: var(--radius);
        padding: 20px; margin-bottom: 16px;
        transition: all 0.2s;
    }
    .card:hover {
        border-color: #6366f1;
        box-shadow: var(--shadow-md);
    }
    .card-header {
        font-size: 15px; font-weight: 600;
        color: var(--st-color-text-primary, #111);
        margin-bottom: 12px;
        display: flex; align-items: center; gap: 8px;
    }
    .card-accent { border-left: 3px solid #6366f1; }
    
    /* ========== Score Ring ========== */
    .score-ring-container { text-align: center; padding: 16px 0; }
    .score-value {
        position: absolute;
        font-size: 36px; font-weight: 800; letter-spacing: -1px;
    }
    
    /* ========== Stat Badges (theme-responsive) ========== */
    .stat-row { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 20px; }
    .stat-item {
        background: var(--st-color-background-secondary, #f8f9fa);
        border: 1px solid var(--st-color-border, #e0e0e0);
        border-radius: var(--radius-sm);
        padding: 14px 18px; flex: 1; min-width: 120px;
        transition: all 0.2s;
    }
    .stat-item:hover { border-color: #6366f1; }
    .stat-item .stat-value {
        font-size: 24px; font-weight: 700;
        color: var(--st-color-text-primary, #111);
    }
    .stat-item .stat-label {
        font-size: 12px;
        color: var(--st-color-text-secondary, #666);
        margin-top: 2px;
    }
    
    /* ========== Question Cards (theme-responsive) ========== */
    .question-card {
        background: var(--st-color-background-secondary, #f8f9fa);
        border: 1px solid var(--st-color-border, #e0e0e0);
        border-radius: var(--radius-sm);
        padding: 16px 18px; margin: 8px 0;
        transition: all 0.2s;
        border-left: 3px solid transparent;
    }
    .question-card:hover {
        border-left-color: #6366f1;
        border-color: #6366f1;
    }
    .question-card .q-title {
        font-weight: 600;
        color: var(--st-color-text-primary, #111);
        font-size: 14px; line-height: 1.5;
    }
    
    /* ========== Tags ========== */
    .tag {
        display: inline-flex; align-items: center;
        padding: 3px 10px; border-radius: 6px;
        font-size: 11px; font-weight: 600;
        margin-right: 4px; white-space: nowrap;
    }
    .tag-tech { background: rgba(59,130,246,0.12); color: #2563eb; }
    .tag-project { background: rgba(16,185,129,0.12); color: #059669; }
    .tag-scene { background: rgba(245,158,11,0.12); color: #d97706; }
    .tag-behavior { background: rgba(236,72,153,0.12); color: #db2777; }
    .tag-ambiguity { background: rgba(168,85,247,0.12); color: #7c3aed; }
    .tag-dim { background: rgba(99,102,241,0.12); color: #4f46e5; }
    
    /* ========== Chat (theme-responsive) ========== */
    .chat-container {
        background: var(--st-color-background-secondary, #f8f9fa);
        border: 1px solid var(--st-color-border, #e0e0e0);
        border-radius: var(--radius); padding: 16px;
        margin-bottom: 12px; max-height: 480px; overflow-y: auto;
    }
    .chat-msg {
        display: flex; gap: 10px; margin-bottom: 16px;
        animation: fadeIn 0.3s ease;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .chat-msg .avatar {
        width: 36px; height: 36px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px; flex-shrink: 0;
    }
    .chat-msg .avatar.interviewer {
        background: linear-gradient(135deg, #4338ca, #6366f1);
    }
    .chat-msg .avatar.candidate {
        background: linear-gradient(135deg, #0e7490, #06b6d4);
    }
    .chat-msg .bubble {
        max-width: 80%; padding: 10px 14px; border-radius: 12px;
        font-size: 14px; line-height: 1.6;
    }
    .chat-msg .bubble.interviewer {
        background: var(--st-color-background-primary, #fff);
        border: 1px solid var(--st-color-border, #e0e0e0);
        color: var(--st-color-text-primary, #111);
        border-bottom-left-radius: 4px;
    }
    .chat-msg .bubble.candidate {
        background: linear-gradient(135deg, #4338ca, #6366f1);
        color: #fff; border-bottom-right-radius: 4px;
    }
    
    /* ========== Status Bar (theme-responsive) ========== */
    .status-bar {
        background: var(--st-color-background-secondary, #f8f9fa);
        border: 1px solid var(--st-color-border, #e0e0e0);
        border-radius: var(--radius-sm);
        padding: 10px 18px; margin-bottom: 16px;
        display: flex; flex-wrap: wrap; gap: 16px;
        font-size: 13px;
        color: var(--st-color-text-secondary, #666);
    }
    .status-bar .status-dot { width: 8px; height: 8px; border-radius: 50%; }
    .status-bar .status-dot.active {
        background: var(--success);
        box-shadow: 0 0 8px rgba(16,185,129,0.5);
    }
    .status-bar .status-dot.pending { background: var(--warning); }
    
    /* ========== Buttons ========== */
    .stButton > button {
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important; font-size: 14px !important;
        padding: 10px 24px !important;
        transition: all 0.2s !important; border: none !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5, #6366f1) !important;
        color: #fff !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4338ca, #4f46e5) !important;
        box-shadow: 0 4px 12px rgba(99,102,241,0.4) !important;
    }
    
    /* ========== Progress Bars ========== */
    .custom-progress {
        height: 8px;
        background: var(--st-color-border, #e0e0e0);
        border-radius: 4px; overflow: hidden;
        margin: 8px 0;
    }
    .custom-progress .fill {
        height: 100%; border-radius: 4px;
        transition: width 0.6s ease;
    }
    
    /* ========== Expanders (theme-responsive) ========== */
    .streamlit-expanderHeader {
        background: var(--st-color-background-secondary, #f8f9fa) !important;
        border: 1px solid var(--st-color-border, #e0e0e0) !important;
        border-radius: var(--radius-sm) !important;
    }
    
    /* ========== Input fields ========== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: var(--radius-sm) !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    }
    
    /* ========== File Uploader ========== */
    .stFileUploader > section {
        border: 2px dashed var(--st-color-border, #ccc) !important;
        border-radius: var(--radius) !important;
        padding: 24px !important;
        transition: border-color 0.2s;
    }
    .stFileUploader > section:hover {
        border-color: #6366f1 !important;
    }
    
    /* ========== Scrollbar ========== */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(128,128,128,0.3); border-radius: 3px;
    }
    
    /* ========== Misc ========== */
    .divider {
        border-top: 1px solid var(--st-color-border, #e0e0e0);
        margin: 20px 0;
    }
    .empty-state {
        text-align: center; padding: 60px 20px;
        color: var(--st-color-text-secondary, #666);
    }
    .empty-state .icon { font-size: 48px; margin-bottom: 16px; }
    .empty-state h3 {
        color: var(--st-color-text-primary, #111);
        margin-bottom: 8px;
    }
    
    /* Sidebar - inherit Streamlit native theming */
    section[data-testid="stSidebar"] .block-container {
        padding: 1.5rem 1rem;
    }
    
    @media (max-width: 768px) {
        .main .block-container { padding: 1rem; }
        .app-header { padding: 20px 24px; }
    }
    /* ── Tab-style radio navigation ── */
    [data-testid="stHorizontalBlock"] [data-testid="stRadio"] > div {
        display: flex; gap: 4px; padding: 4px; background: var(--surface); border-radius: var(--radius);
        border: 1px solid var(--border);
    }
    [data-testid="stHorizontalBlock"] [data-testid="stRadio"] label {
        flex: 1; text-align: center; border-radius: 10px; padding: 8px 16px !important;
        margin: 0 2px; font-weight: 500; color: var(--text-2); cursor: pointer; transition: all 0.25s;
    }
    [data-testid="stHorizontalBlock"] [data-testid="stRadio"] label:hover { color: var(--text); background: var(--surface-hover); }
    [data-testid="stHorizontalBlock"] [data-testid="stRadio"] label[data-selected="true"],
    [data-testid="stHorizontalBlock"] [data-testid="stRadio"] label[data-checked="true"] {
        background: var(--primary); color: #fff; font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

LOGO_B64 = "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"

# ── Session State Init ──────────────────────────────
DEFAULTS = {
    "analysis_done": False, "jd_text": "", "resume_text": "",
    "jd_data": {}, "resume_data": {}, "match_result": {},
    "all_questions": [], "ambiguity_followups": [],
    "selected_questions": [], "remaining_pool": [],
    "interview_started": False, "interviewer": None,
    "chat_messages": [], "interview_done": False,
    "report_data": {}, "tts_enabled": False,
    "tts_engine": "edge-tts (免费)", "tts_voice": "云扬 (专业男声)",
    "digital_human_enabled": True,
    "n_rounds": settings.DEFAULT_SAMPLE_ROUNDS,
    "active_tab": "📄 简历分析",
    "interview_link_info": None,   # 面试链接信息 {token, link, ...}
    "voice_input_text": "",        # 语音识别的文本
}
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Helper Functions ─────────────────────────────────
def tag_class(cat):
    m = {"技术基础":"tag-tech","项目深挖":"tag-project","场景设计":"tag-scene",
         "行为面试":"tag-behavior","模糊点追问":"tag-ambiguity"}
    return m.get(cat, "tag-dim")

def score_color(s):
    if s >= 90: return "#10b981"
    if s >= 75: return "#3b82f6"
    if s >= 60: return "#f59e0b"
    return "#ef4444"

def render_score_ring(score, size=140, stroke=8):
    c = score_color(score)
    r = (size - stroke) // 2
    cx, cy = size // 2, size // 2
    circ = 2 * 3.14159 * r
    dash = (score / 100) * circ
    fsize = 42 if size >= 140 else 28
    return f"""
    <div class="score-ring-container">
        <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
            <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="var(--surface-2)" stroke-width="{stroke}"/>
            <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{c}" stroke-width="{stroke}"
                stroke-dasharray="{dash} {circ}" stroke-linecap="round"/>
        </svg>
        <div class="score-value" style="color:{c}">{score}</div>
    </div>
    """

def render_question_card(q, idx=None):
    """Render a single question card as HTML"""
    cat = q.get("category", "未分类")
    diff = q.get("difficulty", "")
    diff_map = {"简单":"🟢","中等":"🟡","困难":"🔴"}
    diff_icon = diff_map.get(diff, "")
    tags_html = f'<span class="tag {tag_class(cat)}">{cat}</span>'
    title = q.get("question", "")[:120]
    intent = q.get("intent", "")[:80]
    return f"""
    <div class="question-card">
        <div class="q-header">
            <div class="q-title">{diff_icon} {title}</div>
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin-top:6px;">
            {tags_html}
            <span style="color:var(--text-3);font-size:12px;">难度 {diff}</span>
        </div>
        <div style="margin-top:6px;color:var(--text-2);font-size:13px;">{intent}</div>
    </div>"""

def render_digital_human(speak_text="", persona_name="面试官", w=220, h=290):
    """专业 SVG 虚拟面试官形象 — 西装半身，嘴部随语音开合，眨眼联动"""
    mute = st.session_state.get("tts_enabled", False)
    mute_js = "false" if mute else "true"
    # 角色配色（支持多角色扩展，当前统一：深蓝西装+白衬衫+领带）
    suit_color = "#1e2240"
    shirt_color = "#f5f0eb"
    tie_color = "#818cf8"
    skin_color = "#edd9c4"
    hair_color = "#2a1f14"

    html_str = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{
  background:#1a1d27;display:flex;flex-direction:column;align-items:center;
  justify-content:center;height:100%;overflow:hidden;font-family:system-ui,sans-serif;
}}
.svg-wrap{{position:relative;width:{w}px;height:{h-32}px;}}
.name-tag{{
  color:#9aa0b0;font-size:11px;text-align:center;margin-top:6px;
  letter-spacing:0.5px;
}}
/* CSS 呼吸动画 */
@keyframes breathe{{
  0%,100%{{transform:translateY(0);}}
  50%{{transform:translateY(-1.5px);}}
}}
@keyframes blinkE {{
  0%,90%,100%{{ry:8.5;}}
  93%{{ry:1.5;}}
}}
@keyframes blinkPupil {{
  0%,90%,100%{{ry:3.8;opacity:1;}}
  93%{{ry:0.5;opacity:0.3;}}
}}
.breath{{animation:breathe 3.5s ease-in-out infinite;}}
.eye-l{{animation:blinkE 4s ease-in-out infinite;}}
.eye-r{{animation:blinkE 4s ease-in-out 0.15s infinite;}}
.pupil-l{{animation:blinkPupil 4s ease-in-out infinite;}}
.pupil-r{{animation:blinkPupil 4s ease-in-out 0.15s infinite;}}
</style></head><body>
<div class="svg-wrap breath">
<svg viewBox="0 0 220 260" width="220" height="260" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="glow" cx="50%" cy="35%" r="50%">
      <stop offset="0%" stop-color="rgba(99,102,241,0.12)"/>
      <stop offset="100%" stop-color="rgba(99,102,241,0)"/>
    </radialGradient>
    <radialGradient id="cheekL" cx="30%" cy="58%">
      <stop offset="0%" stop-color="rgba(233,150,140,0.2)"/>
      <stop offset="100%" stop-color="rgba(237,217,196,0)"/>
    </radialGradient>
    <radialGradient id="cheekR" cx="70%" cy="58%">
      <stop offset="0%" stop-color="rgba(233,150,140,0.2)"/>
      <stop offset="100%" stop-color="rgba(237,217,196,0)"/>
    </radialGradient>
    <linearGradient id="hairGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#3d2b18"/>
      <stop offset="100%" stop-color="#1a1008"/>
    </linearGradient>
    <filter id="softShadow">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.25"/>
    </filter>
  </defs>

  <!-- Background glow -->
  <ellipse cx="110" cy="90" rx="95" ry="120" fill="url(#glow)"/>

  <!-- === 身体 / 西装 === -->
  <!-- 肩膀轮廓 -->
  <path d="M30,200 Q20,175 28,150 L52,130 L168,130 L192,150 Q200,175 190,200"
        fill="{suit_color}" stroke="#151a30" stroke-width="0.5"/>
  <!-- 肩部线条 -->
  <path d="M28,150 Q35,165 45,175 L110,172 L175,175 Q185,165 192,150"
        fill="none" stroke="#252d4a" stroke-width="1"/>
  <!-- 翻领左 -->
  <path d="M56,132 L75,175 Q85,180 100,170 L110,145 Z" fill="#252d4a"/>
  <!-- 翻领右 -->
  <path d="M164,132 L145,175 Q135,180 120,170 L110,145 Z" fill="#252d4a"/>

  <!-- 衬衫 V 领 -->
  <path d="M88,134 L95,178 L110,188 L125,178 L132,134 Z" fill="{shirt_color}"/>
  <!-- 衬衫中线 -->
  <line x1="110" y1="136" x2="110" y2="175" stroke="#e0d5c5" stroke-width="0.5"/>

  <!-- 领带 -->
  <path d="M102,108 L118,108 L116,145 L112,148 L110,188 L108,148 L104,145 Z" fill="{tie_color}"/>
  <!-- 领带结 -->
  <path d="M104,108 L116,108 L112,100 L108,100 Z" fill="{tie_color}"/>
  <!-- 领带高光 -->
  <line x1="110" y1="102" x2="110" y2="170" stroke="rgba(255,255,255,0.08)" stroke-width="2"/>

  <!-- === 颈部 === -->
  <path d="M96,82 Q108,90 110,90 Q112,90 124,82 L128,135 L92,135 Z" fill="{skin_color}"/>
  <!-- 颈部阴影 -->
  <ellipse cx="110" cy="130" rx="16" ry="4" fill="rgba(180,150,130,0.3)"/>

  <!-- === 头部 === -->
  <!-- 脸型（椭圆+下巴） -->
  <path d="M65,75 Q65,35 90,18 Q110,12 130,18 Q155,35 155,75 Q158,100 145,118 Q130,132 110,134 Q90,132 75,118 Q62,100 65,75 Z"
        fill="{skin_color}" filter="url(#softShadow)"/>
  <!-- 脸颊红晕 -->
  <ellipse cx="85" cy="90" rx="18" ry="12" fill="url(#cheekL)"/>
  <ellipse cx="135" cy="90" rx="18" ry="12" fill="url(#cheekR)"/>

  <!-- 耳朵 -->
  <ellipse cx="62" cy="78" rx="6" ry="11" fill="{skin_color}" stroke="rgba(190,160,135,0.5)" stroke-width="0.5"/>
  <ellipse cx="158" cy="78" rx="6" ry="11" fill="{skin_color}" stroke="rgba(190,160,135,0.5)" stroke-width="0.5"/>
  <!-- 耳朵内部 -->
  <ellipse cx="62" cy="78" rx="3.5" ry="7" fill="rgba(210,175,150,0.5)"/>
  <ellipse cx="158" cy="78" rx="3.5" ry="7" fill="rgba(210,175,150,0.5)"/>

  <!-- === 头发 === -->
  <!-- 后发 -->
  <path d="M60,72 Q55,40 75,20 Q95,8 110,7 Q125,8 145,20 Q165,40 160,72
           Q162,50 140,28 Q120,15 110,14 Q100,15 80,28 Q58,50 60,72 Z"
        fill="{hair_color}" opacity="0.6"/>
  <!-- 主发（波浪M字刘海） -->
  <path d="M58,70 Q56,40 68,24 Q80,10 98,8 L100,18 Q90,22 82,32 Q70,48 66,70 Z"
        fill="url(#hairGrad)"/>
  <path d="M162,70 Q164,40 152,24 Q140,10 122,8 L120,18 Q130,22 138,32 Q150,48 154,70 Z"
        fill="url(#hairGrad)"/>
  <!-- 顶发 -->
  <path d="M70,22 Q80,10 95,6 L105,6 L110,5 L115,6 L125,6 Q140,10 150,22
           Q145,14 130,8 Q115,5 110,6 Q105,5 90,8 Q75,14 70,22 Z"
        fill="url(#hairGrad)"/>
  <!-- 刘海 -->
  <path d="M66,48 Q68,36 78,28 Q85,22 92,26 L96,42 Q86,38 78,44 Q70,48 66,56 Z"
        fill="#352816"/>
  <path d="M154,48 Q152,36 142,28 Q135,22 128,26 L124,42 Q134,38 142,44 Q150,48 154,56 Z"
        fill="#352816"/>
  <path d="M92,24 Q98,20 105,22 Q108,24 106,30 Q102,32 96,30 Q92,27 92,24 Z"
        fill="#2a1a0e"/>
  <path d="M128,24 Q122,20 115,22 Q112,24 114,30 Q118,32 124,30 Q128,27 128,24 Z"
        fill="#2a1a0e"/>

  <!-- === 眉毛 === -->
  <path d="M76,60 Q82,55 94,58" fill="none" stroke="#3d2b18" stroke-width="2.2" stroke-linecap="round"/>
  <path d="M144,60 Q138,55 126,58" fill="none" stroke="#3d2b18" stroke-width="2.2" stroke-linecap="round"/>

  <!-- === 眼睛 === -->
  <!-- 左眼 -->
  <ellipse class="eye-l" cx="90" cy="72" rx="9" ry="8.5" fill="#fff" stroke="#c0a890" stroke-width="0.8"/>
  <ellipse class="pupil-l" cx="90" cy="72" rx="5" ry="3.8" fill="#2a2218"/>
  <circle cx="88" cy="70" r="1.8" fill="#fff" opacity="0.8"/>
  <circle cx="91.5" cy="73" r="0.8" fill="#fff" opacity="0.4"/>
  <!-- 右眼 -->
  <ellipse class="eye-r" cx="130" cy="72" rx="9" ry="8.5" fill="#fff" stroke="#c0a890" stroke-width="0.8"/>
  <ellipse class="pupil-r" cx="130" cy="72" rx="5" ry="3.8" fill="#2a2218"/>
  <circle cx="128" cy="70" r="1.8" fill="#fff" opacity="0.8"/>
  <circle cx="131.5" cy="73" r="0.8" fill="#fff" opacity="0.4"/>
  <!-- 下眼睑 -->
  <path d="M82,79 Q90,83 98,79" fill="none" stroke="rgba(180,150,130,0.4)" stroke-width="0.5"/>
  <path d="M122,79 Q130,83 138,79" fill="none" stroke="rgba(180,150,130,0.4)" stroke-width="0.5"/>

  <!-- === 鼻子 === -->
  <path d="M108,76 Q106,82 105,92 Q104,96 107,98 Q110,100 113,98 Q116,96 115,92"
        fill="none" stroke="rgba(180,150,130,0.5)" stroke-width="0.8"/>
  <ellipse cx="110" cy="98" rx="4.5" ry="2.5" fill="rgba(180,150,130,0.2)"/>
  <!-- 鼻梁高光 -->
  <line x1="110" y1="74" x2="110" y2="90" stroke="rgba(255,255,255,0.08)" stroke-width="1.5"/>

  <!-- === 嘴巴（JS 动画控制开合）=== -->
  <path id="mouth" d="M98,112 Q110,120 122,112" fill="none" stroke="#d4856e" stroke-width="1.6" stroke-linecap="round"/>

  <!-- 下巴阴影 -->
  <ellipse cx="110" cy="128" rx="14" ry="3" fill="rgba(180,150,130,0.15)"/>
</svg>
</div>
<div class="name-tag">🎤 {persona_name}</div>
<script>
(function(){{
  var mouth=document.getElementById("mouth");
  var target=0, current=0;
  var openPaths=[
    "M98,112 Q110,119 122,112",
    "M97,113 Q110,121 123,113",
    "M96,114 Q110,123 124,114",
    "M95,115 Q110,125 125,115"
  ];
  var closedPath="M98,112 Q110,120 122,112";
  function updateMouth(){{
    current+=(target-current)*0.25;
    var idx=Math.min(Math.floor(current*openPaths.length),openPaths.length-1);
    if(current<0.05){{mouth.setAttribute("d",closedPath);}}
    else{{mouth.setAttribute("d",openPaths[idx]);}}
    requestAnimationFrame(updateMouth);
  }}
  if(!{mute_js}){{
    setInterval(function(){{target=Math.random()>0.5?Math.random()*0.55:0;}},150);
  }}
  updateMouth();
}})();
</script></body></html>"""
    components.html(html_str, height=h, scrolling=False)


# ── TTS 语音播报 ──────────────────────────────────────
def speak_text(text: str):
    """
    根据侧边栏设置的语音引擎和发音人，生成 base64 音频，
    存入 session_state，由页面自动播放。
    
    讯飞失败时自动 fallback 到 edge-tts。
    """
    engine = st.session_state.get("tts_engine", "edge-tts (免费)")
    voice_label = st.session_state.get("tts_voice", "云扬 (专业男声)")
    from app.tts_utils import get_voice_code, generate_audio_base64
    voice = get_voice_code(voice_label)
    audio_b64 = None

    try:
        if "讯飞" in engine:
            from app.xunfei_tts import generate_xunfei_base64
            audio_b64 = generate_xunfei_base64(text, voice)
            if not audio_b64:
                # 讯飞失败，降级到 edge-tts
                audio_b64 = generate_audio_base64(text, "zh-CN-YunyangNeural")
        elif engine == "XTTS 离线SDK":
            audio_b64 = None  # SDK DLL 通常不可用，静默跳过
        else:
            audio_b64 = generate_audio_base64(text, voice)
    except Exception:
        # 兜底：edge-tts 默认发音人
        try:
            audio_b64 = generate_audio_base64(text, "zh-CN-YunyangNeural")
        except Exception:
            audio_b64 = None

    if audio_b64:
        st.session_state["pending_audio_b64"] = audio_b64


# ── Sidebar ──────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        _, col_c, _ = st.columns([1, 1, 1])
        with col_c:
            st.image("logo.png", width=60)
        
        st.markdown("---")
        
        # Model info
        st.markdown(f"""
        <div style="font-size:12px;color:var(--text-2);margin-bottom:16px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span>模型</span><span style="color:var(--primary-l);">{settings.LLM_MODEL}</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span>TTS</span><span style="color:var(--primary-l);">{settings.TTS_ENGINE}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span>面试轮数</span><span style="color:var(--primary-l);">{st.session_state.n_rounds}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Settings
        st.markdown("**⚙️ 设置**")
        n = st.slider("面试题数", 3, 15, st.session_state.n_rounds, key="sidebar_rounds")
        st.session_state.n_rounds = n
        st.session_state.tts_enabled = st.toggle("🔊 TTS 语音播报", st.session_state.tts_enabled)
        
        if st.session_state.tts_enabled:
            # TTS 引擎选择
            engines = ["edge-tts (免费)", "讯飞 WebSocket TTS", "XTTS 离线SDK"]
            cur_engine = st.session_state.get("tts_engine", engines[0])
            idx = engines.index(cur_engine) if cur_engine in engines else 0
            st.session_state["tts_engine"] = st.selectbox("语音引擎", engines, index=idx, key="sidebar_tts_engine",
                help="edge-tts: 免费无需配置 | 讯飞: 在线API | XTTS: 离线SDK")
            
            # 发音人选择（从共享 VOICE_REGISTRY 获取）
            from app.tts_utils import get_voice_options
            options = get_voice_options(st.session_state["tts_engine"])
            if options:
                voice_labels = [label for label, _ in options]
                cur_voice = st.session_state.get("tts_voice", voice_labels[0])
                if cur_voice not in voice_labels:
                    cur_voice = voice_labels[0]
                st.session_state["tts_voice"] = st.selectbox(
                    "发音人", voice_labels, 
                    index=voice_labels.index(cur_voice), 
                    key="sidebar_tts_voice"
                )
        
        st.session_state.digital_human_enabled = st.toggle("👤 虚拟主播", st.session_state.digital_human_enabled)
        
        st.markdown("---")
        
        # Reset
        if st.button("🔄 重置会话", use_container_width=True):
            for key in DEFAULTS:
                st.session_state[key] = DEFAULTS[key]
            st.rerun()
        
        # Footer
        st.markdown(f"""
        <div style="position:fixed;bottom:20px;font-size:11px;color:var(--text-3);">
            MIT License · 2026
        </div>
        """, unsafe_allow_html=True)

# ── Voice Input Component ────────────────────────────
def voice_input_widget(key="voice_input"):
    """浏览器语音识别输入组件（Web Speech API）"""
    return st.components.v1.html(f"""
    <div id="voice-container-{key}" style="display:flex;align-items:center;gap:8px;">
        <button id="mic-btn-{key}" onclick="toggleVoice('{key}')"
            style="width:40px;height:40px;border-radius:50%;border:2px solid #6366f1;
            background:#1e1b4b;color:#a5b4fc;font-size:18px;cursor:pointer;
            display:flex;align-items:center;justify-content:center;transition:all 0.2s;"
            title="语音输入">
            🎤
        </button>
        <span id="status-{key}" style="font-size:12px;color:#94a3b8;"></span>
        <input type="hidden" id="result-{key}" value="">
    </div>
    <script>
    (function() {{
        var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        var isRecording = false;
        var recognition = null;

        function initRecognition() {{
            if (!recognition && SpeechRecognition) {{
                recognition = new SpeechRecognition();
                recognition.lang = 'zh-CN';
                recognition.interimResults = false;
                recognition.continuous = false;
                recognition.maxAlternatives = 1;

                recognition.onresult = function(event) {{
                    var transcript = event.results[0][0].transcript;
                    document.getElementById('result-{key}').value = transcript;
                    document.getElementById('mic-btn-{key}').innerHTML = '🎤';
                    document.getElementById('mic-btn-{key}').style.background = '#1e1b4b';
                    document.getElementById('status-{key}').textContent = '';
                    isRecording = false;
                    // Send back to Streamlit
                    var inputEl = window.parent.document.querySelector(
                        'iframe[title="components.vo·voice_input_widget"]'
                    );
                    // Fallback: use Streamlit's postMessage
                    window.parent.postMessage({{
                        isStreamlitMessage: true,
                        type: 'streamlit:setComponentValue',
                        value: transcript
                    }}, '*');
                }};

                recognition.onerror = function(event) {{
                    document.getElementById('status-{key}').textContent = '❌ ' + event.error;
                    document.getElementById('mic-btn-{key}').innerHTML = '🎤';
                    document.getElementById('mic-btn-{key}').style.background = '#1e1b4b';
                    isRecording = false;
                }};

                recognition.onend = function() {{
                    if (isRecording) {{
                        var statusEl = document.getElementById('status-{key}');
                        if (!statusEl.textContent.includes('❌')) {{
                            statusEl.textContent = '';
                        }}
                    }}
                    document.getElementById('mic-btn-{key}').innerHTML = '🎤';
                    document.getElementById('mic-btn-{key}').style.background = '#1e1b4b';
                    isRecording = false;
                }};
            }}
        }}

        window.toggleVoice = function(k) {{
            initRecognition();
            if (!recognition) {{
                document.getElementById('status-{key}').textContent = '⚠️ 浏览器不支持语音识别';
                return;
            }}
            if (isRecording) {{
                recognition.stop();
                isRecording = false;
                document.getElementById('mic-btn-{key}').innerHTML = '🎤';
                document.getElementById('mic-btn-{key}').style.background = '#1e1b4b';
                document.getElementById('status-{key}').textContent = '';
            }} else {{
                try {{
                    recognition.start();
                    isRecording = true;
                    document.getElementById('mic-btn-{key}').innerHTML = '🔴';
                    document.getElementById('mic-btn-{key}').style.background = '#ef4444';
                    document.getElementById('status-{key}').textContent = '正在聆听...';
                }} catch(e) {{
                    document.getElementById('status-{key}').textContent = '⚠️ ' + e.message;
                }}
            }}
        }};
    }})();
    </script>
    """, height=60)

def handle_voice_input():
    """检查语音输入组件返回值，有文本则填充到 session_state"""
    val = voice_input_widget()
    if val and isinstance(val, str) and val.strip():
        st.session_state.voice_input_text = val.strip()
        return val.strip()
    return None

# ── Candidate Interview Page ──────────────────────────
def page_candidate():
    """候选人独立面试页面（通过链接访问）"""
    from app.interview_link import get_interview, deactivate_interview
    from app.interviewer import InterviewerAgent, InterviewState

    token = st.session_state.get("candidate_token", "")
    interview_info = get_interview(token)

    if not interview_info:
        st.markdown("""
        <div style="text-align:center;padding:80px 20px;">
            <div style="font-size:64px;margin-bottom:20px;">⏰</div>
            <h2 style="color:var(--text);">链接已过期或不存在</h2>
            <p style="color:var(--text-2);font-size:14px;">请向面试官索取新的面试链接</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Candidate CSS ──
    st.markdown("""
    <style>
    .candidate-header {
        text-align:center;padding:30px 20px 10px;
        background:linear-gradient(135deg,rgba(99,102,241,0.08),rgba(139,92,246,0.04));
        border-bottom:1px solid rgba(99,102,241,0.1);margin-bottom:20px;
    }
    .candidate-header h1 { font-size:24px;color:var(--text);margin:0; }
    .candidate-header p { color:var(--text-2);font-size:13px;margin:4px 0 0; }
    .candidate-msg { font-size:14px;line-height:1.7;color:var(--text); }
    .candidate-msg.interviewer { background:rgba(99,102,241,0.06);padding:12px 16px;border-radius:12px;border:1px solid rgba(99,102,241,0.1);margin:8px 0; }
    .candidate-msg.candidate { background:rgba(16,185,129,0.06);padding:12px 16px;border-radius:12px;border:1px solid rgba(16,185,129,0.1);margin:8px 0; }
    .interview-ended {
        text-align:center;padding:40px 20px;
        background:linear-gradient(135deg,rgba(16,185,129,0.06),rgba(99,102,241,0.04));
        border-radius:16px;margin:20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Header ──
    st.markdown(f"""
    <div class="candidate-header">
        <h1>🤖 AI 面试</h1>
        <p>{interview_info['jd_title']} · 面试官：{interview_info['persona_name']}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Init candidate state ──
    for ck in ("candidate_name", "candidate_started", "candidate_agent", "candidate_messages", "candidate_done"):
        if ck not in st.session_state:
            st.session_state[ck] = None if ck == "candidate_agent" else ("" if ck == "candidate_name" else ([] if ck == "candidate_messages" else False))

    # ── Step 1: Name input ──
    if not st.session_state.candidate_name:
        st.markdown("""
        <div style="text-align:center;padding:40px 20px;">
            <div style="font-size:48px;margin-bottom:16px;">👋</div>
            <h3>欢迎参加面试</h3>
            <p style="color:var(--text-2);">请输入你的姓名开始面试</p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            name = st.text_input("你的姓名", placeholder="请输入姓名...", label_visibility="collapsed")
            if st.button("✅ 开始面试", type="primary", use_container_width=True, disabled=not name.strip()):
                st.session_state.candidate_name = name.strip()
                st.rerun()
        return

    # ── Step 2: Initialize Agent ──
    if not st.session_state.candidate_started:
        config = interview_info.get("interview_config", {})
        with st.spinner(f"正在准备面试..."):
            max_r = interview_info.get("max_rounds", 6)
            agent = InterviewerAgent(max_rounds=max_r)
            agent.load_parsed_data(
                config.get("jd_data", {}),
                config.get("resume_data", {}),
            )
            agent.initialize_persona()
            # 注入题库
            selected = config.get("selected_questions", [])
            remaining = config.get("remaining_pool", [])
            if selected:
                agent.inject_questions(selected, remaining)
            greeting, first_q = agent.generate_opening()
            # 个性化开场
            greeting = greeting.replace("候选人", st.session_state.candidate_name)
            greeting = greeting.replace("您好", f"{st.session_state.candidate_name}，您好")
            st.session_state.candidate_messages = [
                {"role": "interviewer", "content": f"{greeting}"},
            ]
            if first_q:
                st.session_state.candidate_messages.append(
                    {"role": "interviewer", "content": first_q}
                )
            st.session_state.candidate_agent = agent
            st.session_state.candidate_started = True
            st.rerun()

    # ── Step 3: Interview chat ──
    agent = st.session_state.candidate_agent

    # Display messages
    for msg in st.session_state.candidate_messages:
        cls = "interviewer" if msg["role"] == "interviewer" else "candidate"
        icon = "🤖" if msg["role"] == "interviewer" else "👤"
        st.markdown(f"""
        <div class="candidate-msg {cls}">
            <strong>{icon} {'AI面试官' if msg['role'] == 'interviewer' else st.session_state.candidate_name}</strong><br>
            {msg['content']}
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.candidate_done:
        st.markdown(f"""
        <div class="interview-ended">
            <div style="font-size:48px;">🎉</div>
            <h3>面试结束！</h3>
            <p style="color:var(--text-2);">感谢 {st.session_state.candidate_name} 的参与，面试结果已记录。</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("关闭页面", use_container_width=True):
            deactivate_interview(token)
            st.balloons()
        return

    # ── Voice + Text Input ──
    st.markdown("---")
    st.markdown("**💬 输入你的回答：**")

    # Voice input
    voice_text = handle_voice_input()
    if voice_text:
        st.session_state.voice_input_text = voice_text

    # Text input
    col_v, col_t = st.columns([1, 5])
    with col_v:
        pass  # voice widget already rendered via handle_voice_input above
    with col_t:
        user_input = st.text_input("", key="candidate_text_input",
                                   placeholder="输入回答，或点击 🎤 语音输入...",
                                   label_visibility="collapsed")

    submit_col, voice_status_col = st.columns([2, 3])
    with submit_col:
        submit = st.button("📨 发送回答", type="primary", use_container_width=True)
    with voice_status_col:
        if st.session_state.get("voice_input_text"):
            st.caption(f"🎤 语音识别: _{st.session_state.voice_input_text}_")

    final_input = user_input or st.session_state.get("voice_input_text", "")

    if submit and final_input.strip():
        # Process answer
        result = agent.process_answer(final_input.strip())
        st.session_state.candidate_messages.append(
            {"role": "candidate", "content": final_input.strip()}
        )
        if result["interview_ongoing"]:
            next_msg = result["message"]
            st.session_state.candidate_messages.append(
                {"role": "interviewer", "content": next_msg}
            )
        else:
            st.session_state.candidate_messages.append(
                {"role": "interviewer", "content": result.get("message", "面试结束")}
            )
            st.session_state.candidate_done = True
            deactivate_interview(token)
            # Save interview data for admin review
            st.session_state._last_candidate_data = agent.get_interview_data()
        # Clear voice input
        st.session_state.voice_input_text = ""
        st.rerun()

# ── Tab 1: Resume Analysis ───────────────────────────
def tab_resume_analysis():
    st.markdown("""
    <div class="app-header">
        <h1><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEYAAAA3CAYAAACxUDzgAAAYgElEQVR42t17eZxcVbXut/Y+59TYc7rTGQiGCCEdUJCgoGJ3Mz4mcepWUUFkFFT0Kgros7pEVFR4vJ/iTxC4goBQrU8lCohAdzCQiCFEMpE53UmPNVedqjrT3uv90WkIXPRCSK7i/qeqdp199l7f+tbaa+2B8LpLQvT09BHQ/yr/9QAA+vtJYZ8KU6JzUAJdWNwGftmbe4DB9aCuPb8HMYgudGn0gdEHwmLQq76ydZCouzvAv0Rhpn0BBf9CxXg9TAGSetF7Hl7cEmu+Xhg6rAEEhgVtGAzDZBGJ+74u3/ks0e+QYIEk6df0ZiREEqR7AHn0OTvPbbDCJ8ZNam2OsmyJSd0cN1U8ZvjRRsOP1MkAAAWKHbK0jzC5dlCpmfXCarDqDtfKg7AEIJkoahC7znJ5XOw7AJiI+LVK+5q11Nk5YCxb1h2c/NFnblDegq8GnAdZIWjTAiIRCCsMCAUnXOVKODh6/XVtz6O3X6C/V/1jUFgkQfoz714+O9I454GWaMt7o1IiagKNIUJL1ERz2EDMBEKWj2iU80aEMjKKWqSOomyoKoRaF6kLfciIyzAIgLVH5TT1WSkUjo6/q2kNMwui16as18yYrq4uvWwZcMjh8QdyHFwxUrKGnSDII0SaEfiyVg5JGT7GaGoOhWTxWyA6pyfF6O//x+azoaefLp9cFy/HrIfMaP3bR7y0HzVMI0om5UF2QYtc1hflBtMqNcZN1FtC1Skh476eUS3qAod5Y/OM8HtIi1BQUAFZILgASWgRInIr3ki2REM8Zd77nzEAkGAWSSJ9wvdzf/BnNp0U1OARQbDUTqDdNXJnedwK1feKWUKi3nnPUx9rWNmTYtnf++rOeJqF7z9r432RcNvHXafo1YWlETd0MSxpvCFk1JpDFG6Q0ooJUzeEQ7rOEoiHURZmsK6+2bKams1zDEvEfQ7YsgQJCcAEIFjJBikzQ8XPtb6/8RYeYIO6KTgAPgbY0D8FpM6Xbw7PbjrDi3JIEAFCxKg+cpIT46fEtsrKSKjlBFLBdUQ4pWP9q2tpGpSuMzec79fP+jhEPmhr962GUM3zbc8WvmnJSLRZS0mBZA6HzVg4xLaC2lmSnGsMh98thbmwaGsYVqBMiwXAWpoAmNmKGFSZcEdWb9r58z1seV0zpXg9D/f3kkokWDz13TsfZ7+0OjKL2GhUymzULIRWZnP4eHNeaJuVd9xGI3LyRY8WTu7rA/ekWL6MeQkWy5Z1B6efO3xkuK3xZ+HmdKWpPe0bsZIbSEeF60WzUaeblKgRwqpZhHVboVIcztu1Z3QQao4GsTOi2lzoVAAKBAw2pEUmhUiKMKQIa0MKCbF7rHDTaVcdVcEg5OtxvK+bMQAw2AWBZDLQlQtvCsfq73EsAgEkFJMVlcKzQgctttzn4u3hY0t25BIieqwn9bIx0YbFoGOOYZOtTV+ikLeWLKfNbGiaKyFAKoBlECJALMwKEa2elzNNGciGmJ2LHcPMsRK7kxkXOmKADQUtKwqGwTBNgiGZLdOg2m5n9IHVG29jZgLhdcdV+xZvMHDwpwdDiz517AvWzOjBQUVrzSQIgitK1c6M6V+edpB5oU9A2q6dcMbB0eWpFMveXlKX3LrKvO3SJf6l92y4eHKjfann6rpYfSxcy7tr6yw93NJg7Goyzd0EGil7zmjdtUu3Po3LQkduao+omTuDgcai3zRpkL+iQNgE7KiG1VhyibPHsfL+imP2KajqHGBjWTcFpz2aubZxYcv1bkEHOoDBASuOSImqeuiBI/VDMipPWLu79Jdj5zbezFN9MRFxYmj8EHvIuz2/ufZEecR+vD+xfDVwpbuvQtzB3GoBIV2DsAiiyXWM0xrC21/r1LxfTAkAlg32aQDkZ4I7eLZ3tRGx4rqmGCARuFoHJp0ae1RdgQ9at7z/htvrzsx7jfS9y/OpFMu/2PaRq3L2Wwp16kN3XrSw8GLIn0rJpvwhIuTUi+a3HaoWp8Hr14OTSTD4JSoQgJ5+iI71YP/c6qxYS+inhaJ+n6U4JAE2G8jMT/BD+D/4QIpZ9tK+pSf7HIb3MMt+InX5lsrtdn30wsqkCiggQ/kciKg0/Lz/wO/fZ31MaxZze3tDu/v7nYGJiVgYOOq4trYVRKQSA2xgEDqZJE4wU3IvDTMz/T2HmWAWGwA6dFT9eUa7PN7LMCIGQRKjwQDMDeXjP3Zcw8pp8/0fBWa60/vy+aNXVupWjeQJ0ocIXDArgJldVfU7Hjw1vJP6QEjSy30AM2GP4NMgXLO51NpxcN1BnwrRcwB472deBGWAjWQ3BV/c6X6ivsW6h/PKCxGZlmTV0CClGK49cfGi6MnTMde+yif2tWFvL6kEs/hkU9NzC43gqeZ6IUTAylREhgsVNmVYKPFFIuKePrwYdTLzVJ97BO5JsSQiTo57x8+aG3veIjy71An+/EiBmxN9IH55QkoYhO5hlo4rr3WKYN+DEfggz4OgEig+Wf0+CFj8BpT+hoABpjrXAI6IB9+eZQQsmSADZuGzVDnNhisu6EnZ7f0EjURCTOGxlxaZqaMHnGA2TCluj0ZEu+sotzkk32OG9LXJJOlBQL7k9AdkMkk6/DfvI8KSHbW81oFHwnehLJIUHXNWf6xzxp8S32Sxr75lvwDTS1Os6YzHH7XLbqKlQUjyWEufSFZYxcioQ1leBhB3ou+/9JUYhEwSaX9cfTLSKDtqORVowMz6UAH4ggdXvTCjmyiYZk3XYJfuHGADNfFNVQbrGsBVwLcZrT6owwpuJIC7ut6YXG/Ix+yt9QRA/YBxylr/BTdvzrfTiuGAERBxRU0gMBfe+wWU9zah6Xa5LTAjEbW+MS4PsQLFlgC3NUvpV/S973h47Y3ugkN2v+Md9elp39L7J+fD8frQr0RFqxBBWmDdFJLibdJdd847h5cAh3p7mMn/NMa8KOggxAYiT/h8nVBBUXoUmB4Js6pUA5ntMdu+GESc6HvJLKbZErB/PkXlgnxB6UKNRN4jGsnrYJcS3+pYl1+7sLrFBDMtToORYIGSvIYLYC4BQYEgKkBHSOOwkHM90WEuAPFGQdk/jNkrGk4M7gzlqy2/dfLht5BjLqSKryzXFFx2drkTuUW33jq7RnvccKIPtO2DiFisNoQj8iAKFBuCdLxJGG4h+OUPF5nnfvIZ9wiq8em/6Az/AGD66B3umaFoaCl7WsXCWjbFAj0vZIijws6m447MHU+N8wrMb5wt+4cxU/hyqh8i2T3faQm8R5r9amBWnQ3RwJSyplSTDM+rN8WFRMSJBGTnIGQySTrI+BcTy3n2hNLVAolKESI7ooJ8QX8PANySuDwImzd8fnWpFSD2isH/lq5GXPiIs4bKCNSXDbRG6A5qPDifSu0ftuxHxkxlzMk+8O1P1OZNjHj3F8Y9zZV4a1RHDjU9Ba5Vd0XMyqKv/LC9SgA+cQ/qHCt4wbREO2tmItahesPwK07/fedEes//Te0tZZhrwnNkA2n19cqd2Scbj2z9s4SvDZLC1KxnKKLTFgeZ407RxxBFdjOD3kgacAAYAySTpHv6IS46KTrEHv3MZBkyqsUJs2JvjPlKz4vXHRT1jfOJiEHEk6PpL6iSMas64it3whdu2hflYVeXsup7AGCn9ddNVzboYYao4OONjfITZprA6YCNgkI45/LRzZIOPwQpouiuPWzR+GcmkX9/gmIiAPc9ONG25QX/55Vhr64xgGqWUaO9rmWxpX3/mKg9f+auHHXNbN1hmlazQAAhWVt1jdJxcw//8ZrWM3punHhroBvWioiwOKxx0AKTnG21n3ornA9HGuOtlnB1uylF99uQeedHxbFAZHhqItp/wIj9CQxNzTw0q35mVrnjg3ZtSBfznuMUcyW/MPSHmRZNhKLx8zqidZeEuKVFFR3FFUW6HJBfqEBVazcAgJqUX7acUFhnHQ6rQOk0yAvCJ5pcGwyXNcm8o99iWVSn3GuJokP9/fuXLfsdGABYvLifurspaJELVsYjDZY0PF1UIhgu1fyNoztuu3336Jq2SP01WlVZSikJUIaMUeCWVz523bxln/ny9oNR5E8F6Txz2ZNxUuQM+7rOkQvDc2K2mpyYaNVRI1TLr1t0bvN/coJFby/0/pZjvwPT29ujAab6aNPf3Ko9nPNyUZcIxUg8tml0tPnhhuZzIy11LRxWmmIGcUgCMZOsON8MAJkRdQ1VzZgqlnWIPS1KBGQUhUoaUStyPLn+E+2IU7PEjUSkBgEBEP/LAwMQ9/T0iwu+RAVGdFWZG5q2lMozh7fvCK+ZHR015jaezyGlRb0lKC61aIgKGa2OnHf+nAdP+eSamJd3er18lsn2pOHxZLBTU8j2iTO2rq9ai1pmx2SQ2/7s3HrzNwDQlYTCASjiQLy0o6OHAWD+rPpH33XY7LkLWxvdsbc2PKk/cNznws0iLhsYVoMkI27qcFuIzEZxc+88qr37F2+vGWbwGNUk+W4tzwVA5LQUxYAtW5FZqHBbJHZSxKp+fcHVzcUEEoIOAFv2+6z0X/avifCVpYUbcvMaDs9Vcazlo90vKNa+IPiKCQLaDzIUVA/77acbi0TEn7nq2SUTz5nPhFtEMeLUx+MkjYhhIGZI1JHSs+Mx0dBuv/v917WvSPWw7O2nNw9jAKBzEBIAb/LssmjH2WED7WQEbDUSWfWAUS9UbLYgHXJ//LsLmgp9g5CJREL8/KYlq+a8nVc0hBobUXYFBR4QBIDrK9M1SancmrO/tXsVg+lAgXJAgVnWBQVmyv5h583+rtpEvAU6FAHMKGDGNYdbhAx8N1vbuvEWMFOyC2rDhj7SitH81vD1Xt6H0JqhNUgrsKdgGZKaD1K3Ei3xBxOD8kCedjhgwICIE4OQT9/53rKbK95W1wwRjgsVjhKsKKlYK0gHlVsev/Zd2c5BSBBxfz+pBBLiu5cd9nC4obbKMCKCNCtWWhNbIjCLQ2dfkr0bYOpKdqk3JzAAkoN9Gsy0Y2D9LSpdLdU1CwpHlIo3CWLbKZR3Z38MZlrWtdfMkugSRMSHLYl+L1pvUOAHrP1AWaZBjW3qVpqzpJroHJQHyun+j5UUT23PXrps1w+/x8xfTbOXYOaLnp749vTi9qslpMwsr7pw0+orTtrNn+vcztf1bimNrBqZweBXrgO/+RgDAL2ATjCL9Q/vvH50bfEJg1w/s7H4xM4nd/0gwSySXa8ehxCRmr8ouLC+zR5qbEKxrZ0vm7NkTqa3p3+/LS38S5Uzf/7cnNcSLkyzYmLdQHz1Q5tb96779ypTe0fTbHhN5/QSe3YWps0L/85lb2Ff61LGP4Mp9O9DSBZ75NH00g7ndKyj35Bf2lsz099fpq39oD1mli/uRr7GMQ0wG9Nt9sxYxivGKg4U2rTPz+83mjNhH8YxPZZMpjKXmU+u5WvzX/zf4+O5wh/M78g37pNZ/r7gXb6S+fmHcs7Z03V/qvlda5Vat9wJrp2ue5q5+alAPfu04/8kxSwHeE8MwkzT8QozU2IvDb70m+lWZvMxxz/76Yr3zgSzmB5o6iXKIzXFKNqLsbJS489Xa2pVueQPO1Ve47vq5nKZ26bZkk/Xuv2aynnVIJcfq1zHzLI27t+lKsz2qLutMFRYwCmWAwMDBqZOCxCnXhovMwtOvQqTU2O1Ex9h5nvT/gPTdfdl/bufYubflYOtm5lDAHB/zj1vFTM/UXT+46V44+WB2X+j4dByZn7KDX7335kATwFn7MoEDzIzpzPeIxNjleuz484fmZntfLCuuLvYAgDpXd5SO8O8cfnGOgBw0s5C9pmLW2rfeoWveVV38Xed738O7Ain5x20W2t4X3tOHvTpY2F2KLU9FuUZhjCkUau996L50RU3bg8ebaynEzuK6TnPmE1n1jdaX4Sn5pohmnTL/J3PzJK/uCvv/9FVlG+aYZzbS9D3FjCfYvrnbtZ/DKDTIjHrXa6rbEfJobBdO3veIZHJ8Wxwo8niQyaxMCX9RhdqfWfNj4+v2uF99tC3mD+ZGPavPuxg64bpQW9/wf7m/IWx5Oh29xo7C9HWZn7DrmhpCOOFQsG+I26EPx2LGm/3HT1ml4JNC7pDJ02ucc5qrDOTPvMhliEnnapK1HUY9zs7/TPNFnGVl/XusXzrU5Wy/0j9O8LfFT3M8oLu+U4xFzxck3LWt+fk58bHcVwVcpY3VvvG8Jimoaw8PcEJkS5Q566d+pnjF7RPuHbQ4Vfcv4ha+Wu1kp6QTfKuG7fjULuk1sdnGL2j250TAeLJrHeVhjhB1fSfalVek6lAFipIKydY7uSd4vqt+j4YxuXlgndXKefe7bO4tMrhxwYmJuJ2WZz/wibleNvztzCz2LyZQ8wsRtLZH21Zp51CkT5cq+ltuTTn7QLJatlf7Vb0Druo1roliGpJ766W1OPjf62d0hwPLXXsYKRmVy+slryNsbD85eiTmY6gpluFFp3hWvhnytXza/nqCDOT6BgcJACwJyv3lUvAUD7SbWe8ntwu5X0pNHxzdsRbW8zyGZMPX3mCD2Ep27sHAL7aEfvKQ0+Inz7xbGN5w2bx54lJsJ1RnTue3PSN4c0qKBSMi5gTomgb52/+q//gRfOjK7ZtCX21kAPsLP/l8oPNK0oIHS7D4oND691vXnBo5OpPHRa7amSjew0suXjz9oYTnCJCmUl20mhz0Afcey989AFjTeXKxEjglrLUdFRn9IHsWLC2nAtowTutC446uWFpYbJ6I/lANl2568hzot+pZPE5exI8NuQ+k9lhxMa2qRVUAWpZ8/PVEmcwAZWf8H9tHWHOm3lS890gQCS7ptL38tjG5WPPV0vlnLrCK/FH7LHaUjriCM/NVJeWc3Sknbf6MpsdT9j2/+u5Nddw3q/dle1xfjyuqhfqsv/u9Ham/ISO3HjeUZWx9e6v8xlx9pcevTpRLomIk659l5mpEYW28ii4koVMMAs3r+bWsuBqSW/dc6oKpRw/V9oNPb7b9yrZYK3URsNoNj2fkqQXLwZRknR844zDw7Aa7Ly7NpViWSk4YTvt4o93j7Uxs7BLHMuMANUCRwYG2ChOuI35SehaEWeUc96VlYx/5ra1/tLsuN5WHlPhIA1ZyHEKANal2CIQCxBxT4rlnRe9t+yMZ/6gbGtJkPfajELmDgDQ2cyD1fGq9EuxrspQfjB51szxoFg9NULWu5AuXnbLh2OnFLeW/69XoMDO+C6YyZ3Ifbc05oacavib2a2VFd8/p2ElEXF6Y65aG3aouqvSgMFBUUmnl0+sr3puTn72phW7wg88NRRxMurL6a2O0LmRv+XS9o/LaZ90Jf7Lu342uujYVpipW3NH+vn6+7OjFVXLO9/p7SVVmPDcUsYNMiOeT0Q6O1IJchMIipOe191NQXay8gjZkLU8/+TYCxuX/MfFN524ZW36B+/8bNMPszvB45sRTO52PQbT4j0nyAUATK6fMid3YuJXQS5AbXQ4fVi8+CSYaX7pvtX2yMhWVQTcbO4+MJOXnlyTWTeZmRwVt5157dCgXaze6o7BcHZlIok+0K2fnfu8PZK928sAftb+EQB0JtgYe+rZTH7r8FO6ED99dNn87K5ny5zbOfZpNxOcsPNJM7PiSZ1xcs4pE9tGPpu89PDMxRfPeGZo066LKznnSK9Sv+GhFRMZp2o9XypUZ+/YOtLz/ktb/woAmfFSpJKXVnWyPJV4juVlJQMjPWJbALBpx+YfrVm76yFlx3/xu2uGdl11zcVlDf596kvrmse3p1HZBSOzOW/uvcZjAMCyZLcCgIlNzz0yc4F5gSEqQ1ed995Kz9KUTPYng7Ou7L4gyK0/vLRjw69BR/AfgC2nXvjI8aHmjnN8p+xxUH7MdLz3uJXi8uSPD9YA4JS3iaA6YhvNw78FmLoAnezv1Wdd8uAHlEsfIeWHYqE697avL7j/E1f+7blotO5/GXB1pjT8x1/c8r7NzEx9faCvfINu/+pFDz3SPGPRKUKYcx17cmjnllUP/6i/N51IDBjJZHdQLNrX531nXqUKGwD8Sm7rzt3bLvP80p8B4HM/6bYBnHnnJRvPDgnzeIYzPlIY+tXX7j81d/cnV67eWJWX5sullXvWSfQbyKP+/vzfdcXqK0+/evRPH/x6jk+7fPUXgKkDiP/olMQ/quvpSb1q29Tfqd9fOeErG1BnYkC2bUhz/14XsBIJFoMYFMuSXWp612+qDgJ77iaOzYacNdqnHhs5/VvR+EHH6epk6vHbjr4NiYRAMvmyA4mdfVML2XuYynuAEMAggC6dfMXNuKmMvEsAXQAG0dfXpfZOClM9Kbm+o5WSyem7j0yJBCTQp5Mv9U2pHhatHaCpG5WDOplMamamwT7IriTUm3659E1ZenpSsifFsjMxYLyZ5fj/8goODvwxzz4AAAAASUVORK5CYII=" style="width:36px;height:auto;vertical-align:middle;margin-right:10px;" alt="logo">简历智能分析</h1>
        <p>JD 解析 · 匹配评分 · 试题生成 · 模糊点追问</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.analysis_done:
        # Upload stage
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="card card-accent" style="margin-bottom:0;">
                <div class="card-header">📋 职位描述 (JD)</div>
                <p style="font-size:13px;color:var(--text-2);margin:0 0 12px 0;">上传 PDF / DOCX / TXT 格式</p>
            </div>
            """, unsafe_allow_html=True)
            jd_file = st.file_uploader("上传 JD 文件", type=["pdf", "docx", "txt"], key="jd_upload",
                                       label_visibility="collapsed")

        with col2:
            st.markdown("""
            <div class="card card-accent" style="margin-bottom:0;">
                <div class="card-header">👤 候选人简历</div>
                <p style="font-size:13px;color:var(--text-2);margin:0 0 12px 0;">上传 PDF / DOCX / TXT 格式</p>
            </div>
            """, unsafe_allow_html=True)
            resume_file = st.file_uploader("上传简历文件", type=["pdf", "docx", "txt"], key="resume_upload",
                                           label_visibility="collapsed")

        st.markdown("""
        <div class="divider" style="margin:16px 0;">
            <span style="background:var(--surface);padding:0 12px;color:var(--text-2);font-size:12px;">或</span>
        </div>
        """, unsafe_allow_html=True)

        jd_text_input = st.text_area("直接粘贴 JD 文本", height=80, key="jd_text_input",
                                      placeholder="在此粘贴职位描述...")

        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🔍 开始智能分析", type="primary", use_container_width=True,
                         disabled=not resume_file):
                if resume_file:
                    _run_analysis(jd_file, jd_text_input, resume_file)
    else:
        _show_analysis_results()

def _run_analysis(jd_file, jd_text_input, resume_file):
    """Execute the analysis pipeline"""
    with st.spinner("📖 正在解析文档..."):
        jd_text = ""
        if jd_file:
            jd_text = parse_uploaded_file(jd_file.read(), jd_file.name)
        elif jd_text_input.strip():
            jd_text = jd_text_input.strip()
        resume_text = parse_uploaded_file(resume_file.read(), resume_file.name)
        st.session_state.jd_text = jd_text
        st.session_state.resume_text = resume_text

    if not jd_text or not resume_text:
        st.error("请确保 JD 和简历内容不为空")
        return

    with st.spinner("🎯 正在评估匹配度..."):
        from app.matcher import run_match_pipeline
        pipeline = run_match_pipeline(jd_text, resume_text)
        if not pipeline.get("success"):
            st.error(f"分析失败: {pipeline.get('error', '')}")
            return
        st.session_state.jd_data = pipeline.get("jd_data", {})
        st.session_state.resume_data = pipeline.get("resume_data", {})
        st.session_state.match_result = pipeline.get("match_result", {})

    with st.spinner("📝 正在生成面试题..."):
        from app.question_generator import run_question_pipeline
        qp = run_question_pipeline(
            jd_data=st.session_state.jd_data,
            resume_data=st.session_state.resume_data,
            match_result=st.session_state.match_result,
        )
        if qp.get("success"):
            st.session_state.all_questions = qp.get("questions", {}).get("questions", [])
            st.session_state.ambiguity_followups = qp.get("ambiguity_followups", {})
        else:
            st.warning(f"试题生成部分异常: {qp.get('error', '')}")

    st.session_state.analysis_done = True
    st.rerun()

def _show_analysis_results():
    """Display analysis results"""
    match = st.session_state.match_result
    questions = st.session_state.all_questions

    # 防御：analysis_done=True 但数据丢失（比如服务重启后 session 残留）
    if not match or not isinstance(match, dict) or "overall_score" not in match:
        st.warning("⚠️ 分析数据丢失，请重新上传文件分析。")
        st.session_state.analysis_done = False
        st.rerun()
        return

    # ── Stats Row ──
    score = match.get("overall_score", 0)
    n_questions = len(st.session_state.all_questions)
    rec = match.get("recommendation", "")
    
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-item">
            <div class="stat-value" style="color:{score_color(score)}">{score}<span style="font-size:16px">/100</span></div>
            <div class="stat-label">综合匹配度</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{n_questions}</div>
            <div class="stat-label">面试题</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" style="color:{score_color(score)}">{rec}</div>
            <div class="stat-label">录用建议</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{st.session_state.jd_data.get('title', '?')}</div>
            <div class="stat-label">目标岗位</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Match Details ──
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(render_score_ring(score), unsafe_allow_html=True)
    with col2:
        bd = match.get("score_breakdown", {})
        dim_labels = {"skills_match":"技能匹配","experience_match":"经验匹配",
                      "education_match":"学历匹配","project_relevance":"项目相关"}
        
        st.markdown('<div style="padding-top:8px;">', unsafe_allow_html=True)
        for i, (dim, info) in enumerate(bd.items()):
            s = info.get("score", 0)
            c = score_color(s)
            label = dim_labels.get(dim, dim)
            st.markdown(f"""
            <div class="score-bar-row">
                <span class="score-bar-label">{label}</span>
                <div class="score-bar-track">
                    <div class="score-bar-fill" style="width:{s}%;background:linear-gradient(90deg,{c},{c}88);"></div>
                </div>
                <span class="score-bar-value" style="color:{c};">{s}分</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Recommendation reason
        reason = match.get("recommendation_reason", "")
        if reason:
            st.markdown(f"""
            <div style="margin-top:12px;padding:10px 14px;background:var(--surface-2);border-radius:8px;font-size:13px;">
                <span style="color:var(--text-2);">💡 </span>
                <span style="color:var(--text);">{reason[:200]}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Detail Expanders ──
    with st.expander("📋 匹配详情"):
        tabs = st.tabs(["✅ 优势", "⚠️ 差距", "🔴 风险"])
        with tabs[0]:
            points = match.get("matched_points", [])
            if points:
                for p in points:
                    st.markdown(f"""
                    <div style="padding:6px 10px;margin:4px 0;background:rgba(16,185,129,0.08);border-radius:6px;font-size:13px;color:var(--text);">
                        ✅ {p}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("暂无匹配优势项")
        with tabs[1]:
            points = match.get("gap_points", [])
            if points:
                for p in points:
                    st.markdown(f"""
                    <div style="padding:6px 10px;margin:4px 0;background:rgba(245,158,11,0.08);border-radius:6px;font-size:13px;color:var(--text);">
                        ⚠️ {p}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("暂无差距项")
        with tabs[2]:
            points = match.get("risk_points", [])
            if points:
                for p in points:
                    st.markdown(f"""
                    <div style="padding:6px 10px;margin:4px 0;background:rgba(239,68,68,0.08);border-radius:6px;font-size:13px;color:var(--text);">
                        🔴 {p}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("暂无风险项")

    # ── Questions ──
    if questions:
        st.markdown('<div class="section-title">📝 面试题库</div>', unsafe_allow_html=True)
        by_cat = defaultdict(list)
        for q in questions:
            by_cat[q.get("category", "未分类")].append(q)

        cat_icons = {"技术基础":"💻","项目深挖":"🔬","场景设计":"🏗","行为面试":"💬","模糊点追问":"🔍"}
        cat_colors = {"技术基础":"#60a5fa","项目深挖":"#34d399","场景设计":"#fbbf24","行为面试":"#f472b6","模糊点追问":"#c084fc"}
        for cat, qs in by_cat.items():
            icon = cat_icons.get(cat, "📌")
            cat_color = cat_colors.get(cat, "var(--primary)")
            with st.expander(f"{icon} {cat} · {len(qs)} 题", expanded=(cat=="技术基础")):
                for q in qs:
                    st.markdown(render_question_card(q), unsafe_allow_html=True)

    # ── Ambiguity Followups ──
    followups = st.session_state.ambiguity_followups
    if followups:
        groups = followups.get("followup_groups", [])
        if groups:
            with st.expander("🔍 模糊点深度追问"):
                for g in groups:
                    sev = g.get("severity", "")
                    sev_badge = {"high":"🔴 高危","medium":"🟡 关注","low":"🟢 低风险"}.get(sev, "")
                    sev_bg = {"high":"rgba(239,68,68,0.08)","medium":"rgba(245,158,11,0.08)","low":"rgba(16,185,129,0.08)"}.get(sev, "transparent")
                    st.markdown(f"""
                    <div style="margin:10px 0;padding:12px 14px;background:{sev_bg};border-radius:8px;border-left:3px solid {score_color(90 if sev=='low' else 60 if sev=='medium' else 30)};">
                        <strong>{sev_badge}：{g.get('ambiguous_point', '')}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    for fq in g.get("followups", []):
                        st.markdown(f"- *{fq.get('question', '')}*")
                        if fq.get("red_flag"):
                            st.caption(f"  🚩 {fq['red_flag']}")

    # ── Actions ──
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Interview Link Card ──
    link_info = st.session_state.get("interview_link_info")
    if not link_info:
        st.markdown('<div class="section-title">📎 面试链接</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="padding:12px 16px;margin:8px 0;background:var(--surface-card);border-radius:10px;border:1px dashed var(--border);font-size:13px;color:var(--text-2);">
            💡 生成专属面试链接，发送给候选人即可独立进行 AI 面试（支持语音+文字输入）
        </div>
        """, unsafe_allow_html=True)
        col_link, col_start = st.columns(2)
        with col_link:
            if st.button("📎 生成面试链接", use_container_width=True, disabled=not questions,
                         help="生成候选人专属面试链接"):
                from app.question_sampler import sample_questions_for_interview
                from app.interview_link import create_interview_link
                selected, remaining = sample_questions_for_interview(questions, st.session_state.n_rounds)
                st.session_state.selected_questions = selected
                st.session_state.remaining_pool = remaining
                st.session_state.interview_started = True
                # 打包面试配置供候选人端使用
                config = {
                    "jd_data": st.session_state.jd_data,
                    "resume_data": st.session_state.resume_data,
                    "selected_questions": selected,
                    "remaining_pool": remaining,
                }
                link_info = create_interview_link(
                    base_url=f"http://{settings.HOST}:{settings.PORT}",
                    jd_title=st.session_state.jd_data.get("title", "岗位面试"),
                    persona_name="AI面试官",
                    max_rounds=len(selected) + 2,
                    interview_config=config,
                )
                st.session_state.interview_link_info = link_info
                st.rerun()
        with col_start:
            if st.button("🚀 自行测试面试", type="primary", use_container_width=True, disabled=not questions):
                from app.question_sampler import sample_questions_for_interview
                selected, remaining = sample_questions_for_interview(questions, st.session_state.n_rounds)
                st.session_state.selected_questions = selected
                st.session_state.remaining_pool = remaining
                st.session_state.interview_started = True
                st.session_state.active_tab = "🤖 AI 面试"
                if "_nav_radio" in st.session_state:
                    del st.session_state["_nav_radio"]
                st.rerun()
    else:
        # 已生成链接，展示链接卡片
        st.markdown(f"""
        <div class="section-title">📎 面试链接已生成</div>
        <div style="padding:16px;margin:10px 0;background:linear-gradient(135deg,rgba(99,102,241,0.08),rgba(139,92,246,0.06));border:1px solid rgba(99,102,241,0.2);border-radius:12px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                <span style="font-size:24px;">🔗</span>
                <div>
                    <div style="font-weight:600;color:var(--text);font-size:14px;">面试链接</div>
                    <div style="font-size:12px;color:var(--text-3);">发送给候选人即可开始 · 有效期48小时</div>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
                <code style="flex:1;padding:8px 12px;background:var(--surface);border-radius:6px;font-size:13px;word-break:break-all;color:var(--primary);">
                    {link_info["link"]}
                </code>
            </div>
            <div style="display:flex;gap:8px;margin-top:8px;font-size:12px;color:var(--text-3);">
                <span>📋 {link_info["jd_title"]}</span>
                <span>⏰ 有效期至 {link_info["expires_at"]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Streamlit 原生 copy button
        st.code(link_info["link"], language=None)
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("🔄 重新生成链接", use_container_width=True):
                st.session_state.interview_link_info = None
                st.rerun()
        with col_r2:
            if st.button("🚀 自行测试面试", type="primary", use_container_width=True):
                # 重新采样题库（如果 session 刷新后丢失）
                if not st.session_state.get("selected_questions"):
                    from app.question_sampler import sample_questions_for_interview
                    qs = st.session_state.all_questions
                    if qs:
                        sel, rem = sample_questions_for_interview(qs, st.session_state.n_rounds)
                        st.session_state.selected_questions = sel
                        st.session_state.remaining_pool = rem
                st.session_state.interview_started = True
                st.session_state.active_tab = "🤖 AI 面试"
                if "_nav_radio" in st.session_state:
                    del st.session_state["_nav_radio"]
                st.rerun()

# ── Tab 2: AI Interview ─────────────────────────────
def tab_ai_interview():
    st.markdown("""
    <div class="app-header">
        <h1><img src="data:image/png;base64,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" style="width:36px;height:auto;vertical-align:middle;margin-right:10px;" alt="logo">AI 模拟面试</h1>
        <p>多维度追问 · 数字人交互 · 实时评估</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.analysis_done:
        st.markdown("""
        <div class="empty-illustration">
            <div class="ei-icon">📋</div>
            <div class="ei-title">请先完成简历分析</div>
            <div class="ei-desc">切换到「简历分析」Tab，上传 JD 和简历后系统将自动生成面试题库</div>
        </div>
        """, unsafe_allow_html=True)
        return

    if not st.session_state.interview_started:
        _show_interview_prep()
    else:
        _show_interview_active()

def _show_interview_prep():
    questions = st.session_state.all_questions
    jd_title = st.session_state.jd_data.get('title', '未知岗位')
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="feature-card">
            <span class="fc-icon">📝</span>
            <div class="fc-value">{len(questions)}</div>
            <div class="fc-label">面试题</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="feature-card">
            <span class="fc-icon">🎯</span>
            <div class="fc-value">{st.session_state.n_rounds}</div>
            <div class="fc-label">抽取轮数</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        rec = st.session_state.match_result.get('recommendation', '—')
        score_val = st.session_state.match_result.get('overall_score', 0)
        c = score_color(score_val)
        st.markdown(f"""
        <div class="feature-card">
            <span class="fc-icon">📊</span>
            <div class="fc-value" style="color:{c};">{score_val}</div>
            <div class="fc-label">匹配度 · {rec}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="card card-accent" style="margin-top:16px;">
        <div class="card-header">📊 准备就绪</div>
        <p style="color:var(--text-2);margin:0;">
            已完成 <strong style="color:var(--primary-l);">{jd_title}</strong> 的简历分析，共生成 <strong style="color:var(--primary-l);">{len(questions)}</strong> 道面试题。
            系统将随机抽取 <strong style="color:var(--primary-l);">{st.session_state.n_rounds}</strong> 道进行深度面试。
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Preview questions
    with st.expander("👁 题库预览（将随机抽取 N 道）"):
        cols = st.columns(3)
        for i, q in enumerate(questions[:9]):
            with cols[i % 3]:
                st.markdown(render_question_card(q, i+1), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("🎬 开始面试", type="primary", use_container_width=True):
            from app.question_sampler import sample_questions_for_interview
            selected, remaining = sample_questions_for_interview(questions, st.session_state.n_rounds)
            st.session_state.selected_questions = selected
            st.session_state.remaining_pool = remaining
            st.session_state.interview_started = True
            st.rerun()

def _show_interview_active():
    from app.interviewer import InterviewerAgent, InterviewState

    # Not initialized yet - show start button
    if st.session_state.interviewer is None:
        with st.spinner("🤖 正在启动面试官..."):
            try:
                agent = InterviewerAgent(max_rounds=len(st.session_state.selected_questions) + 2)
                agent.load_parsed_data(st.session_state.jd_data, st.session_state.resume_data)
                agent.initialize_persona()
                agent.inject_questions(st.session_state.selected_questions, st.session_state.remaining_pool)
                greeting, first_q = agent.generate_opening()
                st.session_state.interviewer = agent
                st.session_state.chat_messages = [
                    {"role": "interviewer", "content": greeting},
                    {"role": "interviewer", "content": first_q},
                ]
                if st.session_state.tts_enabled:
                    speak_text(first_q)
                st.rerun()
            except Exception as e:
                st.error(f"初始化失败: {e}")
                st.stop()

    agent = st.session_state.interviewer

    # ── Status Bar ──
    dims_cov = ", ".join(agent.covered_dimensions) or "—"
    dims_pend = ", ".join(agent.pending_dimensions[:2]) or "—"
    progress_pct = int(len(agent.turns) / agent.max_rounds * 100) if agent.max_rounds > 0 else 0
    st.markdown(f"""
    <div class="status-bar">
        <div class="status-item"><span class="status-dot active"></span> 面试中</div>
        <div class="status-item">🎭 <strong>{agent.persona.get('persona_name', '面试官')}</strong></div>
        <div class="status-item">📌 {agent.jd_data.get('title', '岗位')}</div>
        <div class="status-item">🔄 第 {len(agent.turns)}/{agent.max_rounds} 轮</div>
        <div class="status-item">✅ {dims_cov}</div>
    </div>
    <div class="custom-progress" style="margin-bottom:16px;">
        <div class="fill" style="width:{progress_pct}%;background:linear-gradient(90deg,#4f46e5,#6366f1,#818cf8);border-radius:4px;transition:width 0.5s ease;"></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Layout ──
    col_chat, col_dh = st.columns([3, 1])

    with col_dh:
        if st.session_state.digital_human_enabled:
            persona = agent.persona.get("persona_name", "面试官")
            last = ""
            for m in reversed(st.session_state.chat_messages):
                if m["role"] == "interviewer":
                    last = m["content"]
                    break
            render_digital_human(last, persona)
        
        # Interview stats card
        st.markdown(f"""
        <div class="card" style="margin-top:12px;padding:12px;font-size:12px;">
            <div class="card-header" style="font-size:13px;">📋 面试信息</div>
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="color:var(--text-2);">人格</span>
                <span style="color:var(--primary-l);">{agent.persona.get('persona_type', 'balanced')}</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="color:var(--text-2);">已覆盖</span>
                <span style="color:var(--success);">{len(agent.covered_dimensions)}维</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="color:var(--text-2);">题库剩余</span>
                <span style="color:var(--warning);">{len(agent.remaining_pool)}题</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="color:var(--text-2);">待覆盖</span>
                <span style="color:var(--text-2);">{dims_pend}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_chat:
        # Chat messages with improved container
        chat_html = '<div class="chat-container" id="chat-scroll">'
        for i, msg in enumerate(st.session_state.chat_messages):
            role = msg["role"]
            if role == "interviewer":
                avatar_html = '<div class="avatar interviewer">🎭</div>'
                bubble_class = "interviewer"
                name = agent.persona.get("persona_name", "面试官")
            else:
                avatar_html = '<div class="avatar candidate">👤</div>'
                bubble_class = "candidate"
                name = "你（候选人）"
            # Truncate very long messages in display
            content = msg['content'][:500]
            chat_html += f"""
            <div class="chat-msg">
                {avatar_html}
                <div style="flex:1;min-width:0;">
                    <div style="font-size:11px;color:var(--text-3);margin-bottom:4px;">{name}</div>
                    <div class="bubble {bubble_class}">{content}</div>
                </div>
            </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
        
        # Auto-scroll script
        st.markdown("""
        <script>
            var el = document.getElementById("chat-scroll");
            if(el) el.scrollTop = el.scrollHeight;
        </script>
        """, unsafe_allow_html=True)

        # Input
        if agent.state not in (InterviewState.REPORTING, InterviewState.DONE) and not st.session_state.interview_done:
            with st.form("chat_form", clear_on_submit=True):
                col_in, col_btn = st.columns([5, 1])
                with col_in:
                    user_input = st.text_input("", placeholder="输入你的回答...", key="user_input_field",
                                               label_visibility="collapsed")
                with col_btn:
                    submitted = st.form_submit_button("发送 ➤", use_container_width=True)

            if submitted and user_input and user_input.strip():
                _handle_user_answer(user_input.strip())

            col_end1, col_end2, col_end3 = st.columns([1, 2, 1])
            with col_end2:
                if st.button("⏹ 结束面试", use_container_width=True):
                    closing = agent._generate_closing()
                    st.session_state.chat_messages.append({"role": "interviewer", "content": closing})
                    st.session_state.interview_done = True
                    agent.state = InterviewState.REPORTING
                    st.rerun()

        # Done state
        if agent.state in (InterviewState.REPORTING, InterviewState.DONE) or st.session_state.interview_done:
            st.markdown("""
            <div class="card card-accent" style="margin-top:16px;border-color:rgba(16,185,129,0.3);background:rgba(16,185,129,0.05);">
                <p style="margin:0;color:var(--success);text-align:center;font-weight:600;">✅ 面试已结束</p>
            </div>
            """, unsafe_allow_html=True)
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button("📊 查看评估报告", type="primary", use_container_width=True):
                    _generate_report()

def _handle_user_answer(user_input):
    agent = st.session_state.interviewer
    from app.interviewer import InterviewState

    st.session_state.chat_messages.append({"role": "candidate", "content": user_input})

    with st.spinner("🤔 面试官思考中..."):
        result = agent.process_answer(user_input)

    if result.get("interview_ongoing"):
        next_msg = result.get("message", "")
        st.session_state.chat_messages.append({"role": "interviewer", "content": next_msg})

        if st.session_state.tts_enabled and next_msg:
            speak_text(next_msg)
    else:
        st.session_state.chat_messages.append({"role": "interviewer", "content": result.get("message", "")})
        st.session_state.interview_done = True
        agent.state = InterviewState.REPORTING

    st.rerun()

def _generate_report():
    agent = st.session_state.interviewer
    from app.reporter import generate_report
    try:
        report = generate_report(agent.get_interview_data())
        st.session_state.report_data = report
        st.session_state.interview_done = True
        st.session_state.active_tab = "📊 评估报告"
        if "_nav_radio" in st.session_state:
            del st.session_state["_nav_radio"]
    except Exception as e:
        st.error(f"报告生成失败: {e}")
    st.rerun()

# ── Tab 3: Assessment Report ────────────────────────
def tab_report():
    st.markdown("""
    <div class="app-header">
        <h1><img src="data:image/png;base64,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" style="width:36px;height:auto;vertical-align:middle;margin-right:10px;" alt="logo">面试评估报告</h1>
        <p>五维雷达 · 逐题评审 · 录用建议</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.interview_done:
        st.markdown("""
        <div class="empty-illustration">
            <div class="ei-icon">📊</div>
            <div class="ei-title">暂无评估报告</div>
            <div class="ei-desc">请先完成「AI 面试」后系统将自动生成多维度评估报告</div>
        </div>
        """, unsafe_allow_html=True)
        return

    report = st.session_state.report_data
    if not report:
        agent = st.session_state.interviewer
        if agent and len(agent.turns) > 0:
            with st.spinner("正在生成报告..."):
                from app.reporter import generate_report
                report = generate_report(agent.get_interview_data())
                st.session_state.report_data = report
        else:
            st.warning("暂无面试数据")
            return

    if not report:
        return

    score = report.get("overall_score", report.get("calculated_score", 0))
    rec = report.get("recommendation", "")
    rec_map = {"strong_hire":"强烈推荐 🔥","hire":"推荐录用 ✅","hold":"待定 ⏸","no_hire":"不推荐 ❌"}
    rec_text = rec_map.get(rec, rec)

    # ── Stats ──
    turns_count = len(st.session_state.interviewer.turns) if st.session_state.interviewer else 0
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-item">
            <div class="stat-value" style="color:{score_color(score)}">{score}<span style="font-size:16px">/100</span></div>
            <div class="stat-label">综合评分</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{turns_count}</div>
            <div class="stat-label">面试轮数</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" style="color:{score_color(score)}">{rec_text}</div>
            <div class="stat-label">录用建议</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Score Ring + Summary ──
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(render_score_ring(score), unsafe_allow_html=True)
    with col2:
        summary_text = report.get('summary', report.get('overall_comment', '暂无综合评价'))
        st.markdown(f"""
        <div class="card">
            <div class="card-header">📝 综合评价</div>
            <p style="color:var(--text);line-height:1.8;font-size:14px;">{summary_text}</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Radar Chart ──
    dim_scores = report.get("dimension_scores", {})
    if dim_scores:
        st.markdown('<div class="section-title">📈 五维能力雷达</div>', unsafe_allow_html=True)
        
        # Dimension stats above radar
        dim_cols = st.columns(len(dim_scores))
        labels = {"job_match":"岗位匹配","technical_ability":"技术能力","communication":"沟通表达",
                  "comprehensive_quality":"综合素质","integrity":"诚信度"}
        
        for i, (k, v) in enumerate(dim_scores.items()):
            dim_score = v.get("score", 0) if isinstance(v, dict) else v
            with dim_cols[i]:
                st.markdown(f"""
                <div class="feature-card" style="padding:12px 8px;">
                    <span class="fc-icon" style="font-size:20px;">{['📊','💻','💬','🌟','🛡'][i]}</span>
                    <div class="fc-value" style="font-size:20px;color:{score_color(dim_score)};">{dim_score}</div>
                    <div class="fc-label">{labels.get(k, k)}</div>
                </div>
                """, unsafe_allow_html=True)

        import plotly.graph_objects as go
        cats, vals = [], []
        for k, v in dim_scores.items():
            cats.append(labels.get(k, k))
            vals.append(v.get("score", 0) if isinstance(v, dict) else v)

        fig = go.Figure(data=go.Scatterpolar(
            r=vals + [vals[0]], theta=cats + [cats[0]],
            fill='toself', fillcolor='rgba(99,102,241,0.2)',
            line=dict(color='#6366f1', width=3),
            marker=dict(color='#818cf8', size=10),
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(range=[0,100], gridcolor='#2d3245', tickfont=dict(color='#9aa0b0', size=11)),
                angularaxis=dict(gridcolor='#2d3245', tickfont=dict(color='#e8eaed', size=13)),
                bgcolor='rgba(0,0,0,0)',
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=440,
            margin=dict(l=60, r=60, t=20, b=20),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Question Review ──
    q_review = report.get("question_review", [])
    if not q_review and st.session_state.interviewer:
        # Build from turns if report doesn't have it
        q_review = []
        for t in st.session_state.interviewer.turns:
            ev = t.get("evaluation", {})
            q_review.append({
                "round": t.get("round", "?"),
                "question": t.get("question", ""),
                "answer_summary": (t.get("answer", "") or "")[:100],
                "score": ev.get("score", "?"),
                "evaluation": ev.get("answer_quality", ""),
            })

    if q_review:
        st.markdown('<div class="section-title">📋 逐题评审</div>', unsafe_allow_html=True)
        for r in q_review:
            sc = r.get("score", 0)
            if isinstance(sc, (int, float)) and sc > 0:
                c = score_color(int(sc))
                sc_display = f"{int(sc)}分"
                badge_bg = f"background:linear-gradient(135deg,{c}22,{c}11);color:{c};border:1px solid {c}44;"
            else:
                c = "var(--text-3)"
                sc_display = str(sc)
                badge_bg = "background:var(--surface-2);color:var(--text-2);"
            
            question_text = r.get('question', '')[:80]
            with st.expander(f"第{r.get('round','?')}轮 · {question_text}..."):
                st.markdown(f"""
                <div class="card" style="margin:0;">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                        <div style="flex:1;min-width:0;">
                            <div style="font-size:13px;color:var(--text-2);margin-bottom:4px;">📌 问题</div>
                            <div style="font-size:14px;color:var(--text);line-height:1.6;">{r.get('question','')}</div>
                        </div>
                        <span class="score-badge" style="{badge_bg}margin-left:12px;flex-shrink:0;">{sc_display}</span>
                    </div>
                    <div style="font-size:13px;color:var(--text-2);margin-bottom:4px;">💬 回答摘要</div>
                    <div style="font-size:13px;color:var(--text);line-height:1.6;margin-bottom:10px;">{r.get('answer_summary','')}</div>
                    <div style="font-size:13px;">
                        <span style="color:var(--text-2);">📝 评价：</span>
                        <span style="color:var(--text);">{r.get('evaluation','')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Highlights / Concerns ──
    col_h, col_c = st.columns(2)
    with col_h:
        highlights = report.get("highlights", [])
        if highlights:
            st.markdown("### 🌟 亮点")
            for h in highlights:
                st.markdown(f"""
                <div style="padding:10px 12px;margin:6px 0;background:rgba(16,185,129,0.08);border-left:3px solid var(--success);border-radius:0 8px 8px 0;font-size:13px;color:var(--text);">
                    {h}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card" style="text-align:center;padding:20px;">
                <div style="font-size:14px;color:var(--text-2);">暂无明显亮点</div>
            </div>
            """, unsafe_allow_html=True)

    with col_c:
        concerns = report.get("concerns", [])
        if concerns:
            st.markdown("### ⚠️ 关注点")
            for c_item in concerns:
                st.markdown(f"""
                <div style="padding:10px 12px;margin:6px 0;background:rgba(245,158,11,0.08);border-left:3px solid var(--warning);border-radius:0 8px 8px 0;font-size:13px;color:var(--text);">
                    {c_item}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card" style="text-align:center;padding:20px;">
                <div style="font-size:14px;color:var(--text-2);">暂无明显关注点</div>
            </div>
            """, unsafe_allow_html=True)

    if report.get("contradictions"):
        st.markdown("### 🔴 矛盾标注")
        for c_item in report["contradictions"]:
            st.markdown(f"""
            <div style="padding:10px 14px;margin:6px 0;background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);border-radius:8px;font-size:13px;color:var(--text);">
                🔴 {c_item}
            </div>
            """, unsafe_allow_html=True)

# ── Main ─────────────────────────────────────────────

# ── Candidate Interview Routing ──
query_params = st.query_params
if query_params.get("role") == "candidate" and query_params.get("token"):
    token = query_params["token"]
    st.session_state["candidate_token"] = token
    page_candidate()
    st.stop()

render_sidebar()

# 自动播放 pending_audio（由 speak_text 生成）
audio_b64 = st.session_state.get("pending_audio_b64", "")
if audio_b64:
    st.markdown(f"""
    <audio autoplay style="display:none;">
        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
    </audio>
    """, unsafe_allow_html=True)
    st.session_state["pending_audio_b64"] = ""

st.markdown("""
<div style="text-align:center;padding:4px 0 12px;">
    <span style="font-size:13px;color:var(--text-3);">
        AI 招聘系统 · 简历分析 → AI面试 → 评估报告
    </span>
</div>
""", unsafe_allow_html=True)

tab_labels = ["📄 简历分析", "🤖 AI 面试", "📊 评估报告"]
active = st.radio("导航", tab_labels,
    index=tab_labels.index(st.session_state.get("active_tab", "📄 简历分析")),
    key="_nav_radio", horizontal=True, label_visibility="collapsed")
st.session_state.active_tab = active

if active == "📄 简历分析":
    tab_resume_analysis()
elif active == "🤖 AI 面试":
    tab_ai_interview()
elif active == "📊 评估报告":
    tab_report()
