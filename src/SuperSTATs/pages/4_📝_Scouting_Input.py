import SuperSTATs.load as load
import requests, pickle
import streamlit as st

st.set_page_config(
    page_title="[SCOUT] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
    layout="wide",
)


def main():
    load.app_init()

    import SuperSTATs.styles as style

    st.markdown(style.shimmer("#ffb8e5"), unsafe_allow_html=True)
    st.markdown("<div class='shimmer'>📝 Scouting Input 📝</div>", unsafe_allow_html=True)

    df = st.session_state.scouting

    scouted_teams = df["Team #"].unique()

    unscouted_teams_raw = [
        team for team in st.session_state.team_info if team not in scouted_teams
    ]

    teams_raw = st.session_state.team_info.items()

    if len(unscouted_teams_raw) == 0:
        st.success("All teams have scouting info!")
        st.balloons()
    else:
        unscouted_teams = []
        for num, name in teams_raw:
            if num in unscouted_teams_raw:
                unscouted_teams.append(f"{num} | {name}")

        team_num = st.selectbox("Team:", unscouted_teams)
        team_num = team_num.split(" | ")[0]

        columns = st.columns(2)

        length = columns[0].number_input(
            "Frame Size LENGTH [NO BUMPERS]:", step=0.5, min_value=0.0
        )
        width = columns[1].number_input(
            "Frame Size WIDTH [NO BUMPERS]:", step=0.5, min_value=0.0
        )
        weight = columns[0].number_input(
            "Weight [NO BATTERY]:", step=1.0, min_value=0.0
        )

        dt_type = columns[1].radio(
            "Drivetrain Type:",
            ["Swerve", "Westcoast", "Mecanum", "Other"],
            horizontal=True,
        )

        if dt_type == "Other":
            dt_input = st.text_input("[OTHER] Drivetrain Type:")
            dt_type = (
                f"__other_option__&entry.1374859410.other_option_response={dt_input}"
            )

        comments = st.text_input("Additional Comments:")

        prefill_url = f"https://docs.google.com/forms/d/e/1FAIpQLSf0Wm6xqzuUOaYquHo-oIIZHfIXJIAUA9R64M_PnEQibP_jJw/formResponse?usp=pp_url&entry.1329798282={team_num}&entry.2038191838={length}&entry.2133090800={width}&entry.1034225169={weight}&entry.1374859410={dt_type}&entry.820368818={comments.replace(' ', '+')}&submit=Submit"

        if 0.0 not in [length, width, weight]:
            if st.button("Submit", type="primary", use_container_width=True):
                req = requests.get(prefill_url)
                if req.status_code == 200:
                    st.success("Submitted Successfully! Please Refresh...")
                    st.balloons()
                    load.play_audio("yippee.mp3", 4)
                else:
                    st.error("Submission Unsuccessful! Please Try Again...")
        else:
            st.button("Submit", type="primary", use_container_width=True, disabled=True)
            st.warning("Required Input Missing")

        st.write("""---""")

        with st.expander("Pit Map"):
            pit_map = st.file_uploader("Upload Map: ", type=["png", "jpg"])
            if pit_map:
                with open("src\\pickles\\map.pickle", "wb") as f:
                    pickle.dump(pit_map, f, pickle.HIGHEST_PROTOCOL)
            else:
                try:
                    with open("src\\pickles\\map.pickle", "rb") as f:
                        pit_map = pickle.load(f)
                    st.image(pit_map, use_column_width=True)
                except:
                    pass


if __name__ == "__main__":
    main()
