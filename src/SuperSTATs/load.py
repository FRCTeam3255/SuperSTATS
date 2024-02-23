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


df = download_sheets_raw(st.secrets["GID_RAW"])
tba = tbapy.TBA(st.secrets["TBA_API"])


def get_tba_ranks():
    event_rankings = tba.event_rankings(st.secrets["DEFAULT_EVENT_KEY"])["rankings"]
    tba_ranks = {}

    for team in event_rankings:
        tba_ranks[team["team_key"].split("frc")[1]] = team["rank"]

    return tba_ranks


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
    unrecorded = []

    try:
        with open("src\\pickles\\colors.pickle", "rb") as f:
            recorded = pickle.load(f)

        for team in team_info.keys():
            try:
                colors = recorded[str(team)]

                if colors == None or colors == ["003255", "003255"]:
                    unrecorded.append(team)

                else:
                    team_colors[str(team)] = colors

            except:
                unrecorded.append(team)

    except:
        unrecorded.extend(team for team in team_info.keys())

    teams_url = ""
    for team in unrecorded:
        teams_url += f"team={team}&"

    api = f"https://frc-colors.com/api/v1/team"
    response = requests.get(f"{api}/3255", timeout=5)

    if response.status_code == 200:
        response = requests.get(f"{api}?{teams_url}")
        raw_data = response.json()

        for team, colors in raw_data["teams"].items():
            colors = colors["colors"]

            if colors != None:
                primary_color = colors["primaryHex"]
                secondary_color = colors["secondaryHex"]
                team_colors[str(team)] = [primary_color, secondary_color]

            else:
                team_colors[str(team)] = ["003255", "003255"]

        with open("src\\pickles\\colors.pickle", "wb") as f:
            pickle.dump(team_colors, f, pickle.HIGHEST_PROTOCOL)

    else:
        for team in unrecorded:
            team_colors[team] = ["003255", "003255"]

    return team_colors


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
            return row["comp_level"] + " " + str(row["match_number"])

        df["Match Name"] = df.apply(set_match_name, axis=1)

        return df
    except:
        st.error(f"Error getting match data. Please refresh...")
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


def get_unplayed(df, matches):
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

    return unplayed_matches


def get_scouters():
    try:
        with open("src\\pickles\\scouts.pickle", "rb") as f:
            scouts = pickle.load(f)

        return {"scouts": scouts[0], "assigned": scouts[1]}

    except:
        scouts_df = download_sheets_raw(st.secrets["GID_SCOUTS"]).sort_values(by="Name")

        return {
            "scouts": scouts_df["Name"].tolist(),
            "assigned": scouts_df.loc[scouts_df["Assigned"] == "x", "Name"].tolist(),
        }


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


def get_point_values():
    points = {
        f"{value[0]}_{value[1]}_{value[2]}": int(value[3])
        for value in df.columns.str.split("_")
        if len(value) > 1
    }

    for col, point in points.items():
        df[f"{col}_{point}"] *= point

    return points


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


def get_configs():
    configs_raw = download_sheets_raw(st.secrets["GID_CONFIG"])
    configs = {}

    for index, row in configs_raw.iterrows():
        config = row["Config"]
        value = row["Value"]
        configs[config] = value.split(", ")

    configs_path = "src\\pickles\\configs.pickle"

    try:
        with open(configs_path, "rb") as f:
            configs = pickle.load(f)
        return configs
    except:
        with open(configs_path, "wb") as f:
            pickle.dump(configs, f, pickle.HIGHEST_PROTOCOL)
        return configs


