import io
import qrcode
import requests
import SuperSTATs.load as load
import streamlit as st
import random
import traceback
import SuperSTATs.screen_elements as ui

def display_random_susan():
    if random.random() < 0.1:  # 10% chance
        st.markdown(
            "<div style='text-align: center; font-size: small; color: #808080;'>Susan was here😸</div>",
            unsafe_allow_html=True,
        )

def get_match_scouts(team):
    """
    Get the match scouts for a given team.

    Parameters:
    - team (list): A list of scouts in the team.

    Returns:
    - scouts (dict): A dictionary mapping match names to a list of scouts for each match.
    """
    rotation = int(st.session_state.configs["Scouting Rotations"][0])
    match_list = st.session_state.matches["Match"].to_list()
    scouts = {}

    processed = 0
    count = 0
    i = 0

    while processed < len(match_list):
        scout_1 = team[count]
        scout_2 = team[count - 1]
        scout_3 = team[count - 2]

        if i % rotation == 0:
            count += 1

        if count == len(team):
            count = 0

        for match_type in ["Quals", "Playoffs", "Finals"]:
            for j in range(rotation):
                match_name = f"{match_type} {(i + 1) + j}"

                if match_name in match_list:
                    scouts[match_name] = [scout_1, scout_2, scout_3]
                    processed += 1

        i += rotation

    return scouts

def update_page_button():
    st.divider()

    if st.button(
        "Update Page",
        type="primary",
        use_container_width=True,
        key=f"update_page",
    ):
        data_initializer = load.DataInitializer()
        st.session_state.df = data_initializer.organize_df(
            data_initializer.download_sheets_raw(gid=st.secrets["GID_RAW"]).dropna(subset=["Timestamp"])
        )

        st.session_state.unplayed_matches = data_initializer.get_unplayed(
            df=st.session_state.df, matches=st.session_state.matches
        )

    st.divider()

def handle_name_selection(top_columns, bottom_columns, scouters):
    """
    Handles the selection of the scout's name and substitute.

    Parameters:
    - top_columns (list): List of Streamlit columns for the top row.
    - bot_columns (list): List of Streamlit columns for the bottom row.
    - scouters (list): List of available scouters.

    Returns:
    - input_name (str): The selected scout's name.
    - input_sub (str or None): The selected substitute's name, if any.
    """
    name_selection = top_columns[0].empty()
    input_name = name_selection.selectbox("Name:", scouters + ["Sub"])

    if input_name == "Sub":
        input_name = name_selection.selectbox("Original:", scouters)
        input_sub = bottom_columns[0].selectbox("Substitute:", st.session_state.scouts)
    else:
        input_sub = None

    return input_name, input_sub

def assign_scouts(scouts, matches, df_teams, all_match_scouts, scouters):
    for match in st.session_state.matches["Match"]:
        teams = matches[matches["Match"] == match].set_index("Match").transpose()
        if isinstance(df_teams, dict):
            df_teams.update(teams.to_dict())
        else:
            df_teams = teams.to_dict()

        red_scouts = get_match_scouts(scouters[::2])[match]
        blue_scouts = get_match_scouts(scouters[1::2])[match]
        match_scouts = red_scouts + blue_scouts
        all_match_scouts[match] = match_scouts

    return all_match_scouts

def handle_scoutter_match_initialisation(
    all_match_scouts,
    input_name,
    scout_matches,
    unplayed_matches
):
    for match in all_match_scouts:
        if input_name in all_match_scouts[match]:
            scout_matches.append(match)

    unplayed_scout_matches = []

    for match in scout_matches:
        if match in unplayed_matches:
            unplayed_scout_matches.append(match)

    match_index = 0

    if st.session_state.console["practice_mode"]:
        unplayed_scout_matches = [f"Prac {i + 1}" for i in range(50)]

        df = load.download_sheets_raw(st.secrets["GID_RAW"]).dropna(
            subset=["Timestamp"]
        )
        df = df.sort_values(["Match", "Timestamp"], ascending=[True, True])
        df = df.drop_duplicates(subset=["Team", "Match Type", "Match"])
        df = df[df["Event Key"] == st.secrets["DEFAULT_EVENT_KEY"]]

        df["Completed"] = df["Match Type"] + " " + df["Match"].astype(int).astype(str)

        try:
            prac_matches = df[df["Match Type"] == "Prac"]
            match_index = (
                unplayed_scout_matches.index(prac_matches["Completed"].iloc[-1]) + 1
            )
        except:
            match_index = 0

    return unplayed_scout_matches, match_index
    

