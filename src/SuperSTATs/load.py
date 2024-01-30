import streamlit as st
import pandas as pd
import requests
import random
import pickle
import base64
import tbapy
import json
import time


def download_sheets_raw(gid):
    url = f"https://docs.google.com/spreadsheets/d/{st.secrets['GSHEET_DOC_ID']}/edit#gid={gid}"
    doc_id, sheet_id = url.split("/")[5:7]
    sheet_id = sheet_id.split("gid=")[1]
    sheet_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={sheet_id}"
    df = pd.read_csv(sheet_url)
    df.columns = (
        df.columns.str.lstrip()
        .str.replace("[", repl="", regex=False)
        .str.replace("]", repl="", regex=False)
    )
    return df


tba = tbapy.TBA(st.secrets["TBA_API"])
df = download_sheets_raw(st.secrets["GID_RAW"])


def get_scouters():
    try:
        with open("src\\pickles\\scouts.pickle", "rb") as f:
            scouts = pickle.load(f)

        st.session_state.scouts = scouts[0]
        st.session_state.assigned = scouts[1]

    except:
        scouts_df = download_sheets_raw(st.secrets["GID_SCOUTS"]).sort_values(by="Name")
        st.session_state.scouts = scouts_df["Name"].tolist()
        st.session_state.assigned = scouts_df.loc[
            scouts_df["Assigned"] == "x", "Name"
        ].tolist()


def get_phases(df):
    filtered_columns = []
    for column in df.columns:
        if any(c.isdigit() for c in column.split("_")[-1]):
            filtered_columns.append(column)

    phases = []
    for column in filtered_columns:
        column = column.split("_")[0]
        phases.append(column)

    return sorted(list(set(phases)))


def point_values():
    points = {
        f"{value[0]}_{value[1]}_{value[2]}": int(value[3])
        for value in df.columns.str.split("_")
        if len(value) > 1
    }

    for col, point in points.items():
        df[f"{col}_{point}"] *= point

    return points


@st.cache_data(show_spinner=False, persist=True)
def get_team_info():
    tba_teams = tba.event_teams(st.secrets["DEFAULT_EVENT_KEY"])
    team_info = {
        team["team_number"]: tba.team(team["team_number"]).get(
            "nickname", "Unknown Team"
        )
        for team in tba_teams
    }
    return team_info


@st.cache_data(show_spinner=False)
def get_team_colors():
    team_info = st.session_state.team_info
    team_colors = {}

    team_url = ""
    for team in team_info:
        team_url += f"team={team}&"

    api_url = f"https://frc-colors.com/api/v1/team/3255"

    try:
        requests.get("https://frc-colors.com/api/v1/team/3255", timeout=5)

        response = requests.get(api_url)
        response.raise_for_status()
        raw_data = response.json()

        for team in raw_data["teams"].values():
            if team["colors"] is not None:
                primary_color = team["colors"]["primaryHex"]
                secondary_color = team["colors"]["secondaryHex"]
                team_colors[team["teamNumber"]] = [primary_color, secondary_color]
            else:
                team_colors[team["teamNumber"]] = ["003255", "003255"]
    except:
        for team in team_info:
            team_colors[team] = ["003255", "003255"]

    return team_colors


def check_team_colors():
    stuff = st.session_state.team_colors
    values = list(stuff.values())
    if len(set(map(str, values))) == 1:
        get_team_colors.clear()


def get_match_data():
    try:
        df = pd.DataFrame(tba.event_matches(st.secrets["DEFAULT_EVENT_KEY"]))
        df = pd.concat([df, pd.json_normalize(df["alliances"])], axis=1).drop(
            columns="alliances"
        )

        df["comp_level"] = df["comp_level"].replace(
            {"qm": "Quals", "sf": "Playoffs", "f": "Finals"}
        )

        for color in ["red", "blue"]:
            df[f"{color}.team_keys"] = df[f"{color}.team_keys"].apply(
                lambda teams: [int(x.replace("frc", "")) for x in teams]
            )

        def set_match_name(row):
            if row["comp_level"] == "Playoffs":
                return row["comp_level"] + " " + str(row["set_number"])
            else:
                return row["comp_level"] + " " + str(row["match_number"])

        df["Match Name"] = df.apply(set_match_name, axis=1)

        return df
    except:
        st.error(f"ERROR: Nonexistent Match Data...")
        st.stop()


