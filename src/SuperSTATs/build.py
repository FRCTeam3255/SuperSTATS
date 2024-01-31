import SuperSTATs.load as load
import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import pickle
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
    team_num,
    df,
    rank_info=[],
    start_expanded=False,
    calc_bumpers=False,
    error_prefix=False,
    column=st,
):
    team_name = st.session_state.team_info[team_num]

    expander_name = f"[{team_num}] {team_name}"
    if len(rank_info) == 2:
        expander_name += f" [🦸#{rank_info[0]}/💎#{rank_info[1]}]"

    with column.expander(expander_name, start_expanded):
        if len(rank_info) == 2:
            st.text(f"SN Rank: {rank_info[0]} | TBA Rank: {rank_info[1]}")

        sorted_df = df.loc[df["Team #"] == int(team_num)]
        sorted_df = sorted_df.sort_values(by="Timestamp")
        sorted_df = sorted_df.drop_duplicates(keep="last", subset="Team #")

        time_logged = str(sorted_df["Timestamp"].max())

        if time_logged == "nan":
            error_message = (
                f"[{team_num}] {team_name} - No Data" if error_prefix else "No Data"
            )
            column.error(error_message)

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


def gen_bar(
    df=st.session_state.df,
    key=0,
    use_presets=True,
    use_group_filters=True,
    use_hide_picked=True,
    use_hide_nums=True,
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
        "hide_picked" if use_hide_picked else None,
        "hide_nums" if use_hide_nums else None,
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

    def gen_toggle(var_name, var_count, box_name, default, key):
        if var_name in variables:
            variable = columns[var_count].toggle(
                box_name, default, key=f"{var_name}_{key}"
            )
            var_count += 1
        else:
            variable = default

        return [variable, var_count]

    if preset_choice == "None":
        group_filters, var_count = gen_toggle(
            "group_filters", var_count, "Group Filters", True, key
        )

        inline_legend, var_count = gen_toggle(
            "inline_legend", var_count, "Inline Legend", True, key
        )

        hide_picked, var_count = gen_toggle(
            "hide_picked", var_count, "Hide Picked Teams", False, key
        )

        hide_nums, var_count = gen_toggle(
            "hide_nums", var_count, "Hide Team Numbers", False, key
        )

        features, var_count = gen_toggle("features", var_count, "Features", False, key)

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

        if hide_picked:
            picked = pd.DataFrame(st.session_state.picked)
            picked = picked[
                picked["Unavailable"].str.contains("x", case=False, na=False)
            ]
            df = df[~df["Team"].isin(picked["Team"])]

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
                default=feature_choices,
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
        df = df[(df["Drivetrain Type"].isin(selected_features))]

        def get_features(comment):
            return comment.split(", ")

        all_team_features = {}
        kept_teams = []

        def has_features(team):
            if all(item in selected_features for item in all_team_features[team]):
                return True
            return False

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

        if use_max_size:
            min_size = df[["Frame Size LENGTH", "Frame Size WIDTH"]].min().min()
            max_size = df[["Frame Size LENGTH", "Frame Size WIDTH"]].max().max()
            unscouted_size = max_size + 0.5

            size_limit = st.slider(
                "Max Size:",
                min_value=min_size,
                max_value=unscouted_size,
                value=max_size,
                step=0.5,
                key=f"size_limit_{key}",
            )

            if size_limit == unscouted_size:
                st.warning("WARNING: Viewing unscouted teams")

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

        x_min = (
            math.floor(calc_df.min().min()) - 2
            if calc_df.min().min() < 0
            else math.floor(calc_df.min().min())
        )

        x_range = (
            x_range if x_range else [x_min, (round(calc_df["Score Sum"].max()) + 2)]
        )
        x_min, x_max = x_range

        data = data[~data["Team"].isin(compared_teams)]

        tba_rankings = st.session_state.tba_ranks

        data["Team"] = data["Team"].apply(
            lambda team: f"{team} [{str(tba_rankings.get(str(team), 'NA')).zfill(2)}]"
        )
    else:
        group_filters = ""
        inline_legend = ""
        hide_picked = ""
        hide_nums = ""
        features = ""
        agg_type = ""
        selected_filters = [""]
        no_data = ""

    if preset_choice != "None":
        preset = presets[preset_choice]
        hide_nums = preset["hide_nums"]
        x_min = preset["x_range"][0]
        x_max = preset["x_range"][1]
        inline_legend = preset["inline_legend"]
        group_filters = preset["group_filters"]
        data = pd.DataFrame(preset["data"])

    chart = (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X("value:Q", title=" ", scale=alt.Scale(domain=[x_min, x_max])),
            y=alt.Y(
                "Team:N",
                sort=alt.EncodingSortField(field="rank", order="ascending"),
                title="",
                axis=alt.Axis(labels=not hide_nums),
            ),
            color=alt.Color(
                "variable:N",
                title=" ",
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

    if expanders:
        if st.toggle("Ranked Expanders"):
            with st.container(border=True):
                ranked = rank_df.sort_values(by="rank").astype(int)
                for index, row in ranked.iterrows():
                    team_num = row["Team"]
                    scouting_expander(
                        team_num=team_num,
                        df=df_scouting,
                        rank_info=[
                            ranked.loc[ranked["Team"] == team_num, "rank"].to_list()[0],
                            st.session_state.tba_ranks[str(team_num)],
                        ],
                    )

    if use_presets == True and preset_choice == "None":
        preset_name = st.text_input("New Preset Name:")

        if preset_name:
            if st.button("Add Preset", use_container_width=True):
                presets[preset_name] = {
                    "hide_nums": hide_nums,
                    "x_range": x_range,
                    "x_max": x_max,
                    "inline_legend": inline_legend,
                    "group_filters": group_filters,
                    "data": data.to_dict(),
                }
                with open("src\\pickles\\presets.pickle", "wb") as f:
                    pickle.dump(presets, f, pickle.HIGHEST_PROTOCOL)
                st.success("Successfully added preset!")


def calc_projected(team_df, return_row=False):
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
            team_score.loc[:, phases[i]] = add_cols(
                team_score,
                phases[i],
            )

        if return_row:
            team_score["Match Name"] = (
                team_score["Match Type"] + " " + team_score["Match"].astype(str)
            )
            return team_score[["Match Name"] + phases]

        match_count += len(team_score)
        team_score = team_score[phases].sum().to_frame().T
        alliance_score = pd.concat([alliance_score, team_score], ignore_index=True)

    alliance_score = alliance_score.sum().sum()
    projected_score = round(
        (alliance_score / phase_count) * round(match_count / len(team_df))
    )

    return projected_score
