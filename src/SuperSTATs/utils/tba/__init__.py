from datetime import timedelta

from SuperSTATs.utils.constants import DEFAULT_EVENT_KEY
from SuperSTATs.utils import df_utils
from SuperSTATs.utils.tba._api import get_data


import pandas as pd
import streamlit as st


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
    # Best known start: actual if played, else TBA's prediction, else the schedule
    best = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns, UTC]")
    for col in ("actual_time", "predicted_time"):
        if col in df.columns:
            best = best.fillna(pd.to_datetime(df[col], unit="s", utc=True))
    best = best.fillna(df["time"].dt.tz_convert("UTC"))
    df["Start Time"] = best.dt.tz_convert("US/Pacific").dt.strftime("%I:%M %p").str.lstrip("0")
    df["red.score"] = df["red.score"].replace({-1: None})
    df["blue.score"] = df["blue.score"].replace({-1: None})
    df["🏆"] = df["winning_alliance"].replace({"red": "🔴", "blue": "🔵", "": None})
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
    if data is None or not data.get("rankings"):
        return pd.DataFrame(columns=["Team", "rank"]).set_index("Team")
    df = pd.DataFrame().from_dict(data["rankings"])
    if "record" in df.columns:
        df = df_utils.normalize_column(df, "record")
    df["Team"] = df["team_key"].apply(lambda x: int("".join(filter(str.isdigit, x))))
    return df.sort_values("rank").set_index("Team")


class _TBAUnavailable(Exception):
    """Raised inside cached functions so failures are never cached."""


# The roster is fixed once an event starts, so keep it on disk across restarts
@st.cache_data(ttl=timedelta(days=1), persist="disk", show_spinner=False)
def _get_teams(event_key: str, as_simple: bool) -> pd.DataFrame:
    endpoint = f"/event/{event_key}/teams" + ("/simple" if as_simple else "")
    data = get_data(endpoint, as_dataframe=False)
    if data is None:
        raise _TBAUnavailable(endpoint)
    df = pd.DataFrame().from_dict(data)
    df["Team"] = df["team_number"]
    return df.set_index("Team")


def get_teams(
    event_key: str = DEFAULT_EVENT_KEY, as_simple: bool = True
) -> pd.DataFrame:
    try:
        return _get_teams(event_key, as_simple)
    except _TBAUnavailable:
        return pd.DataFrame(columns=["Team", "nickname"]).set_index("Team")


def clear_event_cache() -> None:
    """Clear once-per-event data (use after changing the event key)."""
    _get_teams.clear()
    _get_robot_photo_url.clear()


def get_robot_photo_url(team: int) -> str | None:
    try:
        return _get_robot_photo_url(team)
    except _TBAUnavailable:
        return None


# The images are fixed once an event starts, so keep it on disk across restarts
@st.cache_data(ttl=timedelta(days=1), persist="disk", show_spinner=False)
def _get_robot_photo_url(team: int) -> str | None:
    year = int(DEFAULT_EVENT_KEY[:4])
    media = get_data(f"/team/frc{team}/media/{year}", as_dataframe=False)
    if media is None:
        raise _TBAUnavailable(f"media {team}")
    urls = [m["direct_url"] for m in media if m.get("direct_url")]
    return urls[1] if len(urls) > 1 else (urls[0] if urls else None)
