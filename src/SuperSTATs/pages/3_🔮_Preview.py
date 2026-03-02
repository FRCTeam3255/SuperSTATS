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
match_list = matches.index
match_selection = st.selectbox("Select a Match:", match_list)
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
    df=red_agg_data.assign(emoji="🔴"),
    tba_rank=tba_rank,
    emoji_or_name=tba_team_info[["nickname"]],
)
agg_data_w_rank_blue = gsheets.add_team_num_ranks(
    df=blue_agg_data.assign(emoji="🔵"),
    tba_rank=tba_rank,
    emoji_or_name=tba_team_info[["nickname"]],
)

# ==== Outputs ====
red_col, blue_col = st.columns(2)

with red_col:
    st.subheader("🔴 Red Alliance 🔴")
    st.table(agg_data_w_rank_red["nickname"])
    sub_total_red = agg_data_w_rank_red.sum(numeric_only=True)
    st.metric("Projected Score", round(sub_total_red.sum()))
    st.write("Actual:", selected_match["🔴 Score"])
    st.expander("Projected Score Breakdown", expanded=False).dataframe(
        sub_total_red,
        column_config={"0": st.column_config.NumberColumn(format="%.2f")},
    )


with blue_col:
    st.subheader("🔵 Blue Alliance 🔵")
    st.table(agg_data_w_rank_blue["nickname"])
    sub_total_blue = agg_data_w_rank_blue.sum(numeric_only=True)
    st.metric("Projected Score", round(sub_total_blue.sum()))
    st.write("Actual:", selected_match["🔵 Score"])
    st.expander("Projected Score Breakdown", expanded=False).dataframe(
        sub_total_blue,
        column_config={"0": st.column_config.NumberColumn(format="%.2f")},
    )


agg_data_w_rank = pd.concat([agg_data_w_rank_red, agg_data_w_rank_blue]).drop(
    columns="nickname"
)
plots.hbar(agg_data_w_rank, show_y_labels=show_team_numbers)
