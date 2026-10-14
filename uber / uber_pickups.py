import altair as alt
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

st.set_page_config(page_title="NEONCAB | Uber pickups in NYC", page_icon="🚕",
                   layout="wide")

CYAN, PINK, YELLOW, VIOLET = "#00F5FF", "#FF2E97", "#FFE14D", "#9D4EDD"

# ---------------------------------------------------------------- styling
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;900&family=Inter:wght@400;600&display=swap');
.stApp {{
  background:
    radial-gradient(1200px 600px at 10% -10%, rgba(157,78,221,.28), transparent 60%),
    radial-gradient(900px 500px at 110% 10%, rgba(0,245,255,.18), transparent 60%),
    linear-gradient(180deg, #05010f 0%, #0a0420 60%, #05010f 100%);
  color: #e9e6ff; font-family: 'Inter', sans-serif;
}}
.stApp::before {{                     /* synthwave perspective grid */
  content: ""; position: fixed; left: -50%; right: -50%; bottom: -10%; height: 55%;
  background-image:
    linear-gradient(rgba(255,46,151,.22) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,245,255,.18) 1px, transparent 1px);
  background-size: 60px 60px; transform: perspective(500px) rotateX(62deg);
  animation: gridmove 6s linear infinite; pointer-events: none; z-index: 0;
  mask-image: linear-gradient(to top, black 10%, transparent 90%);
}}
@keyframes gridmove {{ from {{background-position: 0 0;}} to {{background-position: 0 60px;}} }}
header[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 1.2rem; max-width: 1250px; position: relative; z-index: 1; }}
h1, h2, h3, h4 {{ font-family: 'Orbitron', sans-serif !important; letter-spacing: .04em; }}
.navbar {{ display:flex; align-items:center; justify-content:space-between;
  padding: 14px 22px; border-radius: 18px; margin-bottom: 18px;
  background: rgba(20,10,45,.55); backdrop-filter: blur(10px);
  border: 1px solid rgba(0,245,255,.35);
  box-shadow: 0 0 22px rgba(0,245,255,.25), inset 0 0 22px rgba(157,78,221,.18); }}
.brand {{ display:flex; align-items:center; gap:14px; }}
.brand-name {{ font-family:'Orbitron'; font-weight:900; font-size: 28px; letter-spacing:.18em;
  background: linear-gradient(90deg, {CYAN}, {PINK}, {YELLOW}); -webkit-background-clip:text;
  color: transparent; filter: drop-shadow(0 0 10px rgba(255,46,151,.55)); }}
