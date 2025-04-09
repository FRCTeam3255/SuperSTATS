import json
import pickle
import random
import time
import requests
import tbapy
import pandas as pd
import streamlit as st
from SuperSTATs import constants


class DataInitializer:
    def __init__(self):
        with open(constants.JsonPaths.LOADING_MESSAGES, "r") as file:
            self.loading_messages = json.load(file)

        self.ascii_SN = [
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

        for line in range(len(self.ascii_SN)):
            self.ascii_SN[line] = (
                self.ascii_SN[line]
                .replace("r", "<font color='C40301'>#</font>")
                .replace("y", "<font color='ECC412'><b>#</b></font>")
            )

        self.states = [
            "tba",
            "team_info",
            "configs",
            "console",
            "get_console",
            "match_data",
            "matches",
            "nexus",
            "team_colors",
            "scouts",
        ]

        self.start_time = time.time()

        self.tba = tbapy.TBA(st.secrets["TBA_API"])

        self.status_messages = {}
        self.displayed_rows = []

        for i, state in enumerate(self.states):
            row = round(len(self.ascii_SN) / len(self.states) * (i + 1)) - 1
            if row not in self.displayed_rows:
                self.status_messages[state] = (
                    f"<div style='text-align: center'>{self.ascii_SN[row]}</div>"
                )
            else:
                self.status_messages[state] = None
            self.displayed_rows.append(row)

        self.init_status = st.empty()

    def initialise_all(self):
        with self.init_status.status(
            random.choice(self.loading_messages), expanded=True
        ) as self.status:
            st.divider()

            self.display_status("tba")
            st.session_state.tba = self.tba

            self.display_status("team_info")
            st.session_state.team_info = self.get_team_info()

            self.display_status("configs")
            st.session_state.configs = self.get_configs()

            self.display_status("console")
            self.console()

            self.display_status("match_data")
            st.session_state.match_data = self.get_match_data()

            self.display_status("matches")
            st.session_state.matches = self.get_matches()

            self.display_status("nexus")
            st.session_state.nexus_data = self.get_nexus_data()

            self.display_status("team_colors")
            st.session_state.team_colors = self.get_team_colors()

            self.display_status("scouts")
            self.scouters = self.get_scouters()
            st.session_state.scouts = self.scouters["scouts"]
            st.session_state.assigned = self.scouters["assigned"]

    def display_status(self, state):
        if self.status_messages[state] is not None:
            st.markdown(self.status_messages[state], unsafe_allow_html=True)

    def get_nexus_data(
        team_num=st.secrets["TEAM_NUMBER"], event_key=st.secrets["DEFAULT_EVENT_KEY"]
    ):
        try:
            api_url = f"https://frc.nexus/api/v1/event/{event_key}"
            nexus_headers = {"Nexus-Api-Key": st.secrets["NEXUS_API"]}

            response = requests.get(api_url, headers=nexus_headers)
            data = response.json()
            team_num = str(team_num)

            nexus_data = {}

            on_field = [
                match["label"]
                for match in data["matches"]
                if match["status"] == "On field"
            ]
            nexus_data["now_playing"] = on_field[-1]

            team_matches = filter(
                lambda m: team_num in m.get("redTeams", []) + m.get("blueTeams", []),
                data["matches"],
            )
            next_match = next(
                filter(lambda m: not m["status"] == "On field", team_matches), None
            )

            if next_match:
                match_status = next_match["status"]
                queue_status = None if match_status == "Queuing soon" else match_status

                alliance_color = (
                    "red" if team_num in next_match.get("redTeams", []) else "blue"
                )

                nexus_data["team_num"] = team_num
                nexus_data["next_match"] = next_match["label"]
                nexus_data["queue_status"] = queue_status
                nexus_data["alliance_color"] = alliance_color
            else:
                nexus_data["next_match"] = None

            nexus_data["now_queuing"] = data["nowQueuing"]

            return nexus_data
        except Exception:
            nexus_data = None
            return nexus_data

    @st.cache_data(show_spinner=False)
    def get_team_colors(_self):
        """
        Retrieves the colors associated with each team from the FRC-Colors API or a pickle file if the colors are already known.

        Returns:
            dict: A dictionary containing the team colors, where the keys are the team names and the values are lists of primary and secondary colors.
        """
        team_info = st.session_state.team_info
        team_colors = {}
        unrecorded = []

        # Load recorded colors from pickle file
        try:
            with open("src\\pickles\\colors.pickle", "rb") as f:
                recorded = pickle.load(f)

            for team in team_info.keys():
                colors = recorded.get(str(team))
                if not colors or colors == ["003255", "003255"]:
                    unrecorded.append(team)
                else:
                    team_colors[str(team)] = colors
        except FileNotFoundError:
            unrecorded = list(team_info.keys())

        # Fetch unrecorded team colors from the API
        if unrecorded:
            teams_url = "&".join(f"team={team}" for team in unrecorded)
            api_url = f"https://frc-colors.com/api/v1/team?{teams_url}"

            try:
                response = requests.get(api_url, timeout=5)
                if response.status_code == 200:
                    raw_data = response.json()
                    for team, colors in raw_data["teams"].items():
                        if colors and colors["colors"]:
                            primary_color = colors["colors"]["primaryHex"]
                            secondary_color = colors["colors"]["secondaryHex"]
                            team_colors[str(team)] = [primary_color, secondary_color]
                        else:
                            team_colors[str(team)] = ["003255", "003255"]
                else:
                    # Default colors for teams if API fails
                    for team in unrecorded:
                        team_colors[str(team)] = ["003255", "003255"]
            except requests.RequestException:
                for team in unrecorded:
                    team_colors[str(team)] = ["003255", "003255"]

        # Save updated team colors to pickle file
        with open("src\\pickles\\colors.pickle", "wb") as f:
            pickle.dump(team_colors, f, pickle.HIGHEST_PROTOCOL)

        return team_colors

    def get_scouters(self):
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

        except Exception:
            scouts_df = download_sheets_raw(st.secrets["GID_SCOUTS"]).sort_values(
                by="Name"
            )

            return {
                "scouts": scouts_df["Name"].tolist(),
                "assigned": scouts_df.loc[
                    scouts_df["Assigned"] == "x", "Name"
                ].tolist(),
            }

    @st.cache_data(show_spinner=False, persist=True)
    def get_team_info(
        _self,
    ):
        """
        Retrieves team information from TBA API.

        Returns:
            dict: A dictionary containing team information, where the keys are team numbers
                and the values are team nicknames. If the nickname is not available, the
                value will be set to "Unknown Team".
        """

        if st.secrets["DEFAULT_EVENT_KEY"] == "NoTBA":
            matches = download_sheets_raw(st.secrets["GID_MATCHES"])

            # Extract columns excluding "Match"
            custom_teams = matches.loc[:, ~matches.columns.isin(["Match"])]

            # Get unique teams from each column
            unique_teams = []
            for col in custom_teams:
                unique_teams.extend(custom_teams[col].unique().tolist())

            # Flatten the list of unique teams
            team_list = list(set(unique_teams))

            tba_teams = []
            for team in team_list:
                tba_teams.append(_self.tba.team(f"frc{team}"))
        else:
            tba_teams = _self.tba.event_teams(st.secrets["DEFAULT_EVENT_KEY"])

        team_info = {
            team["team_number"]: _self.tba.team(team["team_number"]).get(
                "nickname", "Unknown Team"
            )
            for team in tba_teams
        }
        return team_info

    def get_matches(self):
        """
        Retrieves and processes match data to create a DataFrame of matches with desired alliances.

        Returns:
            pandas.DataFrame: DataFrame containing match data with columns for match number and team keys.
        """
        df = st.session_state.match_data

        # Split team keys into separate columns for red and blue alliances
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

        # Combine the original DataFrame with the new alliance columns
        df = pd.concat([df] + frames, axis=1)

        # Adjust match numbers for playoff matches
        df.loc[df["comp_level"] == "Playoffs", "match_number"] = df.loc[
            df["comp_level"] == "Playoffs", "set_number"
        ]

        # Create a "Match" column combining competition level and match number
        df["Match"] = (
            df["comp_level"] + " " + df["match_number"].astype(int).astype(str)
        )

        # Sort matches by competition level and match number
        df = df.sort_values(
            by=["comp_level", "match_number"], ascending=[False, True]
        ).reset_index(drop=True)

        # Select and reorder columns for the final DataFrame
        df = df[["Match", "Red 1", "Red 2", "Red 3", "Blue 1", "Blue 2", "Blue 3"]]

        return df

    def get_match_data(self):
        """
        Retrieves match data from the TBA API or a custom data source if TBA is unavailable.

        Returns:
            pandas.DataFrame: A DataFrame containing the match data.
        """
        try:
            # Attempt to fetch match data from TBA API
            df = pd.DataFrame(self.tba.event_matches(st.secrets["DEFAULT_EVENT_KEY"]))
        except Exception:
            df = pd.DataFrame()

        if not df.empty:
            # Normalize alliances data and drop the original column
            alliances_df = pd.json_normalize(df["alliances"])
            df = pd.concat([df, alliances_df], axis=1).drop(columns="alliances")

            # Replace competition level codes with readable names
            df["comp_level"] = df["comp_level"].replace(
                {"qm": "Quals", "sf": "Playoffs", "f": "Finals"}
            )

            # Convert team keys to integers
            for color in ["red", "blue"]:
                df[f"{color}.team_keys"] = df[f"{color}.team_keys"].apply(
                    lambda teams: [int(team.replace("frc", "")) for team in teams]
                )

            # Generate match names
            df["Match Name"] = df.apply(
                lambda row: (
                    f"{row['comp_level']} {int(row['set_number'])}"
                    if row["comp_level"] == "Playoffs"
                    else f"{row['comp_level']} {int(row['match_number'])}"
                ),
                axis=1,
            )

            return df

        else:
            # Fallback to custom data source if TBA API is unavailable
            matches = download_sheets_raw(st.secrets["GID_MATCHES"])

            custom_data = []
            for _, row in matches.iterrows():
                match_data = {
                    "comp_level": row["Match"].split()[0],
                    "match_number": int(row["Match"].split()[1]),
                    "set_number": 1,
                    "blue.team_keys": [row["Blue 1"], row["Blue 2"], row["Blue 3"]],
                    "red.team_keys": [row["Red 1"], row["Red 2"], row["Red 3"]],
                    "Match Name": row["Match"],
                }
                custom_data.append(match_data)

            return pd.DataFrame(custom_data)

    def close(self):
        elapsed_time = round(time.time() - self.start_time, 2)

        self.status.update(
            label=f"Initialization complete in {elapsed_time} seconds!",
            state="complete",
            expanded=True,
        )
        st.session_state.init = True

        time.sleep(1)
        self.init_status.empty()

    def get_configs(self):
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

    def console(self):
        st.session_state.console = {}
        for config in st.session_state.configs["Console"]:
            config, default_status = config.split("=")
            st.session_state.console[config] = bool(default_status == "true")


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


def initialise_app():
    """
    Initializes the SuperSTATs application and is called on every page.

    This function sets the page configuration, loads functions, initializes
    session state variables, and performs various data loading and setup tasks.

    Returns:
        None
    """
    try:
        st.set_page_config(
            page_title="SuperSTATs",
            page_icon="🤖",
            initial_sidebar_state="expanded",
            layout="wide",
            menu_items={
                "Get Help": "https://supernurds.com/contact",
                "Report a bug": ("https://github.com/FRCTeam3255/SuperSTATS/issues"),
                "About": "S0L0GUY Was Here",
            },
        )
    except Exception:
        pass

    init = DataInitializer()
    init.initialise_all()
    init.close()

    st.session_state.logged_in = False

    if st.session_state.console["require_login"] and not st.session_state.logged_in:
        sign_in = st.empty()

        pass_input = sign_in.text_input("Password:", type="password")

        if pass_input != st.secrets["APP_PASSWORD"]:
            st.stop()
        else:
            st.session_state.logged_in = True
            sign_in.empty()
