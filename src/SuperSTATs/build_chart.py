import streamlit as st
import altair as alt
import pandas as pd

filters = st.secrets["FILTER_COLS"]
sections = st.secrets["STAT_SECTIONS"]


def add_cols(org_df, reg, filter):
    org_df[filter] = org_df.filter(regex=reg).sum(axis=1)
    return org_df[filter]


def config_chart(df, column, agg, hide_picked):
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
        df[filters[i]] = add_cols(
            df,
            f"{sections[i]}_",
            filters[i],
        )

    if hide_picked:
        df = df[~df["Unavailable"].str.contains("x", case=False, na=False)]

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


def custom_bar_chart(data, hide_teams, wide_chart, height):
    if wide_chart:
        width = 700
    else:
        width = 350

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
                "variable:N", title=" ", legend=alt.Legend(title=None, orient="top")
            ),
            tooltip=tooltip,
        )
        .properties(width=width, height=height)
    )

    return chart
