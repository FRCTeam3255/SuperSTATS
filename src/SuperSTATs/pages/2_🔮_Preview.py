import SuperSTATs.build_chart as build
import SuperSTATs.loader as load
import streamlit as st
import numpy as np

st.set_page_config(
    page_title="[PREVIEW] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
    layout="wide",
)


df_r = load.download_sheets_raw(st.secrets["GID_RAW"])

sections = load.get_match_sections(df_r)


def gen_team_chart(df, column, team_df, agg_type, filter_cols, match_filters):
    team_df = [int(team) for team in team_df]
    column.altair_chart(
        build.custom_bar_chart(
            build.config_chart(
                df.loc[df["Team"].isin(team_df)],
                filter_cols,
                agg_type,
                False,
                False,
                [],
                match_filters,
            ),
            False,
        ),
    )


def check_nan(var_name, var_value, column):
    try:
        if np.isnan(var_value):
            column.text(f"{var_name}: No Data Collected")
    except:
        column.text(f"{var_name}: {var_value}")


def display_team(team_header, column, team_df, show_scouting):
    df = load.download_sheets_raw(st.secrets["GID_SCOUTING"]).dropna(subset="Timestamp")
    column.header(team_header)
    for team_num in team_df:
        team_name = load.get_team(team_num).get("nickname", "N/A")
        column.markdown(
            f"<p style='font-size:20px'><b>[{int(team_num)}]</b> {team_name}</p>",
            unsafe_allow_html=True,
        )
        if show_scouting:
            with column.expander("Scouting Data"):
                sorted_df = df.loc[df["Team #"] == int(team_num)]

                sorted_df = sorted_df.sort_values(by="Timestamp")
                sorted_df = sorted_df.drop_duplicates(keep="last", subset="Team #")

                time_logged = str(sorted_df["Timestamp"].max())
                if time_logged == "nan":
                    column.error("No Data Collected For Team")

                else:
                    length = sorted_df["Frame Size LENGTH"].max()
                    width = sorted_df["Frame Size WIDTH"].max()
                    st.text(f"Length: {length} in | Width: {width} in")
                    st.text(f"Area: {length * width} in²")

                    check_nan("Drivetrain", sorted_df["Drivetrain Type"].max(), st)
                    check_nan("Scouting Comments", sorted_df["Comments"].max(), st)

                    st.text(f"Time Logged: {time_logged}")


def sort_cols(starts_with):
    df = load.download_sheets_raw(st.secrets["GID_RAW"]).dropna(subset="Timestamp")
    df_picked = load.download_sheets_raw(st.secrets["GID_PICKED"])
    df = df.merge(df_picked, on="Team", how="left")

    filter_cols = []
    cols = [col for col in df.columns if col.startswith(starts_with)]
    filter_cols.extend(cols)
    return filter_cols


def calc_score(df, team_num, sections):
    df = df.drop("COMMENT_GENERAL_1", axis=1)
    df_plot = df.loc[(df["Team"] == team_num)]

    mask = df.columns == "Match"
    for section in sections:
        mask = mask | df.columns.str.startswith(f"{section}_")

    df_plot = df_plot.loc[:, mask]

    df_split = []
    for list in df.columns.str.split("_"):
        if len(list) > 1:
            df_split.append(list)

    points = {}
    for value in df_split:
        points.update({f"{value[0]}_{value[1]}_{value[2]}": int(value[2])})

    for col, point in points.items():
        if col in df_plot.columns:
            df_plot[col] *= point

    for score_type in sections:
        columns = [col for col in df_plot.columns if col.startswith(score_type)]
        df_plot[f"{score_type.strip('_').title()} Score"] = df_plot[columns].sum(axis=1)

    excluded_cols = ["Match"]
    sum_cols = [f"{section.title()} Score" for section in sections]
    all_columns = excluded_cols + sum_cols

    df_plot["Total Score"] = df_plot.drop(columns=all_columns, axis=1).sum(axis=1)

    return df_plot


def team_score(df, team_df):
    team_df = [int(team) for team in team_df]
    team_scores = []
    for team in team_df:
        scores = calc_score(df, team, sections)["Total Score"]
        if not np.isnan(scores.mean()):
            team_scores.append(scores.mean())

    if not team_scores:
        return "None"

    if len(team_scores) < 3:
        team_sum = sum(team_scores)
        return f"{str(int(team_sum))} *"
    else:
        return str(int(sum(team_scores)))


