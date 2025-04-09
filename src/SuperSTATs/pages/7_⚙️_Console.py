import pickle
import SuperSTATs.load as load
import streamlit as st
import SuperSTATs.screen_elements as ui

def save_console_configs(settings_raw, updated_configs):
    st.session_state.configs["Console"] = settings_raw
    st.session_state.console = updated_configs

    with open("src\\pickles\\configs.pickle", "wb") as f:
        pickle.dump(st.session_state.configs, f, pickle.HIGHEST_PROTOCOL)

    st.toast("Successfully updated configs! Please refresh...", icon="✅")


def main():
    load.initialise_app()

    ui.display_header("⚙️ Console ⚙️")
    ui.update_button("Update Page")
    st.divider()

    with st.expander("Config"):
        updated_configs = {}

        columns = st.columns(4)

        for i, (config, status) in enumerate(st.session_state.console.items()):
            updated_configs[config] = columns[i % 4].toggle(
                config.title().replace("_", " ").replace("Tba", "TBA"), status
            )

        settings_raw = [
            f"{key}={str(value).lower()}" for key, value in updated_configs.items()
        ]

        ui.update_button("Update Configs", "update_configs")

        save_console_configs(settings_raw, updated_configs)

if __name__ == "__main__":
    main()
