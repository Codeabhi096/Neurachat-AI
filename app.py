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
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG  (must be FIRST Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NeuraChat AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
#  API CLIENT  —  Fixed: try/except for secrets
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    key = ""
    try:
        key = st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        key = os.getenv("OPENROUTER_API_KEY", "")

    if not key:
        st.error("❌ OPENROUTER_API_KEY not found! Add it to `.streamlit/secrets.toml` or `.env`")
        st.stop()

    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=key,
        timeout=60.0,
    )

# ─────────────────────────────────────────────────────────────────────────────
#  MODELS
# ─────────────────────────────────────────────────────────────────────────────
FREE_MODELS = [
    ("🌟 Gemini 2.0 Flash",       "google/gemini-2.0-flash-exp:free"),
    ("🧠 DeepSeek V3",            "deepseek/deepseek-chat-v3-0324:free"),
    ("🦙 LLaMA 4 Maverick",       "meta-llama/llama-4-maverick:free"),
    ("🔮 Mistral Small 3.1",      "mistralai/mistral-small-3.1-24b-instruct:free"),
    ("⚡ Gemini 2.0 Flash Lite",  "google/gemini-2.0-flash-lite-001"),
    ("🤖 Auto (Smart Route)",     "openrouter/auto"),
]
FREE_MODEL_NAMES = [m[0] for m in FREE_MODELS]
FREE_MODEL_IDS   = {m[0]: m[1] for m in FREE_MODELS}

