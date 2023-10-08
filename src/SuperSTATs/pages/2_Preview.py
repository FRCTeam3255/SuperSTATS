import SuperSTATs.build_chart as build
import SuperSTATs.Main as stats
import streamlit as st
import altair as alt
import pandas as pd

st.set_page_config(
    page_title="[PREVIEW] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
)


def gen_team_chart(df, column, team_df, aggType, filter_cols):
    column.altair_chart(
        build.custom_bar_chart(
            build.config_chart(
                df.loc[df["Team"].isin(team_df)], filter_cols, aggType, False
            ),
            350,
            300,
        )
    )


def main():
    stats.set_font()

    st.header("🔮 Match Preview 🔮")

    df = stats.download_sheets_raw("1965907354")

    teams = {}
    teams_raw = list(st.session_state.team_info_dict.items())
    for team in teams_raw:
        teams[team[1]] = int(team[0])

    match_choice = st.selectbox("Match", df["Match"])

    df_sort = df[df["Match"] == match_choice]
    df_sort = df_sort.set_index("Match").transpose()

    df_red = df_sort.filter(like="Red", axis=0)[match_choice].to_list()
    df_blue = df_sort.filter(like="Blue", axis=0)[match_choice].to_list()

    col_red, col_blue = st.columns(2)

    col_red.header("🔴 Red Alliance 🔴")
    for team in df_red:
        col_red.subheader(team)

    col_blue.header("🔵 Blue Alliance 🔵")
    for team in df_blue:
        col_blue.subheader(team)

    df = stats.download_sheets_raw("1318549794").dropna(subset="Timestamp")
    df_picked = stats.download_sheets_raw("337514688")
    df = df.merge(df_picked, on="Team", how="left")

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
            if col.startswith(tuple(["AUTON", "TELEOP", "END"]))
        ]

    selected_filters = st.multiselect("Filters", filter_cols, default=filter_cols)

    filter_cols = ["Autonomous", "Teleop", "Endgame"]

    gen_team_chart(df, col_red, df_red, aggType, selected_filters)
    gen_team_chart(df, col_blue, df_blue, aggType, selected_filters)


if __name__ == "__main__":
    main()
