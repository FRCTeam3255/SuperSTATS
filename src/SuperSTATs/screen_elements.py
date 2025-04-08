import pandas as pd
import streamlit as st
import styles as style


def display_header(title):
    """
    Displays a styled header with a rainbow effect.
    Args:
        title (str): The text to display as the header.
    Notes:
        - This function uses Streamlit's `st.markdown` to render HTML content.
        - The `style.rainbow()` function is assumed to provide the necessary CSS for the rainbow effect.
        - The `unsafe_allow_html=True` parameter is used to allow rendering of raw HTML.
    """

    st.markdown(style.rainbow(), unsafe_allow_html=True)
    st.markdown(f"<div class='rainbow'>{title}</div>", unsafe_allow_html=True)


def display_event_link(event_key):
    """
    Displays a clickable link to an event on The Blue Alliance website using Streamlit's markdown.
    Args:
        event_key (str): The unique identifier for the event. This will be used to construct
                         the URL for the event on The Blue Alliance website.
    Notes:
        - The link is styled to appear centered, with a font size of 1.5em, white text color,
          and no underline.
        - This function uses Streamlit's `st.markdown` with `unsafe_allow_html=True` to render
          custom HTML.
    """

    st.markdown(
        f"<div style='text-align: center; font-size: 1.5em;'><a href='https://www.thebluealliance.com/event/{event_key}' style='color: #ffffff; text-decoration: none;'>Current Dataframe: {event_key}</a></div>",
        unsafe_allow_html=True,
    )


def get_team_selection(teams):
    """
    Creates a Streamlit UI element for team selection.
    Parameters:
        teams (list): A list of team names to populate the selection dropdown.
    Returns:
        tuple: A tuple containing:
            - team (str): The selected team from the dropdown. Defaults to "All Matches" if no specific team is selected.
            - columns (list): A list of Streamlit column objects used for layout.
    """

    columns = st.columns(2)
    team = columns[0].selectbox("Team Selection:", ["All Matches"] + teams)
    return team, columns


def display_scoreboard(matches, team, columns):
    """
    Displays a scoreboard for matches with scores and optional team filtering.
    Args:
        matches (pd.DataFrame): A DataFrame containing match data. Must include a "Match" column.
        team (str): The team to filter matches by. Use "All Matches" to display all matches.
        columns (list): A list of Streamlit column objects for UI interactions.
    Raises:
        KeyError: If the expected keys are missing in the match data's "score_breakdown".
        Exception: For any other errors encountered during processing.
    Notes:
        - The function merges match data with session state data to retrieve score breakdowns.
        - Scores are displayed with red (🔴) and blue (🔵) indicators, and a trophy (🏆) for the winning team.
        - If team filtering is enabled, matches involving the specified team are highlighted.
        - The function uses Streamlit's `st.dataframe` to display the processed match data.
    """

    try:
        # Merge match data
        matches = pd.merge(
            matches,
            st.session_state.match_data[["Match Name", "score_breakdown"]],
            left_on="Match",
            right_on="Match Name",
            how="left",
        )

        # Update scores
        for match_name in matches["Match"]:
            data = matches[matches["Match"] == match_name]["score_breakdown"].to_list()[
                0
            ]
            try:
                red_score = int(data["red"]["totalPoints"])
                blue_score = int(data["blue"]["totalPoints"])

                red_data = f"🔴 {red_score:3}" + (
                    " 🏆" if red_score > blue_score else ""
                )
                blue_data = f"🔵 {blue_score:3}" + (
                    " 🏆" if blue_score > red_score else ""
                )
            except KeyError:
                red_data = blue_data = "🕑 N/A"

            matches.loc[matches["Match"] == match_name, "Red Score"] = red_data
            matches.loc[matches["Match"] == match_name, "Blue Score"] = blue_data

        matches = matches.drop(columns=["Match Name", "score_breakdown"])

        # Filter matches by team
        if team != "All Matches":
            team_id = int(str(team).split(" | ")[0])
            use_team_colors = columns[1].toggle("Use Team Colors")
            team_colors = st.session_state.team_colors[str(team_id)]
            team_color = team_colors if use_team_colors else "#808080"

            team_cols = [
                col
                for col in matches.columns
                if col not in ["Match", "Red Score", "Blue Score"]
            ]

            matches = matches[matches[team_cols].isin([team_id]).any(axis=1)].astype(
                str
            )

            matches = matches.style.map(
                lambda cell: (
                    f"color: {team_color}" if cell == str(team_id) else "color: #808080"
                ),
                subset=pd.IndexSlice[:, team_cols],
            )
        else:
            matches = matches.astype(str)

        # Display matches
        st.dataframe(
            matches.set_index("Match") if team == "All Matches" else matches,
            use_container_width=True,
        )

    except Exception as e:
        st.error(f"⚠️ Error processing matches: {e}")
