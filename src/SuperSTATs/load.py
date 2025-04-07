import json
import random
import time
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

        states = []

        status_messages = {}
        displayed_rows = []

        for i, state in enumerate(states):
            row = round(len(self.ascii_SN) / len(states) * (i + 1)) - 1
            if row not in displayed_rows:
                status_messages[state] = (
                    f"<div style='text-align: center'>{self.ascii_SN[row]}</div>"
                )
            else:
                status_messages[state] = None
            displayed_rows.append(row)



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
