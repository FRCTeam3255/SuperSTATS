import json
import pickle
import random
import time
import pandas as pd
import streamlit as st
from SuperSTATs import constants

class DataInitializer:
    def __init__(self):
        with open(constants.JsonPaths.LOADING_MESSAGES, 'r') as file:
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
            "get_configs",
            "get_console",
        ]

        self.start_time = time.time()

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
        with self.init_status.status(random.choice(self.loading_messages), expanded=True) as self.status:
            st.divider()

            self.display_status("get_configs")
            st.session_state.configs = self.get_configs()

            self.display_status("get_console")
            st.session_state.console = self.get_console()

    def display_status(self, state):
        if self.status_messages[state] is not None:
            st.markdown(self.status_messages[state], unsafe_allow_html=True)

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
                "Report a bug": (
                    "https://github.com/FRCTeam3255/SuperSTATS/issues"
                ),
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