# ─────────────────────────────────────────────────────────────────────────────
#  THEMES
# ─────────────────────────────────────────────────────────────────────────────
THEMES = {
    "🌑 Midnight Glass": {
        "bg":          "#050709",
        "bg2":         "#080b12",
        "card":        "rgba(14,18,30,0.82)",
        "accent":      "#6d71f0",
        "accent_hi":   "#9b9ff7",
        "accent_lo":   "#4a4ec8",
        "soft":        "rgba(109,113,240,0.12)",
        "glow":        "rgba(109,113,240,0.22)",
        "t1":          "#f0f2ff",
        "t2":          "#8892b0",
        "t3":          "#3d4466",
        "brd":         "rgba(109,113,240,0.16)",
        "brd2":        "rgba(109,113,240,0.30)",
        "brd3":        "rgba(255,255,255,0.06)",
        "user_bub":    "linear-gradient(135deg,#3d4bda,#5865f2,#6d71f0)",
        "ai_bub":      "rgba(14,18,30,0.88)",
        "sb_bg":       "rgba(5,7,14,0.97)",
        "tb_bg":       "rgba(5,7,9,0.88)",
        "inp_bg":      "rgba(14,18,32,0.72)",
        "grain":       "radial-gradient(ellipse 90% 70% at 15% 5%,rgba(109,113,240,0.08) 0%,transparent 60%),radial-gradient(ellipse 70% 80% at 85% 95%,rgba(99,102,241,0.06) 0%,transparent 55%)",
    },
    "⚡ Cyberpunk": {
        "bg":          "#040408",
        "bg2":         "#060610",
        "card":        "rgba(8,8,20,0.90)",
        "accent":      "#00ff9f",
        "accent_hi":   "#ff2d78",
        "accent_lo":   "#00cc80",
        "soft":        "rgba(0,255,159,0.10)",
        "glow":        "rgba(0,255,159,0.20)",
        "t1":          "#e8fff5",
        "t2":          "#6affcb",
        "t3":          "#1a4433",
        "brd":         "rgba(0,255,159,0.18)",
        "brd2":        "rgba(0,255,159,0.35)",
        "brd3":        "rgba(0,255,159,0.08)",
        "user_bub":    "linear-gradient(135deg,#ff2d78,#ff6baa)",
        "ai_bub":      "rgba(8,16,12,0.92)",
        "sb_bg":       "rgba(4,4,10,0.98)",
        "tb_bg":       "rgba(4,4,8,0.92)",
        "inp_bg":      "rgba(8,10,18,0.82)",
        "grain":       "radial-gradient(ellipse 80% 60% at 10% 10%,rgba(0,255,159,0.06) 0%,transparent 60%),radial-gradient(ellipse 60% 70% at 90% 90%,rgba(255,45,120,0.06) 0%,transparent 55%)",
    },
    "☀️ Nordic Light": {
        "bg":          "#f5f6fa",
        "bg2":         "#eef0f6",
        "card":        "rgba(255,255,255,0.92)",
        "accent":      "#4f6ef7",
        "accent_hi":   "#2d4fc5",
        "accent_lo":   "#7b93fb",
        "soft":        "rgba(79,110,247,0.10)",
        "glow":        "rgba(79,110,247,0.18)",
        "t1":          "#1a1d2e",
        "t2":          "#4a5068",
        "t3":          "#9aa0b8",
        "brd":         "rgba(79,110,247,0.16)",
        "brd2":        "rgba(79,110,247,0.32)",
        "brd3":        "rgba(0,0,0,0.08)",
        "user_bub":    "linear-gradient(135deg,#4f6ef7,#6b84fa)",
        "ai_bub":      "rgba(255,255,255,0.96)",
        "sb_bg":       "rgba(238,240,248,0.98)",
        "tb_bg":       "rgba(245,246,250,0.94)",
        "inp_bg":      "rgba(255,255,255,0.88)",
        "grain":       "radial-gradient(ellipse 80% 60% at 20% 20%,rgba(79,110,247,0.05) 0%,transparent 60%),radial-gradient(ellipse 60% 70% at 80% 80%,rgba(79,110,247,0.04) 0%,transparent 55%)",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
#  TOPIC / REFS
# ─────────────────────────────────────────────────────────────────────────────
REF_MAP = {
    "code":    ["Stack Overflow","GitHub Repos","Official Docs","MDN Web Docs"],
    "math":    ["Wolfram Alpha","ArXiv Papers","Khan Academy","MathWorld"],
    "science": ["PubMed","Nature Journals","Scientific American","arXiv"],
    "writing": ["Literary Corpus","Style Guides","Grammarly Insights"],
    "general": ["Wikipedia","Web Corpus 2024","Academic Sources"],
    "analysis":["Research Papers","Statistical DBs","Industry Reports"],
    "history": ["Britannica","Historical Archives","Academic Journals"],
}
_CODE_KW    = {"code","python","javascript","function","bug","api","sql","html","css","def ","const ","git","react","node","docker","typescript","golang","rust"}
_MATH_KW    = {"math","equation","calculus","algebra","integral","formula","statistics","matrix","derivative"}
_SCI_KW     = {"science","physics","chemistry","biology","quantum","genetics","molecule"}
_WRITE_KW   = {"write","essay","story","poem","email","letter","blog","creative","fiction"}
_ANALYZE_KW = {"analyze","compare","evaluate","research","investigate","assess"}
_HIST_KW    = {"history","historical","war","ancient","civilization","revolution"}

def detect_topic(text: str) -> str:
    t = text.lower()
    if any(w in t for w in _CODE_KW):    return "code"
    if any(w in t for w in _MATH_KW):    return "math"
    if any(w in t for w in _SCI_KW):     return "science"
    if any(w in t for w in _WRITE_KW):   return "writing"
    if any(w in t for w in _ANALYZE_KW): return "analysis"
    if any(w in t for w in _HIST_KW):    return "history"
    return "general"

def get_refs(prompt: str) -> list:
    return REF_MAP.get(detect_topic(prompt), REF_MAP["general"])[:3]

# ─────────────────────────────────────────────────────────────────────────────
#  STYLES
# ─────────────────────────────────────────────────────────────────────────────
STYLES = {
    "Balanced":  "Clear, well-structured, professional. Use markdown with headers.",
    "Concise":   "Brief and direct. Key points only. Bullet points preferred.",
    "Detailed":  "Comprehensive with examples, edge cases, and full explanations.",
    "Technical": "Precise. Always include code, formulas, implementation details.",
    "Creative":  "Vivid, imaginative, and surprising. Push beyond conventional answers.",
    "Friendly":  "Warm and conversational. Explain like talking to a smart friend.",
}

def build_system_prompt(style: str, tone: str) -> str:
    return (
        f"You are NeuraChat — a premium AI assistant for developers, researchers, and power users.\n\n"
        f"STYLE: {STYLES.get(style, STYLES['Balanced'])}\nTONE: {tone}\n\n"
        "RULES:\n"
        "- Use markdown: ## H2, ### H3, **bold**, *italic*, `code`\n"
        "- Code blocks: always \\`\\`\\`language\n"
        "- Math: $...$ inline, $$...$$ block\n"
        "- Start responses DIRECTLY — no preambles like 'Great question!'\n"
        "- Be accurate, concise, and genuinely helpful."
    )

# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
DEFAULTS = {
    "messages":      [],
    "model_key":     FREE_MODEL_NAMES[0],
    "style":         "Balanced",
    "tone":          "Professional",
    "temperature":   0.7,
    "max_tokens":    2048,
    "show_refs":     True,
    "show_tokens":   True,
    "show_timing":   True,
    "theme":         "🌑 Midnight Glass",
    "session_start": datetime.datetime.now().strftime("%H:%M"),
    "total_chars":   0,
    "_busy":         False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
#  CSS — Fixed: no truncation, reliable selectors, deploy-safe
# ─────────────────────────────────────────────────────────────────────────────
def build_css(t: dict) -> str:
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700;12..96,800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {{
  --bg:   {t["bg"]};   --bg2:  {t["bg2"]};  --card: {t["card"]};
  --acc:  {t["accent"]}; --ahi: {t["accent_hi"]}; --alo: {t["accent_lo"]};
  --soft: {t["soft"]}; --glow: {t["glow"]};
  --t1:   {t["t1"]};   --t2:   {t["t2"]};   --t3:   {t["t3"]};
  --brd:  {t["brd"]};  --brd2: {t["brd2"]}; --brd3: {t["brd3"]};
  --ubub: {t["user_bub"]}; --abub: {t["ai_bub"]};
  --sb:   {t["sb_bg"]}; --tb:  {t["tb_bg"]}; --inp: {t["inp_bg"]};
  --fd: 'Bricolage Grotesque', system-ui, sans-serif;
  --fb: 'DM Sans', system-ui, sans-serif;
  --mono: 'JetBrains Mono', monospace;
  --r: 16px; --rs: 10px;
}}

*,*::before,*::after {{ box-sizing:border-box; margin:0; padding:0; }}

html, body, .stApp {{
  background: var(--bg) !important;
  font-family: var(--fb) !important;
  color: var(--t1) !important;
  overflow-x: hidden;
}}

.stApp::before {{
  content:''; position:fixed; inset:0;
  background: {t["grain"]};
  pointer-events:none; z-index:0;
}}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] {{ display:none !important; }}
.block-container {{ padding:0 !important; max-width:100% !important; }}
.stAppViewBlockContainer {{ padding-top:0 !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width:3px; height:3px; }}
::-webkit-scrollbar-track {{ background:transparent; }}
::-webkit-scrollbar-thumb {{ background:var(--acc)66; border-radius:99px; }}

/* ──────────────── SIDEBAR ──────────────── */
[data-testid="stSidebar"] {{
  background: var(--sb) !important;
  border-right: 1px solid var(--brd) !important;
  backdrop-filter: blur(24px) !important;
  min-width: 270px !important;
  max-width: 290px !important;
  position: relative !important;
  z-index: 100 !important;
}}
[data-testid="stSidebar"] > div {{
  background: transparent !important;
}}
[data-testid="stSidebar"] > div:first-child {{
  padding: 1.2rem 1rem 2rem !important;
  height: 100vh !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
}}

/* Sidebar Selectbox */
[data-testid="stSidebar"] .stSelectbox label {{
  color: var(--t2) !important; font-size:0.72rem !important; font-weight:600 !important;
}}
[data-testid="stSidebar"] .stSelectbox > div > div {{
  background: var(--card) !important; border: 1px solid var(--brd) !important;
  border-radius: var(--rs) !important; color: var(--t1) !important;
  font-size: 0.8rem !important; font-family: var(--fb) !important;
}}
[data-testid="stSidebar"] .stSelectbox > div > div:hover {{ border-color:var(--acc) !important; }}
[data-testid="stSidebar"] .stSelectbox li {{
  background: var(--bg2) !important; color: var(--t1) !important;
}}
/* Sidebar Slider */
[data-testid="stSidebar"] .stSlider label {{
  color: var(--t2) !important; font-size:0.71rem !important;
}}
[data-testid="stSidebar"] .stSlider [data-baseweb="thumb"] {{
  background: var(--acc) !important; border:2px solid var(--bg) !important;
  box-shadow: 0 0 10px var(--glow) !important;
}}
[data-testid="stSidebar"] .stSlider [data-baseweb="track-fill"] {{
  background: linear-gradient(90deg, var(--alo), var(--acc)) !important;
}}
/* Sidebar Toggle */
[data-testid="stSidebar"] .stToggle label {{
  color: var(--t2) !important; font-size:0.75rem !important;
}}

/* ── Buttons ── */
.stButton > button {{
  background: var(--soft) !important; border: 1px solid var(--brd2) !important;
  color: var(--ahi) !important; border-radius: var(--rs) !important;
  font-family: var(--fb) !important; font-size: 0.77rem !important;
  font-weight: 600 !important; width: 100% !important;
  padding: 0.45rem 0.8rem !important; transition: all 0.2s !important;
}}
.stButton > button:hover {{
  background: var(--glow) !important; border-color: var(--acc) !important;
  box-shadow: 0 4px 16px var(--glow) !important;
  transform: translateY(-2px) !important; color: var(--t1) !important;
}}
[data-testid="stDownloadButton"] > button {{
  background: var(--soft) !important; border: 1px solid var(--brd2) !important;
  color: var(--ahi) !important; border-radius: var(--rs) !important;
  font-family: var(--fb) !important; font-size: 0.72rem !important;
  font-weight: 600 !important; width: 100% !important;
  padding: 0.42rem 0.75rem !important; transition: all 0.2s !important;
}}
[data-testid="stDownloadButton"] > button:hover {{
  background: var(--glow) !important; border-color: var(--acc) !important;
  transform: translateY(-2px) !important;
}}

/* ─── Sidebar Custom HTML ─── */
.brand {{ display:flex; align-items:center; gap:10px; padding-bottom:1rem; margin-bottom:1.1rem; border-bottom:1px solid var(--brd3); }}
.b-gem {{
  width:36px; height:36px; flex-shrink:0;
  background: linear-gradient(135deg, var(--alo), var(--acc), var(--ahi));
  border-radius:11px; display:grid; place-items:center; font-size:15px;
  box-shadow: 0 0 20px var(--glow);
  animation: gem-pulse 4s ease-in-out infinite;
}}
@keyframes gem-pulse {{
  0%,100% {{ box-shadow:0 0 18px var(--glow); }}
  50% {{ box-shadow:0 0 38px var(--glow); transform:scale(1.06); }}
}}
.b-name {{ font-family:var(--fd); font-size:0.97rem; font-weight:800; color:var(--t1); line-height:1.2; }}
.b-badge {{
  display:inline-flex; align-items:center; gap:3px;
  background:var(--soft); border:1px solid var(--brd2);
  border-radius:99px; padding:2px 7px; font-size:0.52rem;
  font-weight:700; color:var(--ahi); text-transform:uppercase; letter-spacing:0.1em;
}}
.slbl {{
  font-size:0.55rem; font-weight:700; color:var(--t3);
  text-transform:uppercase; letter-spacing:0.13em;
  margin:12px 0 4px; display:flex; align-items:center; gap:4px;
}}
.st-status {{
  display:inline-flex; align-items:center; gap:7px;
  background:var(--card); border:1px solid var(--brd3);
  border-radius:99px; padding:5px 11px; margin-bottom:4px;
}}
.dot {{ width:6px; height:6px; border-radius:50%; }}
.don {{ background:#10b981; box-shadow:0 0 7px #10b98199; animation:blink 2.5s infinite; }}
.dbz {{ background:#f59e0b; box-shadow:0 0 7px #f59e0b99; animation:blink 0.7s infinite; }}
@keyframes blink {{ 0%,100%{{ opacity:1; }} 50%{{ opacity:0.15; }} }}
.stxt {{ font-size:0.7rem; font-weight:600; color:var(--t2); }}
.sg {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:5px; margin-top:4px; }}
.sc {{
  background:var(--card); border:1px solid var(--brd3);
  border-radius:var(--rs); padding:8px 5px; text-align:center; transition:all 0.2s;
}}
.sc:hover {{ border-color:var(--acc); transform:translateY(-2px); box-shadow:0 6px 16px var(--glow); }}
.sn {{
  font-family:var(--fd); font-size:1.25rem; font-weight:800; line-height:1;
  background:linear-gradient(135deg,var(--acc),var(--ahi));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}}
.sl {{ font-size:0.52rem; color:var(--t3); margin-top:2px; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; }}
.tags {{ display:flex; flex-wrap:wrap; gap:4px; margin-top:5px; }}
.tag {{
  background:var(--soft); border:1px solid var(--brd); color:var(--ahi);
  border-radius:99px; padding:3px 8px; font-size:0.6rem; font-weight:600;
  transition:all 0.18s; cursor:default;
}}
.tag:hover {{ background:var(--glow); border-color:var(--acc); transform:translateY(-2px); }}
.mchip {{
  background:var(--card); border:1px solid var(--brd); border-radius:var(--rs);
  padding:6px 10px; font-family:var(--mono); font-size:0.62rem; color:var(--ahi);
  overflow:hidden; text-overflow:ellipsis; white-space:nowrap; margin-top:4px;
}}
.free-badge {{
  display:inline-block; padding:1px 7px; border-radius:99px;
  font-size:0.57rem; font-weight:700; float:right;
  background:rgba(16,185,129,0.12); color:#10b981; border:1px solid rgba(16,185,129,0.25);
}}
.sb-footer {{
  font-size:0.58rem; color:var(--t3); text-align:center; line-height:1.85;
  margin-top:12px; padding-top:10px; border-top:1px solid var(--brd3);
}}

/* ──────────────── TOP BAR ──────────────── */
.topbar {{
  background: var(--tb);
  backdrop-filter: blur(32px) saturate(180%);
  border-bottom: 1px solid var(--brd3);
  padding: 0.55rem 1.5rem;
  display: flex; align-items: center; justify-content: space-between;
  position: sticky; top: 0; z-index: 998;
}}
.tbl {{ display:flex; align-items:center; gap:9px; }}
.tbico {{
  width:26px; height:26px; flex-shrink:0;
  background:linear-gradient(135deg, var(--alo), var(--acc));
  border-radius:7px; display:grid; place-items:center; font-size:11px;
  box-shadow:0 2px 10px var(--glow);
}}
.tbtitle {{ font-family:var(--fd); font-size:0.91rem; font-weight:800; color:var(--t1); letter-spacing:-0.02em; }}
.tbr {{ display:flex; align-items:center; gap:5px; flex-shrink:0; flex-wrap:wrap; }}
.pill {{
  border-radius:99px; padding:3px 9px; font-size:0.61rem; font-weight:600;
  display:flex; align-items:center; gap:4px; border:1px solid var(--brd3); white-space:nowrap;
  transition:all 0.2s;
}}
.pill:hover {{ border-color:var(--acc); box-shadow:0 2px 10px var(--glow); }}
.pm {{ background:var(--soft); color:var(--ahi); font-family:var(--mono); font-size:0.56rem; }}
.pt {{ background:var(--card); color:var(--t2); }}
.ps {{ background:rgba(16,185,129,0.10); border-color:rgba(16,185,129,0.28) !important; color:#10b981; }}
.pdot {{ width:5px; height:5px; border-radius:50%; background:currentColor; animation:blink 2s infinite; }}

/* ──────────────── WELCOME ──────────────── */
.welcome {{
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  min-height:60vh; padding:3rem 1.25rem 2rem; text-align:center; position:relative; z-index:1;
}}
.w-orb {{
  width:84px; height:84px;
  background:linear-gradient(135deg, var(--alo), var(--acc), var(--ahi));
  border-radius:26px; display:grid; place-items:center; font-size:32px;
  margin-bottom:1.5rem;
  box-shadow:0 0 0 1px var(--brd2), 0 8px 44px var(--glow), inset 0 1px 0 rgba(255,255,255,0.18);
  animation: orb-float 5s ease-in-out infinite;
}}
@keyframes orb-float {{ 0%,100%{{ transform:translateY(0) scale(1); }} 50%{{ transform:translateY(-10px) scale(1.03); }} }}
.w-h {{
  font-family:var(--fd); font-size:clamp(1.65rem,4.5vw,2.4rem); font-weight:800;
  line-height:1.12; color:var(--t1); margin-bottom:0.65rem;
  animation:fade-up 0.5s ease forwards; letter-spacing:-0.025em;
}}
.w-h span {{
  background:linear-gradient(120deg, var(--alo), var(--acc), var(--ahi));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}}
.w-sub {{
  font-size:clamp(0.82rem,2vw,0.91rem); color:var(--t2); max-width:380px;
  line-height:1.7; margin-bottom:2rem; animation:fade-up 0.65s 0.1s ease both;
}}
@keyframes fade-up {{ from{{ opacity:0; transform:translateY(12px); }} to{{ opacity:1; transform:translateY(0); }} }}
.w-grid {{
  display:grid; grid-template-columns:repeat(3,1fr); gap:8px;
  width:100%; max-width:560px; animation:fade-up 0.8s 0.2s ease both;
}}
.w-card {{
  background:var(--card); border:1px solid var(--brd3); border-radius:var(--r);
  padding:11px 9px; text-align:left;
  transition:all 0.22s cubic-bezier(0.25,0.46,0.45,0.94); position:relative; overflow:hidden;
}}
.w-card::before {{
  content:''; position:absolute; inset:0;
  background:linear-gradient(135deg, var(--glow) 0%, transparent 100%);
  opacity:0; transition:opacity 0.22s;
}}
.w-card:hover {{ border-color:var(--acc); transform:translateY(-4px); box-shadow:0 12px 30px var(--glow); }}
.w-card:hover::before {{ opacity:1; }}
.wci {{ font-size:1.2rem; margin-bottom:5px; }}
.wct {{ font-size:0.71rem; font-weight:700; color:var(--t1); margin-bottom:3px; }}
.wcs {{ font-size:0.63rem; color:var(--t2); line-height:1.45; }}

/* ──────────────── CHAT MESSAGES ──────────────── */
.main-wrap {{
  max-width:860px; margin:0 auto;
  padding:1rem clamp(0.7rem,3.5vw,2rem) 0.5rem;
  position:relative; z-index:1;
}}

/* Hide default avatars */
[data-testid="chatAvatarIcon-user"],
[data-testid="chatAvatarIcon-assistant"] {{ display:none !important; }}

[data-testid="stChatMessage"] {{
  background:transparent !important;
  border:none !important;
  padding:0.18rem 0 !important;
}}

/* ── User message ── */
[data-testid="stChatMessage"][data-testid*="user"] .stChatMessageContent,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stChatMessageContent {{
  background: var(--ubub) !important;
  border-radius: 20px 20px 4px 20px !important;
  color: #fff !important;
  max-width: 70% !important;
  margin-left: auto !important;
  padding: 10px 14px !important;
  font-size: 0.88rem !important;
  line-height: 1.62 !important;
  box-shadow: 0 4px 20px var(--glow), inset 0 1px 0 rgba(255,255,255,0.15) !important;
  border: none !important;
  animation: msg-r 0.24s cubic-bezier(0.25,0.46,0.45,0.94) !important;
}}

/* ── Assistant message ── */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stChatMessageContent {{
  background: var(--abub) !important;
  border: 1px solid var(--brd3) !important;
  border-radius: 4px 20px 20px 20px !important;
  color: var(--t1) !important;
  max-width: 83% !important;
  padding: 12px 15px !important;
  font-size: 0.88rem !important;
  line-height: 1.74 !important;
  box-shadow: 0 2px 16px rgba(0,0,0,0.24), inset 0 1px 0 rgba(255,255,255,0.03) !important;
  backdrop-filter: blur(12px) !important;
  animation: msg-l 0.24s cubic-bezier(0.25,0.46,0.45,0.94) !important;
}}

/* Also target by role for extra reliability */
[data-testid="stChatMessage"]:nth-child(odd) .stChatMessageContent {{ }}

@keyframes msg-r {{ from{{ opacity:0; transform:translateX(14px) scale(0.96); }} to{{ opacity:1; transform:none; }} }}
@keyframes msg-l {{ from{{ opacity:0; transform:translateX(-14px) scale(0.96); }} to{{ opacity:1; transform:none; }} }}

/* ── Markdown inside messages ── */
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3 {{
  font-family:var(--fd) !important; color:var(--ahi) !important;
  margin:12px 0 5px !important; font-weight:700 !important;
}}
[data-testid="stChatMessage"] h1 {{ font-size:1.18em !important; border-bottom:1px solid var(--brd3); padding-bottom:4px !important; }}
[data-testid="stChatMessage"] h2 {{ font-size:1.05em !important; }}
[data-testid="stChatMessage"] h3 {{ font-size:0.95em !important; }}
[data-testid="stChatMessage"] p {{ margin-bottom:4px !important; }}
[data-testid="stChatMessage"] ul,
[data-testid="stChatMessage"] ol {{ padding-left:16px !important; margin:5px 0 !important; }}
[data-testid="stChatMessage"] li {{ margin-bottom:3px !important; color:var(--t2) !important; }}
[data-testid="stChatMessage"] strong {{ color:var(--t1) !important; font-weight:700 !important; }}
[data-testid="stChatMessage"] em {{ color:var(--ahi) !important; }}
[data-testid="stChatMessage"] a {{ color:var(--ahi) !important; text-decoration:underline !important; }}

/* ── Code ── */
[data-testid="stChatMessage"] code {{
  background:var(--soft) !important; border:1px solid var(--brd) !important;
  border-radius:5px !important; padding:2px 5px !important;
  font-size:0.81em !important; color:var(--ahi) !important;
  font-family:var(--mono) !important; font-weight:500 !important;
}}
[data-testid="stChatMessage"] pre {{
  background:rgba(5,7,14,0.92) !important; border:1px solid var(--brd) !important;
  border-left:3px solid var(--acc) !important; border-radius:11px !important;
  padding:13px !important; overflow-x:auto !important; margin:9px 0 !important;
}}
[data-testid="stChatMessage"] pre code {{
  background:transparent !important; border:none !important; padding:0 !important;
  color:var(--t1) !important; font-size:0.82em !important;
}}

/* ── Tables ── */
[data-testid="stChatMessage"] table {{
  border-collapse:collapse !important; width:100% !important;
  margin:10px 0 !important; border-radius:var(--rs) !important; overflow:hidden !important;
}}
[data-testid="stChatMessage"] th {{
  background:var(--soft) !important; color:var(--ahi) !important;
  padding:7px 11px !important; font-size:0.7rem !important; font-weight:700 !important;
  text-transform:uppercase !important; letter-spacing:0.06em !important;
  border-bottom:1px solid var(--brd) !important;
}}
[data-testid="stChatMessage"] td {{
  padding:6px 11px !important; border-bottom:1px solid var(--brd3) !important;
  color:var(--t2) !important; font-size:0.84rem !important;
}}
[data-testid="stChatMessage"] tr:hover td {{ background:var(--soft) !important; color:var(--t1) !important; }}
[data-testid="stChatMessage"] blockquote {{
  border-left:3px solid var(--acc) !important; margin:8px 0 !important;
  padding:7px 12px !important; background:var(--soft) !important;
  border-radius:0 9px 9px 0 !important; color:var(--t2) !important; font-style:italic !important;
}}

/* ── Meta / Ref strips ── */
.msg-meta {{ display:flex; flex-wrap:wrap; align-items:center; gap:5px; margin-top:6px; }}
.meta-chip {{
  display:inline-flex; align-items:center; gap:4px; background:var(--card);
  border:1px solid var(--brd3); border-radius:99px; padding:2px 8px;
  font-size:0.59rem; font-weight:600; color:var(--t3); white-space:nowrap;
}}
.meta-chip span {{ color:var(--t2); }}
.ref-card {{
  display:flex; flex-wrap:wrap; align-items:center; gap:5px; margin-top:6px;
  padding:6px 10px; background:var(--soft); border:1px solid var(--brd3);
  border-radius:var(--rs);
}}
.ref-lbl {{ font-size:0.57rem; font-weight:700; color:var(--t3); text-transform:uppercase; letter-spacing:0.1em; margin-right:2px; }}
.ref-pill {{
  background:var(--card); border:1px solid var(--brd); border-radius:99px;
  padding:2px 7px; font-size:0.6rem; font-weight:600; color:var(--ahi); white-space:nowrap;
  transition:all 0.18s;
}}
.ref-pill:hover {{ background:var(--glow); transform:translateY(-2px); }}

/* ── Typing / Generating ── */
.typing {{
  display:flex; align-items:center; gap:5px; padding:10px 14px;
  background:var(--abub); border:1px solid var(--brd3);
  border-radius:4px 17px 17px 17px; width:fit-content; margin:3px 0;
  box-shadow:0 2px 12px rgba(0,0,0,0.22);
}}
.td {{ width:6px; height:6px; border-radius:50%; background:var(--acc); animation:tdot 1.3s ease-in-out infinite; }}
.td:nth-child(1){{ animation-delay:0s; }}
.td:nth-child(2){{ animation-delay:0.22s; }}
.td:nth-child(3){{ animation-delay:0.44s; }}
@keyframes tdot {{ 0%,55%,100%{{ opacity:0.15; transform:translateY(0); }} 28%{{ opacity:1; transform:translateY(-5px); }} }}
.tlbl {{ font-size:0.66rem; color:var(--t3); font-style:italic; margin-left:3px; }}
.ai-gen-pulse {{
  display:inline-flex; align-items:center; gap:7px; background:var(--soft);
  border:1px solid var(--brd2); border-radius:99px; padding:4px 11px;
  font-size:0.67rem; font-weight:600; color:var(--ahi); margin-bottom:7px;
  animation:pulse-bdr 1.2s ease-in-out infinite;
}}
@keyframes pulse-bdr {{ 0%,100%{{ box-shadow:0 0 0 0 var(--glow); }} 50%{{ box-shadow:0 0 0 5px transparent; }} }}
.ai-gen-dot {{ width:7px; height:7px; border-radius:50%; background:var(--acc); animation:gen-d 0.9s ease-in-out infinite alternate; }}
@keyframes gen-d {{ from{{ opacity:0.3; transform:scale(0.7); }} to{{ opacity:1; transform:scale(1.2); }} }}

/* ──────────────── CHAT INPUT ──────────────── */
[data-testid="stBottom"] {{
  background:transparent !important; border-top:none !important;
  padding:0.6rem clamp(0.7rem,4vw,1.8rem) 0.8rem !important;
  position:sticky !important; bottom:0 !important; z-index:100 !important;
}}
[data-testid="stBottom"]::before {{
  content:''; position:absolute; inset:0;
  background:linear-gradient(to top, var(--bg) 0%, transparent 100%);
  backdrop-filter:blur(18px) saturate(140%);
  border-top:1px solid var(--brd3); z-index:-1;
}}
[data-testid="stChatInput"] {{
  background:var(--inp) !important; border:1.5px solid var(--brd2) !important;
  border-radius:20px !important; max-width:820px !important; margin:0 auto !important;
  transition:border-color 0.25s, box-shadow 0.25s !important;
  box-shadow:0 4px 20px rgba(0,0,0,0.26), inset 0 1px 0 rgba(255,255,255,0.05) !important;
  backdrop-filter:blur(16px) !important;
}}
[data-testid="stChatInput"]:focus-within {{
  border-color:var(--acc) !important;
  box-shadow:0 0 0 3px var(--glow), 0 4px 24px var(--glow), inset 0 1px 0 rgba(255,255,255,0.07) !important;
}}
[data-testid="stChatInput"] textarea {{
  background:transparent !important; color:var(--t1) !important;
  font-family:var(--fb) !important; font-size:0.9rem !important;
  caret-color:var(--ahi) !important; padding:12px 15px !important;
  line-height:1.56 !important; min-height:50px !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{ color:var(--t3) !important; font-size:0.89rem !important; }}
[data-testid="stChatInput"] button {{
  background:linear-gradient(135deg, var(--alo), var(--acc)) !important;
  border:none !important; border-radius:12px !important; margin:6px !important;
  transition:opacity 0.18s, transform 0.18s, box-shadow 0.18s !important;
  box-shadow:0 2px 11px var(--glow) !important;
}}
[data-testid="stChatInput"] button:hover {{ opacity:0.88 !important; transform:scale(1.09) !important; }}
[data-testid="stChatInput"] button svg {{ fill:#fff !important; }}

/* ── Misc ── */
.stSpinner > div {{ border-top-color:var(--acc) !important; }}
hr {{ border:none !important; border-top:1px solid var(--brd3) !important; margin:9px 0 !important; }}

/* ── Responsive ── */
@media (max-width: 640px) {{
  .topbar {{ padding:0.45rem 0.8rem; }}
  .pm {{ display:none; }}
  [data-testid="stSidebar"] {{ min-width:255px !important; max-width:272px !important; }}
  .w-h {{ font-size:clamp(1.35rem,7vw,1.7rem); }}
  .w-grid {{ grid-template-columns:1fr 1fr; gap:6px; }}
  .w-orb {{ width:68px; height:68px; font-size:26px; }}
  .sg {{ grid-template-columns:1fr 1fr; }}
  [data-testid="stBottom"] {{ padding:0.5rem 0.6rem 0.7rem !important; }}
  [data-testid="stChatInput"] {{ border-radius:14px !important; }}
  [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stChatMessageContent {{ max-width:91% !important; }}
  [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stChatMessageContent {{ max-width:96% !important; }}
}}
</style>
"""

# ─────────────────────────────────────────────────────────────────────────────
#  EXPORT HELPERS
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
    model = FREE_MODEL_IDS.get(st.session_state.model_key, "unknown")
    lines = [
        "# NeuraChat AI v8.0 — Conversation Export",
        f"*{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}* · Model: `{model}`", "",
    ]
    for m in messages:
        role = "**You**" if m["role"] == "user" else "**NeuraChat AI**"
        lines += [f"### {role}", m["content"], "---", ""]
    return "\n".join(lines).encode("utf-8")

def export_pdf(messages: list) -> bytes:
    class PDF(FPDF):
        def header(self):
            self.set_font("Helvetica", "B", 17)
            self.set_text_color(109, 113, 240)
            self.cell(0, 11, "NeuraChat AI", ln=False, align="C")
            self.ln(7)
            self.set_font("Helvetica", "", 8)
            self.set_text_color(140, 145, 170)
            model = FREE_MODEL_IDS.get(st.session_state.model_key, "?")
            self.cell(0, 5, f"v8.0  ·  {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}  ·  {model}", ln=True, align="C")
            self.ln(2)
            self.set_draw_color(109, 113, 240)
            self.set_line_width(0.5)
            self.line(10, self.get_y(), self.w - 10, self.get_y())
            self.ln(5)

        def footer(self):
            self.set_y(-12)
            self.set_font("Helvetica", "I", 7)
            self.set_text_color(150, 150, 170)
            self.cell(0, 8, f"Page {self.page_no()} — NeuraChat AI v8.0", align="C")

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    for m in messages:
        is_user = m["role"] == "user"
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(60, 80, 220) if is_user else pdf.set_text_color(109, 113, 240)
        pdf.set_fill_color(240, 242, 255) if is_user else pdf.set_fill_color(245, 245, 255)
        pdf.set_draw_color(200, 205, 250)
        pdf.set_line_width(0.2)
        pdf.rect(10, pdf.get_y(), pdf.w - 20, 8, "DF")
        pdf.set_xy(10, pdf.get_y() + 1.5)
        pdf.cell(pdf.w - 20, 5, "  YOU" if is_user else "  NEURACHAT AI", ln=True)
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(30, 34, 60)
        clean = re.sub(r"```[\w]*\n?", "", m["content"])
        clean = re.sub(r"[`*#_\[\]>]+", "", clean)
        clean = re.sub(r"\n{3,}", "\n\n", clean.strip())
        safe = "".join(c if c.encode("latin-1", errors="ignore") else "?" for c in clean)
        pdf.multi_cell(0, 5.8, safe, border=0)
        pdf.ln(5)
        if m["role"] == "assistant":
            wc = len(m["content"].split())
            pdf.set_font("Helvetica", "I", 7.5)
            pdf.set_text_color(160, 165, 185)
            info = f"  {wc} words"
            if m.get("timing"):
                info += f"  ·  {m['timing']:.1f}s"
            pdf.cell(0, 4, info, ln=True)
            pdf.ln(3)
        pdf.set_draw_color(220, 222, 235)
        pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())
        pdf.ln(5)
    return bytes(pdf.output())

def export_docx(messages: list) -> bytes:
    doc = DocxDocument()
    h = doc.add_heading("NeuraChat AI v8.0 — Conversation Export", 0)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in h.runs:
        run.font.color.rgb = RGBColor(109, 113, 240)
    sub = doc.add_paragraph(
        f"Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}  ·  "
        f"Model: {FREE_MODEL_IDS.get(st.session_state.model_key, '?')}"
    )
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if sub.runs:
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
            txt = f"Words: {wc}"
            if m.get("timing"):
                txt += f"  ·  Time: {m['timing']:.1f}s"
            rm = meta.add_run(txt)
            rm.font.size = Pt(7.5)
            rm.font.color.rgb = RGBColor(160, 165, 185)
            rm.italic = True
        doc.add_paragraph()
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

# ─────────────────────────────────────────────────────────────────────────────
#  STREAMING  —  Smart Fallback
# ─────────────────────────────────────────────────────────────────────────────
def stream_response(messages: list, model_key: str, temperature: float, max_tokens: int):
    client = get_client()
    primary = FREE_MODEL_IDS.get(model_key, FREE_MODELS[0][1])
    all_ids = [m[1] for m in FREE_MODELS]
    candidates = [primary] + [mid for mid in all_ids if mid != primary]

    api_msgs = [
        {"role": "system", "content": build_system_prompt(
            st.session_state.style, st.session_state.tone)}
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
                    "X-Title": "NeuraChat AI",
                },
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            return

        except APITimeoutError:
            yield "\n\n⏱️ **Timeout.** Trying next model…\n\n"
            continue
        except RateLimitError:
            if model == candidates[-1]:
                yield "\n\n🚦 **Rate limit reached on all models.** Please wait and retry."
                return
            continue
        except APIConnectionError:
            yield "\n\n🌐 **Connection error.** Check your internet or OpenRouter status."
            return
        except Exception as e:
            err = str(e)
            if any(k in err for k in ["429","404","quota","not found","endpoint","temporarily","overloaded","unavailable"]):
                if model == candidates[-1]:
                    yield "\n\n⚠️ **All models busy.** Please retry shortly."
                    return
                continue
            yield f"\n\n⚠️ **Error:** {err}"
            return

    yield "\n\n⚠️ **All models busy.** Please retry."

# ─────────────────────────────────────────────────────────────────────────────
#  INJECT CSS
# ─────────────────────────────────────────────────────────────────────────────
th = THEMES[st.session_state.theme]
st.markdown(build_css(th), unsafe_allow_html=True)

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
<div class="st-status">
  <div class="dot {'dbz' if busy else 'don'}"></div>
  <span class="stxt">{'Generating…' if busy else 'Ready · All Models Free'}</span>
</div>
""", unsafe_allow_html=True)

    # Theme
    st.markdown('<div class="slbl">🎨 Theme</div>', unsafe_allow_html=True)
    theme_list = list(THEMES.keys())
    old_theme  = st.session_state.theme
    new_theme  = st.selectbox("Theme", theme_list,
        index=theme_list.index(st.session_state.theme), label_visibility="collapsed")
    if new_theme != old_theme:
        st.session_state.theme = new_theme
        st.rerun()

    # Model
    st.markdown('<div class="slbl">🤖 AI Model</div>', unsafe_allow_html=True)
    midx = FREE_MODEL_NAMES.index(st.session_state.model_key) \
           if st.session_state.model_key in FREE_MODEL_NAMES else 0
    st.session_state.model_key = st.selectbox(
        "Model", FREE_MODEL_NAMES, index=midx, label_visibility="collapsed")
    short_id = FREE_MODEL_IDS.get(st.session_state.model_key, "").split("/")[-1].replace(":free","")
    st.markdown(f"""
<div class="mchip">⚡ {short_id}<span class="free-badge">✓ FREE</span></div>
<div style="font-size:0.59rem;color:var(--t3);margin-top:3px;">Smart fallback — auto-retries on failure</div>
""", unsafe_allow_html=True)

    # Generation params
    st.markdown('<div class="slbl">⚙️ Generation</div>', unsafe_allow_html=True)
    st.session_state.temperature = st.slider("🌡️ Temperature", 0.0, 1.0, float(st.session_state.temperature), 0.05)
    st.session_state.max_tokens  = st.slider("📏 Max Tokens",  256, 4096, int(st.session_state.max_tokens), 64)

    # Style
    st.markdown('<div class="slbl">📝 Style & Tone</div>', unsafe_allow_html=True)
    st.session_state.style = st.selectbox("Style", list(STYLES.keys()),
        index=list(STYLES.keys()).index(st.session_state.style))
    st.session_state.tone  = st.selectbox("Tone",
        ["Professional","Friendly","Casual","Academic","Creative","Direct"])

    # Options
    st.markdown('<div class="slbl">🔧 Options</div>', unsafe_allow_html=True)
    st.session_state.show_refs   = st.toggle("📎 Source References", value=st.session_state.show_refs)
    st.session_state.show_tokens = st.toggle("📊 Token Estimate",    value=st.session_state.show_tokens)
    st.session_state.show_timing = st.toggle("⏱️ Response Time",     value=st.session_state.show_timing)

    # Stats
    st.markdown('<div class="slbl">📊 Session Stats</div>', unsafe_allow_html=True)
    uc = sum(1 for m in st.session_state.messages if m["role"] == "user")
    ac = sum(1 for m in st.session_state.messages if m["role"] == "assistant")
    tw = sum(len(m["content"].split()) for m in st.session_state.messages)
    timings = [m["timing"] for m in st.session_state.messages if m.get("timing")]
    avg_t   = sum(timings) / len(timings) if timings else 0
    st.markdown(f"""<div class="sg">
  <div class="sc"><div class="sn">{uc}</div><div class="sl">Sent</div></div>
  <div class="sc"><div class="sn">{ac}</div><div class="sl">Replies</div></div>
  <div class="sc"><div class="sn">{tw}</div><div class="sl">Words</div></div>
</div>""", unsafe_allow_html=True)
    if avg_t:
        st.markdown(
            f'<div style="font-size:0.61rem;color:var(--t3);margin-top:4px;">'
            f'Avg time: <span style="color:var(--t2)">{avg_t:.1f}s</span></div>',
            unsafe_allow_html=True)

    # Capabilities
    st.markdown('<div class="slbl">✨ Capabilities</div>', unsafe_allow_html=True)
    st.markdown("""<div class="tags">
  <span class="tag">💻 Code</span><span class="tag">📊 Data</span>
  <span class="tag">🧮 Math</span><span class="tag">✍️ Writing</span>
  <span class="tag">🔬 Science</span><span class="tag">🎨 Creative</span>
  <span class="tag">🗺️ Diagrams</span><span class="tag">📈 Analysis</span>
</div>""", unsafe_allow_html=True)

    # Export
    st.markdown('<div class="slbl">💾 Export Chat</div>', unsafe_allow_html=True)
    if st.session_state.messages:
        fname = f"neurachat_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}"
        st.download_button("📄 Text (.txt)", data=export_txt(st.session_state.messages),
            file_name=f"{fname}.txt", mime="text/plain")
        st.download_button("📝 Markdown (.md)", data=export_md(st.session_state.messages),
            file_name=f"{fname}.md", mime="text/markdown")
        if HAS_PDF:
            try:
                st.download_button("📕 PDF", data=export_pdf(st.session_state.messages),
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
        st.markdown('<span style="font-size:.7rem;color:var(--t3)">Start chatting to enable export</span>',
                    unsafe_allow_html=True)

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
mshort = FREE_MODEL_IDS.get(st.session_state.model_key, "").split("/")[-1].replace(":free","")
theme_parts = st.session_state.theme.split()
theme_label = f"{theme_parts[0]} {theme_parts[1]}" if len(theme_parts) > 1 else theme_parts[0]

st.markdown(f"""
<div class="topbar">
  <div class="tbl">
    <div class="tbico">✦</div>
    <div class="tbtitle">NeuraChat AI</div>
  </div>
  <div class="tbr">
    <div class="pill pm">⚡ {mshort}</div>
    <div class="pill pt">🎨 {st.session_state.style}</div>
    <div class="pill pt">{theme_label}</div>
    <div class="pill ps"><div class="pdot"></div>Free Unlimited</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Welcome screen
if not st.session_state.messages:
    st.markdown("""
<div class="welcome">
  <div class="w-orb">✦</div>
  <div class="w-h">Hello! What shall we<br><span>explore today?</span></div>
  <div class="w-sub">Unlimited free AI — all models, no limits.<br>Code, math, writing, research, and beyond.</div>
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
                wc   = len(msg["content"].split())
                meta = [f'<div class="meta-chip">📝 <span>{wc} words</span></div>']
                if st.session_state.show_tokens:
                    meta.append(f'<div class="meta-chip">🔢 <span>~{int(wc*1.35)} tokens</span></div>')
                if st.session_state.show_timing and msg.get("timing"):
                    meta.append(f'<div class="meta-chip">⏱️ <span>{msg["timing"]:.1f}s</span></div>')
                st.markdown(f'<div class="msg-meta">{"".join(meta)}</div>', unsafe_allow_html=True)
                if st.session_state.show_refs and msg.get("refs"):
                    pills = "".join(f'<span class="ref-pill">📎 {r}</span>' for r in msg["refs"])
                    st.markdown(f'<div class="ref-card"><span class="ref-lbl">Sources</span>{pills}</div>',
                                unsafe_allow_html=True)
    st.markdown('<div id="bottom-anchor"></div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  INPUT + STREAMING
# ─────────────────────────────────────────────────────────────────────────────
if prompt := st.chat_input(f"Ask NeuraChat… ({st.session_state.style} · {mshort})"):
    refs = get_refs(prompt) if st.session_state.show_refs else []
    st.session_state._busy = True
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        gen_ph     = st.empty()
        typing_ph  = st.empty()
        response_ph = st.empty()

        gen_ph.markdown(
            '<div class="ai-gen-pulse"><div class="ai-gen-dot"></div>Generating…</div>',
            unsafe_allow_html=True)
        typing_ph.markdown(
            '<div class="typing"><div class="td"></div><div class="td"></div>'
            '<div class="td"></div><span class="tlbl">Thinking…</span></div>',
            unsafe_allow_html=True)

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
                gen_ph.empty()
                typing_ph.empty()
                first_chunk = False
            full_reply += chunk
            buf_count  += 1
            if buf_count >= 3:
                response_ph.markdown(full_reply + "▌")
                buf_count = 0

        elapsed = time.time() - start_time
        response_ph.markdown(full_reply)

        wc   = len(full_reply.split())
        meta = [f'<div class="meta-chip">📝 <span>{wc} words</span></div>']
        if st.session_state.show_tokens:
            meta.append(f'<div class="meta-chip">🔢 <span>~{int(wc*1.35)} tokens</span></div>')
        if st.session_state.show_timing:
            meta.append(f'<div class="meta-chip">⏱️ <span>{elapsed:.1f}s</span></div>')
        st.markdown(f'<div class="msg-meta">{"".join(meta)}</div>', unsafe_allow_html=True)

        if refs:
            pills = "".join(f'<span class="ref-pill">📎 {r}</span>' for r in refs)
            st.markdown(f'<div class="ref-card"><span class="ref-lbl">Sources</span>{pills}</div>',
                        unsafe_allow_html=True)

    st.session_state._busy = False
    st.session_state.messages.append({
        "role":    "assistant",
        "content": full_reply,
        "refs":    refs,
        "timing":  elapsed,
    })