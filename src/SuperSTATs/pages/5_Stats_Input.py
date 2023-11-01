import SuperSTATs.loader as load
import streamlit as st

st.set_page_config(
    page_title="[SCOUT] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
    layout="wide",
)


def gen_num_container(
    column, on_mobile, session_state, num_name, btn_key_inc, btn_key_dec, allow_negative
):
    with column.container():
        left_btn, num_value, right_btn = st.columns(3)

        if on_mobile:
            if left_btn.button(
                "➕", key=btn_key_inc, use_container_width=True, type="primary"
            ):
                session_state += 1

            if right_btn.button(
                "➖", key=btn_key_dec, use_container_width=True, type="primary"
            ):
                if allow_negative:
                    session_state -= 1
                else:
                    if session_state > 0:
                        session_state -= 1

        else:
            if left_btn.button(
                "➖", key=btn_key_inc, use_container_width=True, type="primary"
            ):
                if allow_negative:
                    session_state -= 1
                else:
                    if session_state > 0:
                        session_state -= 1

            if right_btn.button(
                "➕", key=btn_key_dec, use_container_width=True, type="primary"
            ):
                session_state += 1

        num_value.markdown(
            f'<div style="text-align: center;">{num_name}: {session_state}</div>',
            unsafe_allow_html=True,
        )

        if on_mobile:
            st.markdown("---")

        return session_state


