from SuperSTATs.utils.tba._api import get_data


import pandas as pd
import streamlit as st

DEFAULT_EVENT_KEY = st.secrets["DEFAULT_EVENT_KEY"]


def get_matches(event_key=DEFAULT_EVENT_KEY, as_simple=False):
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
