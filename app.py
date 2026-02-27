# ═══════════════════════════════════════════════════════════════════════
#  NeuraChat AI  ·  v5.0 — Refined Edition
#  Install: pip install streamlit openai python-dotenv fpdf2 python-docx
#  Run: streamlit run app.py
# ═══════════════════════════════════════════════════════════════════════

import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os, datetime, re, io

try:
    from fpdf import FPDF
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"],
)

# ── Models ──────────────────────────────────────────────────────────────
MODELS = {
    "⚡ Auto (Best)":       "openrouter/auto",
    "🌟 Gemini 2.0 Flash":  "google/gemini-2.0-flash-exp:free",
    "🧠 DeepSeek Chat V3":  "deepseek/deepseek-chat-v3-0324:free",
    "🔮 Mistral Small 3.1": "mistralai/mistral-small-3.1-24b-instruct:free",
    "🦙 LLaMA 4 Maverick":  "meta-llama/llama-4-maverick:free",
    "🎯 Qwen 2.5 72B":      "qwen/qwen-2.5-72b-instruct:free",
}

MODEL_SOURCES = {
    "openrouter/auto":                               ["OpenRouter Pool", "Multiple Sources", "Cross-validated"],
    "google/gemini-2.0-flash-exp:free":              ["Google Knowledge Graph", "Web Corpus 2024", "Gemini Training"],
    "deepseek/deepseek-chat-v3-0324:free":           ["DeepSeek Corpus", "Academic Papers", "Code Repositories"],
    "mistralai/mistral-small-3.1-24b-instruct:free": ["Common Crawl", "Wikipedia", "Books Corpus", "GitHub"],
    "meta-llama/llama-4-maverick:free":              ["Meta AI Training", "Web Corpus", "Academic Sources"],
    "qwen/qwen-2.5-72b-instruct:free":               ["Alibaba DAMO", "Global Corpus", "Scientific Literature"],
}

# ── 4 Curated Themes ────────────────────────────────────────────────────
THEMES = {
    "Snow White": {
        "emoji": "🤍", "is_light": True,
        "bg":"#f8f9fc","sbg":"#f0f2f8","hbg":"rgba(248,249,252,0.94)",
        "card":"#ffffff","card_hov":"#f0f2ff",
        "a":"#5865f2","a2":"#7c85f5","a3":"#3d4bda",
        "t1":"#111827","t2":"#4b5563","t3":"#9ca3af",
        "brd":"rgba(88,101,242,0.12)","brd2":"rgba(88,101,242,0.3)",
        "ub":"linear-gradient(135deg,#3d4bda,#5865f2)","bb":"#ffffff",
        "glow":"rgba(88,101,242,0.14)","tag":"rgba(88,101,242,0.07)",
        "code":"#eef0ff","ibg":"#ffffff","ibrd":"#dde0f8","ifoc":"#5865f2",
        "scr":"#5865f2","shad":"rgba(88,101,242,0.07)",
        "fd":"DM Sans","fb":"DM Sans",
        "fu":"https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700;9..40,800&display=swap",
    },
    "Slate Night": {
        "emoji": "🌙", "is_light": False,
        "bg":"#0f1117","sbg":"#090c12","hbg":"rgba(15,17,23,0.94)",
        "card":"#171b26","card_hov":"#1d2232",
        "a":"#818cf8","a2":"#a5b4fc","a3":"#6366f1",
        "t1":"#e8eaf6","t2":"#9fa8c8","t3":"#4a5080",
        "brd":"rgba(129,140,248,0.11)","brd2":"rgba(129,140,248,0.28)",
        "ub":"linear-gradient(135deg,#5c60d4,#818cf8)","bb":"#171b26",
        "glow":"rgba(129,140,248,0.16)","tag":"rgba(129,140,248,0.09)",
        "code":"#0c0f17","ibg":"#171b26","ibrd":"rgba(129,140,248,0.22)","ifoc":"#818cf8",
        "scr":"#818cf8","shad":"rgba(0,0,0,0.35)",
        "fd":"Outfit","fb":"Outfit",
        "fu":"https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap",
    },
    "Warm Cream": {
        "emoji": "☕", "is_light": True,
        "bg":"#faf7f2","sbg":"#f4efe6","hbg":"rgba(250,247,242,0.94)",
        "card":"#ffffff","card_hov":"#fef3e2",
        "a":"#c2410c","a2":"#ea580c","a3":"#9a3412",
        "t1":"#1c1008","t2":"#6b4226","t3":"#b08060",
        "brd":"rgba(194,65,12,0.14)","brd2":"rgba(194,65,12,0.32)",
        "ub":"linear-gradient(135deg,#9a3412,#c2410c)","bb":"#ffffff",
        "glow":"rgba(194,65,12,0.14)","tag":"rgba(194,65,12,0.07)",
        "code":"#f4efe6","ibg":"#ffffff","ibrd":"#e8d8c4","ifoc":"#c2410c",
        "scr":"#c2410c","shad":"rgba(100,40,10,0.07)",
        "fd":"Lora","fb":"Source Sans 3",
        "fu":"https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;0,700;1,400&family=Source+Sans+3:wght@300;400;500;600;700&display=swap",
    },
    "Midnight Pro": {
        "emoji": "🖤", "is_light": False,
        "bg":"#0a0a0a","sbg":"#050505","hbg":"rgba(10,10,10,0.97)",
        "card":"#141414","card_hov":"#1a1a1a",
        "a":"#e8e8e8","a2":"#ffffff","a3":"#aaaaaa",
        "t1":"#f0f0f0","t2":"#888888","t3":"#444444",
        "brd":"rgba(255,255,255,0.07)","brd2":"rgba(255,255,255,0.15)",
        "ub":"linear-gradient(135deg,#2a2a2a,#555555)","bb":"#141414",
        "glow":"rgba(255,255,255,0.06)","tag":"rgba(255,255,255,0.05)",
        "code":"#050505","ibg":"#141414","ibrd":"rgba(255,255,255,0.12)","ifoc":"#e8e8e8",
        "scr":"#444444","shad":"rgba(0,0,0,0.5)",
        "fd":"Sora","fb":"Sora",
        "fu":"https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&display=swap",
    },
}

