import json
import random
import time

import tbapy
from SuperSTATs import constants
import pandas as pd
import streamlit as st


def download_sheets_raw(gid):
    """
    Downloads a Google Sheets document as a pandas DataFrame.

    Args:
        gid (str): The ID of the Google Sheets document.

    Returns:
        pandas.DataFrame: The downloaded Google Sheets document as a DataFrame.
    """
    url = (
        f"https://docs.google.com/spreadsheets/d/{st.secrets['GSHEET_DOC_ID']}"
        f"/edit#gid={gid}"
    )
    doc_id, sheet_id = url.split("/")[5:7]
    sheet_id = sheet_id.split("gid=")[1]
    sheet_url = (
        f"https://docs.google.com/spreadsheets/d/{doc_id}/export"
        f"?format=csv&gid={sheet_id}"
    )
    df = pd.read_csv(sheet_url)
    df.columns = (
        df.columns.str.lstrip()
        .str.replace("[", repl="", regex=False)
        .str.replace("]", repl="", regex=False)
    )
    return df


def get_point_values():
    """
    Calculates the point values for each column in the dataframe
    based on the values within the column names.

    Returns:
        dict: A dictionary containing the calculated point values
        for each column.
    """
    points = {
        f"{value[0]}_{value[1]}_{value[2]}": int(value[3])
        for value in df.columns.str.split("_")
        if len(value) > 1
    }

    for col, point in points.items():
        df[f"{col}_{point}"] *= point

    return points


df = download_sheets_raw(st.secrets["GID_RAW"])
tba = tbapy.TBA(st.secrets["TBA_API"])


def initialise_app():
    """
        Initializes the SuperSTATs application and is called on every page.

        This function sets the page configuration, loads functions, initializes
        session state variables, and performs various data loading
        and setup tasks.

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
                "About": "Errorz Was Here 🐢",
            },
        )
    except Exception:
        pass

    with open(constants.JsonPaths.LOADING_MESSAGES, 'r') as f:
        loading_messages = json.load(f)

    loading_ascii = [
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

    for line in range(len(loading_ascii)):
        loading_ascii[line] = (
            loading_ascii[line]
            .replace("r", "<font color='C40301'>#</font>")
            .replace("y", "<font color='ECC412'><b>#</b></font>")
        )

    stages = [
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

    for i, stage in enumerate(stages):
        row = round(len(loading_ascii) / len(stages) * (i + 1)) - 1
        if row not in displayed_rows:
            status_messages[stage] = (
                f"<div style='text-align: center'>{loading_ascii[row]}</div>"
            )
        else:
            status_messages[stage] = None
        displayed_rows.append(row)

    init_status = st.empty()

    if "init" not in st.session_state:
        init_status.markdown(
            f"<div style='text-align: center'>"
            f"{random.choice(loading_messages)}</div>",
            unsafe_allow_html=True,
        )
        st.divider()

        start_time = time.time()

        def display_status(stage):
            if status_messages[stage] is not None:
                st.markdown(status_messages[stage], unsafe_allow_html=True)

        display_status("df_raw")
        df = download_sheets_raw(
            st.secrets["GID_RAW"]
        ).dropna(subset=["Timestamp"])

        display_status("points")
        st.session_state.points = get_point_values()

        elapsed_time = round(time.time() - start_time, 2)

        init_status.markdown(
            (
                f"<div style='text-align: center'>Initialization complete in "
                f"{elapsed_time} seconds!</div>"
            ),
            unsafe_allow_html=True,
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
