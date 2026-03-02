from typing import Literal

import pandas as pd

import streamlit as st
from SuperSTATs.utils import gsheets, plots, tba

sn_df = gsheets.get_stats_inputs(as_points=True)
tba_rank = tba.get_rankings()

select_phases = st.multiselect("Phase:", gsheets.PHASES, default=gsheets.PHASES)


def aggregate_team_performance(
    df: pd.DataFrame, level: Literal["Phase", "Metric"]
) -> pd.DataFrame:
    grouped = (
        df[gsheets.PHASES]
        .T.groupby(level=level)
        .sum()
        .T.groupby("Team")
        .mean()
        .assign(sn_rank=lambda x: x.sum(axis=1).rank(ascending=False).astype(int))
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


grouped = aggregate_team_performance(sn_df, level="Phase")
ungrouped = aggregate_team_performance(sn_df, level="Metric")
grouped = add_team_num_ranks(tba_rank, grouped)
ungrouped = add_team_num_ranks(tba_rank, ungrouped)

ungrouped
grouped


# ==== CHART ====
plots.hbar(ungrouped)
plots.hbar(grouped)
