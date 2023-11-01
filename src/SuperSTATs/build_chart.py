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
            df_scouting[["Team #", "Drivetrain Type", "Frame Size AREA"]],
            left_on="Team",
            right_on="Team #",
            how="left",
        )
        merged_df = merged_df.drop(columns=["Team #"])

        try:
            min_area = round(merged_df["Frame Size AREA"].min()) - 5
            max_area = round(merged_df["Frame Size AREA"].max()) + 5
        except:
            min_area = 0
            max_area = 1

        merged_df["Drivetrain Type"].fillna("Unknown Drivetrain", inplace=True)
        merged_df["Frame Size AREA"].fillna(min_area, inplace=True)

        if preset_choice == "None":
            max_area = st.slider("Max Frame Area:", min_area, max_area, max_area, 1)
            st.session_state.max_frame_area = max_area
        else:
            max_area = st.session_state.presets[preset_choice]["max_frame_area"]

        df = merged_df[
            (merged_df["Drivetrain Type"].isin(st.session_state.selected_filters))
            & (merged_df["Frame Size AREA"] <= max_area)
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
