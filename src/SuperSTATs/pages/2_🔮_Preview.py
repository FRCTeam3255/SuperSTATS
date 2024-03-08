import SuperSTATs.build as build
import SuperSTATs.load as load
import streamlit as st


def display_team(
    team_header,
    column,
    team_df,
    opposing_df,
    prediction_weight,
    start_expanded,
    calc_bumpers,
    combined_chart,
    match_choice,
):
    df = st.session_state.scouting

    column.markdown(
        f"<center style='font-size: 2em;'>{team_header[0]} {team_header[1]} Alliance {team_header[0]}</center>",
        unsafe_allow_html=True,
    )

    for team_num in team_df:
        build.scouting_expander(
            df=df,
            team_num=team_num,
            match_name=match_choice,
            start_expanded=start_expanded,
            calc_bumpers=calc_bumpers,
            column=column,
        )

    column.markdown("""---""")

    projected_score = build.calc_projected(team_df, prediction_weight)

    text_color = "#f8312f" if team_header[0] == "🔴" else "#0074ba"
    column.markdown(
        f"<h3 style='color: {text_color};'>Projected Score: {projected_score}</h3>",
        unsafe_allow_html=True,
    )

    match_df = st.session_state.match_data
    match_df = match_df.loc[match_df["Match Name"] == match_choice]
    match_breakdown = match_df["score_breakdown"].to_list()[0]

    try:
        actual_score = match_breakdown[team_header[1].lower()]["totalPoints"]
    except:
        actual_score = -1

    match_key = match_df["key"].to_list()[0]
    match_url = f"https://www.thebluealliance.com/match/{match_key}"

    percent_error = (
        round((actual_score - projected_score) / actual_score * 100)
        if actual_score != 0
        else "inf"
    )

    column.markdown(
        f"<h6><a href='{match_url}' style='color: #808080; text-decoration: none;'>Actual Score: {'Unplayed' if actual_score == -1 else actual_score} {'' if actual_score == -1 else f'({percent_error}%)'}</a></h6>",
        unsafe_allow_html=True,
    )

    df_raw = st.session_state.df
    alliance_pieces = 0

    game_piece_cols = [
        col
        for col in df_raw.columns
        if any(
            piece.upper() in col
            for piece in st.session_state.configs["Game Piece Columns"]
        )
    ]

    team_averages = []

    for team in team_df:
        team_raw = df_raw[df_raw["Team"] == team]
        if len(team_raw) > 0:
            team_pieces = team_raw[list(set(game_piece_cols))].sum().sum() / len(
                team_raw
            )
            team_averages.append((team, round(team_pieces, 2)))
        else:
            team_averages.append((team, -1))

    alliance_pieces = sum(average for _, average in team_averages if average != -1)

    column.divider()

    column.markdown(
        f"<h5>Projected Pieces: {round(alliance_pieces, 2)}</h5>",
        unsafe_allow_html=True,
    )

    for team, average in team_averages:
        column.write(
            f"- Team {team}: {'⚠️ Not enough data' if average == -1 else f'{average} pieces'}"
        )

    column.markdown("""---""")

    if not combined_chart:
        with column.container():
            build.gen_bar(
                df=st.session_state.df,
                key=column,
                use_presets=False,
                use_group_filters=False,
                use_show_available=False,
                use_show_nums=False,
                use_features=False,
                use_agg_type=False,
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
    st.markdown(
        "<div class='shimmer'>🔮 Match Preview 🔮</div>", unsafe_allow_html=True
    )
    st.title("")

    if st.button("Update Page", type="primary", use_container_width=True):
        df = load.download_sheets_raw(st.secrets["GID_RAW"]).dropna(
            subset=["Timestamp"]
        )
        df = df.sort_values(["Match", "Timestamp"], ascending=[True, True])
        df = df.drop_duplicates(subset=["Team", "Match Type", "Match"])
        df = df[df["Event Key"] == st.secrets["DEFAULT_EVENT_KEY"]]
        st.session_state.df = df

    st.divider()

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

    try:
        last_match = int(st.session_state.df["Match"].max())
    except:
        st.error("No Played Matches")
        st.stop()

    if team == show_all:
        while True:
            occurrences = len(
                st.session_state.df.loc[st.session_state.df["Match"] == last_match]
            )
            if occurrences >= 6:
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

    columns = st.columns(4)

    start_expanded = columns[0].toggle("Auto Expand", False)
    combined_chart = columns[1].toggle("Show Combined Chart", False)
    use_weights = columns[2].toggle("Use Weights", False)
    calc_bumpers = columns[3].toggle("Calculate Bumpers", True)

    if use_weights:
        weights_raw = st.session_state.configs["Prediction Slider Weights"]
        weights = {}

        for config in weights_raw:
            config = config.split("=")
            weights[config[0]] = float(config[1])

        with st.form("Threshold Slider", clear_on_submit=False):
            prediction_weight = st.slider(
                "Variance Threshold:",
                value=weights["default"],
                min_value=weights["min"],
                max_value=weights["max"],
                step=weights["step"],
            )
            st.form_submit_button(
                "Set Weights", type="primary", use_container_width=True
            )

    else:
        prediction_weight = 1

    st.divider()

    columns = st.columns(2)

    display_team(
        ["🔴", "Red"],
        columns[0],
        red_alliance,
        blue_alliance,
        prediction_weight,
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
        prediction_weight,
        start_expanded,
        calc_bumpers,
        combined_chart,
        match_choice,
    )

    if combined_chart:
        match_teams = red_alliance + blue_alliance
        toggled_teams = []

        with st.expander("Toggle Teams", True):
            columns = st.columns(len(match_teams))

            for i, team in enumerate(match_teams):
                toggled_state = columns[i].toggle(
                    (
                        f":red[{str(team)}]"
                        if team in red_alliance
                        else f":blue[{str(team)}]"
                    ),
                    True,
                    key=f"{team}_toggle_state",
                )

                if toggled_state:
                    toggled_teams.append(team)

        if len(toggled_teams) == 0:
            toggled_teams = red_alliance + blue_alliance

        build.gen_bar(
            use_presets=False,
            use_show_available=False,
            use_inline_legend=False,
            use_features=False,
            use_max_size=False,
            displayed_teams=toggled_teams,
            expanders=False,
        )


if __name__ == "__main__":
    main()
