import SuperSTATs.Main as stats
import streamlit as st
import pandas as pd
import tbapy

tba = tbapy.TBA(st.secrets["TBA_API"])

# matches = pd.DataFrame(tba.event_matches("CABB"))
# matches = tba.event_predictions("CASD2022")
# st.text(matches)

year = st.sidebar.number_input("Year:", min_value=0, step=1, value=2023)
events = tba.events(int(year))
event_keys = {}

for event in events:
    name = event["name"]
    key = event["key"]
    event_keys[name] = key

# for key, value in event_keys.items():
#     st.text([key, value])

chosen_event = st.sidebar.selectbox("Event:", event_keys.keys())
chosen_event_key = event_keys[chosen_event]

event_matches = tba.event_matches(chosen_event_key)

st.title(f"{chosen_event} Quals")

quals = {}
for match in event_matches:
    if match["comp_level"] == "qm":
        quals[
            match["match_number"]
        ] = f"🔴 {match['alliances']['red']['team_keys']} 🔴 | 🔵 {match['alliances']['blue']['team_keys']} 🔵".replace(
            "frc", ""
        ).replace(
            "'", ""
        )

for qual in sorted(quals.items()):
    output = f"Q{qual[0]} | {qual[1]}"
    st.text(output)

# st.text(tba.event_alliances("2023casd"))