def get_alliance_chart(df, team_df):
    match_sections = load.get_match_sections(df)

    auto_values = []
    tele_values = []
    end_values = []

    for team in team_df:
        team_df = df.loc[(df["Team"] == int(team))]

        section_cols = [
            col
            for col in df.columns
            if any(col.startswith(section) for section in match_sections)
        ]
        team_df = team_df[section_cols].reset_index(drop=True)

        column_values = {}
        team_df = team_df.drop("COMMENT_GENERAL_1", axis=1)
        for column in team_df:
            column_value = int(column.split("_")[2])
            sum_value = int(team_df[column].sum()) * column_value
            column_values[column] = sum_value

        sum_values = ["AUTO", "TELE", "END"]

        for sum_for in sum_values:
            value_sum = sum(
                value for key, value in column_values.items() if key.startswith(sum_for)
            )

            if sum_for == "AUTO":
                auto_values.append(value_sum)
            elif sum_for == "TELE":
                tele_values.append(value_sum)
            elif sum_for == "END":
                end_values.append(value_sum)

    team_r = [sum(auto_values), sum(tele_values), sum(end_values)]

    team_t = ["AUTO", "TELE", "END"]

    chart_team_1 = load.gen_radio_chart(
        team_r, team_t, max(team_r), load.hex_to_rgb("#FF3838"), 0.5
    )
    chart_team_2 = load.gen_radio_chart(
        team_r, team_t, max(team_r), load.hex_to_rgb("#2AD3FF"), 0.5
    )

    combined_chart = chart_team_1.add_trace(chart_team_2.data[0])
    return combined_chart


def main():
    load.init_page()

    st.markdown(
        "<h1 style='text-align: center;'>🔮 Match Preview 🔮</h1>", unsafe_allow_html=True
    )
    st.title("")

    teams = {}
    teams_raw = list(st.session_state.team_info_dict.items())
    for team in teams_raw:
        teams[team[1]] = int(team[0])

    col_1, col_2 = st.columns(2)

    if col_1.checkbox("Use Manual Dataframe"):
        df = load.download_sheets_raw(st.secrets["GID_MATCHES"])
    else:
        df = st.session_state.global_match_df

    show_scouting = col_2.checkbox("Show Scouting Data")

    match_choice = st.selectbox("Match:", df["Match"])

    df_sort = df[df["Match"] == match_choice]
    df_sort = df_sort.set_index("Match").transpose()

    df_red = df_sort.filter(like="Red", axis=0)[match_choice].to_list()
    df_blue = df_sort.filter(like="Blue", axis=0)[match_choice].to_list()

    col_red, col_blue = st.columns(2)

    display_team("🔴 Red Alliance 🔴", col_red, df_red, show_scouting)
    display_team("🔵 Blue Alliance 🔵", col_blue, df_blue, show_scouting)

    df = load.download_sheets_raw(st.secrets["GID_RAW"]).dropna(subset="Timestamp")
    df_picked = load.download_sheets_raw(st.secrets["GID_PICKED"])
    df = df.merge(df_picked, on="Team", how="left")

    df_raw = load.download_sheets_raw(st.secrets["GID_RAW"])
    col_red.subheader(f"Projected Score: {team_score(df_raw, df_red)}")
    col_blue.subheader(f"Projected Score: {team_score(df_raw, df_blue)}")

    col_1, col_2 = st.columns(2)

    group_filters = True
    if group_filters:
        agg_type = col_1.selectbox(
            "Aggregation Type:", ("Mean", "Median", "Sum")
        ).lower()
        filter_cols = sections
    else:
        agg_type = col_1.selectbox(
            "Aggregation Type:", ("Mean", "Median", "Sum", "Count")
        ).lower()

        filter_cols = [col for col in df.columns if col.startswith(tuple(sections))]

        sort_type = st.radio(
            "Sorting Type:", ["NONE", "AUTO", "TELE", "END"], horizontal=True
        )
        if sort_type == "NONE":
            filter_cols = [col for col in df.columns if col.startswith(tuple(sections))]
        else:
            filter_cols = sort_cols(sort_type)

    match_filters = col_2.multiselect(
        "Match Types:",
        ["Prac", "Quals", "Playoffs"],
        default=["Quals", "Playoffs"],
    )

    if match_filters:
        pass
    else:
        match_filters = ["Prac", "Quals", "Playoffs"]

    selected_filters = st.multiselect("Filters", filter_cols, default=filter_cols)

    gen_team_chart(df, col_red, df_red, agg_type, selected_filters, match_filters)
    gen_team_chart(df, col_blue, df_blue, agg_type, selected_filters, match_filters)

    st.button("Update Page", type="primary", use_container_width=True)
    st.text("✱ - one or more teams has no stats")

    combined_chart_1 = get_alliance_chart(df, df_red)
    combined_chart_2 = get_alliance_chart(df, df_blue)

    combined_chart_3 = combined_chart_1.add_trace(combined_chart_2.data[0])
    st.plotly_chart(combined_chart_3, use_container_width=True)


if __name__ == "__main__":
    main()
