import SuperSTATs.Main as stats
import streamlit as st
import pandas as pd
import tbapy

tba = tbapy.TBA(st.secrets["TBA_API"])


def alter_col(match_num):
    return f"Quals {match_num}"


year = st.sidebar.number_input("Year:", min_value=0, step=1, value=2023)
events = tba.events(int(year))
event_keys = {}

for event in events:
    name = event["name"]
    key = event["key"]
    event_keys[name] = key

chosen_event = st.sidebar.selectbox("Event:", event_keys.keys())
chosen_event_key = event_keys[chosen_event]

event_matches = tba.event_matches(chosen_event_key)

st.title(f"{chosen_event} Qualifications")

quals = {}
for match in event_matches:
    if match["comp_level"] == "qm":
        red_teams = match["alliances"]["red"]["team_keys"]
        blue_teams = match["alliances"]["blue"]["team_keys"]

        red_teams = [team.replace("frc", "").replace("'", "") for team in red_teams]
        blue_teams = [team.replace("frc", "").replace("'", "") for team in blue_teams]

        quals[match["match_number"]] = {
            "Red 1": red_teams[0],
            "Red 2": red_teams[1],
            "Red 3": red_teams[2],
            "Blue 1": blue_teams[0],
            "Blue 2": blue_teams[1],
            "Blue 3": blue_teams[2],
        }

df = pd.DataFrame(quals).T.reset_index()
df.columns = ["Match", "Red 1", "Red 2", "Red 3", "Blue 1", "Blue 2", "Blue 3"]
df = df.sort_values(by="Match").reset_index(drop=True)
df["Match"] = df["Match"].apply(alter_col)

global_df = None
if st.button("Assign Dataframe", use_container_width=True):
    global_df = df

    # if "global_match_df" not in st.session_state:
    st.session_state.global_match_df = global_df

st.table(st.session_state.global_match_df)
