import matplotlib.pyplot as plt
import SuperSTATs.load as load
import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import pickle
import time
import math


load.app_init()
pd.options.mode.chained_assignment = None


def add_cols(org_df, filter):
    points = {}

    for key, value in st.session_state.points.items():
        points[f"{key}_{value}"] = value

    relevant_columns = [
        col
        for col in org_df.columns
        if col != "COMMENT_GENERAL_STR_1" and col.startswith(filter)
    ]

    org_df[filter] = org_df[relevant_columns].apply(
        lambda row: sum(
            [points[col] * val for col, val in row.items() if col in points]
        ),
        axis=1,
    )

    return org_df[filter]


def scouting_expander(
    df,
    team_num,
    match_name=None,
    rank_info=[],
    start_expanded=False,
    calc_bumpers=False,
    column=st,
):
    team_name = st.session_state.team_info[team_num]

    expander_name = f"[{team_num}] {team_name}"

    sorted_df = df.loc[df["Team #"] == int(team_num)]
    sorted_df = sorted_df.sort_values(by="Timestamp")
    sorted_df = sorted_df.drop_duplicates(keep="last", subset="Team #")

    time_logged = str(sorted_df["Timestamp"].max())
    has_data = False if time_logged == "nan" else True

    if len(rank_info) == 2:
        expander_name += f" [🦸{rank_info[0]}/💎{rank_info[1]}]"

    with column.expander(
        f"{expander_name} {'⚠️' if not has_data else ''}", start_expanded
    ):
        with st.container(border=True):
            gen_match_comp(team_num, match_name, False)

        if has_data:
            with st.container(border=True):
                if len(rank_info) == 2:
                    st.text(f"SN Rank: {rank_info[0]} | TBA Rank: {rank_info[1]}")

                if st.secrets["TEAM_NUMBER"] not in df["Team #"].values:
                    team_data = {"Frame Size LENGTH": 0, "Frame Size WIDTH": 0}
                else:
                    team_data = df.loc[
                        df["Team #"] == st.secrets["TEAM_NUMBER"],
                        ["Frame Size LENGTH", "Frame Size WIDTH"],
                    ].iloc[0]

                added_length = team_data["Frame Size LENGTH"]
                added_width = team_data["Frame Size WIDTH"]

                length = sorted_df["Frame Size LENGTH"].max()
                width = sorted_df["Frame Size WIDTH"].max()

                bumper_size = 5

                added_length += bumper_size * calc_bumpers
                added_width += bumper_size * calc_bumpers

                length += bumper_size * calc_bumpers
                width += bumper_size * calc_bumpers

                added_length = length + added_length
                added_width = width + added_width

                st.text(f"Length: {length} in ({added_length} in)")
                st.text(f"Width: {width} in ({added_width} in)")
                st.text(f"Area: {length * width} in²")

                def check_nan(var_name, var_value, column):
                    try:
                        if np.isnan(var_value):
                            column.text(f"{var_name}: No Data Collected")
                    except:
                        column.text(f"{var_name}: {var_value}")

                check_nan("Drivetrain", sorted_df["Drivetrain Type"].max(), st)
                check_nan("Scouting Comments", sorted_df["Comments"].max(), st)

                st.markdown(
                    f"<span style='font-size: small; color: #808080;'>Time Logged: {time_logged}</span>",
                    unsafe_allow_html=True,
                )

        else:
            st.error("⚠️ No scouting data")


def calc_projected(team_df, show_ungrouped=False, return_row=False):
    score_df = st.session_state.df
    phases = st.session_state.phases

    phase_count = len(
        [
            col
            for col in score_df.columns
            if any(col.startswith(f"{phase}_") for phase in phases)
        ]
    ) * len(team_df)

    alliance_score = pd.DataFrame(columns=phases)
    match_count = 0

    for team in team_df:
        team_score = score_df[score_df["Team"] == team]

        if show_ungrouped:
            phases = [
                col
                for col in team_score.columns
                if any(col.startswith(f"{phase}_") for phase in phases)
                and col != "COMMENT_GENERAL_STR_1"
            ]

        for i in range(len(phases)):
            team_score.loc[:, phases[i]] = add_cols(
                team_score,
                phases[i],
            )

        if return_row:
            team_score["Match Name"] = (
                team_score["Match Type"] + " " + team_score["Match"].astype(str)
            )
            return {"score": team_score[["Match Name"] + phases], "phases": phases}

        match_count += len(team_score)
        team_score = team_score[phases].sum().to_frame().T
        alliance_score = alliance_score.dropna(axis=1, how="all")
        team_score = team_score.dropna(axis=1, how="all")
        alliance_score = pd.concat([alliance_score, team_score], ignore_index=True)

    alliance_score = alliance_score.sum().sum()
    projected_score = round(
        (alliance_score / phase_count) * round(match_count / len(team_df))
    )

    return projected_score


