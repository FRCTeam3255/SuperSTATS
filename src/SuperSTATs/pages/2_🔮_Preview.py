import SuperSTATs.build as build
import SuperSTATs.load as load
import streamlit as st
import pandas as pd
import numpy as np
import re


def display_team(
    team_header,
    column,
    team_df,
    opposing_df,
    start_expanded,
    combined_chart,
    match_choice,
):
    df = st.session_state.scouting
    column.header(
        f"{team_header[0]} {team_header[1]} Alliance {team_header[0]}", anchor=False
    )

    for team_num in team_df:
        build.scouting_expander(team_num, df, [], start_expanded, True, column)

    column.markdown("""---""")

    score_df = st.session_state.df
    phases = st.session_state.phases

    phase_count = len(
        [
            col
            for col in score_df.columns
            if any(col.startswith(f"{phase}_") for phase in phases)
            and not col.startswith("COMMENT_GENERAL_STR_1")
        ]
    ) * len(team_df)

    alliance_score = pd.DataFrame(columns=phases)
    match_count = 0

    for team in team_df:
        team_score = score_df[score_df["Team"] == team]

        for i in range(len(phases)):
            team_score.loc[:, phases[i]] = build.add_cols(
                team_score,
                phases[i],
            )

        match_count += len(team_score)
        team_score = team_score[phases].sum().to_frame().T
        alliance_score = pd.concat([alliance_score, team_score], ignore_index=True)

    alliance_score = alliance_score.sum().sum()
    projected_score = round(
        (alliance_score / phase_count) * round(match_count / len(team_df))
    )

    text_color = "#f8312f" if team_header[0] == "🔴" else "#0074ba"
    column.markdown(
        f"<h3 style='color: {text_color};'>Projected Score: {projected_score}</h3>",
        unsafe_allow_html=True,
    )

    match_df = pd.DataFrame(
        st.session_state.tba.event_matches(st.secrets["DEFAULT_EVENT_KEY"])
    )
    match_df = pd.concat(
        [match_df, pd.json_normalize(match_df["alliances"])], axis=1
    ).drop(columns="alliances")

    match_df["call"] = (
        match_df["key"]
        .str.replace(st.secrets["DEFAULT_EVENT_KEY"], "")
        .str.replace("_qm", "Quals ")
        .str.replace("_sf", "Playoffs ")
        .str.replace("_f", "Finals ")
        .str.replace(re.compile(r"1m1$"), "1", regex=True)
        .str.replace(re.compile(r"1m2$"), "2", regex=True)
        .str.replace(re.compile(r"1m3$"), "3", regex=True)
        .str.replace(re.compile(r"m1$"), "", regex=True)
    )

    match_df = match_df.loc[match_df["call"] == match_choice]
    match_breakdown = match_df["score_breakdown"].to_list()[0]
    actual_score = match_breakdown[team_header[1].lower()]["totalPoints"]

    match_key = match_df["key"].to_list()[0]
    column.markdown(
        f"<h6><a href='https://www.thebluealliance.com/match/{match_key}' style='color: #808080; text-decoration: none;'>Actual Score: {actual_score}</a></h6>",
        unsafe_allow_html=True,
    )

    column.markdown("""---""")

    if not combined_chart:
        with column.container():
            build.gen_bar(
                st.session_state.df,
                column,
                True,
                False,
                True,
                False,
                True,
                True,
                team_df,
                opposing_df,
                [],
                False,
            )


def main():
    load.app_init()

    st.markdown(
        "<h1 style='text-align: center;'>🔮 Match Preview 🔮</h1>", unsafe_allow_html=True
    )
    st.title("")

    st.button("Update Page", type="primary", use_container_width=True)
    st.markdown("""---""")

    df = st.session_state.matches

    teams = []
    show_all = "All Matches"

    for num, name in st.session_state.team_info.items():
        teams.append(f"{num} | {name}")

    columns = st.columns(2)

    team = columns[0].selectbox("Team Selection:", [show_all] + teams)

    if team != show_all:
        team_number = int(team.split(" | ")[0])
        team_cols = [f"Red {i}" for i in range(1, 4)] + [
            f"Blue {i}" for i in range(1, 4)
        ]
        df = df[df[team_cols].isin([team_number]).any(axis=1)]

    last_match = int(st.session_state.df["Match"].max())

    if team == show_all:
        while True:
            occurrences = len(
                st.session_state.df.loc[st.session_state.df["Match"] == last_match]
            )
            if occurrences >= 3:
                break
            else:
                last_match -= 1
    else:
        last_match = 0

    match_choice = columns[1].selectbox("Match:", df["Match"], last_match)
    df_sort = df[df["Match"] == match_choice]
    df_sort = df_sort.set_index("Match").transpose()[match_choice]

    red_alliance = df_sort.filter(like="Red", axis=0).to_list()
    blue_alliance = df_sort.filter(like="Blue", axis=0).to_list()

    columns = st.columns(2)

    start_expanded = columns[0].checkbox("Auto Expand Scouting", False)
    combined_chart = columns[1].checkbox("Show Combined Chart", False)

    columns = st.columns(2)

    display_team(
        ["🔴", "Red"],
        columns[0],
        red_alliance,
        blue_alliance,
        start_expanded,
        combined_chart,
        match_choice,
    )

    display_team(
        ["🔵", "Blue"],
        columns[1],
        blue_alliance,
        red_alliance,
        start_expanded,
        combined_chart,
        match_choice,
    )

    if combined_chart:
        build.gen_bar(
            st.session_state.df,
            0,
            True,
            False,
            True,
            False,
            True,
            True,
            red_alliance + blue_alliance,
            [],
            [],
            False,
        )


if __name__ == "__main__":
    main()
