import pandas as pd
import streamlit as st


CURRENT_YEAR = pd.Timestamp.now().year

# Google Sheets
DEFAULT_GSHEET_DOC_ID = st.secrets["GSHEET_DOC_ID"]
DEFAULT_EVENT_KEY = st.secrets["DEFAULT_EVENT_KEY"]
RAW_INPUT_SHEET_ID = st.secrets["GID_RAW"]
RAW_PICKED_SHEET_ID = st.secrets["GID_PICKED"]

# TBA API
ROOT_TBA_URL = "https://www.thebluealliance.com/api/v3"
TBA_API_KEY = st.secrets["TBA_API"]

# Plotting
PIXEL_PER_TEAM = 40
MIN_HEIGHT = 200