def gen_match_comp(team_num, match_name, not_preview=True):
    df = st.session_state.df

    team_df = df[df["Team"] == team_num]
    match_count = len(team_df)

    config_columns = st.columns(3)

    if not_preview:
        show_ungrouped = config_columns[0].toggle("Ungroup", False)
    else:
        show_ungrouped = False

    team_df = calc_projected([team_num], show_ungrouped, return_row=True)

    phases = team_df["phases"]
    team_df = team_df["score"]

    skip_phases = ["INFO", "COMMENT"]

    if not_preview and show_ungrouped:
        selected_phase = st.selectbox("Phase:", ["AUTO", "TELE", "END"], index=1)

        if selected_phase:
            if any("_" in phase for phase in phases):
                phases = [
                    phase for phase in phases if phase.startswith(f"{selected_phase}_")
                ]

    team_scores = team_df.drop(columns=["Match Name"])

    team_scores = team_scores.sum()
    team_scores["TOTAL"] = team_scores.sum()

    if not_preview:
        st.divider()

    columns = st.columns(len(phases))

    use_phases = []
    if not_preview:
        for i, phase in enumerate(phases):
            phase_name = phase.split("_")[1] if show_ungrouped else phase
            use = columns[i].toggle(
                phase_name.title(), False if phase in skip_phases else True
            )
            if use:
                use_phases.append(phase)

        st.divider()
    else:
        use_phases = ["AUTO", "TELE", "END", "TOTAL"]

    alt_size = st.columns(len(use_phases) + 1)
    team_averages = {}

    try:
        for phase, score in team_scores.items():
            team_averages[phase] = round(score / match_count)

        if not_preview:
            match_scores = team_df.loc[team_df["Match Name"] == match_name]
        else:
            team_df = team_df.sort_index()

            match_scores = (
                team_df.reset_index(drop=True).loc[len(team_df) - 1].to_frame().T
            )
            match_name = match_scores["Match Name"].to_list()[0]

            query_url = f"Tracker/?team_num={team_num}&match_name={match_name}"

            button_style = (
                "background-color: #141414; border: 1px solid #424242; border-radius: 8px;"
                "color: #ffffff; text-align: center; text-decoration: none;"
                "display: block; width: 100%; padding: 8px 0;"
            )

            st.markdown(
                f"<a href='{query_url}' target='_self' style='{button_style}'>Send To Team Tracker</a>",
                unsafe_allow_html=True,
            )
    except:
        match_scores = team_df.loc[team_df["Match Name"] == match_name]

    team_scores = match_scores.drop(columns=["Match Name"])

    if team_scores.empty:
        st.error(f"No data collected for team {team_num} in {match_name}")

    team_scores = team_scores.sum()
    team_scores["TOTAL"] = team_scores.sum()

    match_score = {}

    for phase, score in team_scores.items():
        match_score[phase] = score

    default_colors = ["#0074ba", "#f8312f"]

    if not_preview:
        use_team_colors = config_columns[1].toggle("Use Team Colors")
        team_colors = st.session_state.team_colors[str(team_num)]

        if use_team_colors:
            if team_colors[0] == "003255" or team_colors[1] == "003255":
                config_columns[2].toggle("Swap Colors", disabled=True)
                use_colors = default_colors
                st.toast(
                    f"Team colors not found for {st.session_state.team_info[team_num]} (Team {team_num})",
                    icon="⚠️",
                )
            else:
                if config_columns[2].toggle("Swap Colors"):
                    use_colors = [team_colors[1], team_colors[0]]
                else:
                    use_colors = [team_colors[0], team_colors[1]]
        else:
            config_columns[2].toggle("Swap Colors", disabled=True)
            use_colors = default_colors

        try:
            for i, phase in enumerate(phases):
                delta = match_score[phase] - team_averages[phase]
                columns[i].metric(
                    label=phase,
                    value=match_score[phase],
                    delta=delta,
                    delta_color="off" if delta == 0 else "normal",
                    label_visibility="hidden",
                )
        except:
            pass
    else:
        use_colors = default_colors

    try:
        df = pd.DataFrame(
            {
                "Phase": use_phases,
                "Average": [team_averages[phase] for phase in use_phases],
                "Match": [match_score[phase] for phase in use_phases],
            }
        )
    except:
        df = pd.DataFrame.from_dict(
            {
                "Phase": [],
                "Average": [],
                "Match": [],
            }
        )
        df["Phase"] = df["Phase"].astype(str)
        df["Average"] = df["Average"].astype(int)
        df["Match"] = df["Match"].astype(int)

    if show_ungrouped:
        df["Phase"] = df["Phase"].apply(lambda x: x.split("_")[1])

    chart = (
        alt.Chart(df.melt("Phase"))
        .mark_bar()
        .encode(
            alt.X(
                "variable:N",
                axis=alt.Axis(title=""),
                sort=["Match", "Average"],
            ),
            alt.Y(
                "value:Q",
                axis=alt.Axis(title=f"{match_name} vs {team_num} Average", grid=False),
            ),
            color=alt.Color(
                "variable:N",
                scale=alt.Scale(
                    domain=["Match", "Average"],
                    range=[use_colors[0], use_colors[1]],
                ),
                legend=alt.Legend(
                    title=None,
                    orient=("right" if not_preview else "bottom"),
                    symbolType="circle",
                ),
            ),
            stroke=alt.value("#ffffff"),
            strokeWidth=alt.value(2),
            column="Phase:O",
        )
        .properties(height=200, width=225)
        .configure_axis(labelAngle=0)
    )

    with alt_size[0].container():
        st.altair_chart(chart, use_container_width=True)

    if not_preview:
        try:
            match_progress = team_df
            match_progress["Match Name"] = match_progress["Match Name"].apply(
                lambda x: f"{x} ⭐" if x == match_name else x
            )

            column_config = {}
            for phase in ["AUTO", "TELE", "END", "INFO"]:
                column_config[phase] = st.column_config.ProgressColumn(
                    phase.title(),
                    format=f"%f/{max(match_progress[phase])}",
                    min_value=min(match_progress[phase]),
                    max_value=max(match_progress[phase]),
                )

            st.divider()

            st.dataframe(
                match_progress.drop(columns=["COMMENT"]),
                column_config=column_config,
                column_order=("Match Name", "AUTO", "TELE", "END", "INFO"),
                hide_index=True,
                use_container_width=True,
            )
        except:
            pass