def get_matches():
    df = st.session_state.match_data

    frames = []
    for color in ["red", "blue"]:
        frame = pd.DataFrame(
            df[f"{color}.team_keys"].to_list(),
            columns=[
                f"{color.capitalize()} 1",
                f"{color.capitalize()} 2",
                f"{color.capitalize()} 3",
            ],
        )
        df.drop(columns=f"{color}.team_keys", inplace=True)
        frames.append(frame)

    df = pd.concat([df] + frames, axis=1)

    df.loc[df["comp_level"] == "Playoffs", "match_number"] = df.loc[
        df["comp_level"] == "Playoffs", "set_number"
    ]

    df["Match"] = df["comp_level"] + " " + df["match_number"].astype(str)

    df = df.sort_values(
        by=["comp_level", "match_number"], ascending=[False, True]
    ).reset_index(drop=True)

    df = df[["Match", "Red 1", "Red 2", "Red 3", "Blue 1", "Blue 2", "Blue 3"]]

    return df


def get_tba_ranks():
    event_rankings = tba.event_rankings(st.secrets["DEFAULT_EVENT_KEY"])["rankings"]
    tba_ranks = {}

    for team in event_rankings:
        tba_ranks[team["team_key"].split("frc")[1]] = team["rank"]

    return tba_ranks


def get_presets():
    presets_path = "src\\pickles\\presets.pickle"
    try:
        with open(presets_path, "rb") as f:
            presets = pickle.load(f)
        return presets
    except:
        with open(presets_path, "wb") as f:
            pickle.dump({}, f, pickle.HIGHEST_PROTOCOL)
        return {}


def play_audio(file_path, delay):
    with open(f"src\\SuperSTATs\\audio\\{file_path}", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        html = f"""
           <audio autoplay="true">
           <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
           </audio>
           """
        placeholder = st.empty()
        placeholder.markdown(html, unsafe_allow_html=True)
        time.sleep(delay)
        placeholder.empty()


def app_init():
    try:
        st.set_page_config(
            page_title=f"SuperSTATs",
            page_icon="🤖",
            initial_sidebar_state="expanded",
            layout="wide",
            menu_items={"About": "Errorz Was Here 🐢"},
        )
    except:
        pass

    init = st.empty()
    load_messages = [
        "Error at frc.robot.subsystems.Drivetrain.getPose2d(Drivetrain.java:408): Unhandled exception: java.lang.OutOfBoundsException: SCP 3255 has escaped containment",
        "Yippee!",
        "Unplugging absolute encoder wires...",
        "Petting Susan 😸",
        "Perchance.",
        "Putting out fires... 🔥",
        "Brewing tea... 🫖",
    ]

    with st.spinner(random.choice(load_messages)):
        init_status = st.empty()

        if "init" not in st.session_state:
            init_status.text("Running initialization...")
            start_time = time.time()

            init_status.text("Downloading Team Info...")
            st.session_state.team_info = get_team_info()

            init_status.text("Getting Team Colors...")
            st.session_state.team_colors = get_team_colors()

            init_status.text("Initializing TBA API...")
            st.session_state.tba = tba

            init_status.text("Downloading Raw Data Sheet...")
            df = download_sheets_raw(st.secrets["GID_RAW"]).dropna(subset=["Timestamp"])

            init_status.text("Organizing Raw Data...")
            df = df.sort_values(["Match", "Timestamp"], ascending=[True, True])
            df = df.drop_duplicates(subset=["Team", "Match Type", "Match"])
            st.session_state.df = df

            init_status.text("Downloading Picked Team Data...")
            st.session_state.picked = download_sheets_raw(st.secrets["GID_PICKED"])

            init_status.text("Downloading Scouting Data...")
            st.session_state.scouting = download_sheets_raw(st.secrets["GID_SCOUTING"])

            init_status.text("Downloading Scouter Info...")
            get_scouters()

            init_status.text("Identifying Phases...")
            st.session_state.phases = get_phases(st.session_state.df)

            init_status.text("Calculating Point Values...")
            st.session_state.points = point_values()

            init_status.text("Loading Match Data...")
            st.session_state.match_data = get_match_data()

            init_status.text("Loading Matchs...")
            st.session_state.matches = get_matches()

            init_status.text("Loading TBA Rankings...")
            st.session_state.tba_ranks = get_tba_ranks()

            init_status.text("Fetching Presets...")
            st.session_state.presets = get_presets()

            elapsed_time = str(time.time() - start_time)[:4]

            init_status.text(f"Initialization complete in {elapsed_time} seconds...")
            st.session_state.init = True

            time.sleep(1)
            init_status.empty()

    init.empty()
