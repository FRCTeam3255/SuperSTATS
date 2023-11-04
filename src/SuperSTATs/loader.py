import plotly.express as px
import streamlit as st
import pandas as pd
import tbapy

tba = tbapy.TBA(st.secrets["TBA_API"])


def init_page():
    if "init" not in st.session_state:
        st.session_state.init = True
        set_global_df()
        st.session_state.team_info_dict = download_team_info()
        st.session_state.unscouted_teams = []
        st.session_state.presets = {}
        st.session_state.signed_in = False
        st.session_state.admin_signed_in = False
        st.session_state.max_value = 0
        st.session_state.comment_options = [
            "Tipped",
            "Mechanism Damaged/Disabled",
            "Excessive Auto Penalties",
            "Pick Up ⚠️ Off Ground",
            "Pick Up 🟪 Off Ground",
            "Pick Up Tipped ⚠️",
            "Single Substation",
            "Double Substation",
        ]
        st.session_state.selected_filters = []
        st.session_state.max_frame_width = 0
        st.session_state.max_frame_length = 0


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
    tba_teams = tba.event_teams(st.secrets["DEFAULT_EVENT_KEY"])

    local_team_info_dict = {}

    for team in tba_teams:
        team = team["team_number"]
        local_team_info_dict[team] = get_team(team).get("nickname", "N/A")

    return local_team_info_dict


def get_tba_rankings():
    event_rankings = tba.event_rankings(st.secrets["DEFAULT_EVENT_KEY"])["rankings"]
    team_rankings = {}

    for team in event_rankings:
        team_rankings[team["team_key"].split("frc")[1]] = team["rank"]

    return team_rankings


def get_team_options():
    teams = {}
    teams_raw = st.session_state.team_info_dict.items()

    for team in teams_raw:
        teams[team[1]] = int(team[0])

    team_options = [
        f"{team_name} | {team_num}" for team_name, team_num in teams.items()
    ]

    return team_options


def get_unscouted_teams():
    df = download_sheets_raw(st.secrets["GID_SCOUTING"]).dropna(subset="Timestamp")

    unique_teams = st.session_state.team_info_dict
    scouted_teams = df["Team #"].unique()
    unscouted_teams = [team for team in unique_teams if team not in scouted_teams]
    return unscouted_teams


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


def set_global_df():
    chosen_event_key = st.secrets["DEFAULT_EVENT_KEY"]
    # chosen_event = st.sidebar.selectbox("Event:", event_keys.keys())
    # chosen_event_key = event_keys[chosen_event]

    # if "global_match_df" not in st.session_state:
    #     chosen_event_key = st.secrets["DEFAULT_EVENT_KEY"]

    event_matches = tba.event_matches(chosen_event_key)

    # Convert matches JSON to DataFrame
    df = pd.DataFrame(event_matches)

    # Flatten Dictionaries into colulns
    df = pd.concat([df, pd.json_normalize(df["alliances"])], axis=1).drop(
        columns="alliances"
    )
    # event_matches_df = pd.concat(
    #     [event_matches_df, pd.json_normalize(event_matches_df["score_breakdown"])],
    #     axis=1,
    # ).drop(columns="score_breakdown")

    # Replace match type with human readable name
    df["comp_level"] = df["comp_level"].replace(
        {"qm": "Quals", "sf": "Playoffs", "f": "Finals"}
    )

    # Remove 'frc' from team number and convert to int
    df["red.team_keys"] = df["red.team_keys"].apply(
        lambda teams: [int(x.replace("frc", "")) for x in teams]
    )
    df["blue.team_keys"] = df["blue.team_keys"].apply(
        lambda teams: [int(x.replace("frc", "")) for x in teams]
    )

    # Expand list to columns
    df = pd.concat(
        [
            df,
            pd.DataFrame(
                df["red.team_keys"].to_list(),
                columns=["Red 1", "Red 2", "Red 3"],
            ),
        ],
        axis=1,
    ).drop(columns="red.team_keys")
    df = pd.concat(
        [
            df,
            pd.DataFrame(
                df["blue.team_keys"].to_list(),
                columns=["Blue 1", "Blue 2", "Blue 3"],
            ),
        ],
        axis=1,
    ).drop(columns="blue.team_keys")

    # Set playoff match_numer to be set_number
    df.loc[df["comp_level"] == "Playoffs", "match_number"] = df.loc[
        df["comp_level"] == "Playoffs", "set_number"
    ]

    # Make human readable match number id
    df["Match"] = df["comp_level"] + " " + df["match_number"].astype(str)

    # Sort values
    df = df.sort_values(
        by=["comp_level", "match_number"], ascending=[False, True]
    ).reset_index(drop=True)

    # Subset
    df = df[
        [
            "Match",
            "Red 1",
            "Red 2",
            "Red 3",
            "Blue 1",
            "Blue 2",
            "Blue 3",
        ]
    ]

    if "global_match_df" not in st.session_state:
        st.session_state.global_match_df = df

    # if st.button(f"Assign Global Dataframe: {chosen_event}", use_container_width=True):
    #     st.session_state.global_match_df = df


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    color_int = int(hex_color, 16)
    red = (color_int >> 16) & 255
    green = (color_int >> 8) & 255
    blue = color_int & 255
    return red, green, blue


def get_rt(df, column, team_num):
    df = df.loc[(df["Team"] == team_num)]
    df = df.drop("COMMENT_GENERAL_1", axis=1)

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


def gen_radio_chart(radar_r, radar_t, max_range, team_color, team_alpha):
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
        fillcolor=f"rgba({team_color[0]}, {team_color[1]}, {team_color[2]}, {team_alpha})",
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
            "Team Color 1:", value="#2AD3FF", label_visibility="hidden"
        )
    )

    selected_team = select_2.selectbox("Select Second Team:", sorted(team_options))
    team_2_num = int(selected_team.split(" | ")[1])
    team_2_color = hex_to_rgb(
        color_2.color_picker(
            "Team Color 2:", value="#2AD3FF", label_visibility="hidden"
        )
    )

    chart_1, chart_2 = st.columns(2)

    team_1_rt = get_rt(df, chart_1, team_1_num)
    team_2_rt = get_rt(df, chart_2, team_2_num)

    team_1_r, team_1_t = team_1_rt
    team_2_r, team_2_t = team_2_rt

    st.session_state.max_value = sorted(team_1_r + team_2_r)[-1]

    chart_team_1 = gen_radio_chart(
        team_1_r, team_1_t, st.session_state.max_value, team_1_color, 0.25
    )
    chart_team_2 = gen_radio_chart(
        team_2_r, team_2_t, st.session_state.max_value, team_2_color, 0.25
    )

    return chart_team_1.add_trace(chart_team_2.data[0])
