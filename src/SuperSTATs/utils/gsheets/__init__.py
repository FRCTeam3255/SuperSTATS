import pandas as pd

from SuperSTATs.utils import constants
from SuperSTATs.utils.gsheets import _api

PHASES = ["INFO", "AUTO", "TELE", "END"]


def _get_raw_sheet() -> pd.DataFrame:
    df = _api.get_data(constants.RAW_INPUT_SHEET_ID)
    df = df.dropna(subset=["Timestamp"])
    df = df.sort_values(["Match", "Timestamp"], ascending=[True, True])
    df = df.loc[df["Event Key"] == constants.DEFAULT_EVENT_KEY]
    df = df.drop_duplicates(subset=["Team", "Match Type", "Match"])
    return df


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
        names=["Phase", "Metric"],
    )
    if as_points:
        # Apply points multiplier to matching columns
        for col in PHASES:
            for subcol in df[col].columns:
                multiplier = int(subcol.split("_")[-1])
                df[(col, subcol)] = df[(col, subcol)] * multiplier

    # if as_points:
    #     # Apply points multiplier to matching columns
    #     for col in df.columns:
    #         if any(phase in col for phase in PHASES):
    #             parts = col.split("_")
    #             multiplier = int(parts[-1])
    #             df[col] = df[col] * multiplier

    return df
