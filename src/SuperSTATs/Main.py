import SuperSTATs.analytics as analytics
import SuperSTATs.load as load
import streamlit as st
import pandas as pd
import datetime
import requests


def display_event_link(event_key):
    st.markdown(
        f"<div style='text-align: center; font-size: 1.5em;'><a href='https://www.thebluealliance.com/event/{event_key}' style='color: #ffffff; text-decoration: none;'>Current Dataframe: {event_key}</a></div>",
        unsafe_allow_html=True,
    )


def get_team_selection(teams):
    columns = st.columns(2)
    team = columns[0].selectbox("Team Selection:", ["All Matches"] + teams)
    return team, columns


def update_match_scores(matches):
    try:
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
            red_data, blue_data = get_match_scores(data)
            matches.loc[matches["Match"] == match_name, "Red Score"] = red_data
            matches.loc[matches["Match"] == match_name, "Blue Score"] = blue_data
        matches = matches.drop(columns=["Match Name", "score_breakdown"])
    except Exception as e:
        st.error(f"⚠️ Error updating match scores: {e}")
    return matches


def get_match_scores(data):
    try:
        red_data = str(data["red"]["totalPoints"]).ljust(3)
        blue_data = str(data["blue"]["totalPoints"]).ljust(3)
        if int(red_data) > int(blue_data):
            red_data = f"🔴 {red_data} 🏆"
            blue_data = f"🔵 {blue_data}"
        elif int(red_data) < int(blue_data):
            red_data = f"🔴 {red_data}"
            blue_data = f"🔵 {blue_data} 🏆"
        else:
            red_data = f"🔴 {red_data}"
            blue_data = f"🔵 {blue_data}"
    except:
        red_data = blue_data = "🕑 N/A"
    return red_data, blue_data


def filter_matches_by_team(matches, team, columns):
    team = int(str(team).split(" | ")[0])
    use_team_colors = columns[1].toggle("Use Team Colors")
    team_colors = st.session_state.team_colors[str(team)]
    team_color = get_team_color(use_team_colors, team_colors, columns)
    team_cols = [
        col
        for col in matches.columns
        if col not in ["Match", "Red Score", "Blue Score"]
    ]
    matches = matches[matches[team_cols].isin([team]).any(axis=1)].astype(str)
    matches = matches.style.map(
        lambda cell: f"color: {team_color}" if cell == str(team) else "color: #808080",
        subset=pd.IndexSlice[:, team_cols],
    )
    return matches


def get_team_color(use_team_colors, team_colors, columns):
    if use_team_colors:
        if team_colors[0] == "003255" or team_colors[1] == "003255":
            columns[1].toggle("Use Secondary Color", disabled=True)
            st.warning("⚠️ Team Colors Not Found")
            return "#ffffff"
        else:
            if columns[1].toggle("Use Secondary Color"):
                return team_colors[1]
            else:
                return team_colors[0]
    else:
        columns[1].toggle("Use Secondary Color", disabled=True)
        return "#ffffff"


def display_matches(matches, team, columns):
    if team != "All Matches":
        matches = filter_matches_by_team(matches, team, columns)
        st.dataframe(matches, use_container_width=True)
    else:
        matches = matches.astype(str)
        st.dataframe(matches.set_index("Match"), use_container_width=True)


def display_nexus_data():
    # nexus_data = st.session_state.nexus_data
    nexus_data = None

    if nexus_data:
        with st.expander("Nexus Data", st.session_state.console["practice_mode"]):
            st.subheader("Now Playing")
            st.write(nexus_data["now_playing"])

            st.subheader("Queue Status")
            queue_status = nexus_data.get("queue_status", "").upper()
            next_match = nexus_data.get("next_match")
            alliance_color = nexus_data.get("alliance_color")

            if next_match:
                st.write(f"[{queue_status}] {next_match} on {alliance_color} alliance")
            else:
                st.write("No scheduled matches found")


def display_event_keys():
    with st.expander("Event Keys", st.session_state.console["practice_mode"]):
        columns = st.columns(2)
        year = columns[0].number_input(
            "Year:", min_value=0, step=1, value=datetime.datetime.now().year
        )
        events = st.session_state.tba.events(year)
        event_keys = {event["name"]: event["key"] for event in events}
        searched_event = columns[1].selectbox(
            "Search Events", ["All Events"] + list(event_keys.keys())
        )
        if searched_event != "All Events":
            selected_key = event_keys.get(searched_event, "")
            st.subheader(f"[{selected_key}] {searched_event}", False)
        else:
            for name, key in event_keys.items():
                st.text(f"[{key}] {name}")
            if len(event_keys) == 0:
                st.error(f"⚠️ No keys found for {year}")


def main():
    load.app_init()
    analytics.collect_analytics("page_change", "main")
    st.title('🦾 SuperSTATs 🦾')
    event_key = st.secrets["DEFAULT_EVENT_KEY"]
    display_event_link(event_key)
    with st.expander("Match Schedule", True):
        matches = st.session_state.matches
        teams = [f"{num} | {name}" for num, name in st.session_state.team_info.items()]
        team, columns = get_team_selection(teams)
        matches = update_match_scores(matches)
        display_matches(matches, team, columns)
    # display_nexus_data()
    display_event_keys()


if __name__ == "__main__":
    main()
