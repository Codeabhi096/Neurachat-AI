# ═══════════════════════════════════════════════════════════════════════
#  NeuraChat AI  ·  Streaming Edition
#  Features : Real-time streaming · 6 Portfolio Themes · Elegant UI
#  Run      : streamlit run app.py
# ═══════════════════════════════════════════════════════════════════════

import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os, datetime

# ── Env ───────────────────────────────────────────────────────────────
load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENAI_API_KEY"],
    #api_key=os.getenv("OPENROUTER_API_KEY"),
)

# ── Models ────────────────────────────────────────────────────────────
MODELS = {
    "⚡ Auto":              "openrouter/auto",
    "🌟 Gemini 2.0 Flash":  "google/gemini-2.0-flash-exp:free",
    "🧠 DeepSeek Chat V3":  "deepseek/deepseek-chat-v3-0324:free",
    "🔮 Mistral Small 3.1": "mistralai/mistral-small-3.1-24b-instruct:free",
    "🦙 LLaMA 4 Maverick":  "meta-llama/llama-4-maverick:free",
}

# ── Themes (matched to mrabhi-7208.netlify.app) ───────────────────────
THEMES = {
    "Cyber Green": {
        "emoji":"🌐","bg":"#09090e","bg2":"#0d0d14","bg3":"#111119","bg4":"#161621",
        "a":"#00ff88","a2":"#00cc6a","a3":"#00ffcc",
        "ub":"linear-gradient(135deg,#00aa55,#00ff88)","bb":"#111119",
        "brd":"rgba(0,255,136,0.13)","brd2":"rgba(0,255,136,0.36)",
        "t1":"#e8fff4","t2":"#55aa77","t3":"#224433",
        "glow":"rgba(0,255,136,0.22)","glow2":"rgba(0,255,136,0.07)",
        "sbg":"#0d0d14","hbg":"rgba(9,9,14,0.95)","ibg":"#111119",
        "grid":"rgba(0,255,136,0.035)",
        "fd":"Orbitron","fb":"Rajdhani",
        "fu":"https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@400;500;600;700&display=swap",
    },
    "Ocean Blue": {
        "emoji":"🌊","bg":"#020c18","bg2":"#040f1e","bg3":"#071426","bg4":"#0a1830",
        "a":"#00aaff","a2":"#0066dd","a3":"#00ddff",
        "ub":"linear-gradient(135deg,#004aaa,#00aaff)","bb":"#071426",
        "brd":"rgba(0,170,255,0.13)","brd2":"rgba(0,170,255,0.36)",
        "t1":"#ddf0ff","t2":"#4488aa","t3":"#1a3344",
        "glow":"rgba(0,170,255,0.22)","glow2":"rgba(0,170,255,0.07)",
        "sbg":"#040f1e","hbg":"rgba(2,12,24,0.95)","ibg":"#071426",
        "grid":"rgba(0,170,255,0.035)",
        "fd":"Exo 2","fb":"Exo 2",
        "fu":"https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;500;600;700;800&display=swap",
    },
    "Neon Purple": {
        "emoji":"💜","bg":"#0c0014","bg2":"#100018","bg3":"#15001f","bg4":"#1b0028",
        "a":"#cc00ff","a2":"#8800bb","a3":"#ff44ff",
        "ub":"linear-gradient(135deg,#6600aa,#cc00ff)","bb":"#15001f",
        "brd":"rgba(204,0,255,0.14)","brd2":"rgba(204,0,255,0.38)",
        "t1":"#f5e6ff","t2":"#9955bb","t3":"#442255",
        "glow":"rgba(204,0,255,0.26)","glow2":"rgba(204,0,255,0.07)",
        "sbg":"#100018","hbg":"rgba(12,0,20,0.95)","ibg":"#15001f",
        "grid":"rgba(204,0,255,0.035)",
        "fd":"Orbitron","fb":"Rajdhani",
        "fu":"https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@400;500;600;700&display=swap",
    },
    "Forest": {
        "emoji":"🌲","bg":"#030e04","bg2":"#051208","bg3":"#08180a","bg4":"#0c1e0e",
        "a":"#00cc55","a2":"#228833","a3":"#44ee66",
        "ub":"linear-gradient(135deg,#166622,#00cc55)","bb":"#08180a",
        "brd":"rgba(0,204,85,0.13)","brd2":"rgba(0,204,85,0.36)",
        "t1":"#e6ffe6","t2":"#448844","t3":"#1e3a1e",
        "glow":"rgba(0,204,85,0.22)","glow2":"rgba(0,204,85,0.07)",
        "sbg":"#051208","hbg":"rgba(3,14,4,0.95)","ibg":"#08180a",
        "grid":"rgba(0,204,85,0.035)",
        "fd":"Nunito","fb":"Nunito",
        "fu":"https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;500;600;700;800;900&display=swap",
    },
    "Light Mode": {
        "emoji":"☀️","bg":"#f7f9ff","bg2":"#eef2ff","bg3":"#e5eaff","bg4":"#d8dfff",
        "a":"#4f38e8","a2":"#7c3aed","a3":"#c026d3",
        "ub":"linear-gradient(135deg,#4f38e8,#7c3aed)","bb":"#ffffff",
        "brd":"rgba(79,56,232,0.13)","brd2":"rgba(79,56,232,0.32)",
        "t1":"#18103c","t2":"#6050a0","t3":"#a090c4",
        "glow":"rgba(79,56,232,0.15)","glow2":"rgba(79,56,232,0.06)",
        "sbg":"#eef2ff","hbg":"rgba(247,249,255,0.95)","ibg":"#ffffff",
        "grid":"rgba(79,56,232,0.04)",
        "fd":"Plus Jakarta Sans","fb":"Plus Jakarta Sans",
        "fu":"https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap",
    },
    "Deep Ocean": {
        "emoji":"🌊","bg":"#00060f","bg2":"#000a18","bg3":"#000e22","bg4":"#00122c",
        "a":"#0066ff","a2":"#0044bb","a3":"#00aaff",
        "ub":"linear-gradient(135deg,#003399,#0066ff)","bb":"#000e22",
        "brd":"rgba(0,102,255,0.13)","brd2":"rgba(0,102,255,0.36)",
        "t1":"#d0e8ff","t2":"#3366aa","t3":"#1a3355",
        "glow":"rgba(0,102,255,0.24)","glow2":"rgba(0,102,255,0.07)",
        "sbg":"#000a18","hbg":"rgba(0,6,15,0.95)","ibg":"#000e22",
        "grid":"rgba(0,102,255,0.035)",
        "fd":"Exo 2","fb":"Exo 2",
        "fu":"https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;500;600;700;800&display=swap",
    },
}

