import SuperSTATs.build as build
import SuperSTATs.load as load
import streamlit as st
import pandas as pd


def main():
    load.app_init()

    import SuperSTATs.styles as style

    st.markdown(style.shimmer("#ff5b5a"), unsafe_allow_html=True)
    st.markdown("<div class='shimmer'>🎯 Team Tracker 🎯</div>", unsafe_allow_html=True)

    st.title("")

    st.button("Update Page", type="primary", use_container_width=True)
    st.markdown("""---""")

    columns = st.columns(2)

    teams = []

    for num, name in st.session_state.team_info.items():
        teams.append(f"{num} | {name}")

    team = columns[0].selectbox("Team:", teams)

    team_num = int(team.split(" | ")[0])
    team_cols = [f"Red {i}" for i in range(1, 4)] + [f"Blue {i}" for i in range(1, 4)]

    match_df = st.session_state.matches
    match_df = match_df[match_df[team_cols].isin([team_num]).any(axis=1)]
    matches = match_df["Match"].to_list()

    match_num = columns[1].selectbox("Match:", matches)

    team_df = [359, 4276, 7157]

    st.write(build.calc_projected(team_df))


if __name__ == "__main__":
    main()
