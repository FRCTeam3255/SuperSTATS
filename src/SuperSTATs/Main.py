import SuperSTATs.loader as load
import streamlit as st
import pandas as pd
import tbapy

st.set_page_config(
    page_title="SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
    menu_items={"About": "Developed by FRC Team 3255 - SuperNURDs"},
)

tba = tbapy.TBA(st.secrets["TBA_API"])


def main():
    load.init_page()

    st.markdown(
        "<div style='display: flex; justify-content: center; font-size: 40px;'><b>🤖 SuperSTATs 🤖</b></div>",
        unsafe_allow_html=True,
    )

    password = st.secrets["GUEST_PASSWORD"]
    display = st.empty()

    if not st.session_state.signed_in:
        pass_input = display.text_input("Password:", type="password").lower()

        if pass_input == password:
            st.session_state.signed_in = True
            display.empty()

    if st.session_state.signed_in:
        st.markdown(
            """
            <div style="display: flex; flex-direction: row; justify-content: center; text-align: center;">
                <a href="https://docs.google.com/spreadsheets/d/1KboyFTIZJiIW_33Z9_ea8jtYkV3T-fuS659ezwsXYmY/edit#gid=1878511843" style="color: #0070E0; font-size: 25px; margin: 10px;">Raw Data Sheet</a>
                <a href="https://www.supernurds.com/statsinput" style="color: #0070E0; font-size: 25px; margin: 10px;">Stats Input Form</a>
                <a href="https://docs.google.com/forms/d/1P32axMIgTIkHJUZuP4BPpiVX1-CMNHobgsAW-aZkse4" style="color: #0070E0; font-size: 25px; margin: 10px;">Scouting Form</a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    logo_path = "src/SuperSTATs/images/SN_Logo.png"

    st.title("")
    st.image(logo_path)

    st.title("")

    st.markdown(
        f"<h1 style='text-align: center;'>Current Dataframe: {st.secrets['DEFAULT_EVENT_KEY']}<h1>",
        unsafe_allow_html=True,
    )
    st.table(st.session_state.global_match_df)

    with st.expander("View Keys"):
        # chosen_event = None
        year = st.number_input("Year:", min_value=0, step=1, value=2023)

        # year = st.sidebar.number_input("Year:", min_value=0, step=1, value=2023)
        # events = tba.events(int(year))
        events = tba.events(year)
        event_keys = {}

        for event in events:
            name = event["name"]
            key = event["key"]
            event_keys[name] = key

        for name, key in event_keys.items():
            st.text(f"{name} : {key}")

    load.set_global_df()


if __name__ == "__main__":
    main()
