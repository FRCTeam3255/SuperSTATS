import SuperSTATs.loader as load
import streamlit as st
import altair as alt
import pandas as pd


df = load.download_sheets_raw(st.secrets["GID_RAW"])
sections = load.get_match_sections(df)
filters = []
for section in sections:
    filters.append(section)

pd.options.mode.chained_assignment = None


def add_cols(org_df, reg, filter):
    relevant_columns = [
        col
        for col in org_df.columns
        if col != "COMMENT_GENERAL_1" and col.startswith(filter)
    ]
    org_df[filter] = org_df[relevant_columns].sum(axis=1)
    return org_df[filter]


def config_chart(
    df, column, agg, hide_picked, preset_choice, comment_filters, match_filters
):
    df = df[df["Match Type"].isin(match_filters)]

    df_split = []
    for list in df.columns.str.split("_"):
        if len(list) > 1:
            df_split.append(list)

    points = {}
    for value in df_split:
        points.update({f"{value[0]}_{value[1]}": int(value[2])})

    for col, point in points.items():
        df[f"{col}_{point}"] *= point

    for i in range(len(filters)):
        df.loc[:, filters[i]] = add_cols(
            df,
            f"{sections[i]}_",
            filters[i],
        )

    if hide_picked:
        df = df[~df["Unavailable"].str.contains("x", case=False, na=False)]

    if comment_filters:
        df_scouting = load.download_sheets_raw(st.secrets["GID_SCOUTING"])
        dt_types = df_scouting["Drivetrain Type"].unique().tolist() + [
            "Unknown Drivetrain"
        ]

        df["COMMENT_GENERAL_1"] = df["COMMENT_GENERAL_1"].fillna("Comments Missing")
        filter_choices = (
            st.session_state.comment_options + ["Comments Missing"] + dt_types
        )

        if preset_choice == "None":
            st.session_state.selected_filters = st.multiselect(
                "Features:", filter_choices, default=filter_choices
            )

        selected_df = pd.DataFrame(columns=df.columns)
        drivetrain_df = pd.DataFrame(columns=df_scouting.columns)

        for filter in st.session_state.selected_filters:
            filter_mask = df["COMMENT_GENERAL_1"].str.contains(
                filter, case=False, na=False
            )
            selected_df = pd.concat([selected_df, df[filter_mask]])

            drivetrain_mask = df_scouting["Drivetrain Type"].str.contains(
                filter, case=False, na=False
            )
            drivetrain_df = pd.concat([drivetrain_df, df_scouting[drivetrain_mask]])

        df_scouting = drivetrain_df
        df = selected_df

        merged_df = df.merge(
            df_scouting[
                ["Team #", "Drivetrain Type", "Frame Size WIDTH", "Frame Size LENGTH"]
            ],
            left_on="Team",
            right_on="Team #",
            how="left",
        )
        merged_df = merged_df.drop(columns=["Team #"])

        try:
            min_width = round(merged_df["Frame Size WIDTH"].min()) - 1
            max_width = round(merged_df["Frame Size WIDTH"].max()) + 1

            min_length = round(merged_df["Frame Size LENGTH"].min()) - 1
            max_length = round(merged_df["Frame Size LENGTH"].max()) + 1
        except:
            min_width, max_width, min_length, max_length = 0, 1, 0, 1

        merged_df["Drivetrain Type"].fillna("Unknown Drivetrain", inplace=True)
        merged_df["Frame Size WIDTH"].fillna(min_width, inplace=True)
        merged_df["Frame Size LENGTH"].fillna(min_length, inplace=True)

        if preset_choice == "None":
            square_frame = st.checkbox("Use Same WIDTH and LENGTH", True)
            frame_slider_1, frame_slider_2 = st.columns(2)

            if square_frame:
                square_sides = [max_width, max_length, min_width, min_length]

                max_width = st.slider(
                    "Max Frame WIDTH/LENGTH:",
                    min(square_sides),
                    max(square_sides),
                    max(square_sides),
                    1,
                )
                st.session_state.max_frame_width = max_width
                st.session_state.max_frame_length = max_width

            else:
                max_width = frame_slider_1.slider(
                    "Max Frame WIDTH:", min_width, max_width, max_width, 1
                )
                max_length = frame_slider_2.slider(
                    "Max Frame LENGTH:", min_length, max_length, max_length, 1
                )
                st.session_state.max_frame_width = max_width
                st.session_state.max_frame_length = max_length

        else:
            max_width = st.session_state.presets[preset_choice]["max_frame_width"]
            max_length = st.session_state.presets[preset_choice]["max_frame_length"]

        df = merged_df[
            (merged_df["Drivetrain Type"].isin(st.session_state.selected_filters))
            & (merged_df["Frame Size WIDTH"] <= max_width)
            & (merged_df["Frame Size LENGTH"] <= max_length)
        ]

    else:
        st.session_state.selected_filters = []

    calc_df = df.groupby("Team")[column].agg(agg)
    calc_df["rank"] = calc_df.sum(axis=1).rank(ascending=False).astype(int)
    calc_df.reset_index(inplace=True)
    calc_chart = pd.melt(
        calc_df,
        id_vars=["Team", "rank"],
        value_vars=column,
        var_name="variable",
        value_name="value",
    )

    return calc_chart


def custom_bar_chart(data, hide_teams):
    if hide_teams:
        tooltip = ["value:Q", "variable:N"]
    else:
        tooltip = ["Team:N", "value:Q", "variable:N"]

    tba_rankings = load.get_tba_rankings()

    data["Team"] = data["Team"].apply(
        lambda team: f"{team} [{str(tba_rankings.get(str(team), 'NA')).zfill(2)}]"
    )

    chart = (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X("value:Q", title=" "),
            y=alt.Y(
                "Team:N",
                sort=alt.EncodingSortField(field="rank", order="ascending"),
                title="",
                axis=alt.Axis(labels=not hide_teams),
            ),
            color=alt.Color(
                "variable:N",
                title=" ",
                legend=alt.Legend(title=None, orient="top", symbolType="circle"),
            ),
            tooltip=tooltip,
        )
    )

    return chart
