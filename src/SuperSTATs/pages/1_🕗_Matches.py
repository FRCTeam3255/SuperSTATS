from SuperSTATs.utils import tba
import streamlit as st

st.header("🕗 Matches")
matches = tba.get_matches(as_simple=True)
matches = matches.set_index("Match Name")[
    ["🔴 Teams", "🔵 Teams", "🔴 Score", "🔵 Score", "🏆"]
]
matches
