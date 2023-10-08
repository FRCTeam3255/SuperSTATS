import SuperSTATs.Main as stats
import streamlit as st
import altair as alt
import pandas as pd

st.set_page_config(
    page_title="[PREVIEW] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
)

def main():
    stats.set_font()

    st.header("🔮 Match Preview 🔮")

    df = stats.download_sheets_raw("1965907354")

    if "team_info_dict" not in st.session_state:
        st.session_state.team_info_dict = stats.download_team_info()

    teams = {}
    teams_raw = list(st.session_state.team_info_dict.items())
    for team in teams_raw:
        teams[team[1]] = int(team[0])

    team_options = [
        f"{team_name} | {team_num}" for team_name, team_num in teams.items()
    ]

    match_choice = st.selectbox("Match", df["Match"])

    df_sort = df[df["Match"]==match_choice]
    df_sort = df_sort.set_index("Match").transpose()

    df_red = df_sort.filter(like="Red", axis=0)[match_choice].to_list()
    df_blue = df_sort.filter(like="Blue", axis=0)[match_choice].to_list()
    st.header(df_red)
    st.header(df_blue)

    # df_blue = df[df["Team"].isin(df_blue)]

if __name__ == "__main__":
    main()
