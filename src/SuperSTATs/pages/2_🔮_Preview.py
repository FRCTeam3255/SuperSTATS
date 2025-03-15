import SuperSTATs.analytics as analytics
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
    """
    Display team information and statistics within an expander.

    Args:
        team_header (tuple): A tuple containing the team header information.
        column (object): The column object to display the team information.
        team_df (list): A list of team numbers.
        opposing_df (list): A list of opposing team numbers.
        prediction_weight (float): The weight for calculating the projected score.
        start_expanded (bool): Whether to start the expanders in an expanded state.
        calc_bumpers (bool): Whether to calculate bumpers.
        combined_chart (bool): Whether to display a combined chart.
        match_choice (str): The match choice.

    Returns:
        None
    """
    df = st.session_state.scouting

    column.markdown(
        f"<center style='font-size: 2em;'>{team_header[0]} {team_header[1]} Alliance {team_header[0]}</center>",
        unsafe_allow_html=True,
    )

    comment_df = st.session_state.df

    for team_num in team_df:
        team_values = (
            comment_df.loc[comment_df["Team"] == team_num, "COMMENT_GENERAL_STR_1"]
            .dropna()
            .tolist()
        )

        team_features = [value.split(", ") for value in team_values]
        team_features = list(
            set([feature for sublist in team_features for feature in sublist])
        )

        build.scouting_expander(
            df=df,
            team_num=team_num,
            team_features=team_features,
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

    if match_choice == "Custom":
        pass
    else:
        try:
            match_breakdown = match_df["score_breakdown"].to_list()[0]

            try:
                actual_score = match_breakdown[team_header[1].lower()]["totalPoints"]
            except:
                actual_score = -1

            match_key = match_df["key"].to_list()[0]
            match_url = f"https://www.thebluealliance.com/match/{match_key}"
        except:
            actual_score = -1
            match_url = None

        percent_error = (
            round((actual_score - projected_score) / actual_score * 100)
            if actual_score != 0
            else "inf"
        )

        if match_url:
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
    team_pieces_df = {}

    for team in team_df:
        team_raw = df_raw[df_raw["Team"] == team]

        if len(team_raw) > 0:
            match_count = len(team_raw)
            team_score_df = team_raw[list(set(game_piece_cols))].sum()

            team_pieces_df[team] = team_score_df / match_count
            team_pieces = team_score_df.sum() / match_count

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
        with column.expander(
            f"[{team}] {'⚠️ Not enough data' if average == -1 else f'{average} pieces'}",
            start_expanded,
        ):
            try:
                st.write(
                    "\n\n".join(
                        [
                            f"{key.split('_')[1].title()}: {round(value, 2)}"
                            for key, value in sorted(team_pieces_df[team].items())
                            if key.startswith("TELE")
                        ]
                    )
                )
            except:
                st.error(f"⚠️ Not enough data collected for team {team}")

    column.markdown("""---""")

    if not combined_chart:
        with column.container():
            build.gen_bar(
                df=st.session_state.df,
                key=column,
                use_presets=False,
                use_group_filters=True,
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


def calc_score(df, team_num, sections):
    df = df.drop("COMMENT_GENERAL_STR_1", axis=1)
    df_plot = df.loc[(df["Team"] == team_num)]

    mask = df.columns == "Match"
    for section in sections:
        mask = mask | df.columns.str.startswith(f"{section}_")

    df_plot = df_plot.loc[:, mask]

    df_split = []
    for col in df.columns:
        split_col = col.split("_")
        if len(split_col) > 1:
            df_split.append(split_col)

    points = {}
    for value in df_split:
        if len(value) == 3:
            points[f"{value[0]}_{value[1]}_{value[2]}"] = int(value[2])

    for col, point in points.items():
        if col in df_plot.columns:
            df_plot[col] *= point

    for score_type in sections:
        columns = [col for col in df_plot.columns if col.startswith(score_type)]
        df_plot[f"{score_type.strip('_').title()} Score"] = df_plot[columns].sum(axis=1)

    excluded_cols = ["Match"]
    sum_cols = [f"{section.strip('_').title()} Score" for section in sections]
    all_columns = excluded_cols + sum_cols

    df_plot["Total Score"] = df_plot.drop(columns=all_columns, axis=1).sum(axis=1)

    return df_plot


def main():
    load.app_init()
    analytics.collect_analytics("page_change", "preview")

    import SuperSTATs.styles as style

    st.markdown(style.shimmer("#d9adff"), unsafe_allow_html=True)
    st.markdown(
        "<div class='shimmer'>🔮 Match Preview 🔮</div>", unsafe_allow_html=True
    )
    st.title("")

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
        st.error("⚠️ No Played Matches")
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

    match_choice = columns[1].selectbox(
        "Match:", df["Match"].to_list() + ["Custom"], last_match
    )

    if match_choice == "Custom":
        alliance_columns = st.columns(2)

        red_alliance = alliance_columns[0].multiselect(
            "Red Alliance:", st.session_state.team_info, []
        )
        blue_alliance = alliance_columns[1].multiselect(
            "Blue Alliance:", st.session_state.team_info, []
        )

        if len(red_alliance) < 3 or len(blue_alliance) < 3:
            st.error("⚠️ Must select 3 teams for each alliance")
            st.stop()

    else:
        df_sort = df[df["Match"] == match_choice]
        df_sort = df_sort.set_index("Match").transpose()[match_choice]

        red_alliance = df_sort.filter(like="Red", axis=0).to_list()
        blue_alliance = df_sort.filter(like="Blue", axis=0).to_list()

    columns = st.columns(4)

    start_expanded = columns[0].toggle("Auto Expand", False)
    combined_chart = columns[1].toggle("Show Combined Chart", False)
    use_calc_error = columns[2].toggle(
        "Error Weights", False, disabled=st.secrets["DEFAULT_EVENT_KEY"] == "NoTBA"
    )
    calc_bumpers = columns[3].toggle("Calculate Bumpers", True)

    prediction_weight = 1

    if use_calc_error:
        all_match_teams = {}
        percent_errors = []

        match_count = int(st.session_state.configs["Error Calc Count"][0])
        match_list = df["Match"].to_list()
        match_index = match_list.index(match_choice)

        prev_matches = match_list[match_index - match_count : match_index]

        if prev_matches == []:
            prev_matches = match_list[:match_count]

        for match_name in prev_matches:
            match_values = df[df["Match"] == match_name]

            red_teams = []
            blue_teams = []

            for col in match_values.columns:
                if "Red" in col:
                    red_teams.append(match_values[col].values[0])

                elif "Blue" in col:
                    blue_teams.append(match_values[col].values[0])

            all_match_teams[match_name] = {"Red": red_teams, "Blue": blue_teams}

        for match in all_match_teams:
            for alliance in all_match_teams[match]:
                team_df = all_match_teams[match][alliance]

                projected_score = build.calc_projected(team_df, prediction_weight)

                match_df = st.session_state.match_data
                match_df = match_df.loc[match_df["Match Name"] == match]

                try:
                    match_breakdown = match_df["score_breakdown"].to_list()[0]
                    try:
                        actual_score = match_breakdown[alliance.lower()]["totalPoints"]
                    except:
                        actual_score = -1
                except:
                    actual_score = -1

                percent_error = (
                    round((actual_score - projected_score) / actual_score * 100)
                    if actual_score != 0
                    else "inf"
                )

                percent_errors.append(percent_error)

        avg_error = round(sum(percent_errors) / len(percent_errors), 2)
        prediction_weight = prediction_weight + prediction_weight * avg_error / 100

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