def main():
    load.init_page()

    st.markdown(
        "<h1 style='text-align: center;'>✏️ Stats Input ✏️</h1>", unsafe_allow_html=True
    )
    st.title("")

    # TODO: Clean up the init/clear and make radio buttons reset to index 0

    if "input_init" not in st.session_state:
        st.session_state.input_init = True

        st.session_state.auto_cone_high = 0
        st.session_state.auto_cube_high = 0
        st.session_state.auto_cone_mid = 0
        st.session_state.auto_cube_mid = 0
        st.session_state.auto_low = 0

        st.session_state.tele_cone_high = 0
        st.session_state.tele_cube_high = 0
        st.session_state.tele_cone_mid = 0
        st.session_state.tele_cube_mid = 0
        st.session_state.tele_low = 0

        st.session_state.info_penalties = 0
        st.session_state.info_notes = 0

    if st.button("Clear Form", use_container_width=True, type="primary"):
        st.session_state.auto_cone_high = 0
        st.session_state.auto_cube_high = 0
        st.session_state.auto_cone_mid = 0
        st.session_state.auto_cube_mid = 0
        st.session_state.auto_low = 0

        st.session_state.tele_cone_high = 0
        st.session_state.tele_cube_high = 0
        st.session_state.tele_cone_mid = 0
        st.session_state.tele_cube_mid = 0
        st.session_state.tele_low = 0

        st.session_state.info_penalties = 0
        st.session_state.info_notes = 0

        st.session_state.comment_options = []

    on_mobile = st.checkbox("Mobile", False)

    teams = {}
    teams_raw = st.session_state.team_info_dict.items()
    for team in teams_raw:
        teams[team[1]] = int(team[0])

    df = st.session_state.global_match_df

    selection_col_1, selection_col_2 = st.columns(2)

    name_input = (selection_col_1.text_input("Your Name:", max_chars=2)).upper()
    match_choice = selection_col_2.selectbox("Match:", df["Match"])

    df_sort = df[df["Match"] == match_choice]
    df_sort = df_sort.set_index("Match").transpose()

    df_red = df_sort.filter(like="Red", axis=0)[match_choice].to_list()
    df_blue = df_sort.filter(like="Blue", axis=0)[match_choice].to_list()

    df_red = [int(value) for value in df_red]
    df_blue = [int(value) for value in df_blue]

    team_color = selection_col_1.radio("Team Color:", ["Red", "Blue"], horizontal=True)

    if team_color == "Red":
        selected_team = selection_col_2.radio("Team Choice:", df_red, horizontal=True)
        color_input = "R"

    if team_color == "Blue":
        selected_team = selection_col_2.radio("Team Choice:", df_blue, horizontal=True)
        color_input = "B"

    match_split = match_choice.split(" ")
    match_type_input = match_split[0]
    if match_type_input == "Playoff":
        match_type_input = "Playoffs"
    match_input = match_split[1]

    team_input = selected_team

    st.markdown("""---""")

    st.markdown(
        f'<div style="text-align: center; font-size: 32px;">Autonomous</div>',
        unsafe_allow_html=True,
    )
    st.title("")

    auto_col_1, auto_col_2 = st.columns(2)

    st.session_state.auto_cone_high = gen_num_container(
        auto_col_1,
        on_mobile,
        st.session_state.auto_cone_high,
        "AUTO ⚠️ HIGH",
        "AUTO⚠️HIGH➕",
        "AUTO⚠️HIGH➖",
        False,
    )

    st.session_state.auto_cube_high = gen_num_container(
        auto_col_2,
        on_mobile,
        st.session_state.auto_cube_high,
        "AUTO 🟪 HIGH",
        "AUTO🟪HIGH➕",
        "AUTO🟪HIGH➖",
        False,
    )

    st.session_state.auto_cone_mid = gen_num_container(
        auto_col_1,
        on_mobile,
        st.session_state.auto_cone_mid,
        "AUTO ⚠️ MID",
        "AUTO⚠️MID➕",
        "AUTO⚠️MID➖",
        False,
    )

    st.session_state.auto_cube_mid = gen_num_container(
        auto_col_2,
        on_mobile,
        st.session_state.auto_cube_mid,
        "AUTO 🟪 MID",
        "AUTO🟪MID➕",
        "AUTO🟪MID➖",
        False,
    )

    st.session_state.auto_low = gen_num_container(
        st,
        on_mobile,
        st.session_state.auto_low,
        "AUTO LOW",
        "AUTO_LOW➕",
        "AUTO_LOW➖",
        False,
    )

    auto_docking_input = [
        "NONE",
        "AUTO_DOCKED NOT ENGAGED_8",
        "AUTO_DOCKED AND ENGAGED_12",
    ]

    auto_docking = st.radio("AUTO_DOCKING", auto_docking_input, horizontal=True)
    auto_docked_input = int(auto_docking_input.index(auto_docking) == 1)
    auto_engaged_input = int(auto_docking_input.index(auto_docking) == 2)

    auto_mobility_input = int(st.checkbox("AUTO_MOBILITY_3"))

    st.markdown("""---""")

    st.markdown(
        f'<div style="text-align: center; font-size: 32px;">Teleop</div>',
        unsafe_allow_html=True,
    )
    st.title("")

    tele_col_1, tele_col_2 = st.columns(2)

    st.session_state.tele_cone_high = gen_num_container(
        tele_col_1,
        on_mobile,
        st.session_state.tele_cone_high,
        "TELE ⚠️ HIGH",
        "TELE⚠️HIGH➕",
        "TELE⚠️HIGH➖",
        False,
    )

    st.session_state.tele_cube_high = gen_num_container(
        tele_col_2,
        on_mobile,
        st.session_state.tele_cube_high,
        "TELE 🟪 HIGH",
        "TELE🟪HIGH➕",
        "TELE🟪HIGH➖",
        False,
    )

    st.session_state.tele_cone_mid = gen_num_container(
        tele_col_1,
        on_mobile,
        st.session_state.tele_cone_mid,
        "TELE ⚠️ MID",
        "TELE⚠️MID➕",
        "TELE⚠️MID➖",
        False,
    )

    st.session_state.tele_cube_mid = gen_num_container(
        tele_col_2,
        on_mobile,
        st.session_state.tele_cube_mid,
        "TELE 🟪 MID",
        "TELE🟪MID➕",
        "TELE🟪MID➖",
        False,
    )

    st.session_state.tele_low = gen_num_container(
        st,
        on_mobile,
        st.session_state.tele_low,
        "TELE LOW",
        "TELE_LOW➕",
        "TELE_LOW➖",
        False,
    )

    if not on_mobile:
        st.markdown("""---""")

    st.markdown(
        f'<div style="text-align: center; font-size: 32px;">Endgame</div>',
        unsafe_allow_html=True,
    )
    st.title("")

    end_docking_input = [
        "NONE",
        "END_PARKED_2",
        "END_DOCKED NOT ENGAGED_6",
        "END_DOCKED AND ENGAGED_10",
    ]

    end_docking = st.radio("END_DOCKING", end_docking_input, horizontal=True)
    end_parked_input = int(end_docking_input.index(end_docking) == 1)
    end_docked_input = int(end_docking_input.index(end_docking) == 2)
    end_engaged_input = int(end_docking_input.index(end_docking) == 3)

    st.markdown("""---""")

    st.markdown(
        f'<div style="text-align: center; font-size: 32px;">Information</div>',
        unsafe_allow_html=True,
    )
    st.title("")

    comments_input = st.multiselect("Comments:", st.session_state.comment_options)

    if on_mobile:
        st.write("""---""")

    info_col_1, info_col_2 = st.columns(2)

    st.session_state.info_penalties = gen_num_container(
        info_col_1,
        on_mobile,
        st.session_state.info_penalties,
        "INFO PENALTIES",
        "INFO_PENALTIES➕",
        "INFO_PENALTIES➖",
        True,
    )

    if on_mobile:
        st.write("""---""")

    info_brick_input = int(info_col_1.checkbox("INFO_BRICK_1"))

    brick_types = [
        "RSL Blinking",
        "RSL Solid",
        "RSL Off",
    ]

    if info_brick_input:
        brick_type = info_col_1.selectbox("Brick Type:", brick_types)
        brick_recovered = info_col_1.checkbox("Recovered", False)

    if not info_brick_input:
        brick_type = None
        brick_recovered = None

    if on_mobile:
        info_col_1.write("""---""")

    st.session_state.info_notes = gen_num_container(
        info_col_2,
        on_mobile,
        st.session_state.info_notes,
        "INFO NOTES",
        "INFO_NOTES➕",
        "INFO_NOTES➖",
        True,
    )

    comment_defense_input = int(info_col_2.checkbox("COMMENT_DEFENSE_1"))

    if not on_mobile:
        st.markdown("""---""")

    if st.button("Submit", use_container_width=True):
        comments_input = ", ".join(comments_input)
        prefill_url = f"https://docs.google.com/forms/d/e/1FAIpQLSeZ0snvF5GZixUzFuiDfGsifffaRJxwuQyszizAdKjR1apMLA/formResponse?usp=pp_url&entry.398002633={name_input}&entry.311722203={match_input}&entry.1823404922={match_type_input}&entry.432823991={color_input}&entry.1873738734={team_input}&entry.2015525146={st.session_state.info_penalties}&entry.250579147={info_brick_input}&entry.268050731={auto_mobility_input}&entry.193989110={st.session_state.auto_low}&entry.1576446792={st.session_state.auto_cone_mid}&entry.243783055={st.session_state.auto_cube_mid}&entry.1746336505={st.session_state.auto_cone_high}&entry.2024239037={st.session_state.auto_cube_high}&entry.2083103665={auto_docked_input}&entry.219114227={auto_engaged_input}&entry.1913479797={st.session_state.tele_low}&entry.539083044={st.session_state.tele_cone_mid}&entry.1061898011={st.session_state.tele_cube_mid}&entry.1767742649={st.session_state.tele_cone_high}&entry.2007109233={st.session_state.tele_cube_high}&entry.735364074={end_parked_input}&entry.1649767813={end_docked_input}&entry.173805537={end_engaged_input}&entry.619894282={comments_input}&entry.629905259={comment_defense_input}&submit=Submit"

        st.balloons()
        st.link_button(
            "Submit Form",
            prefill_url,
            type="primary",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
