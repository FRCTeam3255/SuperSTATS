import SuperSTATs.form as form
import streamlit as st
import pandas as pd
import requests
import random
import pickle
import tbapy
import time


def download_sheets_raw(gid):
    """
    Downloads a Google Sheets document as a pandas DataFrame.

    Args:
        gid (str): The ID of the Google Sheets document.

    Returns:
        pandas.DataFrame: The downloaded Google Sheets document as a DataFrame.
    """
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


def add_cols(org_df, filter):
    """
    Add a new column to the given DataFrame based on the specified filter.

    Args:
        org_df (pandas.DataFrame): The original DataFrame.
        filter (str): The filter to be applied to select relevant columns.

    Returns:
        pandas.Series: The newly added column.
    """
    points = {}

    for key, value in st.session_state.points.items():
        points[f"{key}_{value}"] = value

    relevant_columns = [
        col
        for col in org_df.columns
        if col != "COMMENT_GENERAL_STR_1" and col.startswith(filter)
    ]

    org_df[filter] = org_df[relevant_columns].apply(
        lambda row: sum(
            [points[col] * val for col, val in row.items() if col in points]
        ),
        axis=1,
    )

    return org_df[filter]


def get_point_values():
    """
    Calculates the point values for each column in the dataframe based on the values within the column names.

    Returns:
        dict: A dictionary containing the calculated point values for each column.
    """
    points = {
        f"{value[0]}_{value[1]}_{value[2]}": int(value[3])
        for value in df.columns.str.split("_")
        if len(value) > 1
    }

    for col, point in points.items():
        df[f"{col}_{point}"] *= point

    return points


def organize_df(df):
    """
    Organizes the given DataFrame by performing various operations such as filtering, sorting, and concatenating.

    Args:
        df (pandas.DataFrame): The DataFrame to be organized.

    Returns:
        pandas.DataFrame: The organized DataFrame.
    """
    df = download_sheets_raw(st.secrets["GID_RAW"]).dropna(subset=["Timestamp"])
    df = df.sort_values(["Match", "Timestamp"], ascending=[True, True])
    df = df[df["Event Key"] == st.secrets["DEFAULT_EVENT_KEY"]]
    df = df.drop_duplicates(subset=["Team", "Match Type", "Match"])

    phases = ["AUTO", "TELE", "END"]
    all_non_prac_list = []
    all_prac_list = []

    for team in df["Team"].unique():
        team_df = df[df["Team"] == team]

        non_prac = team_df[~team_df["Match Type"].str.startswith("Prac")]
        prac = team_df[team_df["Match Type"].str.startswith("Prac")]

        if non_prac.empty:
            for _, row in prac.iterrows():
                row = row.to_frame().T
                for i in range(len(phases)):
                    team_df.loc[:, phases[i]] = add_cols(
                        team_df,
                        phases[i],
                    )

                team_df["Score"] = team_df[phases].sum(axis=1)

                max_score_index = team_df["Score"].idxmax()
                max_score_row = team_df.loc[max_score_index]

                prac_match = max_score_row.to_frame().T.drop(phases + ["Score"], axis=1)
                all_prac_list.append(prac_match)

            all_prac_df = (
                pd.concat(all_prac_list, ignore_index=True)
                .sort_values(by="Timestamp")
                .drop_duplicates()
            )
        else:
            for _, row in non_prac.iterrows():
                row = row.to_frame().T
                all_non_prac_list.append(row)

            all_non_prac_df = (
                pd.concat(all_non_prac_list, ignore_index=True)
                .sort_values(by="Timestamp")
                .drop_duplicates()
            )

    try:
        df = pd.concat([all_non_prac_df, all_prac_df], ignore_index=True)
    except:
        df = all_non_prac_df

    return df


def get_configs():
    """
    Retrieves the configurations from a Google Sheets document and saves them to a pickle file.

    Returns:
        dict: A dictionary containing the configurations, where each configuration is a key and its corresponding value is a list of values.
    """
    configs_raw = download_sheets_raw(st.secrets["GID_CONFIG"])
    configs = {}

    for _, row in configs_raw.iterrows():
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


def get_tba_ranks():
    """
    Retrieves the rankings of teams from TBA for a specific event.

    Returns:
        dict: A dictionary containing team rankings, where the keys are team numbers (without the "frc" prefix) and the values are the corresponding ranks.
    """
    event_rankings = tba.event_rankings(st.secrets["DEFAULT_EVENT_KEY"])["rankings"]
    tba_ranks = {}

    for team in event_rankings:
        tba_ranks[team["team_key"].split("frc")[1]] = team["rank"]

    return tba_ranks


