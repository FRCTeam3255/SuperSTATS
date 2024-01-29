import SuperSTATs.load as load
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="[SCOUT] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
    layout="wide",
)


def get_matches(team):
    match_list = st.session_state.matches["Match"].to_list()
    scouts = {}
    rotation = 3

    processed = 0
    count = 0
    i = 0

    while processed < len(match_list):
        p1 = team[count]
        p2 = team[count - 1]
        p3 = team[count - 2]

        if i % rotation == 0:
            count += 1

        if count == len(team):
            count = 0

        for match_type in ["Quals", "Playoffs", "Finals"]:
            for j in range(rotation):
                match_name = f"{match_type} {(i + 1) + j}"
                if match_name in match_list:
                    scouts[match_name] = [p1, p2, p3]
                    processed += 1

        i += rotation

    return scouts


def name_check(value, lst):
    mid_index = len(lst) // 2
    if value in lst[:mid_index]:
        return "R"
    elif value in lst[mid_index:]:
        return "B"
    else:
        return "Other"


def main():
    load.app_init()

    import SuperSTATs.styles as style

    st.markdown(style.shimmer("#ffc1ad"), unsafe_allow_html=True)
    st.markdown("<div class='shimmer'>✏️ Stats Input ✏️</div>", unsafe_allow_html=True)

    st.title("")

    st.button("Update Page", type="primary", use_container_width=True)
    st.markdown("""---""")

    url = st.secrets["FORM_URL"]

    response = requests.get(url)
    html = BeautifulSoup(response.content, "html.parser")

    found = "FB_PUBLIC_LOAD_DATA_ ="

    split_html = str(html).split(found)[1]
    split_html = str(split_html).split('",null,0,[[')

    entries_dict = {"Name": split_html[0].split('"Name",null,1,[[')[1].split(",")[0]}

    for i in range(len(split_html) - 1):
        entries_dict[split_html[i].split('"')[-1]] = split_html[i + 1].split(",")[0]

    gen_entries = {
        name: id
        for name, id in entries_dict.items()
        if any(name.startswith(phase) for phase in st.session_state.phases)
    }

    set_entries = {
        name: id for name, id in entries_dict.items() if name not in gen_entries
    }

    top_columns = st.columns(2)

    df = st.session_state.df
    matches = st.session_state.matches

    df["Completed"] = df["Match Type"] + " " + df["Match"].astype(str)
    df_counts = df["Completed"].value_counts()

    df["Completed"] = df["Completed"].apply(lambda x: x if df_counts[x] >= 3 else None)

    df_unique = df["Completed"].dropna().unique()
    matches_unique = matches["Match"].unique()

    unplayed_matches = pd.concat(
        [pd.DataFrame(df_unique), pd.DataFrame(matches_unique)]
    ).drop_duplicates(keep=False)

    unplayed_matches = [
        match for sublist in unplayed_matches.values.tolist() for match in sublist
    ]

    match_selection = top_columns[1].empty()
    input_match = match_selection.selectbox("Match:", unplayed_matches + ["Other"])
    if input_match == "Other":
        input_match = match_selection.selectbox(
            "Match [OTHER]:", st.session_state.matches
        )

    scouter_list = st.session_state.assigned

    red_scouts = get_matches(scouter_list[::2])[input_match]
    blue_scouts = get_matches(scouter_list[1::2])[input_match]
    match_scouts = red_scouts + blue_scouts

    name_selection = top_columns[0].empty()
    input_name = name_selection.selectbox("Name:", match_scouts + ["Sub"]).upper()

    if input_name == "SUB":
        bot_columns = st.columns(2)
        input_name = name_selection.selectbox("Original:", match_scouts).upper()
        input_sub = bot_columns[0].text_input("Sub:", max_chars=2).upper()
    else:
        input_sub = None

    input_color = name_check(input_name, match_scouts)
    input_type = input_match.split()[0]

    df_teams = matches[matches["Match"] == input_match].set_index("Match").transpose()
    teams = df_teams.filter(like=input_color, axis=0)[input_match].to_list()
    input_match = input_match.split()[1]

    name_index = (
        red_scouts.index(input_name)
        if input_color == "R"
        else blue_scouts.index(input_name)
    )

    input_team = teams[name_index]
    color_icon = "🔴" if input_color == "R" else "🔵"
    input_name = f"{input_sub} [⇄]" if input_sub else input_name

    st.markdown("""---""")

    st.markdown(
        f'<div style="text-align: center; font-size: 2.5em;">{color_icon} {input_team} | {st.session_state.team_info[input_team]} {color_icon}</div>',
        unsafe_allow_html=True,
    )

    set_inputs = [input_name, input_match, input_type, input_color, input_team]
    set_combined = {}

    def combine_set(entry_name, variable):
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
        st.markdown("""---""")
        st.markdown(
            f'<div style="text-align: center; font-size: 32px;">{phase}</div>',
            unsafe_allow_html=True,
        )
        st.title("")

    def gen_phase_input(entries):
        for entry in sorted_entries[entries]:
            entry_parts = entry.split("_")
            entry_name = entry_parts[1].title()

            replacements = {
                "⚠️": "Cone",
                "🟪": "Cube",
            }

            for key, value in replacements.items():
                entry_name = entry_name.replace(key, value)

            if entry_parts[2] == "INT":
                entry_responses[entry] = st.number_input(
                    (entry_name + ":"), min_value=0, step=1, key=entry
                )

            elif entry_parts[2] == "STR":
                selected_options = st.multiselect(
                    (entry_name + ":"), ["K", "A", "N", "E"], key=entry
                )
                entry_responses[entry] = ", ".join(selected_options)

            elif entry_parts[2] == "BOOL":
                entry_responses[entry] = int(st.toggle(entry_name, key=entry))

    submitted = False

    with st.form("Stats Input", clear_on_submit=False, border=False):
        phase_header("Autonomous")
        gen_phase_input("AUTO")

        phase_header("Teleop")
        gen_phase_input("TELE")

        phase_header("Endgame")
        gen_phase_input("END")

        phase_header("Info & Comments")
        gen_phase_input("INFO")
        gen_phase_input("COMMENT")

        st.markdown("""---""")

        gen_combined = {}

        for key in gen_entries.keys():
            if key in entry_responses:
                gen_combined[key] = [gen_entries[key], entry_responses[key]]

        entries_combined = set_combined.copy()
        entries_combined.update(gen_combined)

        entry_url = ""
        for entry, result in entries_combined.items():
            entry_url += f"&entry.{result[0]}={result[1]}"

        prefill_url = f"{url.split('/viewform')[0]}/formResponse?usp=pp_url{entry_url}&submit=Submit"

        if input_name != "":
            submitted = st.form_submit_button(
                "Submit", type="primary", use_container_width=True
            )
        else:
            st.form_submit_button(
                "Submit", type="primary", use_container_width=True, disabled=True
            )
            st.warning("Required Input Missing")

    if submitted:
        requests.get(prefill_url)
        st.balloons()
        st.success("Submission successful! Please refresh the page...")
        load.play_audio("yippee.mp3", 4)


if __name__ == "__main__":
    main()
