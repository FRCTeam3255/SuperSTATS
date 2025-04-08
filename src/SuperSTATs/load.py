import json
import pickle
import random
import time
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
            "team_info",
            "get_configs",
            "get_console",
            "match_data",
            "matches",
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

            self.display_status("team_info")
            st.session_state.team_info = self.get_team_info()

            self.display_status("get_configs")
            st.session_state.configs = self.get_configs()

            self.display_status("get_console")
            st.session_state.console = self.get_console()

            self.display_status("match_data")
            st.session_state.match_data = self.get_match_data()

            self.display_status("matches")
            st.session_state.matches = self.get_matches()

    def display_status(self, state):
        if self.status_messages[state] is not None:
            st.markdown(self.status_messages[state], unsafe_allow_html=True)

    @st.cache_data(show_spinner=False, persist=True)
    def get_team_info(_self): # TODO: Make sure that this is formatted the best it can be
        """
        Retrieves team information from TBA API.

        Returns:
            dict: A dictionary containing team information, where the keys are team numbers
                and the values are team nicknames. If the nickname is not available, the
                value will be set to "Unknown Team".
        """

        if st.secrets["DEFAULT_EVENT_KEY"] == "NoTBA":
            matches = download_sheets_raw(st.secrets["GID_MATCHES"])
            custom_teams = matches.loc[:, ~matches.columns.isin(["Match"])]
            unique_teams = [custom_teams[col].unique().tolist() for col in custom_teams]
            team_list = [team for sublist in unique_teams for team in sublist]

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

    def get_matches(self):  # TODO: Make sure that this is formatted the best it can be
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

    def get_match_data(
        self,
    ):  # TODO: Make sure that this is formatted the best it can be
        """
        Retrieves match data from the TBA API or a custom data source if TBA is down.

        Returns:
            pandas.DataFrame: A DataFrame containing the match data.
        """
        try:
            df = pd.DataFrame(self.tba.event_matches(st.secrets["DEFAULT_EVENT_KEY"]))
        except:
            df = pd.DataFrame()

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
                    "set_number": 1,
                    "score_breakdown": "im having a breakdown",
                    "winning_alliance": "blue",
                    "blue.score": 1,
                    "blue.team_keys": blue_team,
                    "red.score": 0,
                    "red.team_keys": red_team,
                    "Match Name": match_name,
                }

                custom_data[index] = data

            df = pd.DataFrame(custom_data).T

            return df

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

    def get_console(self):
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

    """
    if (
        st.session_state.console["require_login"]
        and not st.session_state.logged_in
    ):
        sign_in = st.empty()

        pass_input = sign_in.text_input("Password:", type="password")

        if pass_input != st.secrets["APP_PASSWORD"]:
            st.stop()
        else:
            st.session_state.logged_in = True
            sign_in.empty()
    """
