import pandas as pd

import streamlit as st
from SuperSTATs.utils import gsheets, plots, tba
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
    show_team_numbers = col1.toggle("Show Team Numbers", True)
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

# ==== DATA Download ====
raw_sn_df = gsheets.get_stats_inputs(as_points=as_points)
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

# Split red and blue teams for separate ranking
red_agg_data = agg_data.loc[agg_data.index.isin(selected_match["🔴 Teams"])]
blue_agg_data = agg_data.loc[agg_data.index.isin(selected_match["🔵 Teams"])]
agg_data_w_rank_red = gsheets.add_team_num_ranks(
    df=red_agg_data.assign(emoji=""),
    tba_rank=tba_rank,
    emoji_or_name=tba_team_info[["nickname"]],
    show_sn_rank=False,
)
agg_data_w_rank_blue = gsheets.add_team_num_ranks(
    df=blue_agg_data.assign(emoji=""),
    tba_rank=tba_rank,
    emoji_or_name=tba_team_info[["nickname"]],
    show_sn_rank=False,
)

# ==== Outputs ====
red_col, blue_col = st.columns(2)


def display_alliance_metrics(alliance_emoji, selected_match, agg_data_w_rank):
    st.subheader(f"{alliance_emoji} Alliances {alliance_emoji}")
    st.metric("Projected Score", round(agg_data_w_rank.sum(numeric_only=True).sum()))
    st.write("Actual:", selected_match[f"{alliance_emoji} Score"])
    average_score_by_team = (
        agg_data_w_rank.reset_index()
        .set_index(["team_num_ranks", "nickname"])
        .sum(numeric_only=True, axis=1)
        .rename("Avg Score")
        .reset_index()
        .rename(columns={"team_num_ranks": "", "nickname": "Team"})
    )
    average_score_by_team = average_score_by_team[["", "Avg Score", "Team"]]

    st.dataframe(
        average_score_by_team,
        column_config={"0": st.column_config.NumberColumn(format="%.2f")},
        hide_index=True,
    )
    st.expander("Projected Score Breakdown", expanded=False).dataframe(
        agg_data_w_rank,
        column_config={"0": st.column_config.NumberColumn(format="%.2f")},
        # hide_index=True,
    )
    plots.hbar(agg_data_w_rank.drop(columns="nickname"), show_y_labels=True)


with red_col:
    display_alliance_metrics("🔴", selected_match, agg_data_w_rank_red)


with blue_col:
    display_alliance_metrics("🔵", selected_match, agg_data_w_rank_blue)


# TODO:
# - [x] Remove S rank
# - [x] Add Average Points per Match to team info and show in table
# - [ ] Lookup chart (balls scored, balls passed, climb)
# - [ ] One drop down per team: Auto balls, Auto Climb, Tele Balls, Tele Passes, End Climb
