import time

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

import neon_theme as nt

st.set_page_config(page_title="HYPERDECK | Plotting Demo", page_icon="📈", layout="wide")
nt.apply("Plotting Demo", "Plotting Demo",
         "This demo illustrates a combination of plotting and animation with Streamlit. "
         "We're generating a bunch of random numbers in a loop for around 5 seconds. Enjoy!")
st.sidebar.header("Plotting Demo")

progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()
chart = st.empty()


def draw(values):
    df = pd.DataFrame({"step": np.arange(len(values)), "value": values})
    line = alt.Chart(df).mark_line(color=nt.CYAN, strokeWidth=2.5).encode(
        x=alt.X("step:Q", title="step"), y=alt.Y("value:Q", title="random walk"))
    glow = alt.Chart(df).mark_line(color=nt.CYAN, strokeWidth=10, opacity=0.15).encode(
        x="step:Q", y="value:Q")
    head = alt.Chart(df.tail(1)).mark_circle(size=140, color=nt.LIME).encode(x="step:Q", y="value:Q")
    chart.altair_chart(nt.neon_chart((glow + line + head).properties(height=420)),
                       width="stretch")


data = np.random.randn(1, 1)
draw(data[:, 0])

for i in range(1, 101):
    new_rows = data[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
    data = np.concatenate([data, new_rows])
    status_text.text("%i%% Complete" % i)
    draw(data[:, 0])
    progress_bar.progress(i)
    time.sleep(0.05)

progress_bar.empty()

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")
nt.footer()