@st.cache_data(show_spinner=False, persist=True)
def get_team_info():
    """
    Retrieves team information from TBA API.

    Returns:
        dict: A dictionary containing team information, where the keys are team numbers
              and the values are team nicknames. If the nickname is not available, the
              value will be set to "Unknown Team".
    """
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
    """
    Retrieves the colors associated with each team from the FRC-Colors API or a picklefile if the colors are already known.

    Returns:
        dict: A dictionary containing the team colors, where the keys are the team names and the values are lists of primary and secondary colors.
    """
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
    """
    Retrieves match data from the TBA API or a custom data source if TBA is down.

    Returns:
        pandas.DataFrame: A DataFrame containing the match data.
    """
    df = pd.DataFrame(tba.event_matches(st.secrets["DEFAULT_EVENT_KEY"]))

    if not df.empty:
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
            """
            Sets the name for a match based on the given row.

            Parameters:
            - row: A dictionary representing a row of match data.

            Returns:
            - match_name: A string representing the name of the match.
            """
            if row["comp_level"] == "Playoffs":
                return row["comp_level"] + " " + str(int(row["set_number"]))
            return row["comp_level"] + " " + str(int(row["match_number"]))

        df["Match Name"] = df.apply(set_match_name, axis=1)

        return df

    else:
        matches = download_sheets_raw(st.secrets["GID_MATCHES"])

        custom_data = {}

        for index, row in matches.iterrows():
            match_name = row["Match"]
            match_level = match_name.split()[0]
            match_num = int(match_name.split()[1])

            red_team = [row["Red 1"], row["Red 2"], row["Red 3"]]
            blue_team = [row["Blue 1"], row["Blue 2"], row["Blue 3"]]

            data = {
                "comp_level": match_level,
                "match_number": match_num,
                "set_number": {f"{index}": 1},
                "score_breakdown": {f"{index}": "im having a breakdown"},
                "winning_alliance": {f"{index}": "blue"},
                "blue.score": {f"{index}": 1},
                "blue.team_keys": blue_team,
                "red.score": {f"{index}": 0},
                "red.team_keys": red_team,
                "Match Name": {f"{index}": match_name},
            }

            custom_data[index] = data

        df = pd.DataFrame(custom_data).T

        return df


def get_matches():
    """
    Retrieves and processes match data to create a DataFrame of matches with desired alliances.

    Returns:
        pandas.DataFrame: DataFrame containing match data with columns for match number and team keys.
    """
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

    df["Match"] = df["comp_level"] + " " + df["match_number"].astype(int).astype(str)

    df = df.sort_values(
        by=["comp_level", "match_number"], ascending=[False, True]
    ).reset_index(drop=True)

    df = df[["Match", "Red 1", "Red 2", "Red 3", "Blue 1", "Blue 2", "Blue 3"]]

    return df


def get_unplayed(df, matches):
    """
    Get a list of unplayed matches based on the given DataFrame and matches.

    Args:
        df (pandas.DataFrame): The DataFrame containing match data.
        matches (pandas.DataFrame): The DataFrame containing match information.

    Returns:
        list: A list of unplayed matches.

    """
    df["Completed"] = df["Match Type"] + " " + df["Match"].astype(int).astype(str)
    df_counts = df["Completed"].value_counts()

    df["Completed"] = df["Completed"].apply(lambda x: x if df_counts[x] >= 3 else None)

    tba_played_matches = []

    for _, row in st.session_state.match_data.iterrows():
        try:
            if row["red.score"] != -1 and row["blue.score"] != -1:
                tba_played_matches.append(row["Match Name"])
        except:
            pass

    df_unique = df["Completed"].dropna().unique()
    matches_unique = matches["Match"].unique()

    unplayed_matches = pd.concat(
        [pd.DataFrame(df_unique), pd.DataFrame(matches_unique)]
    ).drop_duplicates(keep=False)

    unplayed_matches = [
        match for sublist in unplayed_matches.values.tolist() for match in sublist
    ]

    unplayed_copy = unplayed_matches.copy()

    if st.session_state.console["tba_unplayed"]:
        for match in unplayed_copy:
            if match in tba_played_matches:
                unplayed_matches.remove(match)

    unplayed_matches = [
        match for match in unplayed_matches if not match.startswith("Prac")
    ]

    return unplayed_matches