.brand-sub {{ font-size: 12px; color:#a9a3d9; letter-spacing:.22em; text-transform:uppercase; }}
.chip {{ display:inline-block; margin-left:8px; padding:6px 12px; border-radius:999px; font-size:12px;
  border:1px solid rgba(255,46,151,.6); color:#ffd1e8; background: rgba(255,46,151,.08);
  box-shadow: 0 0 10px rgba(255,46,151,.35); }}
.logo {{ animation: spin 9s linear infinite; filter: drop-shadow(0 0 8px {CYAN}); }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
.hero {{ text-align:center; margin: 6px 0 22px; }}
.hero h1 {{ font-size: 46px; margin: 0; line-height:1.1;
  background: linear-gradient(90deg, #fff, {CYAN} 40%, {PINK}); -webkit-background-clip:text; color:transparent;
  text-shadow: 0 0 30px rgba(0,245,255,.25); }}
.hero p {{ color:#c8c2f0; font-size: 16px; margin-top: 10px; }}
.kpis {{ display:grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 6px 0 18px; perspective: 900px; }}
.kpi {{ padding: 18px 20px; border-radius: 18px; background: rgba(15,8,38,.7);
  border: 1px solid rgba(157,78,221,.55); transform-style: preserve-3d;
  transition: transform .35s ease, box-shadow .35s ease;
  box-shadow: 0 10px 30px rgba(0,0,0,.45), 0 0 18px rgba(157,78,221,.25); }}
.kpi:hover {{ transform: rotateX(8deg) rotateY(-10deg) translateZ(18px);
  box-shadow: 0 18px 40px rgba(0,0,0,.55), 0 0 28px rgba(0,245,255,.55); border-color: {CYAN}; }}
.kpi .lab {{ font-size: 11px; letter-spacing:.2em; text-transform:uppercase; color:#a9a3d9; }}
.kpi .val {{ font-family:'Orbitron'; font-size: 30px; font-weight: 900; margin-top: 6px; }}
.kpi .note {{ font-size: 12px; color:#8f88c4; margin-top: 4px; }}
.panel {{ padding: 16px 20px; border-radius: 18px; background: rgba(15,8,38,.6);
  border: 1px solid rgba(0,245,255,.25); margin-bottom: 14px; }}
.stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
.stTabs [data-baseweb="tab"] {{ background: rgba(20,10,45,.6); border-radius: 12px 12px 0 0;
  padding: 10px 18px; border: 1px solid rgba(157,78,221,.4); color:#d8d3ff; font-family:'Orbitron'; font-size: 13px; }}
.stTabs [aria-selected="true"] {{ border-color: {CYAN}; box-shadow: 0 0 16px rgba(0,245,255,.45); color:#fff; }}
div[data-testid="stSlider"] label p, div[data-testid="stCheckbox"] label p {{ color:#e9e6ff; font-weight:600; }}
.foot {{ text-align:center; color:#7e77b3; font-size:12px; margin-top: 26px; }}
@media (max-width: 800px) {{ .kpis {{ grid-template-columns: repeat(2, 1fr); }} .hero h1 {{ font-size: 32px; }} }}
</style>
""", unsafe_allow_html=True)

LOGO = f"""
<svg class="logo" width="46" height="46" viewBox="0 0 64 64">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{PINK}"/></linearGradient></defs>
  <circle cx="32" cy="32" r="28" fill="none" stroke="url(#g)" stroke-width="3" stroke-dasharray="6 5"/>
  <path d="M18 38 L24 26 H40 L46 38 Z" fill="none" stroke="{YELLOW}" stroke-width="3" stroke-linejoin="round"/>
  <circle cx="24" cy="40" r="4" fill="{CYAN}"/><circle cx="40" cy="40" r="4" fill="{PINK}"/>
</svg>"""

st.markdown(f"""
<div class="navbar">
  <div class="brand">{LOGO}
    <div><div class="brand-name">NEONCAB</div>
    <div class="brand-sub">Uber pickups · New York City · September 2014</div></div>
  </div>
  <div><span class="chip">st.cache_data</span><span class="chip">3D hex map</span><span class="chip">live slider</span></div>
</div>
<div class="hero">
  <h1>Uber pickups in NYC</h1>
  <p>When and where does New York call a ride? Slide through the 24 hours and watch the city light up.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------- data (tutorial)
DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
            'streamlit-demo-data/uber-raw-data-sep14.csv.gz')


@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data


data_load_state = st.text('Loading data...')
data = load_data(10000)
data_load_state.text("Done! (using st.cache_data)")
data["hour"] = data[DATE_COLUMN].dt.hour

# ---------------------------------------------------------------- controls
c1, c2 = st.columns([3, 1])
with c1:
    hour_to_filter = st.slider('hour', 0, 23, 17)      # Some number in the range 0-23
with c2:
    st.write("")
    show_raw = st.checkbox('Show raw data')

filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]
hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0, 24))[0]
peak_hour = int(np.argmax(hist_values))
share = 100 * len(filtered_data) / len(data)

st.markdown(f"""
<div class="kpis">
  <div class="kpi"><div class="lab">Pickups loaded</div>
    <div class="val" style="color:{CYAN}">{len(data):,}</div><div class="note">first 10,000 rows, Sep 2014</div></div>
  <div class="kpi"><div class="lab">Selected hour</div>
    <div class="val" style="color:{YELLOW}">{hour_to_filter:02d}:00</div><div class="note">{len(filtered_data):,} pickups</div></div>
  <div class="kpi"><div class="lab">Share of the day</div>
    <div class="val" style="color:{PINK}">{share:.1f}%</div><div class="note">an even spread would be 4.2%</div></div>
  <div class="kpi"><div class="lab">Peak hour</div>
    <div class="val" style="color:{VIOLET}">{peak_hour:02d}:00</div><div class="note">{hist_values[peak_hour]:,} pickups</div></div>
</div>
""", unsafe_allow_html=True)

hist_df = pd.DataFrame({"hour": np.arange(24), "pickups": hist_values})
hist_df["selected"] = np.where(hist_df["hour"] == hour_to_filter, "selected hour", "other hours")
NEON = alt.Scale(domain=["selected hour", "other hours"], range=[YELLOW, CYAN])


def neon(chart):
    return chart.configure(background="transparent").configure_view(stroke=None).configure_axis(
        labelColor="#c8c2f0", titleColor="#e9e6ff", gridColor="rgba(157,78,221,.25)",
        domainColor="#5b4f99", tickColor="#5b4f99").configure_legend(
        labelColor="#e9e6ff", titleColor="#e9e6ff")


tab_city, tab_pulse, tab_clock, tab_map, tab_raw = st.tabs(
    ["🌆  3D city", "📊  Hourly pulse", "🕒  24-hour clock", "🗺️  Pickup map", "🧾  Raw data"])

# ---------------------------------------------------------------- 3D hexagon city
with tab_city:
    st.subheader(f'3D pickup density at {hour_to_filter}:00')
    st.caption("Each hexagon column is ~200 m across; its height and colour show how many pickups "
               "started there. Drag to rotate (right-click or Ctrl + drag), scroll to zoom.")
    layer = pdk.Layer(
        "HexagonLayer", data=filtered_data[["lat", "lon"]], get_position=["lon", "lat"],
        radius=200, elevation_scale=6, elevation_range=[0, 1200], extruded=True, pickable=True,
        coverage=0.9, auto_highlight=True,
        color_range=[[0, 245, 255], [80, 120, 255], [157, 78, 221], [220, 60, 200],
                     [255, 46, 151], [255, 225, 77]])
    st.pydeck_chart(pdk.Deck(
        map_style="dark",
        initial_view_state=pdk.ViewState(latitude=40.73, longitude=-73.98, zoom=10.6,
                                         pitch=55, bearing=-20),
        layers=[layer], tooltip={"text": "{elevationValue} pickups"}), height=560)

# ---------------------------------------------------------------- histogram (tutorial)
with tab_pulse:
    st.subheader('Number of pickups by hour')
    bars = alt.Chart(hist_df).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
        x=alt.X("hour:O", title="hour of day", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("pickups:Q", title="pickups"),
        color=alt.Color("selected:N", scale=NEON, legend=alt.Legend(orient="top", title=None)),
        tooltip=["hour", "pickups"])
    glow = alt.Chart(hist_df).mark_line(color=PINK, strokeWidth=2.5, interpolate="monotone",
                                        point=alt.OverlayMarkDef(color=PINK, size=30)).encode(
        x="hour:O", y="pickups:Q")
    st.altair_chart(neon((bars + glow).properties(height=380)), width="stretch")
    st.caption("Bars: pickups starting in each hour. The highlighted bar follows the hour slider.")

# ---------------------------------------------------------------- radial clock
with tab_clock:
    st.subheader('The city as a 24-hour clock')
    clock_df = hist_df.assign(start=hist_df["hour"] / 24 * 2 * np.pi,
                              label=[f"{h:02d}" for h in hist_df["hour"]])
    radial = alt.Chart(clock_df).mark_arc(innerRadius=60, stroke="#05010f", strokeWidth=2).encode(
        theta=alt.Theta("hour:O", sort="ascending"),
        radius=alt.Radius("pickups:Q", scale=alt.Scale(type="sqrt", zero=True, rangeMin=60)),
        color=alt.condition(f"datum.hour == {hour_to_filter}", alt.value(YELLOW),
                            alt.Color("pickups:Q", legend=None,
                                      scale=alt.Scale(range=[VIOLET, PINK, CYAN]))),
        tooltip=["hour", "pickups"])
    labels = alt.Chart(clock_df).mark_text(radiusOffset=18, color="#c8c2f0", fontSize=11).encode(
        theta=alt.Theta("hour:O", sort="ascending"),
        radius=alt.Radius("pickups:Q", scale=alt.Scale(type="sqrt", zero=True, rangeMin=60)),
        text="label:N")
    st.altair_chart(neon((radial + labels).properties(height=480)), width="stretch")
    st.caption("Midnight at the top, running clockwise. Wedge length shows pickups in that hour.")

# ---------------------------------------------------------------- map (tutorial)
with tab_map:
    st.subheader('Map of all pickups at %s:00' % hour_to_filter)
    st.map(filtered_data, color=PINK, size=40)

# ---------------------------------------------------------------- raw data (tutorial)
with tab_raw:
    if show_raw:
        st.subheader('Raw data')
        st.write(data)
    else:
        st.info("Tick **Show raw data** above the cards to see the table.")

st.markdown('<div class="foot">Data: Uber pickups in New York City, September 2014 '
            '(FiveThirtyEight / NYC TLC, via the Streamlit demo dataset). '
            'Built with Streamlit, Altair and pydeck.</div>', unsafe_allow_html=True)