STYLES = {
    "Balanced":  "Clear, balanced, professional. Use headers and concise paragraphs.",
    "Concise":   "Ultra brief. Key points only. No filler. Bullet points preferred.",
    "Detailed":  "Comprehensive and thorough with examples, edge cases, and full context.",
    "Technical": "Deep technical precision. Include code, formulas, implementation details.",
    "Friendly":  "Warm, conversational, accessible — like explaining to a smart friend.",
    "Creative":  "Vivid, imaginative, surprising. Push beyond conventional answers.",
}

REF_TEMPLATES = {
    "code":    ["Stack Overflow","GitHub Repos","Official Documentation","MDN Web Docs"],
    "math":    ["Wolfram Alpha","ArXiv Papers","Mathematical Literature","Khan Academy"],
    "science": ["PubMed Database","Scientific American","Nature Journals","Wikipedia Science"],
    "writing": ["Literary Corpus","Style Guides","Professional Examples"],
    "general": ["Wikipedia","Web Corpus 2024","Academic Sources","News Archives"],
    "analysis":["Statistical Databases","Research Papers","Industry Reports"],
    "history": ["Historical Archives","Encyclopedia Britannica","Academic Journals"],
}

def detect_topic(text):
    t = text.lower()
    if any(w in t for w in ["code","python","javascript","function","bug","error","api","sql","html","css","import","class","def ","const ","git","program"]): return "code"
    if any(w in t for w in ["math","equation","calculus","algebra","integral","derivative","formula","geometry","statistics","probability","matrix"]): return "math"
    if any(w in t for w in ["science","physics","chemistry","biology","molecule","atom","quantum","evolution","genetics"]): return "science"
    if any(w in t for w in ["write","essay","story","poem","email","letter","article","blog","creative","fiction"]): return "writing"
    if any(w in t for w in ["analyze","compare","evaluate","assess","review","examine","research","investigate"]): return "analysis"
    if any(w in t for w in ["history","historical","war","ancient","civilization","century","empire","revolution"]): return "history"
    return "general"

def get_refs(prompt, model_id):
    topic = detect_topic(prompt)
    topic_refs = REF_TEMPLATES.get(topic, REF_TEMPLATES["general"])[:3]
    model_refs = MODEL_SOURCES.get(model_id, ["Training Data"])[:2]
    combined = list(dict.fromkeys(topic_refs + model_refs))
    return combined[:4]

def make_sys(style, tone):
    return f"""You are NeuraChat — a premium intelligent AI assistant.

STYLE: {STYLES.get(style, STYLES['Balanced'])}
TONE: {tone}

RULES:
- Use proper markdown: ## headers, **bold**, `code`, ```language blocks
- For diagrams use ```mermaid syntax
- NO preamble like "Great question!" — start directly
- Be accurate, structured, genuinely useful
- Match user's language (Hindi/English/etc.) automatically"""

# ── Page ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="NeuraChat AI", page_icon="✦", layout="wide", initial_sidebar_state="expanded")

for k, v in {
    "messages":[], "theme":"Slate Night","model_key":"⚡ Auto (Best)",
    "style":"Balanced","tone":"Professional","temp":0.7,
    "started":datetime.datetime.now().strftime("%I:%M %p"),
    "show_refs":True,
}.items():
    if k not in st.session_state: st.session_state[k] = v

T = THEMES[st.session_state.theme]

