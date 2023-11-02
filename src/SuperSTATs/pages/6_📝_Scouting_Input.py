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

    with st.form("Scouting Input", clear_on_submit=True):
        team_num = st.selectbox("Team", unscouted_teams)
        team_num = team_num.split(" | ")[1]
        length = st.number_input("Frame Size LENGTH [NO BUMPERS]", step=0.5)
        width = st.number_input("Frame Size WIDTH [NO BUMPERS]", step=0.5)
        weight = st.number_input("Weight [NO BATTERY]", step=1)

        dt_type = st.radio(
            "Sorting Type:",
            ["Westcoast", "Swerve", "Mecanum", "Tank"],
            horizontal=True,
        )

        comments = st.text_input("Additional Comments:")

        st.write("""---""")
        submitted = st.form_submit_button("Submit", use_container_width=True)

    if submitted:
        prefill_url = f"https://docs.google.com/forms/d/e/1FAIpQLSf0Wm6xqzuUOaYquHo-oIIZHfIXJIAUA9R64M_PnEQibP_jJw/viewform?usp=pp_url&entry.1329798282={team_num}&entry.2038191838={length}&entry.2133090800={width}&entry.1034225169={weight}&entry.1374859410={dt_type}&entry.820368818={comments.replace(' ', '+')}"

        st.balloons()
        st.link_button(
            "Go To Prefilled Form",
            prefill_url,
            type="primary",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
