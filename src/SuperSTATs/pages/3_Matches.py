import SuperSTATs.build_chart as build
import SuperSTATs.Main as stats
import streamlit as st
import altair as alt

st.set_page_config(
    page_title="[MATCHES] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
)

df = stats.download_sheets_raw(st.secrets["GID_RAW"]).dropna(subset="Timestamp")


def plot_line(df, y_value, color, expand_graph):
    if expand_graph:
        size = 700
    else:
        size = 350

    return (
        alt.Chart(df)
        .mark_line()
        .encode(x="Match", y=alt.Y(y_value, title="Score"), color=alt.value(color))
        .properties(width=size, height=size)
    )


def main():
    stats.set_font()

    st.title(f"📈 Team Matches 📉")
    
    teams = {}
    teams_raw = st.session_state.team_info_dict.items()

    for team in teams_raw:
        teams[team[1]] = int(team[0])

    team_options = [
        f"{team_name} | {team_num}" for team_name, team_num in teams.items()
    ]

    selected_team = st.selectbox("Select Team:", sorted(team_options))
    team_num = int(selected_team.split(" | ")[1])

    df_plot = df.loc[(df["Team"] == team_num)]

    
    mask = (
        (df.columns == "Match")
        | df.columns.str.startswith("AUTON_")
        | df.columns.str.startswith("TELEOP_")
        | df.columns.str.startswith("END_")
    )
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

    score_types = ["AUTON_", "TELEOP_", "END_"]

    for score_type in score_types:
        columns = [col for col in df_plot.columns if col.startswith(score_type)]
        df_plot[f"{score_type.strip('_').title()} Score"] = df_plot[columns].sum(axis=1)

    df_plot["Total Score"] = df_plot.drop(["Match", "Auton Score", "Teleop Score", "End Score"], axis=1).sum(axis=1)

    df_plot = df_plot.reset_index(drop=True)

    expand_graph = st.checkbox("Expand Graph", False)

    stage_colors = {"Auton": "cyan", "Teleop": "lime", "End": "orange"}

    line_chart = plot_line(df_plot, "Total Score", "red", expand_graph).properties(
        title=str(selected_team))

    for stage, color in stage_colors.items():
        line_chart += plot_line(df_plot, f"{stage} Score", color, expand_graph)

    st.altair_chart(line_chart)

    red_col, blue_col, green_col, orange_col = st.columns(4)
    red_col.text("🔴 Score")
    blue_col.text("🔵 Auto")
    green_col.text("🟢 Teleop")
    orange_col.text("🟠 Endgame")

    show_raw = st.checkbox("Show Raw Data")
    if show_raw:
        st.table(df_plot)


if __name__ == "__main__":
    main()
