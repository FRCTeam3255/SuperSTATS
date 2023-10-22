import SuperSTATs.build_chart as build
import SuperSTATs.loader as load
import streamlit as st
import numpy as np

st.set_page_config(
    page_title="[SCOUT] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
    layout="wide",
)

# df_r = load.download_sheets_raw(st.secrets["GID_RAW"])

# sections = load.get_match_sections(df_r)


def main():
    load.init_page()

    df = load.download_sheets_raw(st.secrets["GID_SCOUTING"]).dropna(subset="Timestamp")

    st.markdown(
        "<h1 style='text-align: center;'>🔭 Team Scouting 🔭<", unsafe_allow_html=True
    )
    st.title("")

    compare_teams = st.checkbox("Compare Teams", False)
    col1, col2 = st.columns(2)

    def check_nan(var_name, var_value, column):
        try:
            if np.isnan(var_value):
                column.subheader(f"{var_name}: No Data Collected")
        except:
            column.subheader(f"{var_name}: {var_value}")

    teams = {}
    teams_raw = st.session_state.team_info_dict.items()

    for team in teams_raw:
        teams[team[1]] = int(team[0])

    team_options = [
        f"{team_name} | {team_num}" for team_name, team_num in teams.items()
    ]

    def get_team_scouting(df, column, side_value, check_nan, team_options):
        selected_team = column.selectbox(
            f"Select {side_value} Team:", sorted(team_options)
        )
        team_name = str(selected_team.split(" | ")[0])
        team_num = int(selected_team.split(" | ")[1])

        sorted_df = df.loc[df["Team #"] == team_num]

        sorted_df = sorted_df.sort_values(by="Timestamp")
        sorted_df = sorted_df.drop_duplicates(keep="last", subset="Team #")

        column.title(f"Team {team_num}: {team_name}")

        time_logged = str(sorted_df["Timestamp"].max())
        if time_logged == "nan":
            column.error("No Data Collected For Team")

        else:
            length = sorted_df["Frame Size LENGTH"].max()
            width = sorted_df["Frame Size WIDTH"].max()
            column.subheader(f"Length: {length} in | Width: {width} in")
            column.subheader(f"Area: {length * width} in²")

            check_nan("Drivetrain", sorted_df["Drivetrain Type"].max(), column)
            check_nan(
                "Feeders", sorted_df["Which feeder does your robot go to"].max(), column
            )
            check_nan("Scouting Comments", sorted_df["Comments"].max(), column)

            # match_comments = "[Work in Progress]"
            # check_nan("Match Comments", match_comments)

            column.text(f"Time Logged: {time_logged}")

    if compare_teams:
        get_team_scouting(df, col1, "First", check_nan, team_options)
        get_team_scouting(df, col2, "Second", check_nan, team_options)
    else:
        get_team_scouting(df, st, "", check_nan, team_options)

    st.button("Reload Values", use_container_width=True)

    df_raw = load.download_sheets_raw(st.secrets["GID_RAW"])
    unique_teams = df_raw["Team"].unique()

    scouted_teams = df["Team #"].unique()
    unscouted_teams = [team for team in unique_teams if team not in scouted_teams]

    with st.expander("Unscouted Teams"):
        if not unscouted_teams:
            st.write("All teams have scouting info!")
        else:
            for team in unscouted_teams:
                st.write(f"- {team}")


if __name__ == "__main__":
    main()
