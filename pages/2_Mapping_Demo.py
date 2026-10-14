from urllib.error import URLError

import pandas as pd
import pydeck as pdk
import streamlit as st

import neon_theme as nt

st.set_page_config(page_title="HYPERDECK | Mapping Demo", page_icon="🌍", layout="wide")
nt.apply("Mapping Demo", "Mapping Demo",
         "This demo shows how to use st.pydeck_chart to display geospatial data: "
         "San Francisco bike rentals and BART stations in 3D. Drag to pan, right-drag (or "
         "Ctrl + drag) to tilt and rotate, scroll to zoom.")
st.sidebar.header("Mapping Demo")


@st.cache_data
def from_data_file(filename):
    url = (
        "http://raw.githubusercontent.com/streamlit/"
        "example-data/master/hello/v1/%s" % filename
    )
    return pd.read_json(url)


try:
    ALL_LAYERS = {
        "Bike Rentals": pdk.Layer(
            "HexagonLayer",
            data=from_data_file("bike_rental_stats.json"),
            get_position=["lon", "lat"],
            radius=200,
            elevation_scale=4,
            elevation_range=[0, 1000],
            extruded=True,
            pickable=True,
            color_range=[[0, 240, 255], [80, 130, 255], [157, 78, 221],
                         [220, 60, 200], [255, 46, 151], [182, 255, 59]],
        ),
        "Bart Stop Exits": pdk.Layer(
            "ScatterplotLayer",
            data=from_data_file("bart_stop_stats.json"),
            get_position=["lon", "lat"],
            get_color=[255, 46, 151, 190],
            get_radius="[exits]",
            radius_scale=0.05,
        ),
        "Bart Stop Names": pdk.Layer(
            "TextLayer",
            data=from_data_file("bart_stop_stats.json"),
            get_position=["lon", "lat"],
            get_text="name",
            get_color=[230, 230, 255, 230],
            get_size=15,
            get_alignment_baseline="'bottom'",
        ),
        "Outbound Flow": pdk.Layer(
            "ArcLayer",
            data=from_data_file("bart_path_stats.json"),
            get_source_position=["lon", "lat"],
            get_target_position=["lon2", "lat2"],
            get_source_color=[0, 240, 255, 180],
            get_target_color=[255, 46, 151, 180],
            auto_highlight=True,
            width_scale=0.0001,
            get_width="outbound",
            width_min_pixels=3,
            width_max_pixels=30,
        ),
    }
    st.sidebar.markdown("### Map Layers")
    selected_layers = [
        layer
        for layer_name, layer in ALL_LAYERS.items()
        if st.sidebar.checkbox(layer_name, True)
    ]
    if selected_layers:
        st.pydeck_chart(
            pdk.Deck(
                map_style="dark",
                initial_view_state={
                    "latitude": 37.76,
                    "longitude": -122.4,
                    "zoom": 11,
                    "pitch": 50,
                    "bearing": -15,
                },
                layers=selected_layers,
            ),
            height=600,
        )
    else:
        st.error("Please choose at least one layer above.")
except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
    """
        % e.reason
    )

nt.footer()
