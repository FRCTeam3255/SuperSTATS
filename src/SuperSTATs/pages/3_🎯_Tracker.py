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

    teams = []

    for num, name in st.session_state.team_info.items():
        teams.append(f"{num} | {name}")

    columns = st.columns(2)

    team = columns[0].selectbox("Team:", teams)
    team_num = int(team.split(" | ")[0])
    team_cols = [f"Red {i}" for i in range(1, 4)] + [f"Blue {i}" for i in range(1, 4)]

    match_df = st.session_state.matches
    match_df = match_df[match_df[team_cols].isin([team_num]).any(axis=1)]
    matches = match_df["Match"].to_list()

    match_name = columns[1].selectbox("Match:", matches)

    st.write("""---""")

    build.gen_match_comp(team_num, match_name)


if __name__ == "__main__":
    main()
