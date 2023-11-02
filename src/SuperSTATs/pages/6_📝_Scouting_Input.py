import SuperSTATs.loader as load
import streamlit as st

st.set_page_config(
    page_title="[SCOUT] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
    layout="wide",
)


def main():
    load.init_page()

    st.markdown(
        "<h1 style='text-align: center;'>📝 Scouting Input 📝</h1>",
        unsafe_allow_html=True,
    )
    st.title("")

    unscouted_teams_raw = load.get_unscouted_teams()
    teams_raw = st.session_state.team_info_dict.items()

    unscouted_teams = []
    for num, name in teams_raw:
        if num in unscouted_teams_raw:
            unscouted_teams.append(f"{name} | {num}")

    team_num = st.selectbox("Team", unscouted_teams)
    team_num = team_num.split(" | ")[1]
    length = st.number_input("Frame Size LENGTH [NO BUMPERS]", step=0.5)
    width = st.number_input("Frame Size WIDTH [NO BUMPERS]", step=0.5)
    weight = st.number_input("Weight [NO BATTERY]", step=1)

    dt_type = st.radio(
        "Drivetrain Type:",
        ["Swerve", "Westcoast", "Mecanum", "Tank", "Other"],
        horizontal=True,
    )

    if dt_type == "Other":
        dt_input = st.text_input("[OTHER] Drivetrain Type:")
        dt_type = f"__other_option__&entry.1374859410.other_option_response={dt_input}"

    comments = st.text_input("Additional Comments:")

    st.write("""---""")

    prefill_url = f"https://docs.google.com/forms/d/e/1FAIpQLSf0Wm6xqzuUOaYquHo-oIIZHfIXJIAUA9R64M_PnEQibP_jJw/formResponse?usp=pp_url&entry.1329798282={team_num}&entry.2038191838={length}&entry.2133090800={width}&entry.1034225169={weight}&entry.1374859410={dt_type}&entry.820368818={comments.replace(' ', '+')}&submit=Submit"
    st.link_button(
        "Submit",
        prefill_url,
        type="primary",
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
