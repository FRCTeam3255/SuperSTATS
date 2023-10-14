import SuperSTATs.build_chart as build
import SuperSTATs.Main as stats
import streamlit as st
import altair as alt
import pandas as pd

df_r = stats.download_sheets_raw(st.secrets["GID_RAW"])

sections = stats.get_match_sections(df_r)

st.set_page_config(
    page_title="[PREVIEW] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
    menu_items={"About": "Kane Was Here 👋"},
)


def gen_team_chart(df, column, team_df, agg_type, filter_cols, match_filters):
    column.altair_chart(
        build.custom_bar_chart(
            build.config_chart(
                df.loc[df["Team"].isin(team_df)],
                filter_cols,
                agg_type,
                False,
                match_filters,
            ),
            False,
            False,
            300,
        )
    )


def display_team(team_header, column, team_df):
    column.header(team_header)
    for team_num in team_df:
        team_name = stats.get_team(team_num)["nickname"]
        column.markdown(
            f"<p style='font-size:20px'><b>[{team_num}]</b> {team_name}</p>",
            unsafe_allow_html=True,
        )


def sort_cols(starts_with):
    df = stats.download_sheets_raw(st.secrets["GID_RAW"]).dropna(subset="Timestamp")
    df_picked = stats.download_sheets_raw(st.secrets["GID_PICKED"])
    df = df.merge(df_picked, on="Team", how="left")

    filter_cols = []
    cols = [col for col in df.columns if col.startswith(starts_with)]
    filter_cols.extend(cols)
    return filter_cols


def main():
    stats.set_font()

    st.header("🔮 Match Preview 🔮")

    teams = {}
    teams_raw = list(st.session_state.team_info_dict.items())
    for team in teams_raw:
        teams[team[1]] = int(team[0])

    df = stats.download_sheets_raw(st.secrets["GID_MATCHES"])
    match_choice = st.selectbox("Match", df["Match"])

    df_sort = df[df["Match"] == match_choice]
    df_sort = df_sort.set_index("Match").transpose()

    df_red = df_sort.filter(like="Red", axis=0)[match_choice].to_list()
    df_blue = df_sort.filter(like="Blue", axis=0)[match_choice].to_list()

    col_red, col_blue = st.columns(2)

    display_team("🔴 Red Alliance 🔴", col_red, df_red)
    display_team("🔵 Blue Alliance 🔵", col_blue, df_blue)

    df = stats.download_sheets_raw(st.secrets["GID_RAW"]).dropna(subset="Timestamp")
    df_picked = stats.download_sheets_raw(st.secrets["GID_PICKED"])
    df = df.merge(df_picked, on="Team", how="left")

    col1, col2, col3 = st.columns(3)
    col3.title("")
    group_filters = col3.checkbox("Group Filters", True)

    if group_filters:
        agg_type = col1.selectbox(
            "Aggregation Type:", ("Mean", "Median", "Sum")
        ).lower()
        filter_cols = sections
    else:
        agg_type = col1.selectbox(
            "Aggregation Type:", ("Mean", "Median", "Sum", "Count")
        ).lower()

        filter_cols = [col for col in df.columns if col.startswith(tuple(sections))]

        sort_type = st.radio("Sorting Type:", ["NONE"] + sections, horizontal=True)

        if sort_type == "NONE":
            filter_cols = [col for col in df.columns if col.startswith(tuple(sections))]
        else:
            filter_cols = sort_cols(sort_type)

    match_filters = col2.multiselect(
        "Match Types:", ["Prac", "Quals", "Playoffs"], default=[]
    )

    if match_filters:
        pass
    else:
        match_filters = ["Prac", "Quals", "Playoffs"]

    selected_filters = st.multiselect("Filters", filter_cols, default=filter_cols)

    gen_team_chart(df, col_red, df_red, agg_type, selected_filters, match_filters)
    gen_team_chart(df, col_blue, df_blue, agg_type, selected_filters, match_filters)


if __name__ == "__main__":
    main()
