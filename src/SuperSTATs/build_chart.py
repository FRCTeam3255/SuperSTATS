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


def config_chart(df, column, agg, hide_picked, comment_filters, match_filters):
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

    # TODO: Invert this so it shows any chosen ones, and defaults to show all

    if comment_filters:
        df = df
        pfilters = st.session_state.comment_options
        selected_filters = st.multiselect("Disgard Features:", pfilters)
        mask = [True] * len(df)
        for filter in selected_filters:
            mask = mask & ~df["COMMENT_GENERAL_1"].str.contains(
                filter, case=False, na=False
            )
        df = df[mask]

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
