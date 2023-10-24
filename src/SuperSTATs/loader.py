import requests, tbapy, json
import streamlit as st
import pandas as pd

tba = tbapy.TBA(st.secrets["TBA_API"])


def build_sheet_url(url):
    doc_id, sheet_id = url.split("/")[5:7]
    sheet_id = sheet_id.split("gid=")[1]
    return f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={sheet_id}"


def download_sheets_raw(gid):
    url = f"https://docs.google.com/spreadsheets/d/{st.secrets['GSHEET_DOC_ID']}/edit#gid={gid}"
    df = pd.read_csv(build_sheet_url(url))
    df.columns = (
        df.columns.str.lstrip()
        .str.replace("[", repl="", regex=False)
        .str.replace("]", repl="", regex=False)
    )
    return df


def get_team(team):
    return tba.team(f"frc{int(team)}", True)


@st.cache_data
def download_team_info():
    df = download_sheets_raw(st.secrets["GID_RAW"])
    local_team_info_dict = {}
    for team in df["Team"].unique():
        local_team_info_dict[team] = get_team(team).get("nickname", "N/A")
    return local_team_info_dict


def get_match_sections(df):
    filtered_columns = []
    for column in df.columns:
        if any(c.isdigit() for c in column.split("_")[-1]):
            filtered_columns.append(column)

    sections = []
    for column in filtered_columns:
        column = column.split("_")[0]
        sections.append(column)

    return sorted(list(set(sections)))


def alter_cols(match_num):
    return f"Quals {match_num}"


def set_global_df():
    try:
        with st.expander("View Keys"):
            # chosen_event = None
            chosen_event_key = st.secrets["DEFAULT_EVENT_KEY"]
            year = st.number_input("Year:", min_value=0, step=1, value=2023)

            # year = st.sidebar.number_input("Year:", min_value=0, step=1, value=2023)
            # events = tba.events(int(year))
            events = tba.events(year)
            event_keys = {}

            for event in events:
                name = event["name"]
                key = event["key"]
                event_keys[name] = key

            # chosen_event = st.sidebar.selectbox("Event:", event_keys.keys())
            # chosen_event_key = event_keys[chosen_event]

            # if "global_match_df" not in st.session_state:
            #     chosen_event_key = st.secrets["DEFAULT_EVENT_KEY"]

            event_matches = tba.event_matches(chosen_event_key)

            quals = {}
            for match in event_matches:
                if match["comp_level"] == "qm":
                    red_teams = match["alliances"]["red"]["team_keys"]
                    blue_teams = match["alliances"]["blue"]["team_keys"]

                    red_teams = [
                        team.replace("frc", "").replace("'", "") for team in red_teams
                    ]
                    blue_teams = [
                        team.replace("frc", "").replace("'", "") for team in blue_teams
                    ]

                    quals[match["match_number"]] = {
                        "Red 1": red_teams[0],
                        "Red 2": red_teams[1],
                        "Red 3": red_teams[2],
                        "Blue 1": blue_teams[0],
                        "Blue 2": blue_teams[1],
                        "Blue 3": blue_teams[2],
                    }

            df = pd.DataFrame(quals).T.reset_index()
            df.columns = [
                "Match",
                "Red 1",
                "Red 2",
                "Red 3",
                "Blue 1",
                "Blue 2",
                "Blue 3",
            ]
            df = df.sort_values(by="Match").reset_index(drop=True)
            df["Match"] = df["Match"].apply(alter_cols)

            if "global_match_df" not in st.session_state:
                st.session_state.global_match_df = df

            # if st.button(f"Assign Global Dataframe: {chosen_event}", use_container_width=True):
            #     st.session_state.global_match_df = df

            for name, key in event_keys.items():
                st.text(f"{name} : {key}")
    except:
        st.warning("Please Reload Page")


def fetch_github_data():
    github_url = st.secrets["PRESETS_RAW_URL"]
    response = requests.get(github_url)
    return json.loads(response.text)


def init_page():
    if "team_info_dict" not in st.session_state:
        st.session_state.team_info_dict = download_team_info()
    if "global_match_df" not in st.session_state:
        set_global_df()
    if "presets" not in st.session_state:
        st.session_state.presets = {}
