import SuperSTATs.build_chart as build
import SuperSTATs.loader as load
import streamlit as st
import altair as alt

st.set_page_config(
    page_title="[MATCHES] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
    layout="wide",
)


def plot_line(df, y_value, color):
    return (
        alt.Chart(df)
        .mark_line()
        .encode(x="Match", y=alt.Y(y_value, title="Score"), color=alt.value(color))
    )


def main():
    load.init_page()

    df = load.download_sheets_raw(st.secrets["GID_RAW"]).dropna(subset="Timestamp")

    sections = load.get_match_sections(df)

    st.markdown(
        "<h1 style='text-align: center;'>📈 Team Matches 📉</h1>", unsafe_allow_html=True
    )
    st.title("")

    teams = {}
    teams_raw = st.session_state.team_info_dict.items()

    for team in teams_raw:
        teams[team[1]] = int(team[0])

    team_options = [
        f"{team_name} | {team_num}" for team_name, team_num in teams.items()
    ]

    col1, col2 = st.columns(2)
    selected_team = col2.selectbox("Select Team:", sorted(team_options))
    team_num = int(selected_team.split(" | ")[1])

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

    df_plot = df_plot.reset_index(drop=True)

    selected_filters = col1.multiselect("Filters:", sections, default=sections)

    line_chart = plot_line(df_plot, "Total Score", "red").properties(
        title=str(selected_team)
    )

    colors = iter(["orange", "yellow", "lime", "cyan", "violet"])
    for stage in selected_filters:
        line_chart += plot_line(df_plot, f"{stage.title()} Score", next(colors))

    st.altair_chart(line_chart, use_container_width=True)

    st.title("")
    show_raw = st.checkbox("Show Raw Data")
    if show_raw:
        st.subheader(f"Raw Data For Team {team_num}")
        st.table(df.loc[(df["Team"] == team_num)])


if __name__ == "__main__":
    main()
