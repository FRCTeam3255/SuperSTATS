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

    df = st.session_state.df
    match_df = st.session_state.matches

    columns = st.columns(2)

    teams = []

    for num, name in st.session_state.team_info.items():
        teams.append(f"{num} | {name}")

    team = columns[0].selectbox("Team:", teams)

    team_num = int(team.split(" | ")[0])
    team_cols = [f"Red {i}" for i in range(1, 4)] + [f"Blue {i}" for i in range(1, 4)]

    match_df = match_df[match_df[team_cols].isin([team_num]).any(axis=1)]
    matches = match_df["Match"].to_list()

    match_name = columns[1].selectbox("Match:", matches)

    team_df = df[df["Team"] == team_num]
    match_count = len(team_df)

    team_df = build.calc_projected([team_num], True)
    team_scores = team_df.drop(columns=["Match Name"])

    team_scores = team_scores.sum()
    team_scores["TOTAL"] = team_scores.sum()

    team_averages = {}

    for phase, score in team_scores.items():
        team_averages[phase] = round(score / match_count)

    match_scores = team_df.loc[team_df["Match Name"] == match_name]
    st.write(match_scores)


if __name__ == "__main__":
    main()
