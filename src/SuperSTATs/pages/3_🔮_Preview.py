import pandas as pd

import streamlit as st
from SuperSTATs.utils import gsheets, tables, tba
from pathlib import Path

page_name = Path(__file__).stem.split("_", 1)[1].replace("_", " ")
st.title(page_name)
if st.button("Update Page", type="primary", width="stretch"):
    st.rerun()
st.divider()
print(f"{page_name} loaded:")

# === Page Specific Data ===
tba_team_info = tba.get_teams()
matches = tba.get_matches(as_simple=True)
matches = matches.set_index("Match Name")[
    ["🔴 Teams", "🔵 Teams", "🔴 Score", "🔵 Score", "🏆"]
]
# Add "All Teams" column for easier filtering
matches["All Teams"] = matches["🔴 Teams"] + matches["🔵 Teams"]
teams_matches = (
    matches["All Teams"]
    .explode()
    .reset_index()
    .groupby("All Teams")["Match Name"]
    .apply(list)
)
# Filters
col1, col2 = st.columns(2)
team_selection = col1.selectbox(
    "Select a Team:",
    teams_matches.index,
    index=teams_matches.index.get_loc(st.secrets["TEAM_NUMBER"]),
)
match_selection = col2.selectbox("Select a Match:", teams_matches[team_selection])
selected_match = matches.loc[match_selection]
team_subset = selected_match["🔴 Teams"] + selected_match["🔵 Teams"]
st.divider()

# ==== Settings UI =====
settings_and_filter_expander = st.expander("Settings & Filters", expanded=False)
with settings_and_filter_expander:
    col1, col2, col3, col4 = st.columns(4)
    hide_identifiers = col1.toggle("Hide Identifiers", False)
    chart_type = col2.radio("View by:", gsheets.COLUMN_LEVELS, horizontal=True)
    as_points = (
        col3.radio("View as:", ["Points", "Counts"], horizontal=True) == "Points"
    )
    agg_type = col4.selectbox(
        "Aggregation Type:",
        ["min", "mean", "50%", "75%", "90%", "95%", "99%", "max"],
        format_func=str.capitalize,
        index=1,
    )
    trend_matches = st.number_input(
        "Trend window (matches):", min_value=1, max_value=20, value=3, step=1
    )

# ==== DATA Download ====
raw_sn_df = gsheets.get_stats_inputs(as_points=as_points)
sn_avail = gsheets.get_available()
tba_rank = tba.get_rankings()

# ==== Filters UI ====
with settings_and_filter_expander:
    selected_phases = st.multiselect("Phase:", gsheets.PHASES, default=gsheets.PHASES)
    metrics = raw_sn_df[selected_phases].columns.get_level_values("Metric").unique()
    selected_metrics = st.multiselect("Metric:", metrics, default=metrics)
    selected_phases_and_metrics = pd.IndexSlice[selected_phases, selected_metrics]

# ==== Data Processing ====
sn_df = raw_sn_df.loc[:, selected_phases_and_metrics]
agg_data = gsheets.aggregate_team_performance(
    df=sn_df,
    level=chart_type,
    agg_type=agg_type,
)

# ==== Outputs ====
alliances = {"🔴": selected_match["🔴 Teams"], "🔵": selected_match["🔵 Teams"]}
groups = {team: emoji for emoji, teams in alliances.items() for team in teams}

tables.alliance_table(
    alliance_data={
        emoji: agg_data.loc[agg_data.index.isin(teams)]
        for emoji, teams in alliances.items()
    },
    actual={emoji: selected_match[f"{emoji} Score"] for emoji in alliances},
)

tables.team_stats_table(
    agg_data=agg_data.loc[agg_data.index.isin(groups)],
    raw_sn_df=raw_sn_df,
    sn_df=sn_df,
    tba_rank=tba_rank,
    sn_avail=sn_avail,
    chart_type=chart_type,
    trend_matches=trend_matches,
    hide_identifiers=hide_identifiers,
    selectable=True,
    groups=groups,
    team_names=tba_team_info["nickname"],
    key="preview_table",
)


# TODO:
# - [x] Remove S rank
# - [x] Add Average Points per Match to team info and show in table
# - [ ] Lookup chart (balls scored, balls passed, climb)
# - [ ] One drop down per team: Auto balls, Auto Climb, Tele Balls, Tele Passes, End Climb
