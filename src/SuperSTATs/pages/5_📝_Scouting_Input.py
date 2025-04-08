import SuperSTATs.load as load
import streamlit as st
import SuperSTATs.screen_elements as ui


def main():
    load.initialise_app()

    ui.display_header("📝 Scouting Input 📝")

if __name__ == "__main__":
    main()
