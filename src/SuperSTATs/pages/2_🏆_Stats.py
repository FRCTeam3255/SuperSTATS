from typing import Literal

import pandas as pd

import streamlit as st
from SuperSTATs.utils import gsheets, plots, tba

# ==== DATA PREP ====
raw_sn_df = gsheets.get_stats_inputs(as_points=True)
tba_rank = tba.get_rankings()

# ==== UI for filtering =====
chart_type = st.radio("View by:", gsheets.COLUMN_LEVELS, horizontal=True)
selected_phases = st.multiselect("Phase:", gsheets.PHASES, default=gsheets.PHASES)
metrics = raw_sn_df[selected_phases].columns.get_level_values("Metric").unique()
selected_metrics = st.multiselect("Metric:", metrics, default=metrics)
idx = pd.IndexSlice
sn_df = raw_sn_df.loc[:, idx[selected_phases, selected_metrics]]


def aggregate_team_performance(
    df: pd.DataFrame, level: Literal["Phase", "Metric"]
) -> pd.DataFrame:
    grouped = (
        df.T.groupby(level=level)
        .sum()
        .T.groupby("Team")
        .mean()
        .assign(
            sn_rank=lambda x: (
                x.sum(axis=1).rank(ascending=False, method="dense").astype(int)
            )
        )
    )
    return grouped


def add_team_num_ranks(tba_rank, df):
    df = df.join(tba_rank["rank"], how="left")
    df["team_num_ranks"] = (
        df.index.astype(str)
        + " | T"
        + df["rank"].astype(str).str.zfill(2)
        + " | S"
        + df["sn_rank"].astype(str).str.zfill(2)
    )

    return (
        df.set_index("team_num_ranks")
        .sort_values("sn_rank", ascending=False)
        .drop(columns=["rank", "sn_rank"])
    )


agg_data = aggregate_team_performance(sn_df, level=chart_type)
agg_data_w_rank = add_team_num_ranks(tba_rank, agg_data)


# ==== CHART ====
plots.hbar(agg_data_w_rank)

# ==== TABLE ====
agg_data_w_rank