def get_picked():
    """
    Retrieves the picked teams data from the downloaded sheet.

    Returns:
        pandas.DataFrame: The picked data containing rows where the "Unavailable" column contains an "x".
    """
    picked = download_sheets_raw(st.secrets["GID_PICKED"])
    return picked[picked["Unavailable"].str.contains("x", case=False, na=False)]


def get_scouters():
    """
    Retrieves the list of team scouts and their assigned status.

    If the pickle file exists, it loads the data from the file and returns a dictionary
    with two keys: 'scouts' and 'assigned'. Otherwise downloads the data from Sheets document
    and returns a dictionary with the same keys.

    Returns:
        dict: A dictionary with two keys: 'scouts' and 'assigned'. The 'scouts' key contains a list of
        all scout names, and the 'assigned' key contains a list of scout names that are assigned.
    """
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
    """
    Get a list of unique game phases from the given DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing the columns.

    Returns:
        list: A sorted list of unique phases extracted from the column names.
    """
    filtered_columns = []
    for column in df.columns:
        if any(c.isdigit() for c in column.split("_")[-1]):
            filtered_columns.append(column)

    phases = []
    for column in filtered_columns:
        column = column.split("_")[0]
        phases.append(column)

    return sorted(list(set(phases)))


def get_presets():
    """
    Retrieves the presets from the presets pickle file.

    If the file exists, it loads the presets from the file and returns them otherwise if
    the file does not exist, it creates an empty presets file and returns an empty dictionary.

    Returns:
        dict: The presets loaded from the file or an empty dictionary if the file does not exist.
    """
    presets_path = "src\\pickles\\presets.pickle"

    try:
        with open(presets_path, "rb") as f:
            presets = pickle.load(f)
        return presets
    except:
        with open(presets_path, "wb") as f:
            pickle.dump({}, f, pickle.HIGHEST_PROTOCOL)
        return {}


def app_init():
    """
    Initializes the SuperSTATs application and is called on every page.

    This function sets the page configuration, loads functions, initializes
    session state variables, and performs various data loading and setup tasks.

    Returns:
        None
    """
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
        "Crackin' Krackens... 🦑",
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
        "points",
        "df",
        "configs",
        "console",
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
        "presets",
        "forms",
        "analytics",
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

            display_status("points")
            st.session_state.points = get_point_values()

            display_status("df")
            st.session_state.df = organize_df(df)

            display_status("configs")
            st.session_state.configs = get_configs()

            display_status("console")
            st.session_state.console = {}
            for config in st.session_state.configs["Console"]:
                config, default_status = config.split("=")
                st.session_state.console[config] = bool(default_status == "true")

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
            st.session_state.picked = get_picked()

            display_status("scouting")
            st.session_state.scouting = download_sheets_raw(st.secrets["GID_SCOUTING"])

            display_status("scouts")
            scouters = get_scouters()
            st.session_state.scouts = scouters["scouts"]
            st.session_state.assigned = scouters["assigned"]

            display_status("phases")
            st.session_state.phases = get_phases(st.session_state.df)

            display_status("presets")
            st.session_state.presets = get_presets()

            display_status("forms")
            st.session_state.forms = form.cache_forms(["STATS_FORM", "SCOUTING_FORM"])

            display_status("analytics")
            st.session_state.analytics_settings = [
                "page_change",
                "page_update",
                "button_press",
                "input",
            ]

            st.session_state.analytics = {}

            for analytic in st.session_state.analytics_settings:
                st.session_state.analytics[analytic] = False

            st.session_state.uid = str(random.randint(10**7, 10**8 - 1))
            st.session_state.page = None

            st.session_state.logged_in = False
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

    if st.session_state.console["require_login"] and not st.session_state.logged_in:
        sign_in = st.empty()

        pass_input = sign_in.text_input("Password:", type="password")

        if pass_input != st.secrets["APP_PASSWORD"]:
            st.stop()
        else:
            st.session_state.logged_in = True
            sign_in.empty()

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
                        if creds["pass"] != "":
                            st.session_state.chat["logged_in"] = True
                            sign_in.empty()
                            st.markdown(
                                f'<iframe src="https://ezchat.streamlit.app/?user={creds["user"]}&icon={creds["icon"]}&pass={creds["pass"]}&embed=true" height="450" style="width: 100%; border: none;"></iframe>',
                                unsafe_allow_html=True,
                            )
        except:
            pass
