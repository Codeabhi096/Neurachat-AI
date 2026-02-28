import streamlit as st
from openai import OpenAI, APITimeoutError, APIConnectionError, RateLimitError
from dotenv import load_dotenv
import datetime, re, io, os, time

try:
    from fpdf import FPDF
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    from docx import Document as DocxDocument
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NeuraChat AI v8.0",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
#  API CLIENT
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    key = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", ""))
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=key,
        timeout=60.0,
    )

# ─────────────────────────────────────────────────────────────────────────────
#  MODELS  —  All Free, Smart Fallback Order
# ─────────────────────────────────────────────────────────────────────────────
FREE_MODELS = [
    ("🌟 Gemini 2.0 Flash",         "google/gemini-2.0-flash-exp:free"),
    ("🧠 DeepSeek V3",              "deepseek/deepseek-chat-v3-0324:free"),
    ("🦙 LLaMA 4 Maverick",         "meta-llama/llama-4-maverick:free"),
    ("🔮 Mistral Small 3.1",        "mistralai/mistral-small-3.1-24b-instruct:free"),
    ("⚡ Gemini 2.0 Flash Lite",    "google/gemini-2.0-flash-lite-001"),
    ("🤖 Auto (Smart Route)",       "openrouter/auto"),
]

FREE_MODEL_NAMES  = [m[0] for m in FREE_MODELS]
FREE_MODEL_IDS    = {m[0]: m[1] for m in FREE_MODELS}