def app_init():
    try:
        st.set_page_config(
            page_title=f"SuperSTATs",
            page_icon="🤖",
            initial_sidebar_state="expanded",
            layout="wide",
            menu_items={
                "Get Help": "https://supernurds.com/contact",
                "Report a bug": "https://github.com/FRCTeam3255/SuperSTATS/issues",
                "About": "Errorz Was Here 🐢",
            },
        )
    except:
        pass

    load_messages = [
        "Error at frc.robot.subsystems.Drivetrain.getPose2d(Drivetrain.java:408): Unhandled exception: java.lang.OutOfBoundsException: SCP 3255 has escaped containment",
        "Yippee!",
        "Unplugging absolute encoder wires...",
        "Petting Susan 😸",
        "Perchance.",
        "Putting out fires... 🔥",
        "Brewing tea... 🫖",
        "Downloading more RAM...",
        "Exploding Falcons... 💥",
    ]

    ascii_SN = [
        "     yyyyyyyyyyyyyyyyyyyyyyyyyy     ",
        "   yyyrryyyyyyyrrryyyrrrrrryyryyy   ",
        " yyyrrryyyrrrryyrryyyyrrrrryyrrryyy ",
        " yyrrrryyyrrrrrrrryyyryyrrryyrrrryy ",
        "  yyyrrryyyyyyrrrryyyrryyrryyrryyy  ",
        "    yyrrrryyyyyyrryyyrrryyryyryy    ",
        "      yyrrrrrryyyryyyrrrryyyyy      ",
        "        yyyrrrryyryyyrrrryyy        ",
        "          yyyyyyrryyrrryyy          ",
        "            yyyrrryyyryy            ",
        "              yyrryyyy              ",
        "                yyyy                ",
        "                                    ",
    ]

    for line in range(len(ascii_SN)):
        ascii_SN[line] = (
            ascii_SN[line]
            .replace("r", "<font color='C40301'>#</font>")
            .replace("y", "<font color='ECC412'><b>#</b></font>")
        )

    states = [
        "df_raw",
        "df",
        "tba",
        "tba_ranks",
        "team_info",
        "team_colors",
        "match_data",
        "matches",
        "unplayed_matches",
        "picked",
        "scouting",
        "scouts",
        "phases",
        "points",
        "presets",
        "configs",
        "console",
    ]

    status_messages = {}
    displayed_rows = []

    for i, state in enumerate(states):
        row = round(len(ascii_SN) / len(states) * (i + 1)) - 1
        if row not in displayed_rows:
            status_messages[state] = (
                f"<div style='text-align: center'>{ascii_SN[row]}</div>"
            )
        else:
            status_messages[state] = None
        displayed_rows.append(row)

    init_status = st.empty()

    if "init" not in st.session_state:
        with init_status.status(random.choice(load_messages), expanded=True) as status:
            st.divider()

            start_time = time.time()

            def display_status(state):
                if status_messages[state] is not None:
                    st.markdown(status_messages[state], unsafe_allow_html=True)

            display_status("df_raw")
            df = download_sheets_raw(st.secrets["GID_RAW"]).dropna(subset=["Timestamp"])

            display_status("df")
            df = df.sort_values(["Match", "Timestamp"], ascending=[True, True])
            df = df.drop_duplicates(subset=["Team", "Match Type", "Match"])
            df = df[df["Event Key"] == st.secrets["DEFAULT_EVENT_KEY"]]
            st.session_state.df = df

            display_status("tba")
            st.session_state.tba = tba

            display_status("tba_ranks")
            st.session_state.tba_ranks = get_tba_ranks()

            display_status("team_info")
            st.session_state.team_info = get_team_info()

            display_status("team_colors")
            st.session_state.team_colors = get_team_colors()

            display_status("match_data")
            st.session_state.match_data = get_match_data()

            display_status("matches")
            st.session_state.matches = get_matches()

            display_status("unplayed_matches")
            st.session_state.unplayed_matches = get_unplayed(
                st.session_state.df, st.session_state.matches
            )

            display_status("picked")
            st.session_state.picked = download_sheets_raw(st.secrets["GID_PICKED"])

            display_status("scouting")
            st.session_state.scouting = download_sheets_raw(st.secrets["GID_SCOUTING"])

            display_status("scouts")
            scouters = get_scouters()
            st.session_state.scouts = scouters["scouts"]
            st.session_state.assigned = scouters["assigned"]

            display_status("phases")
            st.session_state.phases = get_phases(st.session_state.df)

            display_status("points")
            st.session_state.points = get_point_values()

            display_status("presets")
            st.session_state.presets = get_presets()

            display_status("configs")
            st.session_state.configs = get_configs()

            display_status("console")
            st.session_state.console = {}
            for config in st.session_state.configs["Console"]:
                config, default_status = config.split("=")
                st.session_state.console[config] = bool(default_status == "true")

            st.session_state.chat = {
                "logged_in": False,
                "user": "",
                "icon": "",
                "pass": "",
            }

            elapsed_time = round(time.time() - start_time, 2)

            status.update(
                label=f"Initialization complete in {elapsed_time} seconds!",
                state="complete",
                expanded=True,
            )
            st.session_state.init = True

            time.sleep(1)
            init_status.empty()

    if st.session_state.console["use_chat"]:
        try:
            with st.sidebar:
                sign_in = st.empty()

                with st.form("chat_login", border=False):
                    login_columns = st.columns(2)

                    if not st.session_state.chat["logged_in"]:
                        st.session_state.chat["user"] = login_columns[0].text_input(
                            "Username:",
                            max_chars=17,
                            value=(
                                st.session_state.chat["user"]
                                if st.session_state.chat["user"] != ""
                                else ""
                            ),
                            key="login_user",
                        )

                        st.session_state.chat["icon"] = login_columns[1].text_input(
                            "Icon:",
                            value=(
                                st.session_state.chat["icon"]
                                if st.session_state.chat["icon"] != ""
                                else ""
                            ),
                            key="login_icon",
                        )

                        if st.session_state.chat["user"] in st.secrets["MODERATORS"]:
                            st.session_state.chat["pass"] = st.text_input(
                                "Password:",
                                type="password",
                                key="login_pass",
                            )
                        else:
                            st.session_state.chat["pass"] = "."
                    else:
                        pass

                    login = st.form_submit_button(
                        "Login",
                        use_container_width=True,
                        disabled=st.session_state.chat["logged_in"],
                    )

                    if login or st.session_state.chat["logged_in"]:
                        creds = st.session_state.chat
                        if not any(value is "" for value in creds.values()):
                            st.session_state.chat["logged_in"] = True
                            sign_in.empty()
                            st.markdown(
                                f'<iframe src="https://ezchat.streamlit.app/?user={creds["user"]}&icon={creds["icon"]}&pass={creds["pass"]}&embed=true" height="450" style="width: 100%; border: none;"></iframe>',
                                unsafe_allow_html=True,
                            )
        except:
            pass
