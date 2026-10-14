"""Shared neon look for the HYPERDECK multipage app (imported by every page)."""

import streamlit as st

CYAN, PINK, LIME, VIOLET, AMBER = "#00F0FF", "#FF2E97", "#B6FF3B", "#9D4EDD", "#FFB547"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;900&family=Inter:wght@400;600&display=swap');
.stApp {{
  background:
    radial-gradient(1000px 520px at 0% 0%, rgba(157,78,221,.30), transparent 60%),
    radial-gradient(900px 520px at 100% 20%, rgba(0,240,255,.16), transparent 60%),
    radial-gradient(700px 420px at 50% 120%, rgba(255,46,151,.16), transparent 60%),
    #04020d;
  color: #e9e6ff; font-family: 'Inter', sans-serif;
}}
.stApp::before {{
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background-image: linear-gradient(rgba(0,240,255,.05) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0,240,255,.05) 1px, transparent 1px);
  background-size: 42px 42px;
}}
header[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ position: relative; z-index: 1; padding-top: 1.4rem; max-width: 1150px; }}
h1, h2, h3 {{ font-family: 'Orbitron', sans-serif !important; letter-spacing: .04em; }}
section[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, rgba(20,8,48,.95), rgba(6,3,20,.95));
  border-right: 1px solid rgba(0,240,255,.25);
}}
section[data-testid="stSidebar"] a {{ border-radius: 10px; }}
section[data-testid="stSidebar"] a:hover {{ background: rgba(0,240,255,.12); }}
.hd-bar {{ display:flex; align-items:center; gap:14px; padding: 12px 20px; border-radius: 18px;
  margin-bottom: 16px; background: rgba(18,8,44,.6); backdrop-filter: blur(8px);
  border: 1px solid rgba(0,240,255,.35);
  box-shadow: 0 0 22px rgba(0,240,255,.22), inset 0 0 18px rgba(157,78,221,.18); }}
.hd-name {{ font-family:'Orbitron'; font-weight:900; font-size: 24px; letter-spacing: .22em;
  background: linear-gradient(90deg, {CYAN}, {PINK}, {LIME}); -webkit-background-clip: text;
  color: transparent; filter: drop-shadow(0 0 10px rgba(255,46,151,.5)); }}
.hd-sub {{ font-size: 11px; letter-spacing: .22em; text-transform: uppercase; color: #a9a3d9; }}
.hd-logo {{ animation: hdspin 10s linear infinite; filter: drop-shadow(0 0 8px {CYAN}); }}
@keyframes hdspin {{ to {{ transform: rotate(360deg); }} }}
.hd-title {{ font-family:'Orbitron'; font-size: 38px; font-weight: 900; margin: 6px 0 4px;
  background: linear-gradient(90deg, #fff, {CYAN} 45%, {PINK}); -webkit-background-clip:text; color:transparent; }}
.hd-lead {{ color:#c8c2f0; font-size: 15px; margin-bottom: 14px; }}
.glass {{ padding: 16px 20px; border-radius: 18px; background: rgba(14,7,36,.65);
  border: 1px solid rgba(157,78,221,.5); box-shadow: 0 0 18px rgba(157,78,221,.22); }}
.tiles {{ display:grid; grid-template-columns: repeat(3, 1fr); gap: 16px; perspective: 1000px; margin: 10px 0 8px; }}
.tile {{ padding: 20px; border-radius: 20px; background: rgba(14,7,36,.7);
  border: 1px solid rgba(0,240,255,.35); transform-style: preserve-3d;
  transition: transform .4s ease, box-shadow .4s ease; min-height: 150px; }}
.tile:hover {{ transform: rotateX(10deg) rotateY(-12deg) translateZ(22px);
  box-shadow: 0 20px 40px rgba(0,0,0,.5), 0 0 30px rgba(255,46,151,.55); border-color: {PINK}; }}
.tile .ico {{ font-size: 30px; }}
.tile .t {{ font-family:'Orbitron'; font-weight: 900; font-size: 17px; margin: 8px 0 6px; }}
.tile .d {{ color:#b9b3e6; font-size: 13px; line-height: 1.45; }}
[data-testid="stVegaLiteChart"], [data-testid="stDeckGlJsonChart"], [data-testid="stArrowVegaLiteChart"] {{
  border-radius: 18px; padding: 8px; background: rgba(10,5,28,.55);
  border: 1px solid rgba(0,240,255,.25); box-shadow: 0 0 24px rgba(0,240,255,.15); }}
.hd-foot {{ text-align:center; color:#7e77b3; font-size: 12px; margin-top: 24px; }}
@media (max-width: 800px) {{ .tiles {{ grid-template-columns: 1fr; }} .hd-title {{ font-size: 28px; }} }}
</style>
"""

LOGO = f"""<svg class="hd-logo" width="42" height="42" viewBox="0 0 64 64">
 <defs><linearGradient id="hg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{PINK}"/></linearGradient></defs>
 <polygon points="32,4 56,18 56,46 32,60 8,46 8,18" fill="none" stroke="url(#hg)" stroke-width="3"/>
 <polygon points="32,16 46,24 46,40 32,48 18,40 18,24" fill="none" stroke="{LIME}" stroke-width="2"/>
 <circle cx="32" cy="32" r="5" fill="{PINK}"/></svg>"""


def apply(page_name: str, title: str, lead: str) -> None:
    """Inject the theme, the brand bar and the page heading."""
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(f"""
<div class="hd-bar">{LOGO}
  <div><div class="hd-name">HYPERDECK</div>
  <div class="hd-sub">Streamlit multipage app · {page_name}</div></div>
</div>
<div class="hd-title">{title}</div>
<div class="hd-lead">{lead}</div>
""", unsafe_allow_html=True)


def footer() -> None:
    st.markdown('<div class="hd-foot">HYPERDECK · built from the Streamlit "Create a multipage app" '
                'tutorial · 36104 Data Visualisation and Narratives</div>', unsafe_allow_html=True)


def neon_chart(chart):
    """Dark, glowing defaults for Altair charts."""
    return chart.configure(background="transparent").configure_view(stroke=None).configure_axis(
        labelColor="#c8c2f0", titleColor="#e9e6ff", gridColor="rgba(157,78,221,.22)",
        domainColor="#4d3f8f", tickColor="#4d3f8f").configure_legend(
        labelColor="#e9e6ff", titleColor="#e9e6ff")
