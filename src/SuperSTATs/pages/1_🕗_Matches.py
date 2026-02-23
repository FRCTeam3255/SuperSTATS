from SuperSTATs import load_v2
import streamlit as st

st.header("🕗 Matches")
matches = load_v2.current_event(as_simple=True)
matches = matches.set_index("Match Name")[
    ["red.team_keys", "blue.team_keys", "red.score", "blue.score", "🏆"]
].rename(
    columns={
        "red.team_keys": "🔴 Teams",
        "blue.team_keys": "🔵 Teams",
        "red.score": "🔴 Score",
        "blue.score": "🔵 Score",
    }
)
matches
