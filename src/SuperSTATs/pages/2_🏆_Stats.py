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
sn_avail = gsheets.get_available()


# ==== Settings UI =====
settings_and_filter_expander = st.expander("Settings & Filters", expanded=False)
with settings_and_filter_expander:
    col1, col2, col3, col4 = st.columns(4)
    show_team_numbers = col1.toggle("Show Team Numbers", True)
    chart_type = col2.radio("View by:", gsheets.COLUMN_LEVELS, horizontal=True, index=1)
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
agg_data_w_rank = gsheets.add_team_num_ranks(
    df=agg_data,
    tba_rank=tba_rank,
    emoji_or_name=sn_avail,
)

# ==== Outputs ====
plots.hbar(agg_data_w_rank, show_y_labels=show_team_numbers)
