from urllib.error import URLError

import altair as alt
import pandas as pd
import streamlit as st

import neon_theme as nt

st.set_page_config(page_title="HYPERDECK | DataFrame Demo", page_icon="📊", layout="wide")
nt.apply("DataFrame Demo", "DataFrame Demo",
         "This demo shows how to use st.write to visualize Pandas DataFrames. "
         "(Data courtesy of the UN Data Explorer.)")
st.sidebar.header("DataFrame Demo")


@st.cache_data
def get_UN_data():
    AWS_BUCKET_URL = "http://streamlit-demo-data.s3-us-west-2.amazonaws.com"
    df = pd.read_csv(AWS_BUCKET_URL + "/agri.csv.gz")
    return df.set_index("Region")


try:
    df = get_UN_data()
    countries = st.multiselect(
        "Choose countries", list(df.index), ["China", "United States of America"]
    )
    if not countries:
        st.error("Please select at least one country.")
    else:
        data = df.loc[countries]
        data /= 1000000.0
        st.write("### Gross Agricultural Production ($B)", data.sort_index())

        data = data.T.reset_index()
        data = pd.melt(data, id_vars=["index"]).rename(
            columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
        )
        palette = [nt.CYAN, nt.PINK, nt.LIME, nt.AMBER, nt.VIOLET, "#7FDBFF", "#FF85C0"]
        area = (
            alt.Chart(data)
            .mark_area(opacity=0.28, line={"strokeWidth": 2.5})
            .encode(
                x=alt.X("year:T", title="year"),
                y=alt.Y("Gross Agricultural Product ($B):Q", stack=None),
                color=alt.Color("Region:N", scale=alt.Scale(range=palette),
                                legend=alt.Legend(orient="top")),
                tooltip=["Region:N", alt.Tooltip("year:T", format="%Y"),
                         alt.Tooltip("Gross Agricultural Product ($B):Q", format=",.1f")],
            )
        )
        st.altair_chart(nt.neon_chart(area.properties(height=420)), width="stretch")
except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
    """
        % e.reason
    )

nt.footer()
