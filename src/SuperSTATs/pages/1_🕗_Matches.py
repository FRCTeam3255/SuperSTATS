from SuperSTATs.utils import tba, constants
import streamlit as st

st.header(f"🕗 Matches for {constants.DEFAULT_EVENT_KEY}")
matches = tba.get_matches(as_simple=True)
matches = matches.set_index("Match Name")[
    ["🔴 Teams", "🔵 Teams", "🔴 Score", "🔵 Score", "🏆"]
]
matches
