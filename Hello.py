import streamlit as st

import neon_theme as nt

st.set_page_config(
    page_title="HYPERDECK | Hello",
    page_icon="👋",
    layout="wide",
)

nt.apply("Home", "Welcome to Streamlit!",
         "Streamlit is an open-source app framework built specifically for Machine Learning and "
         "Data Science projects. <b>👈 Select a demo from the sidebar</b> to see some examples of "
         "what Streamlit can do.")

st.sidebar.success("Select a demo above.")

# A 3D rotating cube whose faces name the three demo pages.
st.markdown(f"""
<style>
.cube-stage {{ height: 230px; display:flex; align-items:center; justify-content:center; perspective: 900px; }}
.cube {{ width: 150px; height: 150px; position: relative; transform-style: preserve-3d;
  animation: cuberot 16s linear infinite; }}
.cube div {{ position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
  font-family:'Orbitron'; font-weight:900; font-size: 15px; letter-spacing:.08em; text-align:center;
  background: rgba(14,7,36,.94); backface-visibility: hidden; border: 2px solid {nt.CYAN};
  box-shadow: 0 0 22px rgba(0,240,255,.45), inset 0 0 26px rgba(255,46,151,.25); color:#fff; }}
.f1 {{ transform: translateZ(75px); }}           .f2 {{ transform: rotateY(90deg) translateZ(75px); border-color:{nt.PINK} !important; }}
.f3 {{ transform: rotateY(180deg) translateZ(75px); border-color:{nt.LIME} !important; }}
.f4 {{ transform: rotateY(-90deg) translateZ(75px); border-color:{nt.VIOLET} !important; }}
.f5 {{ transform: rotateX(90deg) translateZ(75px); }} .f6 {{ transform: rotateX(-90deg) translateZ(75px); }}
@keyframes cuberot {{ from {{ transform: rotateX(-18deg) rotateY(0deg); }} to {{ transform: rotateX(-18deg) rotateY(360deg); }} }}
</style>
<div class="cube-stage"><div class="cube">
  <div class="f1">📈<br>PLOTTING</div><div class="f2">🌍<br>MAPPING</div>
  <div class="f3">📊<br>DATAFRAME</div><div class="f4">⚡<br>STREAMLIT</div>
  <div class="f5"></div><div class="f6"></div>
</div></div>
<div class="tiles">
  <div class="tile"><div class="ico">📈</div><div class="t">Plotting Demo</div>
    <div class="d">A line chart that grows live: random walks generated in a loop and streamed onto the chart, with a progress bar in the sidebar.</div></div>
  <div class="tile"><div class="ico">🌍</div><div class="t">Mapping Demo</div>
    <div class="d">A 3D pydeck map of San Francisco: bike-rental hexagons, BART stop exits and outbound flows. Toggle the layers in the sidebar.</div></div>
  <div class="tile"><div class="ico">📊</div><div class="t">DataFrame Demo</div>
    <div class="d">UN gross agricultural production by country. Pick countries to compare in a table and an area chart.</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="glass">
<h3 style="margin-top:0">Want to learn more?</h3>

- Check out <a href="https://streamlit.io">streamlit.io</a>
- Jump into our <a href="https://docs.streamlit.io">documentation</a>
- Ask a question in our <a href="https://discuss.streamlit.io">community forums</a>

<h3>See more complex demos</h3>

- Use a neural net to <a href="https://github.com/streamlit/demo-self-driving">analyze the Udacity Self-driving Car Image Dataset</a>
- Explore a <a href="https://github.com/streamlit/demo-uber-nyc-pickups">New York City rideshare dataset</a>
</div>
""", unsafe_allow_html=True)

nt.footer()
