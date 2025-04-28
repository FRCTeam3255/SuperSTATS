import pandas as pd
import SuperSTATs.load as load
import streamlit as st
import SuperSTATs.screen_elements as ui


def display_match_schedule_expander() -> None:
    """
    Displays an expander section in the Streamlit app for viewing the match schedule.
    This function creates an expander titled "Match Schedule" that is expanded by default.
    It retrieves match data and team information from the Streamlit session state, allows
    the user to select a team, and displays the corresponding scoreboard.
    Functionality:
    - Retrieves match data from `st.session_state.matches`.
    - Retrieves team information from `st.session_state.team_info` and formats it for selection.
    - Uses `ui.get_team_selection` to allow the user to select a team and relevant columns.
    - Displays the scoreboard for the selected team using `ui.display_scoreboard`.
    Dependencies:
    - Requires `st` (Streamlit) for UI components and session state.
    - Requires `ui` module for team selection and scoreboard display.
    Note:
    Ensure that `st.session_state.matches` and `st.session_state.team_info` are properly
    initialized before calling this function.
    """

    with st.expander("Match Schedule", True):
        matches = st.session_state.matches
        teams = [f"{num} | {name}" for num, name in st.session_state.team_info.items()]
        team, columns = ui.get_team_selection(teams)
        ui.display_scoreboard(matches, team, columns)


def main():
    load.initialise_app()

    ui.display_header("🤖 SuperSTATs 🤖")
    ui.display_event_link(st.secrets["DEFAULT_EVENT_KEY"])

    display_match_schedule_expander()

    ui.display_nexus_data()
    ui.display_event_keys()


if __name__ == "__main__":
    main()
