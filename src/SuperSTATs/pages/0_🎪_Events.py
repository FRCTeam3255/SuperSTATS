from SuperSTATs import load_v2
import pandas as pd
import streamlit as st

st.title("🎪 Events")
year = st.number_input(
    "Year",
    value=load_v2.current_year,
    min_value=1992,
    max_value=load_v2.current_year,
    step=1,
)
events_endpoint = f"/events/{year}/simple"
events = load_v2.get_data(events_endpoint, as_dataframe=True)
events
