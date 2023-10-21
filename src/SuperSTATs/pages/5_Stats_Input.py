import SuperSTATs.Main as stats
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


def main():
    stats.set_font()

    st.markdown(
        "<h1 style='text-align: center;'>✏️ Stats Input ✏️</h1>", unsafe_allow_html=True
    )
    st.title("")

    teams = {}
    teams_raw = st.session_state.team_info_dict.items()

    for team in teams_raw:
        teams[team[1]] = int(team[0])

    df = stats.download_sheets_raw(st.secrets["GID_MATCHES"])

    with st.form("Stats Input", clear_on_submit=True):
        selection_col_1, selection_col_2 = st.columns(2)

        name_input = selection_col_1.text_input("Your Name:", max_chars=2)
        match_choice = selection_col_2.selectbox("Match:", df["Match"])

        df_sort = df[df["Match"] == match_choice]
        df_sort = df_sort.set_index("Match").transpose()

        df_red = df_sort.filter(like="Red", axis=0)[match_choice].to_list()
        df_blue = df_sort.filter(like="Blue", axis=0)[match_choice].to_list()

        df_red = [int(value) for value in df_red]
        df_blue = [int(value) for value in df_blue]

        team_color = selection_col_1.radio(
            "Team Color:", ["Red", "Blue"], horizontal=True
        )

        if team_color == "Red":
            selected_team = selection_col_2.radio(
                "Team Choice:", df_red, horizontal=True
            )
            color_input = "R"

        if team_color == "Blue":
            selected_team = selection_col_2.radio(
                "Team Choice:", df_blue, horizontal=True
            )
            color_input = "B"

        match_split = match_choice.split(" ")
        match_type_input = match_split[0]
        if match_type_input == "Playoff":
            match_type_input = "Playoffs"
        match_input = match_split[1]

        team_input = selected_team

        st.markdown("""---""")

        auto_mobility_input = int(st.checkbox("AUTO_MOBILITY_3"))

        auto_col_1, auto_col_2 = st.columns(2)

        auto_cone_high_input = num_input(auto_col_1, "AUTO_'⚠️' HIGH_6", 0, 9, 0)
        auto_cube_high_input = num_input(auto_col_2, "AUTO_'🟪' HIGH_6", 0, 9, 0)
        auto_cone_mid_input = num_input(auto_col_1, "AUTO_'⚠️' MID_4", 0, 9, 0)
        auto_cube_mid_input = num_input(auto_col_2, "AUTO_'🟪' MID_4", 0, 9, 0)

        auto_low_input = st.number_input("AUTO_LOW_3", step=1, min_value=0, max_value=6)

        auto_docking_input = [
            "NONE",
            "AUTO_DOCKED NOT ENGAGED_8",
            "AUTO_DOCKED AND ENGAGED_12",
        ]

        auto_docking = st.radio("AUTO_DOCKING", auto_docking_input, horizontal=True)
        auto_docked_input = int(auto_docking_input.index(auto_docking) == 1)
        auto_engaged_input = int(auto_docking_input.index(auto_docking) == 2)

        st.markdown("""---""")

        tele_col_1, tele_col_2 = st.columns(2)

        tele_cone_high_input = num_input(tele_col_1, "TELE_'⚠️' HIGH_5", 0, 9, 0)
        tele_cube_high_input = num_input(tele_col_2, "TELE_'🟪' HIGH_5", 0, 9, 0)
        tele_cone_mid_input = num_input(tele_col_1, "TELE_'⚠️' MID_3", 0, 9, 0)
        tele_cube_mid_input = num_input(tele_col_2, "TELE_'🟪' MID_3", 0, 9, 0)
        tele_low_input = num_input(st, "TELE_LOW_2", 0, 9, 0)

        st.markdown("""---""")

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

        comments_input = (st.text_input("General Comments:")).replace(" ", "+")

        info_col_1, info_col_2 = st.columns(2)

        info_penalty_input = num_input(info_col_1, "INFO_PENALTY_1", 0, 2, 0) * -1
        info_brick_input = int(info_col_1.checkbox("INFO_BRICK_1")) * -1
        comment_notes_input = num_input(info_col_2, "COMMENT_NOTES_1", -1, 1, 0)
        comment_defense_input = int(info_col_2.checkbox("COMMENT_DEFENSE_1"))

        st.markdown("""---""")

        submission = st.form_submit_button("Submit", use_container_width=True)

    if submission:
        prefill_url = f"https://docs.google.com/forms/d/e/1FAIpQLSeZ0snvF5GZixUzFuiDfGsifffaRJxwuQyszizAdKjR1apMLA/viewform?usp=pp_url&entry.398002633={name_input}&entry.311722203={match_input}&entry.1823404922={match_type_input}&entry.432823991={color_input}&entry.1873738734={team_input}&entry.2015525146={info_penalty_input}&entry.250579147=-{info_brick_input}&entry.268050731={auto_mobility_input}&entry.542386964={auto_low_input}&entry.530845045={auto_cone_mid_input}&entry.2086503014={auto_cube_mid_input}&entry.1207232700={auto_cone_high_input}&entry.1008310587={auto_cube_high_input}&entry.2083103665={auto_docked_input}&entry.829803960={auto_engaged_input}&entry.1796811601={tele_low_input}&entry.837438137={tele_cone_mid_input}&entry.263379052={tele_cube_mid_input}&entry.597282987={tele_cone_high_input}&entry.2060882466={tele_cube_high_input}&entry.1349917441={end_parked_input}&entry.167115309={end_docked_input}&entry.1695411443={end_engaged_input}&entry.619894282={comments_input}&entry.107629913={comment_notes_input}&entry.629905259={comment_defense_input}"

        st.balloons()
        st.link_button("Link", prefill_url, type="primary", use_container_width=True)

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