def main():
    load.initialise_app()

    ui.display_header("✏️ Stats Input ✏️")

    display_random_susan()

    update_page_button()

    form_ = st.session_state.forms["STATS_FORM"]
    set_entries = form_["set"]
    gen_entries = form_["gen"]

    unplayed_matches = st.session_state.unplayed_matches
    scouters = st.session_state.assigned
    matches = st.session_state.matches

    df_teams = {}
    all_match_scouts = {}
    scout_matches = []

    top_columns = st.columns(2)
    bot_columns = st.columns(2)
    match_selection = top_columns[1].empty()

    input_name, input_sub = handle_name_selection(top_columns, bot_columns, scouters)
    all_match_scouts = assign_scouts(scouters, matches, df_teams, all_match_scouts, scouters)

    unplayed_scout_matches, match_index = handle_scoutter_match_initialisation(
        all_match_scouts,
        input_name,
        scout_matches,
        unplayed_matches
    )

    match_index = 0

    input_match = match_selection.selectbox(
        "Match:",
        unplayed_scout_matches
        + (["Other"] if not st.session_state.console["practice_mode"] else []),
        index=match_index,
    )

    if input_match == "Other":
        input_match = match_selection.selectbox("Match [OTHER]:", matches)
        input_type = input_match.split()[0]

        df_teams = (
            matches[matches["Match"] == input_match].set_index("Match").transpose()
        )

        match_scouts = [input_name for i in range(6)]
        teams = list(df_teams.to_dict()[input_match].values())

        input_team = bot_columns[1].selectbox("Team:", teams)
        input_color = name_check(input_team, teams)
    else:
        input_type = input_match.split()[0]
        df_teams = (
            matches[matches["Match"] == input_match].set_index("Match").transpose()
        )

        try:
            match_scouts = all_match_scouts[input_match]
            input_color = name_check(input_name, match_scouts)
            teams = df_teams.filter(like=input_color, axis=0)[input_match].to_list()
            match_scouts = (
                match_scouts[0:3] if input_color == "R" else match_scouts[3:6]
            )
            input_team = teams[match_scouts.index(input_name)]

        except:
            match_scouts = [input_name for i in range(6)]

            prac_columns = st.columns(2)

            all_teams = [
                f"{team_num} | {team_name}"
                for team_num, team_name in st.session_state.team_info.items()
            ]

            input_team = int(
                prac_columns[0].selectbox("Team:", all_teams).split(" | ")[0]
            )

            input_color = prac_columns[1].radio("Color:", ["R", "B"], horizontal=True)

    if st.session_state.console["practice_mode"]:
        st.error("⚠️ Practice mode enabled")
    else:
        with st.expander("Master Scout List"):
            st.divider()

            match_search = st.text_input("Match:", f"{input_match} ").lower()

            for match in all_match_scouts:
                if match_search in f"{match.lower()} ":
                    scouts = all_match_scouts[match]

                    df_teams = (
                        matches[matches["Match"] == match]
                        .set_index("Match")
                        .transpose()
                    )
                    teams = list(df_teams.to_dict()[match].values())

                    st.divider()

                    st.markdown(
                        f"<span style='font-size: 1.5em;'><b>{match}</b></span>",
                        unsafe_allow_html=True,
                    )

                    red_scout_columns = st.columns(3)
                    blue_scout_columns = st.columns(3)

                    for i, (scout, team) in enumerate(zip(scouts, teams)):
                        color = "#f8312f" if i < 3 else "#0074ba"
                        if i < 3:
                            red_scout_columns[i].markdown(
                                f"<span style='color:{color}'>{scout}</span> - {team}",
                                unsafe_allow_html=True,
                            )
                        else:
                            blue_scout_columns[i - 3].markdown(
                                f"<span style='color:{color}'>{scout}</span> - {team}",
                                unsafe_allow_html=True,
                            )

        if not st.session_state.console["practice_mode"]:
            try:
                event_url = f"https://www.thebluealliance.com/event/{st.secrets['DEFAULT_EVENT_KEY']}"

                response = requests.get(event_url)
                soup = BeautifulSoup(response.content, "html.parser")
                output = str(soup)

                match_data = st.session_state.match_data
                match_data = match_data[match_data["Match Name"] == input_match]
                match_key = match_data["key"].to_list()[0]

                index = output.find("Scheduled at ", output.find(match_key))
                if index != -1:
                    closing_tag_index = output.find(" UTC", index)
                    next_instance = output[
                        index + len("Scheduled at ") + 4 : closing_tag_index
                    ]

                match_time = datetime.datetime.strptime(
                    next_instance, "%I:%M%p"
                ) - datetime.timedelta(
                    hours=int(st.session_state.configs["UTC Offset"][0])
                )

                next_match_index = unplayed_matches.index(unplayed_scout_matches[0])

                st.markdown(
                    f"<div style='text-align: center'>Scheduled {'NOW' if next_match_index == 0 else f'in {next_match_index} matches'}...<br><i>{unplayed_scout_matches[0]} at {match_time.strftime('%I:%M %p')}</i></div>",
                    unsafe_allow_html=True,
                )
            except:
                st.markdown(
                    f"<div style='text-align: center'>Error fetching match time...</div>",
                    unsafe_allow_html=True,
                )

    input_match = input_match.split()[1]

    color_icon = "🔴" if input_color == "R" else "🔵"
    input_name = (
        f"{input_sub} [⇄] {input_name}"
        if input_sub and input_sub != input_name
        else input_name
    )

    input_key = st.secrets["DEFAULT_EVENT_KEY"]

    st.divider()

    try:
        print("Debug: Starting to display team and color icon.")
        st.markdown(
            f'<div style="text-align: center; font-size: 2.5em;">{color_icon} {input_team} | {st.session_state.team_info[input_team]} {color_icon}</div>',
            unsafe_allow_html=True,
        )

        st.divider()

        print("Debug: Loading robot photo dropdown.")
        ui.robot_photo_dropdown(input_team)

        set_inputs = [
            input_name,
            input_match,
            input_type,
            input_color,
            input_team,
            input_key,
        ]

        set_combined = {}

        def combine_set(entry_name, variable):
            print(f"Debug: Combining set for entry {entry_name} with variable {variable}.")
            entry_number = set_entries[entry_name]
            set_combined[entry_name] = [int(entry_number), variable]

        for i in range(len(set_entries)):
            combine_set(list(set_entries.keys())[i], set_inputs[i])

        sorted_entries = {"AUTO": [], "TELE": [], "END": [], "INFO": [], "COMMENT": []}

        for entry in gen_entries.keys():
            for prefix, entries in sorted_entries.items():
                if entry.startswith(prefix):
                    entries.append(entry)
                    break

        entry_responses = {}

        def phase_header(phase):
            print(f"Debug: Displaying header for phase {phase}.")
            st.markdown(
                f'<div style="text-align: center; font-size: 32px;">{phase}</div>',
                unsafe_allow_html=True,
            )
            st.title("")

        def gen_phase_input(entries):
            print(f"Debug: Generating input fields for phase {entries}.")
            for entry in sorted_entries[entries]:
                entry_parts = entry.split("_")
                entry_name = entry_parts[1].title().replace("Rsl", "RSL")

                feature_list = st.session_state.configs["Features"]

                if entry_parts[2] == "INT":
                    entry_responses[entry] = st.number_input(
                        (f"{entry_name}:"), min_value=0, step=1, key=entry
                    )
                elif entry_parts[2] == "STR":
                    selected_options = st.multiselect(
                        (f"{entry_name}:"), feature_list, key=entry
                    )
                    entry_responses[entry] = ", ".join(selected_options)
                elif entry_parts[2] == "BOOL":
                    entry_responses[entry] = int(st.toggle(entry_name, key=entry))

        submitted = False

        with st.form("Stats Input", clear_on_submit=True, border=False):
            with st.expander("Autonomous", True):
                phase_header("Autonomous")
                gen_phase_input("AUTO")

            with st.expander("Teleop", True):
                phase_header("Teleop")
                gen_phase_input("TELE")

            with st.expander("Endgame", True):
                phase_header("Endgame")
                gen_phase_input("END")

            with st.expander("Info & Comments", True):
                phase_header("Info & Comments")
                gen_phase_input("INFO")
                gen_phase_input("COMMENT")

            st.divider()

            gen_combined = {}

            for key in gen_entries.keys():
                if key in entry_responses:
                    gen_combined[key] = [gen_entries[key], entry_responses[key]]

            entries_combined = set_combined.copy()
            entries_combined.update(gen_combined)

            entry_url = ""
            for result in entries_combined.values():
                entry_url += f"&entry.{result[0]}={result[1]}"

            prefill_url = f"{st.secrets['STATS_FORM'].split('/viewform')[0]}/formResponse?usp=pp_url{entry_url}&submit=Submit"

            print(f"Debug: Prefill URL generated: {prefill_url}")

            if input_name != "":
                submitted = st.form_submit_button(
                    "Submit", type="primary", use_container_width=True
                )
            else:
                st.form_submit_button(
                    "Submit", type="primary", use_container_width=True, disabled=True
                )
                st.warning("⚠️ Required Input Missing")

        def gen_qr(contents):
            print(f"Debug: Generating QR code for contents: {contents}")
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
            )

            qr.add_data(contents)
            qr.make(fit=True)

            img = qr.make_image(fill_color="#ffffff", back_color="#141414")

            byte_stream = io.BytesIO()

            img.save(byte_stream, format="JPEG")
            bytes_image = byte_stream.getvalue()

            return bytes_image

        if submitted:
            print("Debug: Form submitted.")
            req = requests.get(prefill_url)

            if req.status_code == 200:
                print("Debug: Submission successful.")
                st.balloons()
                st.toast("Submission successful!", icon="✅")
                if st.session_state.console["force_qr"]:
                    with st.expander("QR Code", False):
                        st.image(gen_qr(prefill_url), use_container_width=True)
            else:
                print("Debug: Submission unsuccessful.")
                st.toast("Submission unsuccessful! Use QR code...", icon="⚠️")
                st.image(gen_qr(prefill_url), use_container_width=True)
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Debug: Exception occurred - {e}\nTraceback:\n{error_trace}")
        st.error(f"⚠️ An error occurred: {e}\n\nLocation:\n{error_trace}")

if __name__ == "__main__":
    main()
