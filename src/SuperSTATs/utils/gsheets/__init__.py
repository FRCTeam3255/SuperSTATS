from typing import Literal

import pandas as pd

from SuperSTATs.utils import constants
from SuperSTATs.utils.gsheets import _api

PHASES = ["INFO", "AUTO", "TELE", "END"]
COLUMN_LEVELS = ["Phase", "Metric"]


def _get_raw_sheet() -> pd.DataFrame:
    df = _api.get_data(constants.RAW_INPUT_SHEET_ID)
    df = df.dropna(subset=["Timestamp"])
    df = df.sort_values(["Match", "Timestamp"], ascending=[True, True])
    df = df.loc[df["Event Key"] == constants.DEFAULT_EVENT_KEY]
    df = df.drop_duplicates(subset=["Team", "Match Type", "Match"])
    return df


# ===========================================================
#               Getting Data
# ===========================================================
def get_stats_inputs(as_points: bool = True) -> pd.DataFrame:
    df = _get_raw_sheet()

    # If team didn't have a non-prac match, keep their prac match. Otherwise, drop prac matches
    teams_w_non_prac = df.loc[~df["Match Type"].str.startswith("Prac")]["Team"].unique()
    non_prac = df.loc[
        df["Team"].isin(teams_w_non_prac) & ~df["Match Type"].str.startswith("Prac")
    ]
    prac = df.loc[~df["Team"].isin(teams_w_non_prac)]
    df = pd.concat([non_prac, prac], axis=0).reset_index(drop=True)

    # Add human columns and formatting
    df = df.astype({"Team": int, "Match": int})
    df["Match Name"] = df["Match Type"] + " " + df["Match"].astype(str)
    df = df.set_index(["Team", "Match Name"])

    # Add column level based on phase prefix (text before first underscore)

    df.columns = pd.MultiIndex.from_tuples(
        [(col.split("_")[0] if "_" in col else "METADATA", col) for col in df.columns],
        names=COLUMN_LEVELS,
    )
    if as_points:
        # Apply points multiplier to matching columns
        for col in PHASES:
            for subcol in df[col].columns:
                multiplier = int(subcol.split("_")[-1])
                df[(col, subcol)] = df[(col, subcol)] * multiplier

    return df


def get_available() -> pd.DataFrame:
    df = _api.get_data(constants.RAW_PICKED_SHEET_ID)
    df["Unavailable"] = df["Unavailable"].str.lower()
    df = df.replace({"x": "🚫"})
    df.loc[df["Team"] == 3255, "Unavailable"] = "💎"
    df = df.astype({"Team": int})
    return df.set_index("Team").rename(columns={"Unavailable": "emoji"})


# ===========================================================
#               Data Processing
# ===========================================================
def aggregate_team_performance(
    df: pd.DataFrame,
    level: Literal["Phase", "Metric"],
    agg_type: Literal["mean", "sum", "median"] = "mean",
) -> pd.DataFrame:
    grouped = (
        df.T.groupby(level=level)
        .sum()
        .T.groupby("Team")
        .describe([0.5, 0.75, 0.9, 0.95, 0.99])
        .xs(agg_type, level=1, axis=1)
        .assign(
            sn_rank=lambda x: (
                x.sum(axis=1).rank(ascending=False, method="dense").astype(int)
            )
        )
    )
    return grouped


def add_team_num_ranks(
    df: pd.DataFrame,
    tba_rank: pd.DataFrame,
    emoji_or_name: pd.DataFrame,
    show_sn_rank: bool = True,
) -> pd.DataFrame:
    df = (
        df.join(tba_rank["rank"], how="left")
        .join(emoji_or_name, how="left")
        .fillna("🟢")
    )
    sn_rank_str = df.index.astype(str) + " | T" if show_sn_rank else ""
    df["team_num_ranks"] = (
        df["emoji"]
        + " "
        + sn_rank_str
        + df["rank"].astype(str).str.zfill(2)
        + " | S"
        + df["sn_rank"].astype(str).str.zfill(2)
    )

    return (
        df.set_index("team_num_ranks")
        .sort_values("sn_rank", ascending=False)
        .drop(columns=["rank", "sn_rank", "emoji"])
    )
