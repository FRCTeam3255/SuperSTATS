import SuperSTATs.Main as stats
import streamlit as st
import altair as alt
import pandas as pd
import tbapy

st.set_page_config(
    page_title="[STATS] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
)

df = stats.download_sheets_raw("1318549794").dropna(subset="Timestamp")
df_picked = stats.download_sheets_raw("337514688")
df = df.merge(df_picked, on="Team", how="left")


def add_cols(org_df, reg, filter):
    org_df[filter] = org_df.filter(regex=reg).sum(axis=1)
    return org_df[filter]


def custom_bar_chart(data):
    chart = (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X("value:Q", title=" "),
            y=alt.Y(
                "Team:N",
                sort=alt.EncodingSortField(field="rank", order="ascending"),
                title="",
            ),
            color=alt.Color("variable:N", title=" "),
            tooltip=["Team:N", "value:Q", "variable:N"],
        )
        .properties(width=700, height=1500)
    )

    return chart


def config_chart(column, agg, hidePicked=False):
    global df
    df_split = []
    for list in df.columns.str.split("_"):
        if len(list) > 1:
            df_split.append(list)

    points = {}
    for value in df_split:
        points.update({f"{value[0]}_{value[1]}": int(value[2])})

    for col, point in points.items():
        df[f"{col}_{point}"] *= point

    df["Autonomous"] = add_cols(
        df,
        r"AUTON_",
        "autonomous",
    )

    df["Teleop"] = add_cols(
        df,
        r"TELEOP_",
        "teleop",
    )

    df["Endgame"] = add_cols(
        df,
        r"END_",
        "endgame",
    )

    if hidePicked:
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


def main():
    stats.set_font()

    st.header("NURD Stats")

    hidePicked = st.checkbox("Hide Picked Teams", False)

    col1, col2 = st.columns(2)
    groupFilters = col2.checkbox("Group Filters", True)

    if groupFilters:
        aggType = col1.selectbox("Aggregation Type", ("Mean", "Median", "Sum")).lower()
    else:
        aggType = col1.selectbox(
            "Aggregation Type", ("Mean", "Median", "Sum", "Count")
        ).lower()

    if groupFilters:
        filter_cols = ["Autonomous", "Teleop", "Endgame"]
    else:
        filter_cols = [
            col
            for col in df.columns
            if col.startswith(tuple(["AUTON_", "TELEOP_", "END_"]))
        ]

    selected_filters = st.multiselect("Filters", filter_cols, default=filter_cols)

    if selected_filters:
        st.altair_chart(
            custom_bar_chart(config_chart(selected_filters, aggType, hidePicked))
        )
    else:
        st.error("Please select at least one filter")


if __name__ == "__main__":
    main()
