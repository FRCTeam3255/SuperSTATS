import streamlit as st

@st.cache_data(show_spinner=False, persist=True)
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
