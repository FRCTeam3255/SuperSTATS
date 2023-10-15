import SuperSTATs.build_chart as build
import SuperSTATs.Main as stats
import streamlit as st
import numpy as np

st.set_page_config(
    page_title="[SCOUT] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
    layout="wide",
)

df_r = stats.download_sheets_raw(st.secrets["GID_RAW"])

sections = stats.get_match_sections(df_r)


def check_nan(var_name, var_value):
    try:
        if np.isnan(var_value):
            st.subheader(f"{var_name}: No Data Collected")
    except:
        st.subheader(f"{var_name}: {var_value}")


def main():
    stats.set_font()

    df = stats.download_sheets_raw(st.secrets["GID_SCOUTING"]).dropna(
        subset="Timestamp"
    )

    st.markdown(
        "<h1 style='text-align: center;'>🔭 Team Scouting 🔭<", unsafe_allow_html=True
    )
    st.title("")

    teams = {}
    teams_raw = st.session_state.team_info_dict.items()

    for team in teams_raw:
        teams[team[1]] = int(team[0])

    team_options = [
        f"{team_name} | {team_num}" for team_name, team_num in teams.items()
    ]

    selected_team = st.selectbox("Select Team:", sorted(team_options))
    team_name = str(selected_team.split(" | ")[0])
    team_num = int(selected_team.split(" | ")[1])

    sorted_df = df.loc[df["Team #"] == team_num]

    sorted_df = sorted_df.sort_values(by="Timestamp")
    sorted_df = sorted_df.drop_duplicates(keep="last", subset="Team #")

    st.title(f"Team: {team_name} | {team_num}")

    time_logged = str(sorted_df["Timestamp"].max())
    if time_logged == "nan":
        st.error("No Data Collected For Team")

    else:
        length = sorted_df["Frame Size LENGTH"].max()
        width = sorted_df["Frame Size WIDTH"].max()
        st.subheader(f"Length: {length} in | Width: {width} in")
        st.subheader(f"Area: {length * width} in²")

        check_nan("Drivetrain", sorted_df["Drivetrain Type"].max())
        check_nan("Feeders", sorted_df["Which feeder does your robot go to"].max())
        check_nan("Scouting Comments", sorted_df["Comments"].max())

        df_raw = stats.download_sheets_raw(st.secrets["GID_RAW"]).dropna(
            subset="Timestamp"
        )
        # match_comments = "[Work in Progress]"
        # check_nan("Match Comments", match_comments)

        st.text(f"Time Logged: {time_logged}")

        st.button("Reload Values")


if __name__ == "__main__":
    main()