# ── CSS ─────────────────────────────────────────────────────────────────
def build_css(T):
    L = T["is_light"]
    inner_shadow = "inset 0 1px 0 rgba(255,255,255,0.6)" if L else "inset 0 1px 0 rgba(255,255,255,0.06)"
    return f"""
<style>
@import url('{T["fu"]}');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
:root{{
  --bg:{T['bg']};--sbg:{T['sbg']};--hbg:{T['hbg']};
  --card:{T['card']};--ch:{T['card_hov']};
  --a:{T['a']};--a2:{T['a2']};--a3:{T['a3']};
  --t1:{T['t1']};--t2:{T['t2']};--t3:{T['t3']};
  --brd:{T['brd']};--brd2:{T['brd2']};
  --glow:{T['glow']};--tag:{T['tag']};
  --code:{T['code']};--ibg:{T['ibg']};
  --ibrd:{T['ibrd']};--ifoc:{T['ifoc']};
  --scr:{T['scr']};--shad:{T['shad']};
  --fd:'{T['fd']}',system-ui,sans-serif;
  --fb:'{T['fb']}',system-ui,sans-serif;
  --mono:'JetBrains Mono',monospace;
  --r:14px;--rs:10px;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
html,body,.stApp{{background:var(--bg)!important;font-family:var(--fb)!important;color:var(--t1)!important;overflow-x:hidden;}}
#MainMenu,footer,header,.stDeployButton,[data-testid="stToolbar"]{{display:none!important;}}
.block-container{{padding:0!important;max-width:100%!important;}}
::-webkit-scrollbar{{width:4px;height:4px;}}
::-webkit-scrollbar-track{{background:transparent;}}
::-webkit-scrollbar-thumb{{background:var(--scr)44;border-radius:99px;}}
::-webkit-scrollbar-thumb:hover{{background:var(--scr)99;}}

/* SIDEBAR */
[data-testid="stSidebar"]{{background:var(--sbg)!important;border-right:1px solid var(--brd)!important;min-width:270px!important;max-width:284px!important;}}
[data-testid="stSidebar"]>div:first-child{{padding:1.4rem 1.15rem 2rem!important;height:100vh;overflow-y:auto;overflow-x:hidden;}}

.brand{{display:flex;align-items:center;gap:12px;padding-bottom:1.2rem;margin-bottom:1.4rem;border-bottom:1px solid var(--brd);}}
.b-ico{{width:42px;height:42px;background:linear-gradient(135deg,var(--a3),var(--a));border-radius:14px;display:grid;place-items:center;font-size:19px;flex-shrink:0;box-shadow:0 4px 20px var(--glow);animation:pulse 4s ease-in-out infinite;}}
@keyframes pulse{{0%,100%{{box-shadow:0 4px 18px var(--glow);}}50%{{box-shadow:0 6px 36px var(--glow);transform:scale(1.05);}}}}
.b-name{{font-family:var(--fd);font-size:1.08rem;font-weight:800;color:var(--t1);letter-spacing:-0.02em;}}
.b-ver{{font-size:0.58rem;color:var(--t3);font-weight:700;letter-spacing:0.1em;text-transform:uppercase;margin-top:2px;}}
.slbl{{font-size:0.6rem;font-weight:700;color:var(--t3);text-transform:uppercase;letter-spacing:0.12em;margin:16px 0 7px;}}
.status{{display:flex;align-items:center;gap:8px;padding:7px 13px;background:var(--tag);border:1px solid var(--brd);border-radius:99px;width:fit-content;}}
.dot{{width:7px;height:7px;border-radius:50%;}}
.don{{background:#22c55e;box-shadow:0 0 8px #22c55e99;animation:blink 2.5s infinite;}}
.dbz{{background:#f59e0b;box-shadow:0 0 8px #f59e0b99;animation:blink 0.7s infinite;}}
@keyframes blink{{0%,100%{{opacity:1;}}50%{{opacity:0.18;}}}}
.stxt{{font-size:0.74rem;font-weight:600;color:var(--t2);}}
.mchip{{background:var(--tag);border:1px solid var(--brd);border-radius:var(--rs);padding:7px 11px;font-family:var(--mono);font-size:0.68rem;color:var(--a);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-top:5px;}}
.sg{{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:6px;}}
.sc{{background:var(--card);border:1px solid var(--brd);border-radius:var(--rs);padding:10px 8px;text-align:center;transition:all 0.2s;}}
.sc:hover{{border-color:var(--a);transform:translateY(-2px);box-shadow:0 6px 20px var(--glow);}}
.sn{{font-family:var(--fd);font-size:1.45rem;font-weight:800;background:linear-gradient(135deg,var(--a),var(--a2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1;}}
.sl{{font-size:0.58rem;color:var(--t3);margin-top:3px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;}}
.tags{{display:flex;flex-wrap:wrap;gap:5px;margin-top:7px;}}
.tag{{background:var(--tag);border:1px solid var(--brd);color:var(--a);border-radius:99px;padding:4px 10px;font-size:0.64rem;font-weight:600;transition:all 0.18s;cursor:default;}}
.tag:hover{{background:var(--glow);border-color:var(--a);transform:translateY(-2px);box-shadow:0 4px 14px var(--glow);}}

[data-testid="stSidebar"] .stSelectbox>div>div{{background:var(--card)!important;border:1px solid var(--brd)!important;border-radius:var(--rs)!important;color:var(--t1)!important;font-size:0.82rem!important;font-family:var(--fb)!important;transition:border-color .2s!important;}}
[data-testid="stSidebar"] .stSelectbox>div>div:hover{{border-color:var(--a)!important;}}
[data-testid="stSidebar"] .stSelectbox li{{background:var(--card)!important;color:var(--t1)!important;}}
[data-testid="stSidebar"] .stSelectbox label{{color:var(--t2)!important;font-size:0.75rem!important;font-weight:600!important;}}
[data-testid="stSidebar"] .stSlider [data-baseweb="thumb"]{{background:var(--a)!important;border:3px solid var(--sbg)!important;box-shadow:0 0 14px var(--glow)!important;}}
[data-testid="stSidebar"] .stSlider [data-baseweb="track-background"]{{background:var(--brd2)!important;}}
[data-testid="stSidebar"] .stSlider [data-baseweb="track-fill"]{{background:linear-gradient(90deg,var(--a3),var(--a))!important;}}
[data-testid="stSidebar"] .stSlider label{{color:var(--t2)!important;font-size:0.74rem!important;}}
[data-testid="stSidebar"] .stToggle label{{color:var(--t2)!important;font-size:0.78rem!important;}}

.stButton>button{{background:var(--tag)!important;border:1px solid var(--brd2)!important;color:var(--a)!important;border-radius:var(--rs)!important;font-family:var(--fb)!important;font-size:0.8rem!important;font-weight:600!important;width:100%!important;padding:0.52rem 0.9rem!important;transition:all .2s!important;}}
.stButton>button:hover{{background:var(--glow)!important;border-color:var(--a)!important;box-shadow:0 4px 18px var(--glow)!important;transform:translateY(-2px)!important;color:var(--t1)!important;}}
[data-testid="stDownloadButton"]>button{{background:var(--tag)!important;border:1px solid var(--brd2)!important;color:var(--a)!important;border-radius:var(--rs)!important;font-family:var(--fb)!important;font-size:0.78rem!important;font-weight:600!important;width:100%!important;padding:0.5rem 0.8rem!important;transition:all .2s!important;}}
[data-testid="stDownloadButton"]>button:hover{{background:var(--glow)!important;border-color:var(--a)!important;transform:translateY(-2px)!important;}}

.sb-footer{{font-size:0.62rem;color:var(--t3);text-align:center;line-height:1.9;margin-top:16px;padding-top:14px;border-top:1px solid var(--brd);}}

/* TOP BAR */
.topbar{{background:var(--hbg);backdrop-filter:blur(28px) saturate(180%);-webkit-backdrop-filter:blur(28px) saturate(180%);border-bottom:1px solid var(--brd);padding:0.68rem 2rem;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:999;}}
.tbl{{display:flex;align-items:center;gap:11px;}}
.tbico{{width:32px;height:32px;background:linear-gradient(135deg,var(--a3),var(--a));border-radius:10px;display:grid;place-items:center;font-size:14px;box-shadow:0 2px 12px var(--glow);}}
.tbtitle{{font-family:var(--fd);font-size:1rem;font-weight:800;color:var(--t1);letter-spacing:-0.02em;}}
.tbr{{display:flex;align-items:center;gap:7px;flex-wrap:wrap;}}
.pill{{border-radius:99px;padding:5px 12px;font-size:0.67rem;font-weight:600;display:flex;align-items:center;gap:5px;border:1px solid var(--brd);white-space:nowrap;transition:all .2s;}}
.pill:hover{{border-color:var(--a);box-shadow:0 2px 10px var(--glow);}}
.pm{{background:var(--tag);color:var(--a);font-family:var(--mono);font-size:0.61rem;}}
.pt{{background:var(--card);color:var(--t2);}}
.ps{{background:rgba(34,197,94,0.1);border-color:rgba(34,197,94,0.3)!important;color:#22c55e;}}
.pdot{{width:5px;height:5px;border-radius:50%;background:currentColor;animation:blink 2s infinite;}}

/* MAIN WRAP */
.main-wrap{{max-width:900px;margin:0 auto;padding:1.4rem clamp(1rem,4vw,2.5rem) 0.5rem;}}

/* WELCOME */
.welcome{{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:62vh;padding:3rem 1.5rem 2rem;text-align:center;}}
.worb{{width:88px;height:88px;background:linear-gradient(135deg,var(--a3),var(--a),var(--a2));border-radius:28px;display:grid;place-items:center;font-size:34px;margin-bottom:1.85rem;box-shadow:0 8px 50px var(--glow);animation:wfloat 5s ease-in-out infinite;position:relative;}}
.worb::after{{content:'';position:absolute;inset:-5px;border-radius:33px;background:linear-gradient(135deg,var(--a),var(--a3));z-index:-1;opacity:0.22;filter:blur(10px);animation:wring 5s ease-in-out infinite;}}
@keyframes wfloat{{0%,100%{{transform:translateY(0);}}50%{{transform:translateY(-12px);}}}}
@keyframes wring{{0%,100%{{opacity:0.18;transform:scale(1);}}50%{{opacity:0.45;transform:scale(1.18);}}}}
.wh{{font-family:var(--fd);font-size:clamp(1.8rem,4vw,2.5rem);font-weight:800;line-height:1.12;color:var(--t1);margin-bottom:0.8rem;animation:fu .6s ease forwards;letter-spacing:-0.02em;}}
.wh span{{background:linear-gradient(120deg,var(--a3),var(--a));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}}
.ws{{font-size:0.95rem;color:var(--t2);max-width:420px;line-height:1.75;margin-bottom:2.4rem;animation:fu .75s .1s ease both;}}
@keyframes fu{{from{{opacity:0;transform:translateY(14px);}}to{{opacity:1;transform:translateY(0);}}}}
.wgrid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;width:100%;max-width:620px;animation:fu .9s .2s ease both;}}
.wcard{{background:var(--card);border:1px solid var(--brd);border-radius:var(--r);padding:14px 13px;text-align:left;transition:all .22s;}}
.wcard:hover{{border-color:var(--a);transform:translateY(-5px);box-shadow:0 12px 36px var(--glow);background:var(--ch);}}
.wci{{font-size:1.35rem;margin-bottom:7px;}}
.wct{{font-size:0.79rem;font-weight:700;color:var(--t1);margin-bottom:3px;}}
.wcs{{font-size:0.7rem;color:var(--t2);line-height:1.5;}}

/* CHAT */
[data-testid="chatAvatarIcon-user"],[data-testid="chatAvatarIcon-assistant"]{{display:none!important;}}
[data-testid="stChatMessage"]{{background:transparent!important;border:none!important;padding:.25rem 0!important;}}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]){{justify-content:flex-end!important;}}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stChatMessageContent{{background:{T['ub']}!important;border-radius:22px 22px 5px 22px!important;color:#fff!important;max-width:68%!important;margin-left:auto!important;padding:11px 17px!important;font-size:.91rem!important;line-height:1.65!important;box-shadow:0 4px 22px var(--glow)!important;border:none!important;animation:sr .28s cubic-bezier(.25,.46,.45,.94)!important;}}
@keyframes sr{{from{{opacity:0;transform:translateX(18px) scale(.96);}}to{{opacity:1;transform:none;}}}}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stChatMessageContent{{background:{T['bb']}!important;border:1px solid var(--brd)!important;border-radius:5px 22px 22px 22px!important;color:var(--t1)!important;max-width:82%!important;padding:13px 18px!important;font-size:.91rem!important;line-height:1.78!important;box-shadow:0 2px 18px var(--shad)!important;animation:sl .28s cubic-bezier(.25,.46,.45,.94)!important;}}
@keyframes sl{{from{{opacity:0;transform:translateX(-18px) scale(.96);}}to{{opacity:1;transform:none;}}}}
[data-testid="stChatMessage"] h1,[data-testid="stChatMessage"] h2,[data-testid="stChatMessage"] h3{{font-family:var(--fd)!important;color:var(--a)!important;margin:15px 0 6px!important;font-weight:700!important;letter-spacing:-0.01em!important;}}
[data-testid="stChatMessage"] h1{{font-size:1.25em!important;}}[data-testid="stChatMessage"] h2{{font-size:1.1em!important;}}[data-testid="stChatMessage"] h3{{font-size:1em!important;}}
[data-testid="stChatMessage"] p{{margin-bottom:7px!important;}}
[data-testid="stChatMessage"] ul,[data-testid="stChatMessage"] ol{{padding-left:20px!important;margin:8px 0!important;}}
[data-testid="stChatMessage"] li{{margin-bottom:4px!important;color:var(--t2)!important;}}
.stChatMessage strong{{color:var(--t1)!important;font-weight:700!important;}}
.stChatMessage em{{color:var(--t2)!important;}}
.stChatMessage code{{background:var(--code)!important;border:1px solid var(--brd)!important;border-radius:6px!important;padding:2px 7px!important;font-size:.84em!important;color:var(--a)!important;font-family:var(--mono)!important;font-weight:500!important;}}
.stChatMessage pre{{background:var(--code)!important;border:1px solid var(--brd)!important;border-left:3px solid var(--a)!important;border-radius:12px!important;padding:15px!important;overflow-x:auto!important;margin:11px 0!important;}}
.stChatMessage pre code{{background:transparent!important;border:none!important;padding:0!important;color:var(--t1)!important;font-size:.85em!important;}}
.stChatMessage table{{border-collapse:collapse!important;width:100%!important;margin:13px 0!important;border-radius:var(--rs)!important;overflow:hidden!important;}}
.stChatMessage th{{background:var(--tag)!important;color:var(--a)!important;padding:9px 13px!important;font-size:.75rem!important;font-weight:700!important;text-transform:uppercase!important;letter-spacing:.06em!important;text-align:left!important;border-bottom:1px solid var(--brd)!important;}}
.stChatMessage td{{padding:8px 13px!important;border-bottom:1px solid var(--brd)!important;color:var(--t2)!important;font-size:.87rem!important;}}
.stChatMessage tr:hover td{{background:var(--tag)!important;color:var(--t1)!important;}}
.stChatMessage tr:last-child td{{border-bottom:none!important;}}
.stChatMessage blockquote{{border-left:3px solid var(--a)!important;margin:11px 0!important;padding:10px 15px!important;background:var(--tag)!important;border-radius:0 10px 10px 0!important;color:var(--t2)!important;font-style:italic!important;}}

/* REFERENCE CARD */
.ref-card{{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin-top:10px;padding:9px 13px;background:var(--tag);border:1px solid var(--brd);border-radius:var(--rs);animation:fu .5s ease both;}}
.ref-lbl{{font-size:.63rem;font-weight:700;color:var(--t3);text-transform:uppercase;letter-spacing:.1em;margin-right:2px;white-space:nowrap;}}
.ref-pill{{background:var(--card);border:1px solid var(--brd2);border-radius:99px;padding:3px 10px;font-size:.65rem;font-weight:600;color:var(--a);white-space:nowrap;transition:all .18s;cursor:default;}}
.ref-pill:hover{{background:var(--glow);transform:translateY(-2px);box-shadow:0 4px 12px var(--glow);}}

/* TYPING */
.typing{{display:flex;align-items:center;gap:6px;padding:12px 17px;background:{T['bb']};border:1px solid var(--brd);border-radius:5px 20px 20px 20px;width:fit-content;margin:3px 0;box-shadow:0 2px 12px var(--shad);}}
.td{{width:7px;height:7px;border-radius:50%;background:var(--a);animation:tb 1.3s ease-in-out infinite;}}
.td:nth-child(1){{animation-delay:0s;}}.td:nth-child(2){{animation-delay:.22s;}}.td:nth-child(3){{animation-delay:.44s;}}
@keyframes tb{{0%,55%,100%{{opacity:.18;transform:translateY(0);}}28%{{opacity:1;transform:translateY(-6px);}}}}
.tlbl{{font-size:.71rem;color:var(--t3);font-style:italic;margin-left:4px;}}

/* INPUT — Claude-style elegant */
[data-testid="stBottom"]{{
  background:var(--hbg)!important;
  border-top:1px solid var(--brd)!important;
  padding:.85rem clamp(1rem,5vw,2.5rem) 1rem!important;
  backdrop-filter:blur(24px);
}}
[data-testid="stChatInput"]{{
  background:var(--ibg)!important;
  border:1.5px solid var(--ibrd)!important;
  border-radius:20px!important;
  max-width:880px!important;margin:0 auto!important;
  transition:border-color .25s,box-shadow .25s!important;
  box-shadow:0 2px 18px var(--shad),{inner_shadow}!important;
}}
[data-testid="stChatInput"]:focus-within{{
  border-color:var(--ifoc)!important;
  box-shadow:0 0 0 3px var(--glow),0 4px 28px var(--glow)!important;
}}
[data-testid="stChatInput"] textarea{{
  background:transparent!important;color:var(--t1)!important;
  font-family:var(--fb)!important;font-size:.94rem!important;font-weight:400!important;
  caret-color:var(--ifoc)!important;
  padding:14px 18px!important;line-height:1.6!important;min-height:52px!important;
  letter-spacing:.002em!important;
}}
[data-testid="stChatInput"] textarea::placeholder{{
  color:var(--t3)!important;font-style:normal!important;font-size:.93rem!important;
  font-family:var(--fb)!important;
}}
[data-testid="stChatInput"] button{{
  background:linear-gradient(135deg,var(--a3),var(--a))!important;
  border:none!important;border-radius:14px!important;margin:7px!important;
  transition:opacity .18s,transform .18s,box-shadow .18s!important;
  box-shadow:0 2px 12px var(--glow)!important;
}}
[data-testid="stChatInput"] button:hover{{opacity:.88!important;transform:scale(1.08)!important;box-shadow:0 4px 22px var(--glow)!important;}}
[data-testid="stChatInput"] button svg{{fill:#fff!important;}}

.stSpinner>div{{border-top-color:var(--a)!important;}}
hr{{border:none!important;border-top:1px solid var(--brd)!important;margin:13px 0!important;}}

@media(max-width:768px){{
  .topbar{{padding:.65rem 1rem;}}
  .pm,.pt{{display:none;}}
  [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stChatMessageContent{{max-width:88%!important;}}
  [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stChatMessageContent{{max-width:96%!important;}}
  .wgrid{{grid-template-columns:1fr 1fr;}}
}}
@media(max-width:480px){{.wgrid{{grid-template-columns:1fr;}}}}
</style>"""

