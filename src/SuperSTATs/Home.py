import SuperSTATs.load as load
import streamlit as st
import SuperSTATs.screen_elements as ui


def main():
    load.initialise_app()

    ui.display_header("🤖 SuperSTATs 🤖")

    event_key = st.secrets["DEFAULT_EVENT_KEY"]
    ui.display_event_link(event_key)


if __name__ == "__main__":
    main()
