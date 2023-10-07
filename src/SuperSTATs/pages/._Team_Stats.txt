import SuperSTATs.Main as stats
import streamlit as st
import altair as alt
import pandas as pd

st.set_page_config(
    page_title="[TEAM] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
    menu_items={"About": "Kane Was Here 👋"},
)

bar_height = 110


def custom_bar_chart(data, height):
    chart = (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X("mean:Q", title=" "),
            y=alt.Y("Team:N", title=""),
            color=alt.Color("variable:N", title=""),
            tooltip=["Team:N", "mean:Q", "variable:N"],
        )
        .properties(height=height)
    )
    return chart


def config_chart(team_num, df, grouped_cols):
    team_data = df[df["Team"] == team_num]
    row_avg = round(team_data[grouped_cols].mean(), 3)
    row_avg = pd.DataFrame(row_avg, columns=["mean"]).reset_index()
    row_avg["Team"] = team_num
    row_avg["variable"] = row_avg["index"]
    return row_avg


def main():
    stats.set_font()

    df = stats.download_sheets_raw("1318549794")

    teams = {}
    teams_raw = list(st.session_state.team_info_dict.items())
    for team in teams_raw:
        teams[team[1]] = int(team[0])

    team_options = [
        f"{team_name} | {team_num}" for team_name, team_num in teams.items()
    ]

    selected_team = st.selectbox("Select Team:", sorted(team_options))
    team_num = int(selected_team.split(" | ")[1])
    st.title(f"📈 Team {team_num} Averages 📉")

    with st.expander("[ Auto ]"):
        row_avg = config_chart(
            team_num,
            df,
            [
                "Auton Top",
                "Auton Middle",
                "Auton Bottom",
                "Auton Mobility",
                "Auton Docked NOT engaged",
                "Auton Docked ENGAGED",
            ],
        )
        st.altair_chart(custom_bar_chart(row_avg, bar_height))

    with st.expander("[ Teleop ]"):
        row_avg = config_chart(
            team_num,
            df,
            [
                "Top Row",
                "Middle Row",
                "Bottom Row",
            ],
        )
        st.altair_chart(custom_bar_chart(row_avg, bar_height))

    with st.expander("[ End Game ]"):
        row_avg = config_chart(
            team_num,
            df,
            [
                "Parked",
                "Docked NOT engaged",
                "Docked ENGAGED",
            ],
        )
        st.altair_chart(custom_bar_chart(row_avg, bar_height))


if __name__ == "__main__":
    main()
