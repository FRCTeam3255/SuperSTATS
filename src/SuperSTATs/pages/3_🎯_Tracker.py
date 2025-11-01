import SuperSTATs.analytics as analytics
import SuperSTATs.load as load
import streamlit as st


def main():
    load.app_init()
    analytics.collect_analytics("page_change", "tracker")

    import SuperSTATs.build as build

    st.title("🎯 Team Tracker 🎯")

    if st.button(
        "Update Page",
        type="primary",
        use_container_width=True,
        key=f"update_page",
        on_click=analytics.button_press,
        args=("update_page",),
    ):
        st.session_state.df = load.organize_df(
            load.download_sheets_raw(st.secrets["GID_RAW"]).dropna(subset=["Timestamp"])
        )

    st.divider()

    team_info = st.session_state.team_info
    teams = []

    url_query = st.query_params.to_dict()

    if url_query:
        url_team_num = int(url_query["team_num"])
        url_team_name = f"{url_team_num} | {team_info[url_team_num]}"
        url_match_name = url_query["match_name"].replace("_", " ")
    else:
        url_team_num = None
        url_match_name = None

    for num, name in team_info.items():
        teams.append(f"{num} | {name}")

    columns = st.columns(2)

    team = columns[0].selectbox(
        "Team:",
        teams,
        index=teams.index(url_team_name) if url_team_num else 0,
    )

    team_num = int(team.split(" | ")[0])
    team_cols = [f"Red {i}" for i in range(1, 4)] + [f"Blue {i}" for i in range(1, 4)]

    match_df = st.session_state.matches
    match_df = match_df[match_df[team_cols].isin([team_num]).any(axis=1)]
    matches = match_df["Match"].to_list()

    try:
        match_index = matches.index(url_match_name)
    except:
        match_index = 0
        if url_query:
            st.query_params.clear()
            st.toast("URL parameters cleared", icon="🗑️")

    match_name = columns[1].selectbox(
        "Match:",
        matches,
        index=match_index,
    )

    st.write("""---""")

    build.gen_match_comp(st.session_state.df, team_num, match_name)


if __name__ == "__main__":
    main()
