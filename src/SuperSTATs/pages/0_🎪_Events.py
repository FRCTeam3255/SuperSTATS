from SuperSTATs.utils.tba import _api
from SuperSTATs.utils import constants
import streamlit as st


st.title("🎪 Events")
year = st.number_input(
    "Year",
    value=constants.CURRENT_YEAR,
    min_value=1992,
    max_value=constants.CURRENT_YEAR,
    step=1,
)
events_endpoint = f"/events/{year}/simple"
events = _api.get_data(events_endpoint, as_dataframe=True)
events
