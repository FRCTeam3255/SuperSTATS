import requests, tbapy, json
import plotly.express as px
import streamlit as st
import pandas as pd

tba = tbapy.TBA(st.secrets["TBA_API"])


def init_page():
    if "team_info_dict" not in st.session_state:
        st.session_state.team_info_dict = download_team_info()
    if "global_match_df" not in st.session_state:
        set_global_df()
    if "presets" not in st.session_state:
        st.session_state.presets = {}
    if "max_value" not in st.session_state:
        st.session_state.max_value = 0


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


def get_team_options():
    teams = {}
    teams_raw = st.session_state.team_info_dict.items()

    for team in teams_raw:
        teams[team[1]] = int(team[0])

    team_options = [
        f"{team_name} | {team_num}" for team_name, team_num in teams.items()
    ]

    return team_options


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


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    color_int = int(hex_color, 16)
    red = (color_int >> 16) & 255
    green = (color_int >> 8) & 255
    blue = color_int & 255
    return red, green, blue


def get_rt(df, column, team_num, team_color):
    df = df.loc[(df["Team"] == team_num)]
    sections = get_match_sections(df)

    section_cols = [
        col
        for col in df.columns
        if any(col.startswith(section) for section in sections)
    ]
    df = df[section_cols].reset_index(drop=True)

    column_values = {}
    for column in df:
        column_value = int(column.split("_")[2])
        sum_value = int(df[column].sum()) * column_value
        column_values[column] = sum_value

    sum_values = ["AUTO", "TELE", "END"]

    radar_r = []
    radar_t = []

    for sum_for in sum_values:
        value_sum = sum(
            value for key, value in column_values.items() if key.startswith(sum_for)
        )
        radar_r.append(value_sum)
        radar_t.append(sum_for)

    return [radar_r, radar_t]


def gen_radio_chart(radar_r, radar_t, max_range, team_color):
    radar_df = pd.DataFrame(
        {
            "r": radar_r,
            "theta": radar_t,
        }
    )

    radar_chart = px.line_polar(radar_df, r="r", theta="theta", line_close=True)
    radar_chart.update_traces(fill="toself")

    radar_chart.update_layout(
        polar_bgcolor="#212121",
        paper_bgcolor="#141414",
        polar=dict(radialaxis=dict(visible=True, range=[0, max_range * 1.05])),
    )

    radar_chart.update_traces(
        fill="toself",
        fillcolor=f"rgba({team_color[0]}, {team_color[1]}, {team_color[2]}, 0.25)",
        line=dict(
            color="#000000",
            width=2,
        ),
    )

    return radar_chart


def gen_radial_charts(df, team_options):
    select_1, color_1, select_2, color_2 = st.columns(4)

    selected_team = select_1.selectbox("Select First Team:", sorted(team_options))
    team_1_num = int(selected_team.split(" | ")[1])
    team_1_color = hex_to_rgb(
        color_1.color_picker(
            "Team Color 1:", value="#910000", label_visibility="hidden"
        )
    )

    selected_team = select_2.selectbox("Select Second Team:", sorted(team_options))
    team_2_num = int(selected_team.split(" | ")[1])
    team_2_color = hex_to_rgb(
        color_2.color_picker(
            "Team Color 2:", value="#910000", label_visibility="hidden"
        )
    )

    chart_1, chart_2 = st.columns(2)

    team_1_rt = get_rt(df, chart_1, team_1_num, team_1_color)
    team_2_rt = get_rt(df, chart_2, team_2_num, team_2_color)

    team_1_r, team_1_t = team_1_rt
    team_2_r, team_2_t = team_2_rt

    st.session_state.max_value = sorted(team_1_r + team_2_r)[-1]

    chart_team1 = gen_radio_chart(
        team_1_r, team_1_t, st.session_state.max_value, team_1_color
    )
    chart_team2 = gen_radio_chart(
        team_2_r, team_2_t, st.session_state.max_value, team_2_color
    )

    return chart_team1.add_trace(chart_team2.data[0])
