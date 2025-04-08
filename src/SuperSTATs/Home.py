import SuperSTATs.load as load
import streamlit as st
import SuperSTATs.screen_elements as ui


def main():
    load.initialise_app()

    ui.display_header("🤖 SuperSTATs 🤖")

    event_key = st.secrets["DEFAULT_EVENT_KEY"]
    ui.display_event_link(event_key)

    with st.expander("Match Schedule", True):
        matches = st.session_state.matches
        teams = [f"{num} | {name}" for num, name in st.session_state.team_info.items()]
        """
        team, columns = get_team_selection(teams)
        matches = update_match_scores(matches)
        display_matches(matches, team, columns)
        """


if __name__ == "__main__":
    main()
