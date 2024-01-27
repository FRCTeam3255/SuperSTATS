import SuperSTATs.build as build
import SuperSTATs.load as load
import streamlit as st
import pandas as pd


def display_team(
    team_header,
    column,
    team_df,
    opposing_df,
    start_expanded,
    calc_bumpers,
    combined_chart,
    match_choice,
):
    df = st.session_state.scouting
    column.header(
        f"{team_header[0]} {team_header[1]} Alliance {team_header[0]}", anchor=False
    )

    for team_num in team_df:
        build.scouting_expander(
            team_num=team_num,
            df=df,
            start_expanded=start_expanded,
            calc_bumpers=calc_bumpers,
            error_prefix=True,
            column=column,
        )

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

    match_df = st.session_state.match_data
    match_df = match_df.loc[match_df["Match Name"] == match_choice]
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
                key=column,
                use_hide_picked=False,
                use_features=False,
                use_max_size=False,
                displayed_teams=team_df,
                compared_teams=opposing_df,
                expanders=False,
                use_inline_legend=False,
            )


def main():
    load.app_init()

    import SuperSTATs.styles as style

    st.markdown(style.shimmer("#d9adff"), unsafe_allow_html=True)
    st.markdown("<div class='shimmer'>🔮 Match Preview 🔮</div>", unsafe_allow_html=True)
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

    columns = st.columns(3)

    start_expanded = columns[0].toggle("Auto Expand Scouting", False)
    calc_bumpers = columns[1].toggle("Calculate Bumpers", True)
    combined_chart = columns[2].toggle("Show Combined Chart", False)

    columns = st.columns(2)

    display_team(
        ["🔴", "Red"],
        columns[0],
        red_alliance,
        blue_alliance,
        start_expanded,
        calc_bumpers,
        combined_chart,
        match_choice,
    )

    display_team(
        ["🔵", "Blue"],
        columns[1],
        blue_alliance,
        red_alliance,
        start_expanded,
        calc_bumpers,
        combined_chart,
        match_choice,
    )

    if combined_chart:
        build.gen_bar(
            use_max_size=False,
            displayed_teams=red_alliance + blue_alliance,
            expanders=False,
            use_inline_legend=False,
        )


if __name__ == "__main__":
    main()
