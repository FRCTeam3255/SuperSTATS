import SuperSTATs.loader as load
import streamlit as st

st.set_page_config(
    page_title="[SCOUT] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
    layout="wide",
)


def num_input(column, label, min_value, max_value, default_index):
    return column.number_input(
        label, step=1, min_value=min_value, max_value=max_value, value=default_index
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

    # if st.button("Clear Form", use_container_width=True, type="primary"):
    #     st.session_state.auto_cone_high = 0

    on_mobile = st.checkbox("Mobile", False)

    teams = {}
    teams_raw = st.session_state.team_info_dict.items()
    for team in teams_raw:
        teams[team[1]] = int(team[0])

    df = st.session_state.global_match_df

    selection_col_1, selection_col_2 = st.columns(2)

    name_input = selection_col_1.text_input("Your Name:", max_chars=2)
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

    # [TODO]

    st.markdown(
        f'<div style="text-align: center; font-size: 32px;">Information</div>',
        unsafe_allow_html=True,
    )
    st.title("")

    comment_options = [
        "Tipped",
        "Mechanism Damaged/Disabled",
        "Excessive Auto Penalties",
        "Pick Up ⚠️ Off Ground",
        "Pick Up 🟪 Off Ground",
        "Pick Up Tipped ⚠️",
        "[SUBSTATION] Single",
        "[SUBSTATION] Double",
    ]

    comments_input = st.multiselect("Comments:", comment_options)

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

    info_brick_input = int(info_col_1.checkbox("INFO_BRICK_1")) * -1

    brick_types = [
        "RSL Blinking",
        "RSL Solid",
        "RSL Off",
        "Recovered",
    ]

    if info_brick_input:
        info_col_1.selectbox("Brick Type:", brick_types)

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
        prefill_url = f"https://docs.google.com/forms/d/e/1FAIpQLSeZ0snvF5GZixUzFuiDfGsifffaRJxwuQyszizAdKjR1apMLA/viewform?usp=pp_url&entry.398002633={name_input}&entry.311722203={match_input}&entry.1823404922={match_type_input}&entry.432823991={color_input}&entry.1873738734={team_input}&entry.2015525146={info_penalty_input}&entry.250579147=-{info_brick_input}&entry.268050731={auto_mobility_input}&entry.542386964={auto_low_input}&entry.530845045={auto_cone_mid_input}&entry.2086503014={auto_cube_mid_input}&entry.1207232700={auto_cone_high_input}&entry.1008310587={auto_cube_high_input}&entry.2083103665={auto_docked_input}&entry.829803960={auto_engaged_input}&entry.1796811601={tele_low_input}&entry.837438137={tele_cone_mid_input}&entry.263379052={tele_cube_mid_input}&entry.597282987={tele_cone_high_input}&entry.2060882466={tele_cube_high_input}&entry.1349917441={end_parked_input}&entry.167115309={end_docked_input}&entry.1695411443={end_engaged_input}&entry.619894282={comments_input}&entry.107629913={comment_notes_input}&entry.629905259={comment_defense_input}"

        st.balloons()
        st.link_button(
            "Go To Prefilled Form",
            prefill_url,
            type="primary",
            use_container_width=True,
        )

    # prefill_url = f"https://docs.google.com/forms/d/e/1FAIpQLSeZ0snvF5GZixUzFuiDfGsifffaRJxwuQyszizAdKjR1apMLA/viewform?usp=pp_url&entry.398002633=0&entry.311722203=0&entry.1823404922=Prac&entry.432823991=R&entry.1873738734=0&entry.2015525146=-1&entry.250579147=-1&entry.268050731=1&entry.542386964=1&entry.530845045=1&entry.2086503014=1&entry.1207232700=1&entry.1008310587=1&entry.2083103665=1&entry.1796811601=1&entry.837438137=1&entry.263379052=1&entry.597282987=1&entry.2060882466=1&entry.1349917441=1&entry.619894282=NONE&entry.107629913=-1&entry.629905259=1"

    # entry_ids = prefill_url.replace("entry.", "")
    # entry_ids = entry_ids.split("&")

    # for i, entry in enumerate(entry_ids):
    #     id = entry.split("=")
    #     entry_ids[i] = f"{id[0]} : {id[1]}"

    # entry_ids = entry_ids[1:]
    # for entry_id in entry_ids:
    #     st.text(entry_id)


if __name__ == "__main__":
    main()