def gen_bar(
    df=st.session_state.df,
    key=0,
    use_presets=True,
    use_group_filters=True,
    use_show_available=True,
    use_show_nums=True,
    use_inline_legend=True,
    use_features=True,
    use_agg_type=True,
    use_filter_selection=True,
    use_max_size=True,
    displayed_teams=[],
    compared_teams=[],
    x_range=[],
    expanders=True,
):
    phases = st.session_state.phases

    variables = [
        "group_filters" if use_group_filters else None,
        "inline_legend" if use_inline_legend else None,
        "show_available" if use_show_available else None,
        "show_nums" if use_show_nums else None,
        "features" if use_features else None,
    ]

    variables = [var for var in variables if var != None]

    if use_presets:
        presets = st.session_state.presets
        preset_choice = st.selectbox("Preset Choice:", ["None"] + list(presets))

        if preset_choice != "None":
            st.header(
                f"Selected Preset: {preset_choice}",
                False,
                help=str(presets[preset_choice]),
            )
    else:
        preset_choice = "None"

    if len(variables) != 0:
        columns = st.columns(len(variables))

    var_count = 0

    def gen_toggle(var_name, var_count, box_name, default, key, disabled):
        if var_name in variables:
            variable = columns[var_count].toggle(
                box_name, default, key=f"{var_name}_{key}", disabled=disabled
            )
            var_count += 1
        else:
            variable = default

        return [variable, var_count]

    if preset_choice == "None":
        group_filters, var_count = gen_toggle(
            "group_filters", var_count, "Group Filters", True, key, False
        )

        inline_legend, var_count = gen_toggle(
            "inline_legend",
            var_count,
            "Inline Legend",
            not group_filters,
            key,
            group_filters,
        )

        show_nums, var_count = gen_toggle(
            "show_nums", var_count, "Team Numbers", True, key, False
        )

        show_available, var_count = gen_toggle(
            "show_available", var_count, "Availability", show_nums, key, not show_nums
        )

        features, var_count = gen_toggle(
            "features", var_count, "Features", False, key, False
        )

        if use_agg_type:
            agg_type = st.selectbox(
                "Aggregation Type:", ("Mean", "Median", "Sum"), key=f"agg_type_{key}"
            ).lower()
        else:
            agg_type = "mean"

        if not group_filters:
            selected_phases = st.multiselect("Phases:", phases, default=phases, key=key)
            phases = [
                col
                for col in df.columns
                if any(col.startswith(f"{phase}_") for phase in selected_phases)
            ]
            selected_filters = phases
            filter_choices = phases
        else:
            filter_choices = phases

        comment_df = df
        df = df.drop("COMMENT_GENERAL_STR_1", axis=1)

        for i in range(len(phases)):
            df.loc[:, phases[i]] = add_cols(
                df,
                phases[i],
            )

        if not use_inline_legend:
            inline_legend = False

        picked = pd.DataFrame(st.session_state.picked)
        picked = picked[picked["Unavailable"].str.contains("x", case=False, na=False)]

        if displayed_teams:
            df = df[df["Team"].isin(displayed_teams + compared_teams)]
        else:
            df = df

        if df.empty:
            df.loc[0] = 0
            no_data = True
        else:
            no_data = False

        feature_list = list(
            comment_df["COMMENT_GENERAL_STR_1"]
            .dropna()
            .str.split(", ")
            .explode()
            .unique()
        )

        df_scouting = st.session_state.scouting
        dt_types = df_scouting["Drivetrain Type"].unique().tolist() + [
            "Unknown Drivetrain"
        ]

        feature_choices = []

        for filter in feature_list + dt_types:
            if str(filter) == "nan":
                pass
            else:
                feature_choices.append(filter)

        selected_features = (
            st.multiselect(
                "Features:",
                feature_choices,
                default=[],
                key=f"selected_features_{key}",
            )
            if use_features and features
            else feature_choices
        )

        df = df.merge(
            df_scouting[
                ["Team #", "Drivetrain Type", "Frame Size LENGTH", "Frame Size WIDTH"]
            ].fillna("Unknown Drivetrain"),
            left_on="Team",
            right_on="Team #",
            how="left",
        ).drop(columns=["Team #"])

        df["Drivetrain Type"] = df["Drivetrain Type"].fillna("Unknown Drivetrain")

        if any(dt in selected_features for dt in dt_types):
            df = df[(df["Drivetrain Type"].isin(selected_features))]

        def get_features(comment):
            return comment.split(", ")

        all_team_features = {}
        kept_teams = []

        def has_features(team):
            if not features:
                return True

            for feature in selected_features:
                if feature not in all_team_features[team] + dt_types:
                    return False

            return True

        for team in comment_df["Team"]:
            comment_df = comment_df.dropna()
            team_values = comment_df.loc[
                comment_df["Team"] == team, "COMMENT_GENERAL_STR_1"
            ].tolist()

            team_features = [get_features(value) for value in team_values]
            team_features = list(
                set([feature for sublist in team_features for feature in sublist])
            )

            all_team_features[team] = team_features

            if has_features(team):
                kept_teams.append(team)

        df = df[df["Team"].isin(kept_teams)]

        if use_filter_selection:
            selected_filters = st.multiselect(
                "Filters:",
                filter_choices,
                default=filter_choices,
                key=f"selected_filters_{key}",
            )
        else:
            selected_filters = filter_choices

        rank_df = df.groupby("Team")[selected_filters].agg(agg_type)
        rank_df["rank"] = rank_df.sum(axis=1).rank(ascending=False).astype(int)
        rank_df.reset_index(inplace=True)

        if use_max_size and features:
            min_size = df[["Frame Size LENGTH", "Frame Size WIDTH"]].min().min()
            max_size = df[["Frame Size LENGTH", "Frame Size WIDTH"]].max().max()
            unscouted_size = max_size + 0.5

            size_limit = st.slider(
                "Max Size:",
                min_value=min_size,
                max_value=unscouted_size,
                value=unscouted_size,
                step=0.5,
                key=f"size_limit_{key}",
            )

            if size_limit == unscouted_size:
                st.toast("Viewing unscouted teams", icon="⚠️")

            df["Frame Size LENGTH"] = df["Frame Size LENGTH"].fillna(unscouted_size)
            df["Frame Size WIDTH"] = df["Frame Size WIDTH"].fillna(unscouted_size)

            df = df[
                (df["Frame Size LENGTH"] <= size_limit)
                & (df["Frame Size WIDTH"] <= size_limit)
            ]

        calc_df = df.groupby("Team")[selected_filters].agg(agg_type)
        calc_df["rank"] = calc_df.sum(axis=1).rank(ascending=False).astype(int)
        calc_df.reset_index(inplace=True)
        data = pd.melt(
            calc_df,
            id_vars=["Team", "rank"],
            value_vars=selected_filters,
            var_name="variable",
            value_name="value",
        )

        calc_df["Score Sum"] = calc_df[selected_filters].sum(axis=1)

        try:
            x_min = (
                math.floor(calc_df.min().min()) - 2
                if calc_df.min().min() < 0
                else math.floor(calc_df.min().min())
            )
        except:
            st.error("No bots found with selected features")
            st.stop()

        x_range = (
            x_range if x_range else [x_min, (round(calc_df["Score Sum"].max()) + 2)]
        )
        x_min, x_max = x_range

        data = data[~data["Team"].isin(compared_teams)]

        tba_rankings = st.session_state.tba_ranks

        def format_y(team, show_available, picked):
            if show_available:
                picked = (
                    "💎"
                    if team == st.secrets["TEAM_NUMBER"]
                    else "🚫" if team in picked["Team"].values else "🟢"
                )

            else:
                picked = ""

            rank = str(tba_rankings.get(str(team), "NA")).zfill(2)

            return f"{picked} {str(team).rjust(4)} [{rank}]"

        data["Team"] = data["Team"].apply(
            lambda team: format_y(team, show_available, picked)
        )

    else:
        no_data = False

    def rgba_to_hex(rgba):
        r, g, b, a = rgba
        return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))

    def gen_cmap(length, cmap_name="Blues"):
        cmap = plt.get_cmap(cmap_name)
        colors = [rgba_to_hex(cmap(i)) for i in np.linspace(0, 0.8, length)]
        return colors

    if preset_choice != "None":
        preset = presets[preset_choice]
        data = pd.DataFrame(preset["data"])
        x_min, x_max = preset["x_range"]
        show_nums = preset["show_nums"]
        selected_filters = preset["selected_filters"]
        inline_legend = preset["inline_legend"]
        group_filters = preset["group_filters"]

    chart = (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X("value:Q", title=" ", scale=alt.Scale(domain=[x_min, x_max])),
            y=alt.Y(
                "Team:N",
                sort=alt.EncodingSortField(field="rank", order="ascending"),
                title="",
                axis=alt.Axis(labels=show_nums),
            ),
            color=alt.Color(
                "variable:N",
                title=" ",
                scale=alt.Scale(
                    domain=selected_filters,
                    range=gen_cmap(len(data["variable"].unique())),
                ),
                legend=alt.Legend(
                    title=None,
                    orient=(
                        "bottom-right"
                        if inline_legend and not group_filters
                        else "bottom"
                    ),
                    symbolType="circle",
                    labelBaseline="alphabetic",
                    labelLimit=0,
                    offset=5,
                    padding=0,
                    rowPadding=0,
                    labelFontSize=(10.5 if inline_legend and not group_filters else 14),
                ),
            ),
            stroke=alt.value("#141414"),
            strokeWidth=alt.value(2),
            tooltip=["value:Q", "variable:N"],
        )
    )

    if selected_filters:
        if not no_data:
            st.altair_chart(chart, use_container_width=True)

        else:
            st.error("Not enough data")
    else:
        st.error("Please select at least one filter")

    if expanders and preset_choice == "None":
        if st.toggle("Ranked Expanders"):
            with st.container(border=True):
                start_time = time.time()
                ranked = rank_df.sort_values(by="rank").astype(int)

                for index, row in ranked.iterrows():
                    team_num = row["Team"]

                    scouting_expander(
                        df=df_scouting,
                        team_num=team_num,
                        rank_info=[
                            ranked.loc[ranked["Team"] == team_num, "rank"].to_list()[0],
                            st.session_state.tba_ranks[str(team_num)],
                        ],
                    )

                st.markdown(
                    f"<span style='font-size: small; color: #808080;'>Loaded in {round(time.time() - start_time, 2)} seconds...</span>",
                    unsafe_allow_html=True,
                )

    if use_presets == True and preset_choice == "None":
        preset_name = st.text_input("New Preset Name:")

        if preset_name.replace(" ", ""):
            if st.button("Add Preset", use_container_width=True):
                presets[preset_name] = {
                    "data": data.to_dict(),
                    "x_range": x_range,
                    "show_nums": show_nums,
                    "selected_filters": selected_filters,
                    "inline_legend": inline_legend,
                    "group_filters": group_filters,
                }

                with open("src\\pickles\\presets.pickle", "wb") as f:
                    pickle.dump(presets, f, pickle.HIGHEST_PROTOCOL)
                st.toast("Successfully added preset!", icon="✅")
