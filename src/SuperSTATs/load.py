import json
import random
import time
import streamlit as st
from SuperSTATs import constants


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

    load_messages = json.loads(constants.JsonPaths.LOADING_MESSAGES)

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
        "nexus",
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

            display_status("points")

            display_status("df")

            display_status("configs")

            display_status("console")
            st.session_state.console = {}
            for config in st.session_state.configs["Console"]:
                config, default_status = config.split("=")
                st.session_state.console[config] = bool(
                    default_status == "true"
                )

            display_status("tba")

            display_status("tba_ranks")

            display_status("team_info")

            display_status("team_colors")

            display_status("match_data")

            display_status("matches")

            display_status("unplayed_matches")

            display_status("nexus")

            display_status("picked")

            display_status("scouting")

            display_status("scouts")

            display_status("phases")

            display_status("presets")

            display_status("forms")

            display_status("analytics")
            st.session_state.analytics_settings = [
                "page_change",
                "page_update",
                "button_press",
                "input",
            ]

            st.session_state.logged_in = False

            elapsed_time = round(time.time() - start_time, 2)

            status.update(
                label=f"Initialization complete in {elapsed_time} seconds!",
                state="complete",
                expanded=True,
            )
            st.session_state.init = True

            time.sleep(1)
            init_status.empty()

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
