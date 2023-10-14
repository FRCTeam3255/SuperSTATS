import SuperSTATs.build_chart as build
import SuperSTATs.Main as stats
import streamlit as st

st.set_page_config(
    page_title="[SCOUT] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
    layout="wide",
)

df_r = stats.download_sheets_raw(st.secrets["GID_RAW"])

sections = stats.get_match_sections(df_r)


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

    sorted_df = df.loc[df['Team #'] == team_num]

    sorted_df = sorted_df.sort_values(by="Timestamp")
    sorted_df = sorted_df.drop_duplicates(keep="last", subset="Team #")

    st.title(f"Team: {team_name} | {team_num}")

    try:
        frame_length = int(sorted_df["Frame Size LENGTH"])
        frame_width = int(sorted_df["Frame Size WIDTH"])
        st.subheader(f"Length: {frame_length} in | Width: {frame_width} in | Area: {frame_length * frame_width} in²")

        weight = int(sorted_df["Weight"])
        st.subheader(f"Weight: {weight} lbs")
        
        drivetrain = str(sorted_df["Drivetrain Type"].max())
        st.subheader(f"Drivetrain: {drivetrain}")

        time_logged = str(sorted_df["Timestamp"].max())
        st.text(f"Time Logged: {time_logged}")

        st.button("Reload Values")
    except:
        st.error("No Data Collected For This Team")

if __name__ == "__main__":
    main()
