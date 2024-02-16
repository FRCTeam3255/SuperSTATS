import SuperSTATs.load as load
import streamlit as st
import pandas as pd
import datetime


def main():
    load.app_init()

    import SuperSTATs.styles as style

    st.markdown(style.rainbow(), unsafe_allow_html=True)
    st.markdown("<div class='rainbow'>🤖 SuperSTATs 🤖</div>", unsafe_allow_html=True)

    st.markdown(
        f"<div style='font-weight: bold; text-align: center; font-size: 2.5em;'>Current Dataframe: {st.secrets['DEFAULT_EVENT_KEY']}</div>",
        unsafe_allow_html=True,
    )

    with st.expander("Match Schedule", True):
        matches = st.session_state.matches

        teams = []
        show_all = "All Matches"

        columns = st.columns(2)

        for num, name in st.session_state.team_info.items():
            teams.append(f"{num} | {name}")

        team = columns[0].selectbox("Team Selection:", [show_all] + teams)

        matches = pd.merge(
            matches,
            st.session_state.match_data[["Match Name", "score_breakdown"]],
            left_on="Match",
            right_on="Match Name",
            how="left",
        )

        for match_name in matches["Match"]:
            data = matches[matches["Match"] == match_name]["score_breakdown"].to_list()[
                0
            ]

            if str(data) != "nan":
                red_data = str(data["red"]["totalPoints"]).ljust(3)
                blue_data = str(data["blue"]["totalPoints"]).ljust(3)

                if int(red_data) > int(blue_data):
                    red_data = f"🔴 {str(red_data)} 🏆"
                    blue_data = f"🔵 {str(blue_data)}"
                else:
                    red_data = f"🔴 {str(red_data)}"
                    blue_data = f"🔵 {str(blue_data)} 🏆"
            else:
                red_data = blue_data = "🕑 N/A"

            matches.loc[matches["Match"] == match_name, "Red Score"] = red_data
            matches.loc[matches["Match"] == match_name, "Blue Score"] = blue_data

        matches = matches.drop(columns=["Match Name", "score_breakdown"])

        if team != show_all:
            team = int(str(team).split(" | ")[0])

            use_team_colors = columns[1].toggle("Use Team Colors")
            team_colors = st.session_state.team_colors[str(team)]

            if use_team_colors:
                if team_colors[0] == "003255" or team_colors[1] == "003255":
                    columns[1].toggle("Use Secondary Color", disabled=True)
                    st.warning("Team Colors Not Found")
                    team_color = "#ffffff"
                else:
                    if columns[1].toggle("Use Secondary Color"):
                        team_color = team_colors[1]
                    else:
                        team_color = team_colors[0]
            else:
                columns[1].toggle("Use Secondary Color", disabled=True)
                team_color = "#ffffff"

            team_cols = [
                col
                for col in matches.columns
                if col not in ["Match", "Red Score", "Blue Score"]
            ]

            matches = matches[matches[team_cols].isin([team]).any(axis=1)].astype(str)
            matches = matches.style.map(
                lambda cell: (
                    f"color: {team_color}" if cell == str(team) else "color: #808080"
                ),
                subset=pd.IndexSlice[:, team_cols],
            )

            st.dataframe(matches, use_container_width=True)
        else:
            matches = matches.astype(str)

            st.dataframe(
                matches.set_index("Match"),
                use_container_width=True,
            )

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
            st.subheader(f"[{selected_key}] {searched_event}", False)

        else:
            for name, key in event_keys.items():
                st.text(f"[{key}] {name}")

            if len(event_keys) == 0:
                st.error(f"No keys found {year}")


if __name__ == "__main__":
    main()