STYLES = {
    "Balanced":  "Clear, balanced, professional. Use markdown structure.",
    "Concise":   "Be brief. Bullet points preferred. No fluff.",
    "Detailed":  "Thorough with examples, context, and full explanations.",
    "Creative":  "Vivid, imaginative, and engaging language.",
    "Technical": "Precise and technical. Include code examples where relevant.",
}

def make_system_prompt(style, tone):
    return f"""You are NeuraChat — a premium AI assistant.
STYLE: {STYLES.get(style, STYLES['Balanced'])}
TONE: {tone}
- Answer ANY question on ANY topic.
- For diagrams use Mermaid syntax in ```mermaid blocks.
- Use markdown: headers, bold, tables, code blocks, lists.
- Match the user's language. Be direct, accurate, and genuinely useful."""

# ── Page ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NeuraChat AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session defaults ──────────────────────────────────────────────────
for k, v in {
    "messages": [], "theme": "Cyber Green",
    "model_key": "⚡ Auto", "style": "Balanced",
    "tone": "Professional", "temp": 0.7,
    "started": datetime.datetime.now().strftime("%H:%M"),
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

T = THEMES[st.session_state.theme]


# ══════════════════════════════════════════════════════════════════════
#  CSS ENGINE
# ══════════════════════════════════════════════════════════════════════
def build_css(T):
    is_light = st.session_state.theme == "Light Mode"
    use_orbitron = T["fd"] == "Orbitron"

    return f"""
<style>
@import url('{T["fu"]}');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

:root {{
    --bg:{T['bg']};--bg2:{T['bg2']};--bg3:{T['bg3']};--bg4:{T['bg4']};
    --a:{T['a']};--a2:{T['a2']};--a3:{T['a3']};
    --brd:{T['brd']};--brd2:{T['brd2']};
    --t1:{T['t1']};--t2:{T['t2']};--t3:{T['t3']};
    --glow:{T['glow']};--glow2:{T['glow2']};
    --fd:'{T['fd']}',sans-serif;
    --fb:'{T['fb']}',sans-serif;
    --mono:'JetBrains Mono',monospace;
    --r:15px;--rs:10px;
}}

*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}

html,body,.stApp{{
    background:var(--bg) !important;
    background-image:
        linear-gradient({T['grid']} 1px,transparent 1px),
        linear-gradient(90deg,{T['grid']} 1px,transparent 1px) !important;
    background-size:48px 48px !important;
    font-family:var(--fb) !important;
    color:var(--t1) !important;
    overflow-x:hidden;
}}

#MainMenu,footer,header,.stDeployButton,[data-testid="stToolbar"]{{display:none!important;}}
.block-container{{padding:0!important;max-width:100%!important;}}

::-webkit-scrollbar{{width:3px;height:3px;}}
::-webkit-scrollbar-track{{background:transparent;}}
::-webkit-scrollbar-thumb{{background:linear-gradient(var(--a),var(--a2));border-radius:99px;}}

/* ━━━━ SIDEBAR ━━━━ */
[data-testid="stSidebar"]{{
    background:{T['sbg']} !important;
    border-right:1px solid var(--brd) !important;
    min-width:265px!important;max-width:282px!important;
}}
[data-testid="stSidebar"]>div:first-child{{
    padding:1.4rem 1.15rem 2rem!important;
    height:100vh;overflow-y:auto;
}}

/* Brand */
.brand{{display:flex;align-items:center;gap:11px;padding-bottom:1.2rem;margin-bottom:1.4rem;border-bottom:1px solid var(--brd);}}
.brand-gem{{
    width:42px;height:42px;
    background:linear-gradient(135deg,var(--a),var(--a2));
    border-radius:13px;display:grid;place-items:center;font-size:18px;flex-shrink:0;
    box-shadow:0 0 26px var(--glow);
    animation:gem 3.5s ease-in-out infinite;
}}
@keyframes gem{{0%,100%{{box-shadow:0 0 22px var(--glow);}}50%{{box-shadow:0 0 50px var(--glow),0 0 90px var(--glow2);}}}}
.brand-name{{
    font-family:var(--fd);
    font-size:{'1.05rem' if use_orbitron else '1.2rem'};
    font-weight:900;
    letter-spacing:{'0.08em' if use_orbitron else '0'};
    background:linear-gradient(120deg,var(--t1) 0%,var(--a) 100%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}}
.brand-sub{{font-size:0.6rem;color:var(--t3);letter-spacing:0.1em;margin-top:2px;font-weight:600;}}

/* Status */
.s-row{{display:flex;align-items:center;gap:8px;background:var(--bg3);border:1px solid var(--brd);border-radius:var(--rs);padding:9px 12px;margin-bottom:4px;}}
.s-dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0;}}
.d-on{{background:var(--a);box-shadow:0 0 9px var(--a);animation:blink 2s infinite;}}
.d-th{{background:#f59e0b;box-shadow:0 0 9px #f59e0b;animation:blink 0.55s infinite;}}
.d-er{{background:#ef4444;box-shadow:0 0 9px #ef4444;}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0.18}}}}
.s-txt{{font-size:0.78rem;font-weight:700;color:var(--t2);font-family:var(--fb);}}

/* Labels */
.slbl{{font-size:0.62rem;font-weight:700;color:var(--t3);text-transform:uppercase;letter-spacing:0.12em;margin:15px 0 6px;}}

/* Model chip */
.m-chip{{background:var(--bg3);border:1px solid var(--brd);border-radius:var(--rs);padding:7px 11px;font-family:var(--mono);font-size:0.7rem;color:var(--a);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-top:4px;}}

/* Stats */
.stat-g{{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:6px;}}
.stat-b{{background:var(--bg3);border:1px solid var(--brd);border-radius:var(--rs);padding:11px 8px;text-align:center;transition:border-color 0.2s,transform 0.2s;}}
.stat-b:hover{{border-color:var(--a);transform:translateY(-2px);}}
.stat-n{{font-family:var(--fd);font-size:1.55rem;font-weight:900;background:linear-gradient(135deg,var(--a),var(--a2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1;}}
.stat-l{{font-size:0.6rem;color:var(--t3);margin-top:3px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;}}

/* Tags */
.tags{{display:flex;flex-wrap:wrap;gap:5px;margin-top:7px;}}
.tag{{background:var(--glow2);border:1px solid var(--brd);color:var(--a);border-radius:99px;padding:3px 9px;font-size:0.66rem;font-weight:700;transition:all 0.18s;cursor:default;}}
.tag:hover{{background:var(--glow);border-color:var(--a);transform:translateY(-2px);box-shadow:0 4px 14px var(--glow);}}

/* Sidebar selects / sliders */
[data-testid="stSidebar"] .stSelectbox>div>div{{background:var(--bg3)!important;border:1px solid var(--brd)!important;border-radius:var(--rs)!important;color:var(--t1)!important;font-size:0.82rem!important;font-family:var(--fb)!important;}}
[data-testid="stSidebar"] .stSelectbox>div>div:hover{{border-color:var(--a)!important;}}
[data-testid="stSidebar"] .stSelectbox li{{background:var(--bg3)!important;color:var(--t1)!important;}}
[data-testid="stSidebar"] .stSlider [data-baseweb="thumb"]{{background:var(--a)!important;border:3px solid var(--bg)!important;box-shadow:0 0 12px var(--glow)!important;}}
[data-testid="stSidebar"] .stSlider [data-baseweb="track-background"]{{background:var(--brd2)!important;}}
[data-testid="stSidebar"] .stSlider [data-baseweb="track-fill"]{{background:linear-gradient(90deg,var(--a),var(--a2))!important;}}
[data-testid="stSidebar"] .stSlider label{{color:var(--t2)!important;font-size:0.75rem!important;}}

/* Sidebar buttons */
.stButton>button{{
    background:var(--glow2)!important;border:1px solid var(--brd2)!important;
    color:var(--a)!important;border-radius:var(--rs)!important;
    font-family:var(--fb)!important;font-size:0.82rem!important;font-weight:700!important;
    width:100%!important;padding:0.58rem 1rem!important;transition:all 0.2s!important;
}}
.stButton>button:hover{{
    background:var(--glow)!important;border-color:var(--a)!important;
    box-shadow:0 4px 22px var(--glow)!important;transform:translateY(-2px)!important;color:var(--t1)!important;
}}
.stButton>button:active{{transform:translateY(0)!important;}}

.sb-footer{{font-size:0.63rem;color:var(--t3);text-align:center;line-height:1.75;margin-top:14px;padding-top:14px;border-top:1px solid var(--brd);}}

/* ━━━━ TOP BAR ━━━━ */
.topbar{{
    background:{T['hbg']};
    backdrop-filter:blur(32px) saturate(200%);
    -webkit-backdrop-filter:blur(32px) saturate(200%);
    border-bottom:1px solid var(--brd);
    padding:0.75rem 2rem;
    display:flex;align-items:center;justify-content:space-between;
    position:sticky;top:0;z-index:999;
}}
.tb-l{{display:flex;align-items:center;gap:10px;}}
.tb-ico{{width:30px;height:30px;background:linear-gradient(135deg,var(--a),var(--a2));border-radius:9px;display:grid;place-items:center;font-size:13px;box-shadow:0 0 16px var(--glow);}}
.tb-title{{
    font-family:var(--fd);font-size:{'0.88rem' if use_orbitron else '1rem'};font-weight:900;
    letter-spacing:{'0.08em' if use_orbitron else '0.01em'};
    background:linear-gradient(120deg,var(--t1),var(--a));
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}}
.tb-r{{display:flex;align-items:center;gap:8px;flex-wrap:wrap;}}
.pill{{border-radius:99px;padding:4px 11px;font-size:0.67rem;font-weight:700;display:flex;align-items:center;gap:5px;white-space:nowrap;}}
.p-a{{background:var(--glow2);border:1px solid var(--brd2);color:var(--a);font-family:var(--mono);font-size:0.61rem;}}
.p-th{{background:var(--bg3);border:1px solid var(--brd);color:var(--t2);}}
.p-on{{background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);color:#22c55e;}}
.p-th2{{background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);color:#f59e0b;}}
.p-er{{background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);color:#ef4444;}}
.pdot{{width:5px;height:5px;border-radius:50%;background:currentColor;animation:blink 2s infinite;}}

/* ━━━━ WELCOME ━━━━ */
.welcome{{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:62vh;padding:3rem 1.5rem 2rem;text-align:center;}}
.w-orb{{
    width:86px;height:86px;
    background:linear-gradient(135deg,var(--a) 0%,var(--a2) 50%,var(--a3) 100%);
    border-radius:26px;display:grid;place-items:center;font-size:34px;margin-bottom:1.75rem;
    box-shadow:0 0 60px var(--glow),0 0 110px var(--glow2);
    animation:wfloat 4s ease-in-out infinite;position:relative;
}}
.w-orb::after{{content:'';position:absolute;inset:-3px;border-radius:29px;background:linear-gradient(135deg,var(--a),var(--a3));z-index:-1;opacity:0.35;animation:wring 4s ease-in-out infinite;}}
@keyframes wfloat{{0%,100%{{transform:translateY(0) scale(1);}}50%{{transform:translateY(-11px) scale(1.04);}}}}
@keyframes wring{{0%,100%{{opacity:0.25;transform:scale(1);}}50%{{opacity:0.55;transform:scale(1.1);}}}}
.w-h{{
    font-family:var(--fd);
    font-size:clamp(1.65rem,4vw,2.5rem);font-weight:900;line-height:1.1;
    letter-spacing:{'0.04em' if use_orbitron else '-0.01em'};margin-bottom:0.75rem;
    background:linear-gradient(120deg,var(--t1) 0%,var(--a) 55%,var(--a3) 100%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
    animation:fi 0.75s ease forwards;
}}
.w-s{{font-size:0.95rem;color:var(--t2);max-width:420px;line-height:1.7;margin-bottom:2.25rem;font-weight:400;animation:fi 0.95s 0.15s ease both;}}
@keyframes fi{{from{{opacity:0;transform:translateY(12px);}}to{{opacity:1;transform:translateY(0);}}}}
.w-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(185px,1fr));gap:9px;width:100%;max-width:600px;animation:fi 1.1s 0.3s ease both;}}
.w-card{{
    background:rgba(255,255,255,0.02);
    border:1px solid var(--brd);
    border-radius:var(--r);padding:14px 15px;text-align:left;
    transition:all 0.22s cubic-bezier(.25,.46,.45,.94);cursor:default;
}}
.w-card:hover{{background:var(--glow2);border-color:var(--a);transform:translateY(-4px);box-shadow:0 10px 36px var(--glow);}}
.wc-i{{font-size:1.25rem;margin-bottom:6px;}}
.wc-t{{font-size:0.78rem;font-weight:700;color:var(--t1);margin-bottom:3px;letter-spacing:0.02em;}}
.wc-s{{font-size:0.71rem;color:var(--t2);line-height:1.5;}}

/* ━━━━ CHAT MESSAGES ━━━━ */
[data-testid="chatAvatarIcon-user"],
[data-testid="chatAvatarIcon-assistant"]{{display:none!important;}}
[data-testid="stChatMessage"]{{background:transparent!important;border:none!important;padding:0.28rem 0!important;}}
.chat-area{{max-width:900px;margin:0 auto;padding:1.5rem clamp(1rem,4vw,2.5rem) 0.5rem;}}

/* User bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]){{justify-content:flex-end!important;}}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stChatMessageContent{{
    background:{T['ub']}!important;
    border-radius:20px 20px 5px 20px!important;
    color:#fff!important;max-width:70%!important;margin-left:auto!important;
    padding:11px 16px!important;font-size:0.9rem!important;line-height:1.65!important;
    box-shadow:0 4px 24px var(--glow)!important;border:none!important;
    animation:mr .28s cubic-bezier(.25,.46,.45,.94)!important;
}}
@keyframes mr{{from{{opacity:0;transform:translateX(18px) scale(0.95);}}to{{opacity:1;transform:translateX(0) scale(1);}}}}

/* Bot bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stChatMessageContent{{
    background:{T['bb']}!important;
    border:1px solid var(--brd)!important;
    border-radius:5px 20px 20px 20px!important;
    color:var(--t1)!important;max-width:83%!important;
    padding:13px 17px!important;font-size:0.9rem!important;line-height:1.74!important;
    box-shadow:0 2px 16px rgba(0,0,0,0.22)!important;
    animation:ml .28s cubic-bezier(.25,.46,.45,.94)!important;
}}
@keyframes ml{{from{{opacity:0;transform:translateX(-18px) scale(0.95);}}to{{opacity:1;transform:translateX(0) scale(1);}}}}

/* Markdown inside bot */
[data-testid="stChatMessage"] h1,[data-testid="stChatMessage"] h2,[data-testid="stChatMessage"] h3{{
    font-family:var(--fd)!important;color:var(--a)!important;margin:14px 0 5px!important;font-weight:700!important;
}}
.stChatMessage strong{{color:var(--t1)!important;}}
.stChatMessage code{{
    background:var(--glow2)!important;border:1px solid var(--brd)!important;
    border-radius:5px!important;padding:2px 6px!important;font-size:0.83em!important;
    color:var(--a)!important;font-family:var(--mono)!important;
}}
.stChatMessage pre{{
    background:var(--bg)!important;border:1px solid var(--brd)!important;
    border-left:3px solid var(--a)!important;border-radius:10px!important;
    padding:14px!important;overflow-x:auto!important;margin:10px 0!important;
}}
.stChatMessage pre code{{background:transparent!important;border:none!important;padding:0!important;color:var(--t1)!important;font-size:0.84em!important;}}
.stChatMessage table{{border-collapse:collapse!important;width:100%!important;margin:12px 0!important;}}
.stChatMessage th{{background:var(--glow2)!important;color:var(--a)!important;padding:9px 13px!important;font-size:0.77rem!important;font-weight:700!important;text-transform:uppercase!important;letter-spacing:0.06em!important;text-align:left!important;border-bottom:1px solid var(--brd)!important;}}
.stChatMessage td{{padding:8px 12px!important;border-bottom:1px solid var(--brd)!important;color:var(--t2)!important;font-size:0.87rem!important;}}
.stChatMessage tr:hover td{{background:var(--glow2)!important;}}
.stChatMessage tr:last-child td{{border-bottom:none!important;}}
.stChatMessage blockquote{{border-left:3px solid var(--a)!important;margin:10px 0!important;padding:9px 14px!important;background:var(--glow2)!important;border-radius:0 9px 9px 0!important;color:var(--t2)!important;font-style:italic!important;}}

/* Typing dots */
.typing{{display:flex;align-items:center;gap:5px;padding:12px 16px;background:{T['bb']};border:1px solid var(--brd);border-radius:5px 18px 18px 18px;width:fit-content;margin:2px 0;}}
.td{{width:7px;height:7px;border-radius:50%;background:var(--a);opacity:0.25;}}
.td:nth-child(1){{animation:td 1.2s 0s infinite;}}
.td:nth-child(2){{animation:td 1.2s .22s infinite;}}
.td:nth-child(3){{animation:td 1.2s .44s infinite;}}
@keyframes td{{0%,55%,100%{{opacity:.2;transform:translateY(0);}}28%{{opacity:1;transform:translateY(-6px);}}}}

/* ━━━━ INPUT ━━━━ */
[data-testid="stBottom"]{{
    background:{T['hbg']}!important;
    border-top:1px solid var(--brd)!important;
    padding:0.8rem clamp(1rem,5vw,2.5rem) 1rem!important;
    backdrop-filter:blur(24px);
}}
[data-testid="stChatInput"]{{
    background:{T['ibg']}!important;
    border:1.5px solid var(--brd2)!important;
    border-radius:16px!important;max-width:880px!important;margin:0 auto!important;
    transition:border-color .2s,box-shadow .2s!important;
}}
[data-testid="stChatInput"]:focus-within{{
    border-color:var(--a)!important;
    box-shadow:0 0 0 3px var(--glow2),0 4px 28px var(--glow)!important;
}}
[data-testid="stChatInput"] textarea{{
    background:transparent!important;color:var(--t1)!important;
    font-family:var(--fb)!important;font-size:0.92rem!important;
    caret-color:var(--a)!important;padding:13px 17px!important;line-height:1.55!important;
}}
[data-testid="stChatInput"] textarea::placeholder{{color:var(--t3)!important;font-style:italic!important;}}
[data-testid="stChatInput"] button{{
    background:linear-gradient(135deg,var(--a),var(--a2))!important;
    border:none!important;border-radius:11px!important;margin:6px!important;
    transition:opacity .18s,transform .18s,box-shadow .18s!important;
}}
[data-testid="stChatInput"] button:hover{{opacity:.88!important;transform:scale(1.07)!important;box-shadow:0 4px 20px var(--glow)!important;}}
[data-testid="stChatInput"] button svg{{fill:#fff!important;}}

/* Misc */
.stSpinner>div{{border-top-color:var(--a)!important;}}
.stInfo{{background:var(--glow2)!important;border:1px solid var(--brd2)!important;border-radius:var(--rs)!important;color:var(--a)!important;font-size:0.8rem!important;}}
hr{{border:none!important;border-top:1px solid var(--brd)!important;margin:12px 0!important;}}

@media(max-width:768px){{
    .topbar{{padding:.7rem 1rem;}}
    .p-a,.p-th{{display:none;}}
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stChatMessageContent{{max-width:88%!important;}}
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stChatMessageContent{{max-width:95%!important;}}
    .w-grid{{grid-template-columns:1fr 1fr;}}
}}
@media(max-width:480px){{.w-grid{{grid-template-columns:1fr;}}}}
</style>"""

st.markdown(build_css(T), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  STREAMING RESPONSE  ← This is what makes it feel like ChatGPT
# ══════════════════════════════════════════════════════════════════════
def stream_response(messages, model_key):
    """
    Yields text chunks in real-time using OpenRouter streaming API.
    Falls back through all models if one fails.
    """
    model_id  = MODELS[model_key]
    fallbacks = [v for v in MODELS.values() if v != model_id]
    all_models = [model_id] + fallbacks

    api_msgs = [
        {"role": "system", "content": make_system_prompt(
            st.session_state.style, st.session_state.tone
        )}
    ] + messages

    for model in all_models:
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=api_msgs,
                max_tokens=4096,
                temperature=st.session_state.temp,
                stream=True,            # ← KEY: enables streaming
            )
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
            return  # success — stop trying fallbacks

        except Exception as e:
            err = str(e)
            if any(k in err for k in ["429","404","rate","quota","not found","endpoint","temporarily"]):
                continue
            yield f"\n\n⚠️ **Error:** {err}"
            return

    yield "\n\n⚠️ All models are at capacity. Please try again shortly."


# ══════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:

    st.markdown(f"""
    <div class="brand">
        <div class="brand-gem">✦</div>
        <div>
            <div class="brand-name">NeuraChat</div>
            <div class="brand-sub">v3.1 · STREAMING EDITION</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Status
    thinking = "_thinking" in st.session_state and st.session_state._thinking
    dc = "d-th" if thinking else "d-on"
    sl = "Streaming…" if thinking else "Online"
    st.markdown(f"""
    <div class="s-row">
        <div class="s-dot {dc}"></div>
        <span class="s-txt">{sl}</span>
    </div>
    """, unsafe_allow_html=True)

    # Theme
    st.markdown('<div class="slbl">🎨 Theme</div>', unsafe_allow_html=True)
    tlist  = list(THEMES.keys())
    tlabels = [f"{THEMES[t]['emoji']} {t}" for t in tlist]
    cidx   = tlist.index(st.session_state.theme)
    chosen = st.selectbox("theme", tlabels, index=cidx, label_visibility="collapsed")
    new_t  = chosen.split(" ", 1)[1]
    if new_t != st.session_state.theme:
        st.session_state.theme = new_t
        st.rerun()

    # Model
    st.markdown('<div class="slbl">🤖 AI Model</div>', unsafe_allow_html=True)
    mkeys   = list(MODELS.keys())
    midx    = mkeys.index(st.session_state.model_key) if st.session_state.model_key in mkeys else 0
    st.session_state.model_key = st.selectbox("model", mkeys, index=midx, label_visibility="collapsed")
    mshort  = MODELS[st.session_state.model_key].split("/")[-1].replace(":free","")
    st.markdown(f'<div class="m-chip">⚡ {mshort}</div>', unsafe_allow_html=True)

    # Settings
    st.markdown('<div class="slbl">⚙️ Settings</div>', unsafe_allow_html=True)
    st.session_state.style = st.selectbox(
        "Response Style", list(STYLES.keys()),
        index=list(STYLES.keys()).index(st.session_state.style),
    )
    st.session_state.tone = st.selectbox(
        "Tone", ["Professional","Friendly","Casual","Academic","Creative"],
    )
    st.session_state.temp = st.slider("🌡️ Creativity", 0.0, 1.0, st.session_state.temp, 0.05)

    # Stats
    st.markdown('<div class="slbl">📊 Session</div>', unsafe_allow_html=True)
    uc = len([m for m in st.session_state.messages if m["role"] == "user"])
    tc = len(st.session_state.messages)
    st.markdown(f"""
    <div class="stat-g">
        <div class="stat-b"><div class="stat-n">{uc}</div><div class="stat-l">Sent</div></div>
        <div class="stat-b"><div class="stat-n">{tc}</div><div class="stat-l">Total</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Tags
    st.markdown('<div class="slbl">✨ Capabilities</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="tags">
        <span class="tag">💻 Code</span><span class="tag">📊 Diagrams</span>
        <span class="tag">🧮 Math</span><span class="tag">✍️ Writing</span>
        <span class="tag">🔬 Science</span><span class="tag">🌐 Any Topic</span>
        <span class="tag">🗺️ Flowcharts</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    if st.button("🗑️  Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

    st.markdown(f"""
    <div class="sb-footer">
        ✦ NeuraChat AI · v3.1<br>
        {T['emoji']} {st.session_state.theme} · OpenRouter<br>
        Session started {st.session_state.started}
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  MAIN AREA
# ══════════════════════════════════════════════════════════════════════

# Top bar
mshort = MODELS[st.session_state.model_key].split("/")[-1].replace(":free","")

st.markdown(f"""
<div class="topbar">
    <div class="tb-l">
        <div class="tb-ico">✦</div>
        <div class="tb-title">NEURACHAT AI</div>
    </div>
    <div class="tb-r">
        <div class="pill p-a">⚡ {mshort}</div>
        <div class="pill p-th">{T['emoji']} {st.session_state.theme}</div>
        <div class="pill p-on"><div class="pdot"></div>Online</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Welcome screen
if not st.session_state.messages:
    st.markdown(f"""
    <div class="welcome">
        <div class="w-orb">{T['emoji']}</div>
        <div class="w-h">What can I help<br>you with today?</div>
        <div class="w-s">
            Ask me anything — code, diagrams, flowcharts, mathematics,<br>
            research, analysis, writing, or any topic you can imagine.
        </div>
        <div class="w-grid">
            <div class="w-card">
                <div class="wc-i">📊</div>
                <div class="wc-t">Flowchart / Diagram</div>
                <div class="wc-s">Mermaid diagrams for any system or process</div>
            </div>
            <div class="w-card">
                <div class="wc-i">💻</div>
                <div class="wc-t">Write Code</div>
                <div class="wc-s">Clean, commented code in any language</div>
            </div>
            <div class="w-card">
                <div class="wc-i">🧮</div>
                <div class="wc-t">Math & Science</div>
                <div class="wc-s">Step-by-step problem solving & explanations</div>
            </div>
            <div class="w-card">
                <div class="wc-i">✍️</div>
                <div class="wc-t">Creative Writing</div>
                <div class="wc-s">Essays, stories, emails — polished & professional</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Chat history
with st.container():
    st.markdown('<div class="chat-area">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    st.markdown('</div>', unsafe_allow_html=True)


# ── Input & Streaming ─────────────────────────────────────────────────
if prompt := st.chat_input(f"Ask me anything… [{st.session_state.theme} · {st.session_state.style}]"):

    # Add and show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Stream bot response — text appears word by word like ChatGPT
    with st.chat_message("assistant"):
        # Show typing indicator briefly
        typing_ph = st.empty()
        typing_ph.markdown("""
        <div class="typing">
            <div class="td"></div><div class="td"></div><div class="td"></div>
        </div>""", unsafe_allow_html=True)

        # Start streaming — replaces typing indicator on first token
        response_placeholder = st.empty()
        full_reply = ""
        first_token = True

        for chunk in stream_response(st.session_state.messages, st.session_state.model_key):
            if first_token:
                typing_ph.empty()   # remove typing dots the moment text starts
                first_token = False
            full_reply += chunk
            # Live update — shows text as it arrives
            response_placeholder.markdown(full_reply + "▌")  # cursor effect

        # Final render without cursor
        response_placeholder.markdown(full_reply)

    # Save to history
    st.session_state.messages.append({"role": "assistant", "content": full_reply})