# ─────────────────────────────────────────────────────────────────────────────
#  THEMES
# ─────────────────────────────────────────────────────────────────────────────
THEMES = {
    "🌑 Midnight Glass": {
        "bg_deep":      "#050709",
        "bg_mid":       "#080b12",
        "bg_card":      "rgba(14, 18, 30, 0.80)",
        "accent":       "#6d71f0",
        "accent_hi":    "#9b9ff7",
        "accent_lo":    "#4a4ec8",
        "accent_soft":  "rgba(109, 113, 240, 0.12)",
        "accent_glow":  "rgba(109, 113, 240, 0.22)",
        "t1":           "#f0f2ff",
        "t2":           "#8892b0",
        "t3":           "#3d4466",
        "t4":           "#1e2240",
        "brd":          "rgba(109, 113, 240, 0.14)",
        "brd2":         "rgba(109, 113, 240, 0.28)",
        "brd3":         "rgba(255, 255, 255, 0.06)",
        "user_bubble":  "linear-gradient(135deg, #3d4bda, #5865f2, #6d71f0)",
        "ai_bubble":    "rgba(14, 18, 30, 0.85)",
        "sidebar_bg":   "rgba(6, 8, 16, 0.97)",
        "topbar_bg":    "rgba(5, 7, 9, 0.85)",
        "input_bg":     "rgba(14, 18, 32, 0.70)",
        "noise_opacity":"0.4",
        "grain":        "radial-gradient(ellipse 90% 70% at 15% 5%, rgba(109,113,240,0.08) 0%, transparent 60%), radial-gradient(ellipse 70% 80% at 85% 95%, rgba(99,102,241,0.06) 0%, transparent 55%)",
    },
    "⚡ Cyberpunk": {
        "bg_deep":      "#040408",
        "bg_mid":       "#060610",
        "bg_card":      "rgba(8, 8, 20, 0.88)",
        "accent":       "#00ff9f",
        "accent_hi":    "#ff2d78",
        "accent_lo":    "#00cc80",
        "accent_soft":  "rgba(0, 255, 159, 0.10)",
        "accent_glow":  "rgba(0, 255, 159, 0.20)",
        "t1":           "#e8fff5",
        "t2":           "#6affcb",
        "t3":           "#1a4433",
        "t4":           "#0a1a14",
        "brd":          "rgba(0, 255, 159, 0.18)",
        "brd2":         "rgba(0, 255, 159, 0.35)",
        "brd3":         "rgba(0, 255, 159, 0.08)",
        "user_bubble":  "linear-gradient(135deg, #ff2d78, #ff6baa)",
        "ai_bubble":    "rgba(8, 16, 12, 0.90)",
        "sidebar_bg":   "rgba(4, 4, 10, 0.98)",
        "topbar_bg":    "rgba(4, 4, 8, 0.90)",
        "input_bg":     "rgba(8, 10, 18, 0.80)",
        "noise_opacity":"0.3",
        "grain":        "radial-gradient(ellipse 80% 60% at 10% 10%, rgba(0,255,159,0.06) 0%, transparent 60%), radial-gradient(ellipse 60% 70% at 90% 90%, rgba(255,45,120,0.06) 0%, transparent 55%)",
    },
    "☀️ Nordic Light": {
        "bg_deep":      "#f5f6fa",
        "bg_mid":       "#eef0f6",
        "bg_card":      "rgba(255, 255, 255, 0.90)",
        "accent":       "#4f6ef7",
        "accent_hi":    "#2d4fc5",
        "accent_lo":    "#7b93fb",
        "accent_soft":  "rgba(79, 110, 247, 0.10)",
        "accent_glow":  "rgba(79, 110, 247, 0.18)",
        "t1":           "#1a1d2e",
        "t2":           "#4a5068",
        "t3":           "#9aa0b8",
        "t4":           "#dde0ec",
        "brd":          "rgba(79, 110, 247, 0.16)",
        "brd2":         "rgba(79, 110, 247, 0.32)",
        "brd3":         "rgba(0, 0, 0, 0.08)",
        "user_bubble":  "linear-gradient(135deg, #4f6ef7, #6b84fa)",
        "ai_bubble":    "rgba(255, 255, 255, 0.95)",
        "sidebar_bg":   "rgba(238, 240, 248, 0.98)",
        "topbar_bg":    "rgba(245, 246, 250, 0.92)",
        "input_bg":     "rgba(255, 255, 255, 0.85)",
        "noise_opacity":"0.12",
        "grain":        "radial-gradient(ellipse 80% 60% at 20% 20%, rgba(79,110,247,0.05) 0%, transparent 60%), radial-gradient(ellipse 60% 70% at 80% 80%, rgba(79,110,247,0.04) 0%, transparent 55%)",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
#  TOPIC DETECTION
# ─────────────────────────────────────────────────────────────────────────────
REF_TEMPLATES = {
    "code":    ["Stack Overflow", "GitHub Repos", "Official Docs", "MDN Web Docs"],
    "math":    ["Wolfram Alpha", "ArXiv Papers", "Khan Academy", "MathWorld"],
    "science": ["PubMed", "Nature Journals", "Scientific American", "arXiv"],
    "writing": ["Literary Corpus", "Style Guides", "Grammarly Insights"],
    "general": ["Wikipedia", "Web Corpus 2024", "Academic Sources"],
    "analysis":["Research Papers", "Statistical DBs", "Industry Reports"],
    "history": ["Britannica", "Historical Archives", "Academic Journals"],
}

def detect_topic(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["code","python","javascript","function","bug","api","sql","html","css","def ","const ","git","react","node","docker"]): return "code"
    if any(w in t for w in ["math","equation","calculus","algebra","integral","formula","statistics","matrix","derivative"]): return "math"
    if any(w in t for w in ["science","physics","chemistry","biology","quantum","genetics","molecule"]): return "science"
    if any(w in t for w in ["write","essay","story","poem","email","letter","blog","creative","fiction"]): return "writing"
    if any(w in t for w in ["analyze","compare","evaluate","research","investigate","assess"]): return "analysis"
    if any(w in t for w in ["history","historical","war","ancient","civilization","revolution"]): return "history"
    return "general"

def get_refs(prompt: str) -> list:
    return REF_TEMPLATES.get(detect_topic(prompt), REF_TEMPLATES["general"])[:3]

# ─────────────────────────────────────────────────────────────────────────────
#  RESPONSE STYLES
# ─────────────────────────────────────────────────────────────────────────────
RESPONSE_STYLES = {
    "Balanced":  "Clear, well-structured, professional. Use markdown formatting with headers.",
    "Concise":   "Brief and direct. Key points only. Bullet points preferred. No fluff.",
    "Detailed":  "Comprehensive with examples, edge cases, and full explanations.",
    "Technical": "Precise and technical. Always include code, formulas, and implementation details.",
    "Creative":  "Vivid, imaginative, and surprising. Push beyond conventional answers.",
    "Friendly":  "Warm and conversational. Explain like talking to a smart friend.",
}

def build_system_prompt(style: str, tone: str) -> str:
    return f"""You are NeuraChat — a premium, production-grade AI assistant built for developers, researchers, and power users.

RESPONSE STYLE: {RESPONSE_STYLES.get(style, RESPONSE_STYLES['Balanced'])}
TONE: {tone}

FORMATTING RULES (follow strictly):
- Use proper markdown: ## H2, ### H3, **bold**, *italic*, `inline code`
- Code blocks: always use ```language with proper syntax highlighting
- Math (LaTeX): wrap in $...$ inline or $$...$$ for blocks
- Tables: use proper markdown table syntax
- Start responses DIRECTLY — no preambles like "Great question!"
- Be genuinely accurate, helpful, and concise

You can handle: coding, debugging, math, science, writing, research, analysis, creative work, data, architecture, and any topic."""

# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
_defaults = {
    "messages":       [],
    "model_key":      FREE_MODEL_NAMES[0],
    "style":          "Balanced",
    "tone":           "Professional",
    "temperature":    0.7,
    "max_tokens":     2048,
    "show_refs":      True,
    "show_tokens":    True,
    "show_timing":    True,
    "theme":          "🌑 Midnight Glass",
    "session_start":  datetime.datetime.now().strftime("%H:%M"),
    "total_chars":    0,
    "_busy":          False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
#  DYNAMIC CSS  —  Theme-Aware
# ─────────────────────────────────────────────────────────────────────────────
def build_css(th: dict) -> str:
    return f"""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500;12..96,600;12..96,700;12..96,800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {{
  --bg-deep:     {th["bg_deep"]};
  --bg-mid:      {th["bg_mid"]};
  --bg-card:     {th["bg_card"]};
  --accent:      {th["accent"]};
  --accent-hi:   {th["accent_hi"]};
  --accent-lo:   {th["accent_lo"]};
  --accent-soft: {th["accent_soft"]};
  --accent-glow: {th["accent_glow"]};
  --t1:          {th["t1"]};
  --t2:          {th["t2"]};
  --t3:          {th["t3"]};
  --t4:          {th["t4"]};
  --brd:         {th["brd"]};
  --brd2:        {th["brd2"]};
  --brd3:        {th["brd3"]};
  --user-bubble: {th["user_bubble"]};
  --ai-bubble:   {th["ai_bubble"]};
  --sidebar-bg:  {th["sidebar_bg"]};
  --topbar-bg:   {th["topbar_bg"]};
  --input-bg:    {th["input_bg"]};
  --fd: 'Bricolage Grotesque', system-ui, sans-serif;
  --fb: 'DM Sans', system-ui, sans-serif;
  --mono: 'JetBrains Mono', monospace;
  --r: 16px; --rs: 10px;
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, .stApp {{
  background: var(--bg-deep) !important;
  font-family: var(--fb) !important;
  color: var(--t1) !important;
  overflow-x: hidden;
}}

.stApp::before {{
  content: '';
  position: fixed; inset: 0;
  background: {th["grain"]};
  pointer-events: none; z-index: 0;
}}

#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"] {{ display: none !important; }}
.block-container {{ padding: 0 !important; max-width: 100% !important; }}

::-webkit-scrollbar {{ width: 3px; height: 3px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--accent)66; border-radius: 99px; }}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {{
  background: var(--sidebar-bg) !important;
  border-right: 1px solid var(--brd) !important;
  backdrop-filter: blur(24px) !important;
  min-width: 272px !important; max-width: 292px !important;
  position: relative; z-index: 100;
}}
[data-testid="stSidebar"] > div:first-child {{
  padding: 1.2rem 1.05rem 2rem !important;
  height: 100vh; overflow-y: auto; overflow-x: hidden;
}}

.brand {{ display: flex; align-items: center; gap: 10px; padding-bottom: 1rem; margin-bottom: 1.2rem; border-bottom: 1px solid var(--brd3); }}
.b-gem {{
  width: 38px; height: 38px; flex-shrink: 0;
  background: linear-gradient(135deg, var(--accent-lo), var(--accent), var(--accent-hi));
  border-radius: 12px; display: grid; place-items: center; font-size: 16px;
  box-shadow: 0 0 22px var(--accent-glow); animation: gem-pulse 4s ease-in-out infinite;
}}
@keyframes gem-pulse {{ 0%,100%{{ box-shadow: 0 0 18px var(--accent-glow); }} 50%{{ box-shadow: 0 0 42px var(--accent-glow); transform: scale(1.06); }} }}
.b-name {{ font-family: var(--fd); font-size: 1rem; font-weight: 800; color: var(--t1); }}
.b-badge {{ display: inline-flex; align-items: center; gap: 3px; background: var(--accent-soft); border: 1px solid var(--brd2); border-radius: 99px; padding: 2px 7px; font-size: 0.54rem; font-weight: 700; color: var(--accent-hi); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 3px; }}

.slbl {{ font-size: 0.57rem; font-weight: 700; color: var(--t3); text-transform: uppercase; letter-spacing: 0.13em; margin: 13px 0 5px; display: flex; align-items: center; gap: 4px; }}

.status {{ display: inline-flex; align-items: center; gap: 7px; background: var(--bg-card); border: 1px solid var(--brd3); border-radius: 99px; padding: 5px 11px; margin-bottom: 3px; }}
.dot {{ width: 6px; height: 6px; border-radius: 50%; }}
.don {{ background: #10b981; box-shadow: 0 0 7px #10b98199; animation: blink 2.5s infinite; }}
.dbz {{ background: #f59e0b; box-shadow: 0 0 7px #f59e0b99; animation: blink 0.7s infinite; }}
@keyframes blink {{ 0%,100%{{ opacity:1; }} 50%{{ opacity:0.15; }} }}
.stxt {{ font-size: 0.71rem; font-weight: 600; color: var(--t2); }}

.sg {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; margin-top: 4px; }}
.sc {{ background: var(--bg-card); border: 1px solid var(--brd3); border-radius: var(--rs); padding: 8px 5px; text-align: center; transition: all 0.2s; cursor: default; }}
.sc:hover {{ border-color: var(--accent); transform: translateY(-2px); box-shadow: 0 6px 18px var(--accent-glow); }}
.sn {{ font-family: var(--fd); font-size: 1.3rem; font-weight: 800; line-height: 1; background: linear-gradient(135deg, var(--accent), var(--accent-hi)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
.sl {{ font-size: 0.54rem; color: var(--t3); margin-top: 2px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; }}

.tags {{ display: flex; flex-wrap: wrap; gap: 4px; margin-top: 5px; }}
.tag {{ background: var(--accent-soft); border: 1px solid var(--brd); color: var(--accent-hi); border-radius: 99px; padding: 3px 8px; font-size: 0.61rem; font-weight: 600; transition: all 0.18s; cursor: default; }}
.tag:hover {{ background: var(--accent-glow); border-color: var(--accent); transform: translateY(-2px); }}

.mchip {{ background: var(--bg-card); border: 1px solid var(--brd); border-radius: var(--rs); padding: 6px 10px; font-family: var(--mono); font-size: 0.64rem; color: var(--accent-hi); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-top: 4px; }}

.free-badge {{ display: inline-block; padding: 1px 7px; border-radius: 99px; font-size: 0.59rem; font-weight: 700; letter-spacing: 0.06em; float: right; background: rgba(16,185,129,0.12); color: #10b981; border: 1px solid rgba(16,185,129,0.25); }}

[data-testid="stSidebar"] .stSelectbox > div > div {{
  background: var(--bg-card) !important; border: 1px solid var(--brd) !important;
  border-radius: var(--rs) !important; color: var(--t1) !important;
  font-size: 0.8rem !important; font-family: var(--fb) !important;
}}
[data-testid="stSidebar"] .stSelectbox > div > div:hover {{ border-color: var(--accent) !important; }}
[data-testid="stSidebar"] .stSelectbox li {{ background: var(--bg-mid) !important; color: var(--t1) !important; }}
[data-testid="stSidebar"] .stSelectbox label {{ color: var(--t2) !important; font-size: 0.73rem !important; font-weight: 600 !important; }}
[data-testid="stSidebar"] .stSlider [data-baseweb="thumb"] {{ background: var(--accent) !important; border: 2px solid var(--bg-deep) !important; box-shadow: 0 0 12px var(--accent-glow) !important; }}
[data-testid="stSidebar"] .stSlider [data-baseweb="track-fill"] {{ background: linear-gradient(90deg, var(--accent-lo), var(--accent)) !important; }}
[data-testid="stSidebar"] .stSlider label {{ color: var(--t2) !important; font-size: 0.72rem !important; }}
[data-testid="stSidebar"] .stToggle label {{ color: var(--t2) !important; font-size: 0.76rem !important; }}

.stButton > button {{
  background: var(--accent-soft) !important; border: 1px solid var(--brd2) !important;
  color: var(--accent-hi) !important; border-radius: var(--rs) !important;
  font-family: var(--fb) !important; font-size: 0.78rem !important; font-weight: 600 !important;
  width: 100% !important; padding: 0.48rem 0.8rem !important; transition: all 0.2s !important;
}}
.stButton > button:hover {{
  background: var(--accent-glow) !important; border-color: var(--accent) !important;
  box-shadow: 0 4px 18px var(--accent-glow) !important; transform: translateY(-2px) !important; color: var(--t1) !important;
}}
[data-testid="stDownloadButton"] > button {{
  background: var(--accent-soft) !important; border: 1px solid var(--brd2) !important;
  color: var(--accent-hi) !important; border-radius: var(--rs) !important;
  font-family: var(--fb) !important; font-size: 0.73rem !important; font-weight: 600 !important;
  width: 100% !important; padding: 0.44rem 0.75rem !important; transition: all 0.2s !important;
}}
[data-testid="stDownloadButton"] > button:hover {{
  background: var(--accent-glow) !important; border-color: var(--accent) !important; transform: translateY(-2px) !important;
}}

.sb-footer {{ font-size: 0.59rem; color: var(--t3); text-align: center; line-height: 1.85; margin-top: 13px; padding-top: 11px; border-top: 1px solid var(--brd3); }}

/* ── TOP BAR ── */
.topbar {{
  background: var(--topbar-bg);
  backdrop-filter: blur(32px) saturate(180%);
  border-bottom: 1px solid var(--brd3);
  padding: 0.6rem 1.6rem;
  display: flex; align-items: center; justify-content: space-between;
  position: sticky; top: 0; z-index: 998;
}}
.tbl {{ display: flex; align-items: center; gap: 9px; }}
.tbico {{ width: 28px; height: 28px; flex-shrink: 0; background: linear-gradient(135deg, var(--accent-lo), var(--accent)); border-radius: 8px; display: grid; place-items: center; font-size: 12px; box-shadow: 0 2px 10px var(--accent-glow); }}
.tbtitle {{ font-family: var(--fd); font-size: 0.93rem; font-weight: 800; color: var(--t1); letter-spacing: -0.02em; }}
.tbr {{ display: flex; align-items: center; gap: 5px; flex-shrink: 0; }}
.pill {{ border-radius: 99px; padding: 4px 10px; font-size: 0.63rem; font-weight: 600; display: flex; align-items: center; gap: 4px; border: 1px solid var(--brd3); white-space: nowrap; transition: all 0.2s; }}
.pill:hover {{ border-color: var(--accent); box-shadow: 0 2px 10px var(--accent-glow); }}
.pm {{ background: var(--accent-soft); color: var(--accent-hi); font-family: var(--mono); font-size: 0.58rem; }}
.pt {{ background: var(--bg-card); color: var(--t2); }}
.ps {{ background: rgba(16,185,129,0.10); border-color: rgba(16,185,129,0.28) !important; color: #10b981; }}
.pdot {{ width: 5px; height: 5px; border-radius: 50%; background: currentColor; animation: blink 2s infinite; }}

/* ── WELCOME ── */
.welcome {{ display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 60vh; padding: 3rem 1.25rem 2rem; text-align: center; position: relative; z-index: 1; }}
.w-orb {{
  width: 88px; height: 88px;
  background: linear-gradient(135deg, var(--accent-lo), var(--accent), var(--accent-hi));
  border-radius: 27px; display: grid; place-items: center; font-size: 34px;
  margin-bottom: 1.6rem;
  box-shadow: 0 0 0 1px var(--brd2), 0 8px 48px var(--accent-glow), inset 0 1px 0 rgba(255,255,255,0.18);
  animation: orb-float 5s ease-in-out infinite; position: relative;
}}
@keyframes orb-float {{ 0%,100%{{ transform: translateY(0) scale(1); }} 50%{{ transform: translateY(-11px) scale(1.03); }} }}
.w-h {{ font-family: var(--fd); font-size: clamp(1.7rem, 4.5vw, 2.5rem); font-weight: 800; line-height: 1.12; color: var(--t1); margin-bottom: 0.7rem; animation: fade-up 0.55s ease forwards; letter-spacing: -0.025em; }}
.w-h span {{ background: linear-gradient(120deg, var(--accent-lo), var(--accent), var(--accent-hi)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
.w-sub {{ font-size: clamp(0.83rem, 2vw, 0.93rem); color: var(--t2); max-width: 390px; line-height: 1.72; margin-bottom: 2.1rem; animation: fade-up 0.7s 0.1s ease both; }}
@keyframes fade-up {{ from{{ opacity:0; transform:translateY(13px); }} to{{ opacity:1; transform:translateY(0); }} }}
.w-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; width: 100%; max-width: 570px; animation: fade-up 0.85s 0.2s ease both; }}
.w-card {{ background: var(--bg-card); border: 1px solid var(--brd3); border-radius: var(--r); padding: 12px 10px; text-align: left; transition: all 0.22s cubic-bezier(0.25, 0.46, 0.45, 0.94); position: relative; overflow: hidden; }}
.w-card::before {{ content: ''; position: absolute; inset: 0; background: linear-gradient(135deg, var(--accent-glow) 0%, transparent 100%); opacity: 0; transition: opacity 0.22s; }}
.w-card:hover {{ border-color: var(--accent); transform: translateY(-4px); box-shadow: 0 12px 34px var(--accent-glow); }}
.w-card:hover::before {{ opacity: 1; }}
.wci {{ font-size: 1.25rem; margin-bottom: 5px; }}
.wct {{ font-size: 0.73rem; font-weight: 700; color: var(--t1); margin-bottom: 3px; }}
.wcs {{ font-size: 0.65rem; color: var(--t2); line-height: 1.45; }}

/* ── CHAT MESSAGES ── */
.main-wrap {{ max-width: 870px; margin: 0 auto; padding: 1.1rem clamp(0.7rem, 3.5vw, 2rem) 0.5rem; position: relative; z-index: 1; }}

[data-testid="chatAvatarIcon-user"],
[data-testid="chatAvatarIcon-assistant"] {{ display: none !important; }}
[data-testid="stChatMessage"] {{ background: transparent !important; border: none !important; padding: 0.2rem 0 !important; }}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{ justify-content: flex-end !important; }}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stChatMessageContent {{
  background: var(--user-bubble) !important;
  border-radius: 22px 22px 4px 22px !important;
  color: #ffffff !important; max-width: 70% !important; margin-left: auto !important;
  padding: 10px 15px !important; font-size: 0.89rem !important; line-height: 1.63 !important;
  box-shadow: 0 4px 22px var(--accent-glow), inset 0 1px 0 rgba(255,255,255,0.15) !important;
  border: none !important; animation: msg-right 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
}}
@keyframes msg-right {{ from{{ opacity:0; transform:translateX(15px) scale(0.96); }} to{{ opacity:1; transform:none; }} }}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stChatMessageContent {{
  background: var(--ai-bubble) !important;
  border: 1px solid var(--brd3) !important;
  border-radius: 4px 22px 22px 22px !important;
  color: var(--t1) !important; max-width: 82% !important;
  padding: 12px 16px !important; font-size: 0.89rem !important; line-height: 1.76 !important;
  box-shadow: 0 2px 18px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.03) !important;
  backdrop-filter: blur(12px) !important; animation: msg-left 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
}}
@keyframes msg-left {{ from{{ opacity:0; transform:translateX(-15px) scale(0.96); }} to{{ opacity:1; transform:none; }} }}

[data-testid="stChatMessage"] h1,[data-testid="stChatMessage"] h2,[data-testid="stChatMessage"] h3 {{ font-family: var(--fd) !important; color: var(--accent-hi) !important; margin: 13px 0 5px !important; font-weight: 700 !important; }}
[data-testid="stChatMessage"] h1 {{ font-size: 1.2em !important; border-bottom: 1px solid var(--brd3); padding-bottom: 5px !important; }}
[data-testid="stChatMessage"] h2 {{ font-size: 1.07em !important; }}
[data-testid="stChatMessage"] h3 {{ font-size: 0.96em !important; }}
[data-testid="stChatMessage"] p {{ margin-bottom: 5px !important; }}
[data-testid="stChatMessage"] ul,[data-testid="stChatMessage"] ol {{ padding-left: 17px !important; margin: 6px 0 !important; }}
[data-testid="stChatMessage"] li {{ margin-bottom: 3px !important; color: var(--t2) !important; }}
.stChatMessage strong {{ color: var(--t1) !important; font-weight: 700 !important; }}
.stChatMessage em {{ color: var(--accent-hi) !important; }}
.stChatMessage a {{ color: var(--accent-hi) !important; text-decoration: underline !important; }}

/* ── Code blocks ── */
.stChatMessage code {{
  background: var(--accent-soft) !important; border: 1px solid var(--brd) !important;
  border-radius: 5px !important; padding: 2px 6px !important;
  font-size: 0.82em !important; color: var(--accent-hi) !important;
  font-family: var(--mono) !important; font-weight: 500 !important;
}}
.stChatMessage pre {{
  background: rgba(5, 7, 14, 0.9) !important; border: 1px solid var(--brd) !important;
  border-left: 3px solid var(--accent) !important; border-radius: 12px !important;
  padding: 14px !important; overflow-x: auto !important; margin: 10px 0 !important;
  position: relative;
}}
.stChatMessage pre code {{
  background: transparent !important; border: none !important; padding: 0 !important;
  color: var(--t1) !important; font-size: 0.83em !important;
}}

/* ── Tables ── */
.stChatMessage table {{ border-collapse: collapse !important; width: 100% !important; margin: 11px 0 !important; border-radius: var(--rs) !important; overflow: hidden !important; }}
.stChatMessage th {{ background: var(--accent-soft) !important; color: var(--accent-hi) !important; padding: 8px 12px !important; font-size: 0.72rem !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 0.06em !important; text-align: left !important; border-bottom: 1px solid var(--brd) !important; }}
.stChatMessage td {{ padding: 7px 12px !important; border-bottom: 1px solid var(--brd3) !important; color: var(--t2) !important; font-size: 0.85rem !important; }}
.stChatMessage tr:hover td {{ background: var(--accent-soft) !important; color: var(--t1) !important; }}
.stChatMessage blockquote {{ border-left: 3px solid var(--accent) !important; margin: 9px 0 !important; padding: 8px 13px !important; background: var(--accent-soft) !important; border-radius: 0 10px 10px 0 !important; color: var(--t2) !important; font-style: italic !important; }}

/* ── Meta strip below AI message ── */
.msg-meta {{ display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-top: 7px; }}
.meta-chip {{ display: inline-flex; align-items: center; gap: 4px; background: var(--bg-card); border: 1px solid var(--brd3); border-radius: 99px; padding: 3px 9px; font-size: 0.6rem; font-weight: 600; color: var(--t3); white-space: nowrap; }}
.meta-chip span {{ color: var(--t2); }}

/* ── Source reference ── */
.ref-card {{ display: flex; flex-wrap: wrap; align-items: center; gap: 5px; margin-top: 7px; padding: 7px 11px; background: var(--accent-soft); border: 1px solid var(--brd3); border-radius: var(--rs); animation: fade-up 0.4s ease both; }}
.ref-lbl {{ font-size: 0.59rem; font-weight: 700; color: var(--t3); text-transform: uppercase; letter-spacing: 0.1em; margin-right: 2px; }}
.ref-pill {{ background: var(--bg-card); border: 1px solid var(--brd); border-radius: 99px; padding: 2px 8px; font-size: 0.61rem; font-weight: 600; color: var(--accent-hi); white-space: nowrap; transition: all 0.18s; cursor: default; }}
.ref-pill:hover {{ background: var(--accent-glow); transform: translateY(-2px); }}

/* ── Typing indicator ── */
.typing {{ display: flex; align-items: center; gap: 5px; padding: 11px 15px; background: var(--ai-bubble); border: 1px solid var(--brd3); border-radius: 4px 18px 18px 18px; width: fit-content; margin: 3px 0; box-shadow: 0 2px 12px rgba(0,0,0,0.25); }}
.td {{ width: 6px; height: 6px; border-radius: 50%; background: var(--accent); animation: typing-dot 1.3s ease-in-out infinite; }}
.td:nth-child(1){{ animation-delay: 0s; }}
.td:nth-child(2){{ animation-delay: 0.22s; }}
.td:nth-child(3){{ animation-delay: 0.44s; }}
@keyframes typing-dot {{ 0%,55%,100%{{ opacity:0.15; transform:translateY(0); }} 28%{{ opacity:1; transform:translateY(-5px); }} }}
.tlbl {{ font-size: 0.67rem; color: var(--t3); font-style: italic; margin-left: 3px; }}

/* ── AI Generating Pulse on avatar-like indicator ── */
.ai-gen-pulse {{
  display: inline-flex; align-items: center; gap: 7px;
  background: var(--accent-soft); border: 1px solid var(--brd2);
  border-radius: 99px; padding: 4px 12px; font-size: 0.68rem; font-weight: 600; color: var(--accent-hi);
  margin-bottom: 8px; animation: pulse-border 1.2s ease-in-out infinite;
}}
@keyframes pulse-border {{ 0%,100%{{ box-shadow: 0 0 0 0 var(--accent-glow); }} 50%{{ box-shadow: 0 0 0 5px transparent; }} }}
.ai-gen-dot {{ width: 7px; height: 7px; border-radius: 50%; background: var(--accent); animation: gen-dot 0.9s ease-in-out infinite alternate; }}
@keyframes gen-dot {{ from{{ opacity:0.3; transform:scale(0.7); }} to{{ opacity:1; transform:scale(1.2); }} }}

/* ── CHAT INPUT ── */
[data-testid="stBottom"] {{
  background: transparent !important; border-top: none !important;
  padding: 0.65rem clamp(0.7rem, 4vw, 1.8rem) 0.85rem !important;
  position: sticky !important; bottom: 0 !important; z-index: 100 !important;
}}
[data-testid="stBottom"]::before {{
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(to top, var(--bg-deep) 0%, transparent 100%);
  backdrop-filter: blur(18px) saturate(140%); border-top: 1px solid var(--brd3); z-index: -1;
}}
[data-testid="stChatInput"] {{
  background: var(--input-bg) !important; border: 1.5px solid var(--brd2) !important;
  border-radius: 20px !important; max-width: 830px !important; margin: 0 auto !important;
  transition: border-color 0.25s, box-shadow 0.25s !important;
  box-shadow: 0 4px 22px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.05) !important;
  backdrop-filter: blur(16px) !important;
}}
[data-testid="stChatInput"]:focus-within {{
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--accent-glow), 0 4px 26px var(--accent-glow), inset 0 1px 0 rgba(255,255,255,0.07) !important;
}}
[data-testid="stChatInput"] textarea {{
  background: transparent !important; color: var(--t1) !important;
  font-family: var(--fb) !important; font-size: 0.91rem !important;
  caret-color: var(--accent-hi) !important; padding: 13px 16px !important;
  line-height: 1.58 !important; min-height: 50px !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{ color: var(--t3) !important; font-size: 0.9rem !important; }}
[data-testid="stChatInput"] button {{
  background: linear-gradient(135deg, var(--accent-lo), var(--accent)) !important;
  border: none !important; border-radius: 13px !important; margin: 6px !important;
  transition: opacity 0.18s, transform 0.18s, box-shadow 0.18s !important;
  box-shadow: 0 2px 12px var(--accent-glow) !important;
}}
[data-testid="stChatInput"] button:hover {{ opacity: 0.88 !important; transform: scale(1.09) !important; }}
[data-testid="stChatInput"] button svg {{ fill: #fff !important; }}

/* ── Scroll to bottom button ── */
.scroll-btn {{
  position: fixed; bottom: 90px; right: 24px; z-index: 999;
  width: 40px; height: 40px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-lo), var(--accent));
  border: none; cursor: pointer; display: grid; place-items: center;
  box-shadow: 0 4px 18px var(--accent-glow); color: #fff;
  font-size: 16px; transition: all 0.22s; text-decoration: none;
}}
.scroll-btn:hover {{ transform: scale(1.12) translateY(-2px); box-shadow: 0 6px 24px var(--accent-glow); }}

.stSpinner > div {{ border-top-color: var(--accent) !important; }}
hr {{ border: none !important; border-top: 1px solid var(--brd3) !important; margin: 10px 0 !important; }}

/* ── RESPONSIVE ── */
@media (max-width: 640px) {{
  .topbar {{ padding: 0.5rem 0.85rem; }}
  .pm {{ display: none; }}
  [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stChatMessageContent {{ max-width: 90% !important; font-size: 0.85rem !important; }}
  [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stChatMessageContent {{ max-width: 96% !important; font-size: 0.85rem !important; }}
  .w-h {{ font-size: clamp(1.4rem, 7vw, 1.75rem); }}
  .w-grid {{ grid-template-columns: 1fr 1fr; gap: 7px; }}
  .w-orb {{ width: 70px; height: 70px; font-size: 27px; }}
  [data-testid="stBottom"] {{ padding: 0.55rem 0.65rem 0.75rem !important; }}
  [data-testid="stChatInput"] {{ border-radius: 15px !important; }}
  [data-testid="stSidebar"] {{ min-width: 255px !important; max-width: 275px !important; }}
  .sg {{ grid-template-columns: 1fr 1fr; }}
  .scroll-btn {{ bottom: 75px; right: 14px; width: 36px; height: 36px; font-size: 14px; }}
}}
</style>
"""

# ─────────────────────────────────────────────────────────────────────────────
#  EXPORT FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def export_txt(messages: list) -> bytes:
    lines = [
        "NeuraChat AI v8.0 — Conversation Export",
        f"Date  : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Model : {FREE_MODEL_IDS.get(st.session_state.model_key, 'unknown')}",
        "═" * 62, "",
    ]
    for m in messages:
        role = "You" if m["role"] == "user" else "NeuraChat AI"
        lines += [f"[{role}]", m["content"], ""]
    return "\n".join(lines).encode("utf-8")

def export_md(messages: list) -> bytes:
    lines = [
        "# NeuraChat AI v8.0 — Conversation Export",
        f"*{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}* · Model: `{FREE_MODEL_IDS.get(st.session_state.model_key, 'unknown')}`", "",
    ]
    for m in messages:
        role = "**You**" if m["role"] == "user" else "**NeuraChat AI**"
        lines += [f"### {role}", m["content"], "---", ""]
    return "\n".join(lines).encode("utf-8")

def export_pdf(messages: list) -> bytes:
    class NeuraChat_PDF(FPDF):
        def header(self):
            self.set_font("Helvetica", "B", 18)
            self.set_text_color(109, 113, 240)
            self.cell(0, 12, "NeuraChat AI", ln=False, align="C")
            self.ln(8)
            self.set_font("Helvetica", "", 8)
            self.set_text_color(140, 145, 170)
            self.cell(0, 5, f"v8.0  ·  {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}  ·  Model: {FREE_MODEL_IDS.get(st.session_state.model_key, '?')}", ln=True, align="C")
            self.ln(2)
            # Decorative divider
            self.set_draw_color(109, 113, 240)
            self.set_line_width(0.5)
            self.line(10, self.get_y(), self.w - 10, self.get_y())
            self.ln(5)

        def footer(self):
            self.set_y(-12)
            self.set_font("Helvetica", "I", 7)
            self.set_text_color(150, 150, 170)
            self.cell(0, 8, f"Page {self.page_no()} — NeuraChat AI v8.0", align="C")

    pdf = NeuraChat_PDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    for i, m in enumerate(messages):
        is_user = m["role"] == "user"
        # Role header
        pdf.set_font("Helvetica", "B", 10)
        if is_user:
            pdf.set_text_color(60, 80, 220)
        else:
            pdf.set_text_color(109, 113, 240)
        role_label = "  YOU" if is_user else "  NEURACHAT AI"
        pdf.set_fill_color(240, 242, 255) if is_user else pdf.set_fill_color(245, 245, 255)
        pdf.set_draw_color(200, 205, 250)
        pdf.set_line_width(0.2)
        pdf.rect(10, pdf.get_y(), pdf.w - 20, 8, "DF")
        pdf.set_xy(10, pdf.get_y() + 1.5)
        pdf.cell(pdf.w - 20, 5, role_label, ln=True)
        pdf.ln(2)

        # Content
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(30, 34, 60)
        clean = re.sub(r"```[\w]*\n?", "", m["content"])
        clean = re.sub(r"[`*#_\[\]>]+", "", clean)
        clean = re.sub(r"\n{3,}", "\n\n", clean.strip())

        # Safe latin-1 encode
        safe = ""
        for ch in clean:
            try:
                ch.encode("latin-1")
                safe += ch
            except UnicodeEncodeError:
                safe += "?"

        pdf.multi_cell(0, 5.8, safe, border=0)
        pdf.ln(5)

        # Timing/word count if present
        if m["role"] == "assistant":
            wc = len(m["content"].split())
            timing = m.get("timing", None)
            pdf.set_font("Helvetica", "I", 7.5)
            pdf.set_text_color(160, 165, 185)
            info = f"  {wc} words"
            if timing:
                info += f"  ·  {timing:.1f}s response time"
            pdf.cell(0, 4, info, ln=True)
            pdf.ln(3)

        # Separator
        pdf.set_draw_color(220, 222, 235)
        pdf.set_line_width(0.2)
        pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())
        pdf.ln(5)

    return bytes(pdf.output())

def export_docx(messages: list) -> bytes:
    doc = DocxDocument()
    h = doc.add_heading("NeuraChat AI v8.0 — Conversation Export", 0)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in h.runs:
        run.font.color.rgb = RGBColor(109, 113, 240)
    sub = doc.add_paragraph(f"Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}  ·  Model: {FREE_MODEL_IDS.get(st.session_state.model_key, '?')}")
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.runs[0].font.size = Pt(9)
    sub.runs[0].font.color.rgb = RGBColor(130, 130, 150)
    doc.add_paragraph()
    for m in messages:
        role = "You" if m["role"] == "user" else "NeuraChat AI"
        p = doc.add_paragraph()
        run = p.add_run(f"[{role}]")
        run.bold = True
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(109, 113, 240) if m["role"] == "assistant" else RGBColor(50, 50, 80)
        clean = re.sub(r"[`*#_]+", "", m["content"])
        dp = doc.add_paragraph(clean)
        if dp.runs:
            dp.runs[0].font.size = Pt(10)
        if m["role"] == "assistant":
            meta = doc.add_paragraph()
            wc = len(m["content"].split())
            timing = m.get("timing", None)
            meta_text = f"Words: {wc}"
            if timing:
                meta_text += f"  ·  Time: {timing:.1f}s"
            run_m = meta.add_run(meta_text)
            run_m.font.size = Pt(7.5)
            run_m.font.color.rgb = RGBColor(160, 165, 185)
            run_m.italic = True
        doc.add_paragraph()
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

# ─────────────────────────────────────────────────────────────────────────────
#  STREAMING  —  Smart Fallback
# ─────────────────────────────────────────────────────────────────────────────
def stream_response(messages: list, model_key: str, temperature: float, max_tokens: int):
    client = get_client()
    primary_id = FREE_MODEL_IDS.get(model_key, FREE_MODELS[0][1])

    # Build fallback list: primary first, then all other free models
    all_ids = [m[1] for m in FREE_MODELS]
    candidates = [primary_id] + [mid for mid in all_ids if mid != primary_id]

    api_msgs = [
        {"role": "system", "content": build_system_prompt(
            st.session_state.style,
            st.session_state.tone,
        )}
    ] + [{"role": m["role"], "content": m["content"]} for m in messages]

    for model in candidates:
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=api_msgs,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                extra_headers={
                    "HTTP-Referer": "https://neurachat.ai",
                    "X-Title": "NeuraChat AI ",
                },
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            return

        except APITimeoutError:
            yield "\n\n⏱️ **Request timed out.** Trying next model…\n\n"
            continue
        except RateLimitError:
            if model == candidates[-1]:
                yield "\n\n🚦 **Rate limit reached on all models.** Please wait a moment and retry."
                return
            continue
        except APIConnectionError:
            yield "\n\n🌐 **Connection error.** Check your internet connection or OpenRouter status."
            return
        except Exception as e:
            err = str(e)
            if any(k in err for k in ["429", "404", "quota", "not found", "endpoint", "temporarily", "overloaded", "unavailable"]):
                if model == candidates[-1]:
                    yield "\n\n⚠️ **All models are currently busy.** Please retry shortly."
                    return
                continue
            yield f"\n\n⚠️ **Error:** {err}"
            return

    yield "\n\n⚠️ **All models busy.** Please retry in a moment."


# ─────────────────────────────────────────────────────────────────────────────
#  INJECT CSS
# ─────────────────────────────────────────────────────────────────────────────
current_theme = THEMES[st.session_state.theme]
st.markdown(build_css(current_theme), unsafe_allow_html=True)

# Scroll to bottom JS
st.markdown("""
<script>
function scrollToBottom() {
  const msgs = document.querySelectorAll('[data-testid="stChatMessage"]');
  if (msgs.length) msgs[msgs.length - 1].scrollIntoView({ behavior: 'smooth', block: 'end' });
}
</script>
<a href="#bottom-anchor" class="scroll-btn" title="Scroll to bottom">↓</a>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    busy = st.session_state.get("_busy", False)

    st.markdown(f"""
    <div class="brand">
      <div class="b-gem">✦</div>
      <div>
        <div class="b-name">NeuraChat AI</div>
        <div class="b-badge">✦ v8.0 Unlimited</div>
      </div>
    </div>
    <div class="status">
      <div class="dot {'dbz' if busy else 'don'}"></div>
      <span class="stxt">{'Generating…' if busy else 'Ready · All Models Free'}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Theme ──
    st.markdown('<div class="slbl">🎨 Theme</div>', unsafe_allow_html=True)
    theme_names = list(THEMES.keys())
    old_theme = st.session_state.theme
    st.session_state.theme = st.selectbox("Theme", theme_names,
        index=theme_names.index(st.session_state.theme), label_visibility="collapsed")
    if st.session_state.theme != old_theme:
        st.rerun()

    # ── Model ──
    st.markdown('<div class="slbl">🤖 AI Model (All Free)</div>', unsafe_allow_html=True)
    midx = FREE_MODEL_NAMES.index(st.session_state.model_key) if st.session_state.model_key in FREE_MODEL_NAMES else 0
    st.session_state.model_key = st.selectbox("Model", FREE_MODEL_NAMES, index=midx, label_visibility="collapsed")
    mshort_id = FREE_MODEL_IDS.get(st.session_state.model_key, "").split("/")[-1].replace(":free", "")
    st.markdown(f"""
    <div class="mchip">⚡ {mshort_id}<span class="free-badge">✓ FREE</span></div>
    <div style="font-size:0.6rem;color:var(--t3);margin-top:3px;">Smart fallback active — auto-retries on failure</div>
    """, unsafe_allow_html=True)

    # ── Generation ──
    st.markdown('<div class="slbl">⚙️ Generation</div>', unsafe_allow_html=True)
    st.session_state.temperature = st.slider("🌡️ Temperature", 0.0, 1.0, st.session_state.temperature, 0.05)
    st.session_state.max_tokens  = st.slider("📏 Max Tokens", 256, 4096, st.session_state.max_tokens, 64)

    # ── Style ──
    st.markdown('<div class="slbl">📝 Response Style</div>', unsafe_allow_html=True)
    st.session_state.style = st.selectbox("Style", list(RESPONSE_STYLES.keys()),
        index=list(RESPONSE_STYLES.keys()).index(st.session_state.style))
    st.session_state.tone = st.selectbox("Tone",
        ["Professional", "Friendly", "Casual", "Academic", "Creative", "Direct"])

    # ── Options ──
    st.markdown('<div class="slbl">🔧 Options</div>', unsafe_allow_html=True)
    st.session_state.show_refs   = st.toggle("📎 Source References", value=st.session_state.show_refs)
    st.session_state.show_tokens = st.toggle("📊 Token Estimate",    value=st.session_state.show_tokens)
    st.session_state.show_timing = st.toggle("⏱️ Response Time",     value=st.session_state.show_timing)

    # ── Session Stats ──
    st.markdown('<div class="slbl">📊 Session Stats</div>', unsafe_allow_html=True)
    uc = len([m for m in st.session_state.messages if m["role"] == "user"])
    ac = len([m for m in st.session_state.messages if m["role"] == "assistant"])
    tw = sum(len(m["content"].split()) for m in st.session_state.messages)
    avg_t = ""
    timings = [m.get("timing",0) for m in st.session_state.messages if m.get("timing")]
    avg_timing = sum(timings)/len(timings) if timings else 0
    st.markdown(f"""<div class="sg">
      <div class="sc"><div class="sn">{uc}</div><div class="sl">Sent</div></div>
      <div class="sc"><div class="sn">{ac}</div><div class="sl">Replies</div></div>
      <div class="sc"><div class="sn">{tw}</div><div class="sl">Words</div></div>
    </div>""", unsafe_allow_html=True)
    if avg_timing:
        st.markdown(f'<div style="font-size:0.62rem;color:var(--t3);margin-top:4px;">Avg response time: <span style="color:var(--t2)">{avg_timing:.1f}s</span></div>', unsafe_allow_html=True)

    # ── Capabilities ──
    st.markdown('<div class="slbl">✨ Capabilities</div>', unsafe_allow_html=True)
    st.markdown("""<div class="tags">
      <span class="tag">💻 Code</span>
      <span class="tag">📊 Data</span>
      <span class="tag">🧮 Math</span>
      <span class="tag">✍️ Writing</span>
      <span class="tag">🔬 Science</span>
      <span class="tag">🎨 Creative</span>
      <span class="tag">🗺️ Diagrams</span>
      <span class="tag">📈 Analysis</span>
    </div>""", unsafe_allow_html=True)

    # ── Export ──
    st.markdown('<div class="slbl">💾 Export Chat</div>', unsafe_allow_html=True)
    if st.session_state.messages:
        fname = f"neurachat_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}"
        st.download_button("📄 Notepad (.txt)", data=export_txt(st.session_state.messages),
            file_name=f"{fname}.txt", mime="text/plain")
        st.download_button("📝 Markdown (.md)", data=export_md(st.session_state.messages),
            file_name=f"{fname}.md",  mime="text/markdown")
        if HAS_PDF:
            try:
                st.download_button("📕 PDF Document", data=export_pdf(st.session_state.messages),
                    file_name=f"{fname}.pdf", mime="application/pdf")
            except Exception as e:
                st.caption(f"⚠️ PDF error: {e}")
        if HAS_DOCX:
            try:
                st.download_button("📘 Word (.docx)", data=export_docx(st.session_state.messages),
                    file_name=f"{fname}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            except Exception as e:
                st.caption(f"⚠️ DOCX error: {e}")
    else:
        st.markdown('<span style="font-size:.71rem;color:var(--t3)">Start chatting to enable export</span>', unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

    st.markdown(f"""<div class="sb-footer">
      ✦ NeuraChat AI · v8.0 Unlimited<br>
      All Free · Smart Fallback · OpenRouter<br>
      Session started {st.session_state.session_start}
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN AREA
# ─────────────────────────────────────────────────────────────────────────────
mshort_display = FREE_MODEL_IDS.get(st.session_state.model_key, "").split("/")[-1].replace(":free", "")

st.markdown(f"""
<div class="topbar">
  <div class="tbl">
    <div class="tbico">✦</div>
    <div class="tbtitle">NeuraChat AI</div>
  </div>
  <div class="tbr">
    <div class="pill pm">⚡ {mshort_display}</div>
    <div class="pill pt">🎨 {st.session_state.style}</div>
    <div class="pill pt">{st.session_state.theme.split()[0]} {st.session_state.theme.split()[1] if len(st.session_state.theme.split())>1 else ""}</div>
    <div class="pill ps"><div class="pdot"></div>Free Unlimited</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Welcome
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome">
      <div class="w-orb">✦</div>
      <div class="w-h">Hello! What shall we<br><span>explore today?</span></div>
      <div class="w-sub">
        Unlimited free AI — all models, no limits, no login.<br>
        Code, math, writing, research, and beyond.
      </div>
      <div class="w-grid">
        <div class="w-card"><div class="wci">💻</div><div class="wct">Code & Debug</div><div class="wcs">Any language, architecture, bug fixing</div></div>
        <div class="w-card"><div class="wci">📊</div><div class="wct">Diagrams</div><div class="wcs">Mermaid flowcharts, ERDs, sequences</div></div>
        <div class="w-card"><div class="wci">🧮</div><div class="wct">Math & LaTeX</div><div class="wcs">Equations, proofs, step-by-step</div></div>
        <div class="w-card"><div class="wci">✍️</div><div class="wct">Writing</div><div class="wcs">Reports, emails, essays, blogs</div></div>
        <div class="w-card"><div class="wci">🔍</div><div class="wct">Research</div><div class="wcs">Deep analysis, summaries, compare</div></div>
        <div class="w-card"><div class="wci">🎨</div><div class="wct">Creative</div><div class="wcs">Brainstorm, fiction, worldbuilding</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# Chat history
with st.container():
    st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                # Meta strip
                meta_parts = []
                wc = len(msg["content"].split())
                meta_parts.append(f'<div class="meta-chip">📝 <span>{wc} words</span></div>')
                if st.session_state.show_tokens:
                    est = int(wc * 1.35)
                    meta_parts.append(f'<div class="meta-chip">🔢 <span>~{est} tokens</span></div>')
                if st.session_state.show_timing and msg.get("timing"):
                    meta_parts.append(f'<div class="meta-chip">⏱️ <span>{msg["timing"]:.1f}s</span></div>')
                if meta_parts:
                    st.markdown(f'<div class="msg-meta">{"".join(meta_parts)}</div>', unsafe_allow_html=True)
                # Source refs
                if st.session_state.show_refs and msg.get("refs"):
                    pills = "".join([f'<span class="ref-pill">📎 {r}</span>' for r in msg["refs"]])
                    st.markdown(f'<div class="ref-card"><span class="ref-lbl">Sources</span>{pills}</div>', unsafe_allow_html=True)

    # Bottom anchor for scroll
    st.markdown('<div id="bottom-anchor"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  INPUT + STREAMING
# ─────────────────────────────────────────────────────────────────────────────
placeholder = f"Ask NeuraChat… ({st.session_state.style} · {mshort_display})"

if prompt := st.chat_input(placeholder):
    refs = get_refs(prompt) if st.session_state.show_refs else []
    st.session_state._busy = True

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Generating pulse indicator
        gen_ph = st.empty()
        gen_ph.markdown("""
        <div class="ai-gen-pulse">
          <div class="ai-gen-dot"></div>
          Generating…
        </div>""", unsafe_allow_html=True)

        # Typing dots
        typing_ph = st.empty()
        typing_ph.markdown("""
        <div class="typing">
          <div class="td"></div><div class="td"></div><div class="td"></div>
          <span class="tlbl">Thinking…</span>
        </div>""", unsafe_allow_html=True)

        response_ph = st.empty()
        full_reply  = ""
        first_chunk = True
        buf_count   = 0
        start_time  = time.time()

        for chunk in stream_response(
            st.session_state.messages,
            st.session_state.model_key,
            st.session_state.temperature,
            st.session_state.max_tokens,
        ):
            if first_chunk:
                typing_ph.empty()
                gen_ph.empty()
                first_chunk = False
            full_reply += chunk
            buf_count  += 1
            if buf_count >= 3:
                response_ph.markdown(full_reply + "▌")
                buf_count = 0

        elapsed = time.time() - start_time
        response_ph.markdown(full_reply)

        # Meta strip
        wc = len(full_reply.split())
        meta_parts = [f'<div class="meta-chip">📝 <span>{wc} words</span></div>']
        if st.session_state.show_tokens:
            est = int(wc * 1.35)
            meta_parts.append(f'<div class="meta-chip">🔢 <span>~{est} tokens</span></div>')
        if st.session_state.show_timing:
            meta_parts.append(f'<div class="meta-chip">⏱️ <span>{elapsed:.1f}s</span></div>')
        st.markdown(f'<div class="msg-meta">{"".join(meta_parts)}</div>', unsafe_allow_html=True)

        # Source refs
        if refs:
            pills = "".join([f'<span class="ref-pill">📎 {r}</span>' for r in refs])
            st.markdown(f'<div class="ref-card"><span class="ref-lbl">Sources</span>{pills}</div>', unsafe_allow_html=True)

    st.session_state._busy = False
    st.session_state.messages.append({
        "role":    "assistant",
        "content": full_reply,
        "refs":    refs,
        "timing":  elapsed,
    })