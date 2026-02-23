import requests
import requests_cache
import pandas as pd
import streamlit as st

current_year = pd.Timestamp.now().year
root_url = "https://www.thebluealliance.com/api/v3"
api_key = st.secrets["TBA_API"]

# Create cached session with TBA API best practices
# - Respects ETag/If-None-Match headers for 304 responses
# - Honors Cache-Control/max-age from TBA
# - In-memory cache (no file persistence)
# - With cache_control=True, 304 responses are handled transparently
session = requests_cache.CachedSession(
    cache_name="tba_cache",
    backend="memory",
    expire_after=None,  # Respect Cache-Control headers from TBA
    cache_control=True,  # Honor Cache-Control/max-age - handles 304s transparently
    allowable_codes=(200, 304, 404),  # Cache these status codes
    stale_if_error=True,  # Return stale cache on error instead of None
)
session.headers["X-TBA-Auth-Key"] = api_key


def get_data(endpoint, as_dataframe=False):
    """Fetch data from TBA API with HTTP caching.

    Uses ETag/If-None-Match and Cache-Control headers per TBA API docs:
    https://www.thebluealliance.com/apidocs

    Requests-cache with cache_control=True and stale_if_error=True ensures
    that cached data is returned even when the server returns 304 Not Modified
    or when network errors occur.

    Args:
        endpoint: TBA API endpoint (e.g., "/event/2024arc/teams")
        as_dataframe: If True, return a pandas DataFrame instead of raw JSON

    Returns:
        JSON response as dict/list, pandas DataFrame, or None on error
    """
    url = f"{root_url}{endpoint}"
    try:
        response = session.get(url, timeout=10)

        # With cache_control=True, requests-cache handles 304s transparently
        # by returning cached data. We only process 200 status codes here.
        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            return None

        data = response.json()
        return pd.DataFrame().from_dict(data) if as_dataframe and data else data

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def current_event(as_simple=False):
    event_key = st.secrets["DEFAULT_EVENT_KEY"]
    endpoint = f"/event/{event_key}/matches" + ("/simple" if as_simple else "")
    df = get_data(endpoint, as_dataframe=True)
    if not df.empty:
        # Normalize nested JSON columns and clean up the DataFrame
        df = pd.concat([df, pd.json_normalize(df["alliances"])], axis=1).drop(
            columns="alliances"
        )
        if "score_breakdown" in df.columns:
            df = pd.concat(
                [
                    df,
                    pd.json_normalize(df["score_breakdown"]).add_prefix(
                        "score_breakdown."
                    ),
                ],
                axis=1,
            ).drop(columns="score_breakdown")

        # Convert comp_level to more readable format
        df["comp_level"] = df["comp_level"].replace(
            {"qm": "Quals", "sf": "Playoffs", "f": "Finals"}
        )

        def set_match_name(row):
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

        df["Match Name"] = df.apply(set_match_name, axis=1)

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

        return df.sort_values("time")
    return pd.DataFrame()
