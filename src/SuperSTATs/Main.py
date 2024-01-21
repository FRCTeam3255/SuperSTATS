import SuperSTATs.load as load
import streamlit as st
import pandas as pd
import datetime


def main():
    load.app_init()

    st.markdown(
        "<div style='display: flex; justify-content: center; font-size: 40px;'><b>🤖 SuperSTATs 🤖</b></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<h1 style='text-align: center;'>Current Dataframe: {st.secrets['DEFAULT_EVENT_KEY']}<h1>",
        unsafe_allow_html=True,
    )

    matches = pd.DataFrame(st.session_state.matches)

    teams = []
    show_all = "All Matches"

    for num, name in st.session_state.team_info.items():
        teams.append(f"{num} | {name}")

    columns = st.columns(2)

    team = columns[0].selectbox("Team Selection:", [show_all] + teams)

    if team != show_all:
        team = int(str(team).split(" | ")[0])

        use_team_colors = columns[1].checkbox("Use Team Colors", False)
        team_colors = st.session_state.team_colors[team]

        if use_team_colors:
            if team_colors[0] == "003255" or team_colors[1] == "003255":
                st.warning("Team Colors Not Found")
                team_color = "#ffffff"
            else:
                if columns[1].checkbox("Use Secondary Color", False):
                    team_color = team_colors[1]
                else:
                    team_color = team_colors[0]
        else:
            team_color = "#ffffff"

        team_cols = [col for col in matches.columns if "Match" not in col]
        matches = matches[matches[team_cols].isin([team]).any(axis=1)]
        matches = matches.style.applymap(
            lambda cell: f"color: {team_color}" if cell == team else "color: #808080",
            subset=pd.IndexSlice[:, team_cols],
        )

    st.table(matches)

    with st.expander("Event Keys", True):
        columns = st.columns(2)

        year = columns[0].number_input(
            "Year:", min_value=0, step=1, value=datetime.datetime.now().year
        )

        events = st.session_state.tba.events(year)
        event_keys = {}

        for event in events:
            name = event["name"]
            key = event["key"]
            event_keys[name] = key

        show_all = "All Events"

        searched_event = columns[1].selectbox(
            "Search Events", [show_all] + list(event_keys.keys())
        )

        if searched_event != show_all:
            selected_key = event_keys.get(searched_event, "")
            st.subheader(f"[{selected_key}] {searched_event}")

        else:
            for name, key in event_keys.items():
                st.text(f"[{key}] {name}")

            if len(event_keys) == 0:
                st.error(f"No keys found {year}")


if __name__ == "__main__":
    main()