st.markdown(build_css(T), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  EXPORT FUNCTIONS
# ══════════════════════════════════════════════════════════════════════
def export_txt(messages):
    lines = ["NeuraChat AI — Conversation Export",
             f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", "="*60, ""]
    for m in messages:
        role = "You" if m["role"]=="user" else "NeuraChat"
        lines += [f"[{role}]", m["content"], ""]
    return "\n".join(lines).encode("utf-8")

def export_pdf(messages):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica","B",16)
    pdf.cell(0,10,"NeuraChat AI - Conversation Export",ln=True,align="C")
    pdf.set_font("Helvetica","",9)
    pdf.set_text_color(120,120,120)
    pdf.cell(0,6,f"Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",ln=True,align="C")
    pdf.ln(5)
    for m in messages:
        role = "You" if m["role"]=="user" else "NeuraChat AI"
        pdf.set_font("Helvetica","B",10)
        if m["role"]=="assistant": pdf.set_text_color(88,101,242)
        else: pdf.set_text_color(50,50,50)
        pdf.cell(0,7,f"[{role}]",ln=True)
        pdf.set_font("Helvetica","",9)
        pdf.set_text_color(30,30,30)
        clean = re.sub(r'[`*#_\[\]]+','',m["content"])
        clean = re.sub(r'\n{3,}','\n\n',clean)
        clean = clean.encode('latin-1','replace').decode('latin-1')
        pdf.multi_cell(0,5.5,clean)
        pdf.ln(4)
    return bytes(pdf.output())

def export_docx(messages):
    doc = Document()
    h = doc.add_heading("NeuraChat AI — Conversation Export",0)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in h.runs: r.font.color.rgb = RGBColor(88,101,242)
    sub = doc.add_paragraph(f"Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.runs[0].font.size = Pt(9)
    sub.runs[0].font.color.rgb = RGBColor(130,130,130)
    doc.add_paragraph()
    for m in messages:
        role = "You" if m["role"]=="user" else "NeuraChat AI"
        p = doc.add_paragraph()
        r = p.add_run(f"[{role}]")
        r.bold = True; r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(88,101,242) if m["role"]=="assistant" else RGBColor(50,50,50)
        clean = re.sub(r'[`*#_]+','',m["content"])
        dp = doc.add_paragraph(clean)
        dp.runs[0].font.size = Pt(10) if dp.runs else None
        doc.add_paragraph()
    buf = io.BytesIO(); doc.save(buf); return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════
#  STREAM RESPONSE
# ══════════════════════════════════════════════════════════════════════
def stream_response(messages, model_key):
    model_id = MODELS[model_key]
    fallbacks = [v for v in MODELS.values() if v != model_id]
    api_msgs = [{"role":"system","content":make_sys(st.session_state.style,st.session_state.tone)}] + messages
    for model in [model_id]+fallbacks:
        try:
            stream = client.chat.completions.create(
                model=model, messages=api_msgs, max_tokens=4096,
                temperature=st.session_state.temp, stream=True,
                extra_headers={"HTTP-Referer":"https://neurachat.ai","X-Title":"NeuraChat AI"}
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            return
        except Exception as e:
            err = str(e)
            if any(k in err for k in ["429","404","rate","quota","not found","endpoint","temporarily","overloaded"]): continue
            yield f"\n\n⚠️ **Error:** {err}"; return
    yield "\n\n⚠️ All models busy — please retry."


# ══════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    busy = st.session_state.get("_busy",False)
    st.markdown(f"""
    <div class="brand">
      <div class="b-ico">{T['emoji']}</div>
      <div><div class="b-name">NeuraChat AI</div><div class="b-ver">v5.0 · Refined</div></div>
    </div>
    <div class="status">
      <div class="dot {'dbz' if busy else 'don'}"></div>
      <span class="stxt">{'Thinking…' if busy else 'Ready'}</span>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="slbl">🎨 Theme</div>', unsafe_allow_html=True)
    tlist = list(THEMES.keys())
    tlbls = [f"{THEMES[t]['emoji']} {t}" for t in tlist]
    chosen = st.selectbox("Theme", tlbls, index=tlist.index(st.session_state.theme), label_visibility="collapsed")
    new_t = chosen.split(" ",1)[1]
    if new_t != st.session_state.theme:
        st.session_state.theme = new_t; st.rerun()

    st.markdown('<div class="slbl">🤖 Model</div>', unsafe_allow_html=True)
    mkeys = list(MODELS.keys())
    midx = mkeys.index(st.session_state.model_key) if st.session_state.model_key in mkeys else 0
    st.session_state.model_key = st.selectbox("Model", mkeys, index=midx, label_visibility="collapsed")
    mshort = MODELS[st.session_state.model_key].split("/")[-1].replace(":free","")
    st.markdown(f'<div class="mchip">⚡ {mshort}</div>', unsafe_allow_html=True)

    st.markdown('<div class="slbl">⚙️ Response</div>', unsafe_allow_html=True)
    st.session_state.style = st.selectbox("Style", list(STYLES.keys()),
        index=list(STYLES.keys()).index(st.session_state.style))
    st.session_state.tone = st.selectbox("Tone", ["Professional","Friendly","Casual","Academic","Creative","Direct"])
    st.session_state.temp = st.slider("🌡️ Creativity", 0.0, 1.0, st.session_state.temp, 0.05)
    st.session_state.show_refs = st.toggle("📎 Show Source References", value=st.session_state.show_refs)

    st.markdown('<div class="slbl">📊 Session</div>', unsafe_allow_html=True)
    uc = len([m for m in st.session_state.messages if m["role"]=="user"])
    ac = len([m for m in st.session_state.messages if m["role"]=="assistant"])
    st.markdown(f"""<div class="sg">
      <div class="sc"><div class="sn">{uc}</div><div class="sl">Sent</div></div>
      <div class="sc"><div class="sn">{ac}</div><div class="sl">Replies</div></div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="slbl">✨ Capabilities</div>', unsafe_allow_html=True)
    st.markdown("""<div class="tags">
      <span class="tag">💻 Code</span><span class="tag">📊 Diagrams</span>
      <span class="tag">🧮 Math</span><span class="tag">✍️ Writing</span>
      <span class="tag">🔬 Science</span><span class="tag">🌐 Any Topic</span>
      <span class="tag">🎨 Creative</span><span class="tag">📈 Analysis</span>
    </div>""", unsafe_allow_html=True)

    # Export
    st.markdown('<div class="slbl">💾 Export Conversation</div>', unsafe_allow_html=True)
    if st.session_state.messages:
        fname = f"neurachat_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}"
        st.download_button("📄 Notepad (.txt)", data=export_txt(st.session_state.messages), file_name=f"{fname}.txt", mime="text/plain")
        if HAS_PDF:
            try:
                st.download_button("📕 PDF Document", data=export_pdf(st.session_state.messages), file_name=f"{fname}.pdf", mime="application/pdf")
            except: st.caption("⚠️ PDF error")
        if HAS_DOCX:
            try:
                st.download_button("📘 Word Document (.docx)", data=export_docx(st.session_state.messages), file_name=f"{fname}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            except: st.caption("⚠️ Word error")
    else:
        st.markdown('<span style="font-size:.74rem;color:var(--t3)">Start chatting to enable export</span>', unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🗑️ Clear Conversation"): st.session_state.messages = []; st.rerun()
    st.markdown(f"""<div class="sb-footer">✦ NeuraChat AI · v5.0<br>{T['emoji']} {st.session_state.theme} · OpenRouter<br>Session · {st.session_state.started}</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════
mshort = MODELS[st.session_state.model_key].split("/")[-1].replace(":free","")
st.markdown(f"""
<div class="topbar">
  <div class="tbl"><div class="tbico">✦</div><div class="tbtitle">NeuraChat AI</div></div>
  <div class="tbr">
    <div class="pill pm">⚡ {mshort}</div>
    <div class="pill pt">{T['emoji']} {st.session_state.theme}</div>
    <div class="pill ps"><div class="pdot"></div>Online</div>
  </div>
</div>""", unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown(f"""
    <div class="welcome">
      <div class="worb">{T['emoji']}</div>
      <div class="wh">Hello! What shall we<br><span>explore today?</span></div>
      <div class="ws">Ask anything — code, math, writing, research, analysis,<br>creative work, or any topic you can imagine.</div>
      <div class="wgrid">
        <div class="wcard"><div class="wci">💻</div><div class="wct">Write & Debug Code</div><div class="wcs">Any language, clean & explained</div></div>
        <div class="wcard"><div class="wci">📊</div><div class="wct">Diagrams & Flowcharts</div><div class="wcs">Mermaid charts instantly</div></div>
        <div class="wcard"><div class="wci">🧮</div><div class="wct">Math & Science</div><div class="wcs">Step-by-step solutions</div></div>
        <div class="wcard"><div class="wci">✍️</div><div class="wct">Writing & Essays</div><div class="wcs">Polished, professional output</div></div>
        <div class="wcard"><div class="wci">🔍</div><div class="wct">Deep Research</div><div class="wcs">Comprehensive topic analysis</div></div>
        <div class="wcard"><div class="wci">🎨</div><div class="wct">Creative Work</div><div class="wcs">Stories, ideas, brainstorming</div></div>
      </div>
    </div>""", unsafe_allow_html=True)

# Render existing history
with st.container():
    st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"]=="assistant" and st.session_state.show_refs:
                refs = msg.get("refs",[])
                if refs:
                    pills = "".join([f'<span class="ref-pill">📎 {r}</span>' for r in refs])
                    st.markdown(f'<div class="ref-card"><span class="ref-lbl">Sources</span>{pills}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Input
if prompt := st.chat_input(f"Message NeuraChat… ({st.session_state.style} · {st.session_state.tone})"):
    model_id = MODELS[st.session_state.model_key]
    refs = get_refs(prompt, model_id) if st.session_state.show_refs else []

    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        tph = st.empty()
        tph.markdown("""<div class="typing"><div class="td"></div><div class="td"></div><div class="td"></div><span class="tlbl">Thinking…</span></div>""", unsafe_allow_html=True)
        rph = st.empty()
        full = ""; first = True; buf = 0

        for chunk in stream_response(st.session_state.messages, st.session_state.model_key):
            if first: tph.empty(); first = False
            full += chunk; buf += 1
            if buf >= 4: rph.markdown(full+"▌"); buf = 0

        rph.markdown(full)

        if refs and st.session_state.show_refs:
            pills = "".join([f'<span class="ref-pill">📎 {r}</span>' for r in refs])
            st.markdown(f'<div class="ref-card"><span class="ref-lbl">Sources</span>{pills}</div>', unsafe_allow_html=True)

    st.session_state.messages.append({"role":"assistant","content":full,"refs":refs})