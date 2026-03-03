from SuperSTATs.utils.constants import DEFAULT_EVENT_KEY
from SuperSTATs.utils import df_utils
from SuperSTATs.utils.tba._api import get_data


import pandas as pd


def _set_match_name(row):
    """
    Sets the name for a match based on the given row.

    Parameters:
    - row: A dictionary representing a row of match data.

    Returns:
    - match_name: A string representing the name of the match.
    """
    if row["comp_level"] == "Playoffs":
        return row["comp_level"] + " " + str(int(row["set_number"]))
    return row["comp_level"] + " " + str(int(row["match_number"]))


def get_matches(
    event_key: str = DEFAULT_EVENT_KEY, as_simple: bool = False
) -> pd.DataFrame:
    endpoint = f"/event/{event_key}/matches" + ("/simple" if as_simple else "")
    df = get_data(endpoint, as_dataframe=True)
    if df is None or df.empty:
        return pd.DataFrame()  # Return empty DataFrame on error
    # Normalize nested JSON columns and clean up the DataFrame
    df = df_utils.normalize_column(df, "alliances")
    if "score_breakdown" in df.columns:
        df = pd.concat(
            [
                df,
                pd.json_normalize(df["score_breakdown"]).add_prefix("score_breakdown."),
            ],
            axis=1,
        ).drop(columns="score_breakdown")

    # Convert comp_level to more readable format
    df["comp_level"] = df["comp_level"].replace(
        {"qm": "Quals", "sf": "Playoffs", "f": "Finals"}
    )

    df["Match Name"] = df.apply(_set_match_name, axis=1)

    # Convert team keys to integers for easier filtering later
    for color in ["red", "blue"]:
        df[f"{color}.team_keys"] = df[f"{color}.team_keys"].apply(
            lambda teams: [int("".join(filter(str.isdigit, x))) for x in teams]
        )

    # Convert time to PST timezone and format as 12 hr string
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True).dt.tz_convert(
        "US/Pacific"
    )
    df["Match Day"] = df["time"].dt.strftime("%D")
    df["Match Time"] = df["time"].dt.strftime("%I:%M %p")
    df["🏆"] = df["winning_alliance"].replace({"red": "🔴", "blue": "🔵", "": "🟪"})
    df = df.rename(
        columns={
            "red.team_keys": "🔴 Teams",
            "blue.team_keys": "🔵 Teams",
            "red.score": "🔴 Score",
            "blue.score": "🔵 Score",
        }
    )

    return df.sort_values("time")


def get_rankings(event_key: str = DEFAULT_EVENT_KEY) -> pd.DataFrame:
    endpoint = f"/event/{event_key}/rankings"
    data = get_data(endpoint, as_dataframe=False)
    if data is None:
        return pd.DataFrame(columns=["Team", "rank"]).set_index("Team")
    df = pd.DataFrame().from_dict(data["rankings"])
    df = df_utils.normalize_column(df, "record")
    df["Team"] = df["team_key"].apply(lambda x: int("".join(filter(str.isdigit, x))))
    return df.sort_values("rank").set_index("Team")


def get_teams(
    event_key: str = DEFAULT_EVENT_KEY, as_simple: bool = True
) -> pd.DataFrame:
    endpoint = f"/event/{event_key}/teams" + ("/simple" if as_simple else "")
    data = get_data(endpoint, as_dataframe=False)
    if data is None:
        return pd.DataFrame(columns=["Team", "nickname"]).set_index("Team")
    df = pd.DataFrame().from_dict(data)
    df["Team"] = df["team_number"]
    return df.set_index("Team")
