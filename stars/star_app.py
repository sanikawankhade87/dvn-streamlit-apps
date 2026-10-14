# AppStar.  Run with:  streamlit run star_app.py
#
# Python runs once: it precomputes the star's state over a grid of
# masses and ages, then ships one Altair chart whose sliders are
# Vega parameters. Dragging them filters the grid in the browser,
# so the star updates live, with no Python rerun.
#
# Extension (see the Metallicity section of Part D): add a
# metallicity slider with st.slider and thread `zr` through the two
# marked lines, then add the pair-instability branch. Mass and age
# stay live; a new metallicity rebuilds the grid on release.

import math

import altair as alt
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import streamlit as st

SUN_T = 5772.0

st.set_page_config(page_title="STELLARIS | AppStar", page_icon="⭐", layout="wide")

# ---- space theme: twinkling starfield, nebula glow, glass panels -------
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;900&family=Inter:wght@400;600&display=swap');
.stApp {
  background:
    radial-gradient(900px 500px at 15% 10%, rgba(120,60,255,.25), transparent 60%),
    radial-gradient(800px 500px at 90% 30%, rgba(255,90,170,.16), transparent 60%),
    radial-gradient(700px 400px at 50% 110%, rgba(0,200,255,.14), transparent 60%),
    #02010a;
  color: #e8e8ff; font-family: 'Inter', sans-serif;
}
.stApp::before, .stApp::after {
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background-image:
    radial-gradient(1px 1px at 20px 30px, #fff, transparent),
    radial-gradient(1px 1px at 120px 80px, #cde, transparent),
    radial-gradient(1.5px 1.5px at 200px 160px, #fff, transparent),
    radial-gradient(1px 1px at 300px 40px, #fde, transparent),
    radial-gradient(1px 1px at 380px 190px, #fff, transparent),
    radial-gradient(1.5px 1.5px at 60px 220px, #ccf, transparent);
  background-size: 420px 260px; animation: twinkle 5s ease-in-out infinite alternate;
}
.stApp::after { background-size: 610px 370px; animation-delay: 2.5s; opacity: .7; }
@keyframes twinkle { from { opacity: .35; } to { opacity: 1; } }
header[data-testid="stHeader"] {background: transparent;}
.block-container {padding-top: 1rem; max-width: 1100px; position: relative; z-index: 1;}
h1, h2, h3 {font-family: 'Orbitron', sans-serif !important; color: #f0f0ff;}
.nav {display:flex; align-items:center; justify-content:space-between; padding: 14px 22px;
  border-radius: 18px; margin-bottom: 14px; background: rgba(15,10,40,.55);
  backdrop-filter: blur(8px); border: 1px solid rgba(150,120,255,.45);
  box-shadow: 0 0 24px rgba(130,90,255,.35), inset 0 0 20px rgba(255,90,170,.12);}
.brand {display:flex; align-items:center; gap: 14px;}
.brand-name {font-family:'Orbitron'; font-weight:900; font-size: 28px; letter-spacing:.2em;
  background: linear-gradient(90deg, #ffd27d, #ff7ac6, #8fd3ff); -webkit-background-clip:text;
  color: transparent; filter: drop-shadow(0 0 10px rgba(255,200,120,.5));}
.brand-sub {font-size: 12px; letter-spacing: .22em; text-transform: uppercase; color: #a9a6d8;}
.logo {animation: pulse 3s ease-in-out infinite;}
@keyframes pulse {0%,100% {filter: drop-shadow(0 0 6px #ffd27d);} 50% {filter: drop-shadow(0 0 18px #ff9a3c);}}
.orbit {transform-origin: 32px 32px; animation: spin 8s linear infinite;}
@keyframes spin {to {transform: rotate(360deg);}}
.hero {text-align:center; margin: 4px 0 14px;}
.hero h1 {font-size: 40px; margin: 0; background: linear-gradient(90deg, #fff, #ffd27d 45%, #ff7ac6);
  -webkit-background-clip: text; color: transparent;}
.hero p {color: #c9c6f0; margin-top: 8px;}
.cards {display:grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin: 8px 0 12px; perspective: 900px;}
.card {padding: 14px 18px; border-radius: 16px; background: rgba(15,10,40,.65);
  border: 1px solid rgba(150,120,255,.45); transition: transform .3s ease, box-shadow .3s ease;
  box-shadow: 0 0 16px rgba(130,90,255,.25);}
.card:hover {transform: rotateX(8deg) rotateY(-8deg) translateZ(14px);
  box-shadow: 0 0 28px rgba(255,200,120,.55); border-color: #ffd27d;}
.card .lab {font-size: 11px; letter-spacing: .2em; text-transform: uppercase; color: #a9a6d8;}
.card .val {font-family:'Orbitron'; font-size: 24px; font-weight: 900; margin-top: 4px;}
form.vega-bindings {display: flex; justify-content: center; gap: 3rem; margin-top: 0.8rem;
  color: #ffe2b0; font-weight: 700; font-family: 'Orbitron', sans-serif; font-size: 13px;}
form.vega-bindings input[type="range"] {width: 260px; accent-color: #ff7ac6;}
.orb-wrap {position: relative; width: 120px; height: 120px; margin: 6px auto 4px; perspective: 700px;}
.orb {position: absolute; inset: 0; transform-style: preserve-3d;
  animation: tilt 14s linear infinite;}
.orb-wrap .core {position:absolute; inset: 28px; border-radius: 50%; z-index: 2;
  background: radial-gradient(circle at 35% 30%, #fffbe8, #ffd27d 40%, #ff8a3c 70%, #b8341b);
  box-shadow: 0 0 40px #ffb347, 0 0 90px rgba(255,140,60,.6);}
.orb .ring {position:absolute; inset: 0; border-radius: 50%; border: 2px solid rgba(143,211,255,.7);
  box-shadow: 0 0 12px rgba(143,211,255,.6);}
.orb .r1 {transform: rotateX(72deg);} .orb .r2 {transform: rotateY(72deg) rotateX(20deg); border-color: rgba(255,122,198,.7);}
.orb .r3 {transform: rotateX(72deg) rotateY(60deg); border-color: rgba(255,210,125,.6);}
@keyframes tilt {from {transform: rotateY(0deg) rotateX(12deg);} to {transform: rotateY(360deg) rotateX(12deg);}}
[data-testid="stPlotlyChart"] {border-radius: 20px; overflow: hidden; border: 1px solid rgba(150,120,255,.35);
  box-shadow: 0 0 30px rgba(120,80,255,.3);}
.foot {text-align:center; color:#7f7bb0; font-size: 12px; margin-top: 18px;}
@media (max-width: 800px) {.cards {grid-template-columns: 1fr;} .hero h1 {font-size: 28px;}}
</style>""", unsafe_allow_html=True)

st.markdown("""
<div class="nav"><div class="brand">
  <svg class="logo" width="48" height="48" viewBox="0 0 64 64">
    <defs><radialGradient id="sun"><stop offset="0" stop-color="#fff6d8"/>
      <stop offset=".55" stop-color="#ffd27d"/><stop offset="1" stop-color="#ff7a3c"/></radialGradient></defs>
    <circle cx="32" cy="32" r="11" fill="url(#sun)"/>
    <g class="orbit"><ellipse cx="32" cy="32" rx="27" ry="10" fill="none" stroke="#8fd3ff"
       stroke-width="1.6" stroke-dasharray="4 4" transform="rotate(-25 32 32)"/>
      <circle cx="57" cy="22" r="3.5" fill="#ff7ac6"/></g>
  </svg>
  <div><div class="brand-name">STELLARIS</div>
  <div class="brand-sub">AppStar · life and death of a star</div></div></div>
</div>
<div class="orb-wrap"><div class="orb"><div class="ring r1"></div><div class="ring r2"></div><div class="ring r3"></div></div><div class="core"></div></div>
<div class="hero"><h1>Build a star. Watch it live and die.</h1>
<p>Drag <b>mass</b> and <b>age</b> under the charts. The portrait, the HR diagram and the
phase plane all follow your star. Change <b>metallicity</b> to rewrite its fate.</p></div>
""", unsafe_allow_html=True)

alt.data_transformers.disable_max_rows()

# Metallicity is now a Streamlit slider. Releasing it reruns the script
# and rebuilds the grid; mass and age stay live in the browser.
lz = st.slider("log10 metallicity", -4.0, -1.4, -1.7, step=0.05)
Z = 10 ** lz
zr = Z / 0.02
pi_open = Z < 0.001
st.markdown(f"""<div class="cards">
  <div class="card"><div class="lab">Metallicity Z</div>
    <div class="val" style="color:#8fd3ff">{Z:.4f}</div>{zr:.2g} x the Sun</div>
  <div class="card"><div class="lab">Black holes form above</div>
    <div class="val" style="color:#ff7ac6">{18 + 7 * zr:.1f} suns</div>neutron stars below this mass</div>
  <div class="card"><div class="lab">Pair-instability window</div>
    <div class="val" style="color:{'#ffd27d' if pi_open else '#7f7bb0'}">{'OPEN' if pi_open else 'closed'}</div>
    {'140-260 suns explode with no remnant' if pi_open else 'opens below Z = 0.001'}</div>
</div>""", unsafe_allow_html=True)


def bb_rgb(T):
    # Approximate black-body colour, valid from about 1000 to 40000 K.
    t = T / 100.0
    r = 255.0 if t <= 66 else 329.7 * (t - 60) ** -0.1332
    g = 99.47 * math.log(t) - 161.1 if t <= 66 else 288.1 * (t - 60) ** -0.0755
    if t >= 66:
        b = 255.0
    elif t <= 19:
        b = 0.0
    else:
        b = 138.5 * math.log(t - 10) - 305.0
    return tuple(min(255.0, max(0.0, v)) / 255 for v in (r, g, b))


def rgb_str(T):
    r, g, b = (int(round(255 * c)) for c in bb_rgb(min(T, 40000)))
    return f"rgb({r},{g},{b})"


def star_state(mass, age):
    # the same rules as the course page
    L = mass ** 3.5 * zr ** -0.1        # luminosity, suns  [uses zr]
    R = mass ** 0.8                     # radius, suns
    T = SUN_T * (L / R ** 2) ** 0.25    # surface temperature, K
    t_pre = 0.03 * mass ** -1.5
    t_ms = (10.0 * mass ** -2.5 * (1 + 2.5 * math.exp(-mass / 0.12))
            + 0.0025)
    t_g = 1.15 * t_ms

    if age <= t_pre:
        phase = "protostar"
    elif age <= t_ms:
        phase = "main sequence"
    elif mass < 0.25:
        phase = "white dwarf"           # fully convective: no giant
    elif mass < 8:
        phase = "red giant" if age <= t_g else "white dwarf"
    elif age <= t_g:
        frac = (age - t_ms) / (t_g - t_ms)
        phase = "blue supergiant" if frac < 0.4 else "red supergiant"
    elif age <= 1.10 * t_g:
        phase = "supernova"
    elif 140 <= mass <= 260 and Z < 0.001:
        phase = "no remnant"            # pair-instability supernova
    elif mass < 18 + 7 * zr:            # remnant boundary  [uses zr]
        phase = "neutron star"
    else:
        phase = "black hole"

    T_show, L_show, R_show = float(T), L, R
    if phase == "protostar":
        T_show, L_show, R_show = 0.75 * T, 2 * L, 3 * R
    elif phase == "red giant":
        T_show = 3900.0
        R_show = max(R * 60, 10.0)
        L_show = R_show ** 2 * (T_show / SUN_T) ** 4
    elif phase == "blue supergiant":
        frac = (age - t_ms) / (t_g - t_ms)
        T_show = 12000.0
        R_show = 30 + 120 * frac
        L_show = R_show ** 2 * (T_show / SUN_T) ** 4
    elif phase == "red supergiant":
        frac = (age - t_ms) / (t_g - t_ms)
        T_show = 3500.0
        R_show = min(200 + 900 * frac, 900)
        L_show = R_show ** 2 * (T_show / SUN_T) ** 4
    elif phase == "white dwarf":
        cool = max(age - (t_ms if mass < 0.25 else t_g), 0.001)
        T_show = float(np.clip(60000.0 * (0.01 / cool) ** 0.3,
                               3500, 150000))
        R_show = 0.009
        L_show = R_show ** 2 * (T_show / SUN_T) ** 4
    elif phase == "supernova":
        # no luminosity: an explosion is an event, not an equilibrium state,
        # and its ~5e9 suns would stretch an HR luminosity axis by four
        # decades to hold one transient point
        T_show, L_show, R_show = 8000.0, None, None
    elif phase == "neutron star":
        T_show, L_show, R_show = 1e6, None, 1.7e-5
    elif phase == "black hole":
        T_show, L_show, R_show = None, None, 4.2e-6 * mass / 10
    elif phase == "no remnant":
        T_show, L_show, R_show = None, None, None
    return phase, T_show, L_show, R_show, t_ms


# ---- the grid: one row per slider combination ------------------------
lms = [round(-1.0 + 0.05 * k, 2) for k in range(70)]   # mass 0.1 to 282
las = [round(-4.0 + 0.06 * k, 2) for k in range(127)]  # age 1e-4 to 3631

rows = []
for lm in lms:
    for la in las:
        m = 10.0 ** lm
        a = 10.0 ** la
        phase, T, L, R, t_ms = star_state(m, a)
        if phase == "no remnant":
            colour, px = "#000000", 0.0
        elif phase == "black hole":
            colour, px = "rgb(16,16,16)", 40.0
        elif phase == "neutron star":
            colour, px = "#CDE7FF", 6.0
        elif phase == "supernova":
            colour, px = "#FFD27D", 150.0
        else:
            colour = rgb_str(T)
            px = float(np.clip(14 + 26 * (np.log10(R) + 2.2), 5, 150))
        rows.append(dict(
            lm=lm, la=la, mass=m, age=a,
            temp_K=T, lum=L, rad=R,
            colour=colour, size=px ** 2, phase=phase,
            massage=f"mass {m:.2g} suns, age {a:.2g} Gyr",
            temp=f"surface {T:,.0f} K" if T else "",
            lr=(f"luminosity {L:.3g} suns, radius {R:.3g} suns"
                if L and R else
                f"radius {R:.3g} suns" if R else ""),
            life=f"main-sequence lifetime {t_ms:.2g} Gyr",
        ))
grid = pd.DataFrame(rows)

m_sel = alt.param(name="m_sel", value=0.0, bind=alt.binding_range(
    min=-1.0, max=2.45, step=0.05, name="log10 mass (suns)  "))
a_sel = alt.param(name="a_sel", value=0.66, bind=alt.binding_range(
    min=-4.0, max=3.56, step=0.06, name="log10 age (Gyr)  "))
# Half-step tolerances, so the default age (0.66, the Sun's 4.6 Gyr) still
# picks its nearest grid row (0.68) instead of matching nothing.
pick = ("abs(datum.lm - m_sel) < 0.026"
        " && abs(datum.la - a_sel) < 0.031")

# ---- the portrait ----------------------------------------------------
CX, CY = 160, 168
disc = alt.Chart(grid).transform_filter(pick).mark_circle(
    opacity=1).encode(
    x=alt.value(CX), y=alt.value(CY),
    size=alt.Size("size:Q", scale=None, legend=None),
    color=alt.Color("colour:N", scale=None, legend=None))
bh_ring = alt.Chart(grid).transform_filter(
    pick + ' && datum.phase == "black hole"').mark_point(
    filled=False, size=2400, stroke="#E07000", strokeWidth=3,
    opacity=1).encode(x=alt.value(CX), y=alt.value(CY))
# the Sun's size on the same log scale, for reference
sun_ring = alt.Chart(pd.DataFrame({"z": [0]})).mark_point(
    filled=False, size=int((14 + 26 * 2.2) ** 2),
    stroke="#DAA520", strokeWidth=1.5, opacity=1).encode(
    x=alt.value(CX), y=alt.value(CY))


def readout(field, y_px, size=12, color="#9aa1a8", bold=False):
    return alt.Chart(grid).transform_filter(pick).mark_text(
        fontSize=size, color=color,
        fontWeight="bold" if bold else "normal").encode(
        x=alt.value(CX), y=alt.value(y_px), text=field)


def halo(factor, opacity):
    # soft glow rings in the star's own colour
    return alt.Chart(grid).transform_filter(
        pick + ' && datum.phase != "black hole" && datum.phase != "no remnant"'
    ).transform_calculate(halo_size=f"datum.size * {factor}").mark_circle(
        opacity=opacity).encode(
        x=alt.value(CX), y=alt.value(CY),
        size=alt.Size("halo_size:Q", scale=None, legend=None),
        color=alt.Color("colour:N", scale=None, legend=None))


portrait = alt.layer(
    halo(4.5, 0.06), halo(2.6, 0.12), halo(1.6, 0.22), disc, bh_ring, sun_ring,
    readout("massage:N", 340),
    readout("phase:N", 364, size=15, color="#f5f2ea", bold=True),
    readout("temp:N", 386),
    readout("lr:N", 404),
    readout("life:N", 422),
).properties(width=320, height=440)

# ---- the phase plane, with the star riding the sliders ---------------
Ml = np.unique(np.concatenate([np.geomspace(0.1, 300, 160),
                               [0.25, 8.0, 25.0]]))
pre_l = 0.03 * Ml ** -1.5
ms_l = (10.0 * Ml ** -2.5 * (1 + 2.5 * np.exp(-Ml / 0.12)) + 0.0025)
g_l = 1.15 * ms_l
Y0 = 1e-4
Y1 = 1.15 * (10.0 * 0.1 ** -2.5 * (1 + 2.5 * np.exp(-0.1 / 0.12))
             + 0.0025)

cls_edge_T = [3700, 5200, 6000, 7500, 10000, 30000]
cls_edge_M = [(t / SUN_T) ** (1 / 0.475) for t in cls_edge_T]
CLS_T = {"M": 3050, "K": 4400, "G": 5500, "F": 6750, "A": 8700,
         "B": 17000, "O": 40000}
cls_bounds = [0.1] + cls_edge_M + [300.0]

MASS_SCALE = alt.Scale(type="log", domain=[0.1, 300], nice=False)
AGE_SCALE = alt.Scale(type="log", domain=[Y0, Y1], nice=False)
PX = alt.X("mass:Q", title="mass (suns), log scale",
           scale=MASS_SCALE,
           axis=alt.Axis(values=[0.1, 1, 10, 100],
                         gridColor="#2b303b",
                         labelColor="#c8c8c8", titleColor="#c8c8c8"))
PY = alt.Y("lo:Q", title="age (billion years), log scale",
           scale=AGE_SCALE,
           axis=alt.Axis(values=[1e-3, 1e-2, 0.1, 1, 10, 100, 1000],
                         gridColor="#2b303b",
                         labelColor="#c8c8c8", titleColor="#c8c8c8"))


def region(lo, hi, keep=None):
    df = pd.DataFrame({"mass": Ml, "lo": np.clip(lo, Y0, Y1),
                       "hi": np.clip(hi, Y0, Y1)})
    if keep is not None:
        df = df[keep]
    return df[df["hi"] > df["lo"]]


floor = np.full_like(Ml, Y0)
ceiling = np.full_like(Ml, Y1)
stages = [(region(floor, pre_l), "#4a3118")]                # protostar
for n, blo, bhi in zip("MKGFABO", cls_bounds[:-1], cls_bounds[1:]):
    seg = (Ml >= blo) & (Ml <= bhi)
    stages.append((region(pre_l, ms_l, seg), rgb_str(CLS_T[n])))
stages += [
    (region(ms_l, g_l, Ml >= 0.25), "#c73b25"),             # giant
    (region(ms_l, ceiling, Ml <= 0.25), "#b7aec4"),
    (region(g_l, ceiling, (Ml >= 0.25) & (Ml <= 8)), "#b7aec4"),
    (region(g_l, ceiling, (Ml >= 8) & (Ml <= 18 + 7 * zr)), "#7f7590"),
    (region(g_l, ceiling, Ml >= 18 + 7 * zr), "#4a4256"),   # black hole
]
if Z < 0.001:                                               # pair instability
    stages.append((region(g_l, ceiling, (Ml >= 140) & (Ml <= 260)), "#000000"))
areas = [alt.Chart(df).mark_area(opacity=1, color=col).encode(
             x=PX, y=PY, y2=alt.Y2("hi"))
         for df, col in stages]

sn_keep = Ml >= 8
sn_line = alt.Chart(pd.DataFrame(
    {"mass": Ml[sn_keep], "lo": np.clip(g_l[sn_keep], Y0, Y1)})
    ).mark_line(color="#ccff00", strokeWidth=0.75).encode(x=PX, y=PY)
uni_rule = alt.Chart(pd.DataFrame({"lo": [13.8]})).mark_rule(
    color="#8a2be2", strokeWidth=2, strokeDash=[6, 4],
    opacity=0.8).encode(y=PY)

plane_labels = alt.Chart(pd.DataFrame({
    "mass": [0.7, 2.5, 80],
    "lo":   [1.2e-3, 50.0, 0.1],
    "t":    ["protostars", "white dwarfs", "black holes"],
    "c":    ["#f5f2ea", "#26323c", "#f5f2ea"],
})).mark_text(fontSize=11).encode(
    x=PX, y=PY, text="t:N",
    color=alt.Color("c:N", scale=None, legend=None))
uni_label = alt.Chart(pd.DataFrame(
    {"mass": [0.105], "lo": [16.5]})).mark_text(
    align="left", fontSize=9, color="#8a2be2").encode(
    x=PX, y=PY, text=alt.value("age of the universe"))
ns_label = alt.Chart(pd.DataFrame(
    {"mass": [14.1], "lo": [0.47]})).mark_text(
    fontSize=11, color="#f5f2ea").encode(
    x=PX, y=PY, text=alt.value(["neutron", "stars"]))
giants_label = alt.Chart(pd.DataFrame(
    {"mass": [0.40], "lo": [205.0]})).mark_text(
    fontSize=11, angle=49, color="#c73b25").encode(
    x=PX, y=PY, text=alt.value("giants"))
ms_label = alt.Chart(pd.DataFrame(
    {"mass": [4.2], "lo": [0.06]})).mark_text(
    fontSize=12, angle=47, color="#5a616b").encode(
    x=PX, y=PY, text=alt.value("main sequence"))
sn_label = alt.Chart(pd.DataFrame(
    {"mass": [13], "lo": [0.038]})).mark_text(
    fontSize=10, angle=44, color="#ccff00").encode(
    x=PX, y=PY, text=alt.value("supernova"))

cls_mid = [float(np.sqrt(blo * bhi))
           for blo, bhi in zip(cls_bounds[:-1], cls_bounds[1:])]
cls_lo = list(np.clip([0.548 * m ** -2 for m in cls_mid],
                      1.5e-4, None))
cls_lo[0] = 1.8
cls_mid[-1] = 40.0
cls_lo[-1] = 3.4e-4
cls_labels = alt.Chart(pd.DataFrame({
    "mass": cls_mid, "lo": cls_lo, "t": list("MKGFABO"),
})).mark_text(fontSize=10, fontWeight=600, color="#26323c").encode(
    x=PX, y=PY, text="t:N")

sun_pt = alt.Chart(pd.DataFrame(
    {"mass": [1.0], "lo": [4.6]})).mark_circle(
    size=55, color="#1e7d32", opacity=1).encode(x=PX, y=PY)
sun_txt = alt.Chart(pd.DataFrame(
    {"mass": [1.0], "lo": [1.7]})).mark_text(
    fontSize=11, fontWeight=700, color="#1e7d32").encode(
    x=PX, y=PY, text=alt.value("Sun"))

# your star, riding the slider signals via the filtered grid row
you = alt.Chart(grid).transform_filter(pick).mark_point(
    shape=("M 0 -1 L 0.24 -0.31 L 0.95 -0.31 L 0.38 0.12 L 0.59 0.81"
           " L 0 0.38 L -0.59 0.81 L -0.38 0.12 L -0.95 -0.31"
           " L -0.24 -0.31 Z"),
    filled=True, size=280, color="#FFC300",
    stroke="#8C6A2F", strokeWidth=1.2, opacity=1).encode(
    x=alt.X("mass:Q", scale=MASS_SCALE),
    y=alt.Y("age:Q", scale=AGE_SCALE))

# ---- the HR diagram, with the same star riding the same sliders ------
T_SCALE = alt.Scale(type="log", domain=[200000, 2000], nice=False)  # hot on the left
L_SCALE = alt.Scale(type="log", domain=[1e-4, 1e6], nice=False)
HX = alt.X("temp_K:Q", title="surface temperature (K), log scale, hot on the left",
           scale=T_SCALE,
           axis=alt.Axis(values=[100000, 30000, 10000, 5000, 3000],
                         gridColor="#2b303b", labelColor="#c8c8c8",
                         titleColor="#c8c8c8", format=","))
HY = alt.Y("lum:Q", title="luminosity (suns), log scale", scale=L_SCALE,
           axis=alt.Axis(values=[1e-4, 1e-2, 1, 1e2, 1e4, 1e6], format="~e",
                         gridColor="#2b303b", labelColor="#c8c8c8",
                         titleColor="#c8c8c8"))
band_M = np.geomspace(0.1, 10 ** 2.45, 200)
band = pd.DataFrame({"lum": band_M ** 3.5, "temp_K": SUN_T * band_M ** 0.475})
band = band[(band["lum"] <= 1e6)]
ms_band = alt.Chart(band).mark_line(strokeWidth=14, opacity=0.35,
                                    color="#8d9aa8", strokeCap="round").encode(
    x=HX, y=HY)
hr_labels = alt.Chart(pd.DataFrame({
    "temp_K": [9000, 3900, 30000], "lum": [8e2, 2e4, 2e-3],
    "t": ["main sequence", "giants", "white dwarfs"],
    "c": ["#c8c8c8", "#c73b25", "#b7aec4"]})).mark_text(fontSize=11).encode(
    x=HX, y=HY, text="t:N", color=alt.Color("c:N", scale=None, legend=None))
hr_sun = alt.Chart(pd.DataFrame({"temp_K": [SUN_T], "lum": [1.0]})).mark_circle(
    size=55, color="#1e7d32", opacity=1).encode(x=HX, y=HY)
hr_sun_txt = alt.Chart(pd.DataFrame({"temp_K": [SUN_T], "lum": [0.25]})).mark_text(
    fontSize=11, fontWeight=700, color="#1e7d32").encode(
    x=HX, y=HY, text=alt.value("Sun"))
hr_you = alt.Chart(grid).transform_filter(pick).transform_filter(
    "isValid(datum.lum) && isValid(datum.temp_K)").mark_point(
    shape=("M 0 -1 L 0.24 -0.31 L 0.95 -0.31 L 0.38 0.12 L 0.59 0.81"
           " L 0 0.38 L -0.59 0.81 L -0.38 0.12 L -0.95 -0.31"
           " L -0.24 -0.31 Z"),
    filled=True, size=280, color="#FFC300",
    stroke="#8C6A2F", strokeWidth=1.2, opacity=1).encode(x=HX, y=HY)
hr = alt.layer(ms_band, hr_labels, hr_sun, hr_sun_txt, hr_you).properties(
    width=470, height=440,
    title=alt.Title("Hertzsprung-Russell diagram", color="#f0f0f0"))

plane = alt.layer(
    *areas, sn_line, uni_rule, plane_labels, uni_label, ns_label,
    giants_label, ms_label, sn_label, cls_labels, sun_pt, sun_txt,
    you,
).properties(width=470, height=440,
             title=alt.Title("Stellar mass-age phase plane",
                             color="#f0f0f0"))

chart = alt.vconcat(
    alt.hconcat(portrait, hr),
    plane,
).add_params(
    m_sel, a_sel).configure(background="transparent").configure_view(
    fill="transparent", stroke=None)

st.altair_chart(chart, width="content")

with st.expander("How to read this app"):
    st.markdown("""
- **Portrait (top left):** the star's colour comes from its surface temperature (black-body colour);
  its size is drawn on a log scale. The gold ring is the Sun's size for comparison.
- **HR diagram (top right):** hot stars on the left, bright stars at the top. The grey band is the
  main sequence; giants move up and right, white dwarfs drop down and left.
- **Phase plane (bottom):** every mass and age, coloured by what the star is at that moment.
- **Metallicity:** metal-poor stars are slightly brighter, and below Z = 0.001 the most massive stars
  (140-260 suns) blow themselves apart and leave no remnant.
""")
# ---- 3D: every star in the model, in mass-age-luminosity space ---------
st.markdown("### 3D stellar landscape")
st.caption("Every mass and age in the model, lifted to its luminosity and painted in its own "
           "black-body colour. Drag to rotate, scroll to zoom, hover a point for its phase. "
           "The main sequence is the bright sloping shelf; giants rise above it before the "
           "stars fall to white dwarfs. Neutron stars, black holes and supernovae have no "
           "plotted luminosity, so they leave the landscape.")
land = grid.dropna(subset=["lum", "temp_K"])
fig3d = go.Figure(go.Scatter3d(
    x=land["lm"], y=land["la"], z=np.log10(land["lum"]),
    mode="markers",
    marker=dict(size=2.6, color=land["colour"], opacity=0.85),
    text=[f"{ph}<br>{ma}<br>{t}" for ph, ma, t in zip(land["phase"], land["massage"], land["temp"])],
    hoverinfo="text"))
axis = dict(gridcolor="rgba(150,120,255,.25)", backgroundcolor="rgba(0,0,0,0)",
            color="#c9c6f0", showbackground=True, zerolinecolor="rgba(150,120,255,.4)")
fig3d.update_layout(
    height=620, paper_bgcolor="rgba(5,3,20,0.6)", margin=dict(l=0, r=0, t=10, b=0),
    scene=dict(xaxis=dict(title="log10 mass (suns)", **axis),
               yaxis=dict(title="log10 age (Gyr)", **axis),
               zaxis=dict(title="log10 luminosity (suns)", **axis),
               camera=dict(eye=dict(x=1.6, y=-1.5, z=0.9)), aspectmode="manual",
               aspectratio=dict(x=1.2, y=1.2, z=0.8)),
    font=dict(color="#e8e8ff"))
st.plotly_chart(fig3d, theme=None, width="stretch")

st.markdown('<div class="foot">STELLARIS · built on the 36104 AppStar starter · '
            'Streamlit + Altair (Vega-Lite parameters keep mass and age live in the browser)</div>',
            unsafe_allow_html=True)
