import SuperSTATs.load as load
import streamlit as st
import altair as alt
import pandas as pd


def main():
    load.app_init()

    import SuperSTATs.styles as style
    import SuperSTATs.build as build

    st.markdown(style.shimmer("#ff5b5a"), unsafe_allow_html=True)
    st.markdown("<div class='shimmer'>🎯 Team Tracker 🎯</div>", unsafe_allow_html=True)

    st.title("")

    st.button("Update Page", type="primary", use_container_width=True)
    st.markdown("""---""")

    team_info = st.session_state.team_info
    teams = []

    url_query = st.query_params.to_dict()

    if url_query:
        url_team_num = int(url_query["team_num"])
        url_team_name = f"{url_team_num} | {team_info[url_team_num]}"
        url_match_name = url_query["match_name"]
        st.query_params.clear()
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

    match_name = columns[1].selectbox(
        "Match:",
        matches,
        index=matches.index(url_match_name) if url_match_name else 0,
    )

    st.write("""---""")

    build.gen_match_comp(team_num, match_name)


if __name__ == "__main__":
    main()
