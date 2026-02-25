import pandas as pd

from SuperSTATs.utils import constants
from SuperSTATs.utils.gsheets import _api


def _get_raw_sheet():
    df = _api.get_data(constants.RAW_INPUT_SHEET_ID)
    df = df.dropna(subset=["Timestamp"])
    df = df.sort_values(["Match", "Timestamp"], ascending=[True, True])
    df = df.loc[df["Event Key"] == constants.DEFAULT_EVENT_KEY]
    df = df.drop_duplicates(subset=["Team", "Match Type", "Match"])
    return df


def get_stats_inputs(as_points: bool = True):
    df = _get_raw_sheet()

    # If team didn't have a non-prac match, keep their prac match. Otherwise, drop prac matches
    teams_w_non_prac = df.loc[~df["Match Type"].str.startswith("Prac")]["Team"].unique()
    non_prac = df.loc[
        df["Team"].isin(teams_w_non_prac) & ~df["Match Type"].str.startswith("Prac")
    ]
    prac = df.loc[~df["Team"].isin(teams_w_non_prac)]
    df = pd.concat([non_prac, prac], axis=0).reset_index(drop=True)

    if as_points:
        # Apply points multiplier to matching columns
        for col in df.columns:
            parts = col.split("_")
            if len(parts) > 3 and parts[-1].isdigit():
                multiplier = int(parts[-1])
                df[col] = df[col] * multiplier

    return df
