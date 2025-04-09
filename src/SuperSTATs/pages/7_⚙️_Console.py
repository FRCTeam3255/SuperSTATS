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

def save_scouts(scout_list, scouts):
    st.session_state.assigned = scout_list

    with open("src\\pickles\\scouts.pickle", "wb") as f:
        pickle.dump([scouts, scout_list], f, pickle.HIGHEST_PROTOCOL)

    st.toast("Successfully set scouters! Please refresh...", icon="✅")


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

        if ui.update_button("Update Configs", "update_configs"):
            save_console_configs(settings_raw, updated_configs)

    with st.expander("Scouts"):
        scouts = st.session_state.scouts
        assigned = st.session_state.assigned

        columns = st.columns(4)

        scout_list = []

        for i, scout in enumerate(scouts):
            initial_state = True if scout in assigned else False

            toggled_state = columns[i % 4].toggle(scout, initial_state)

            if toggled_state:
                scout_list.append(scout)

        scout_amount = len(scout_list)

        if scout_amount < 6:
            st.error(f"⚠️ Not enough scouters ({scout_amount}/6)")
            scout_list.extend([f"N/A {i}" for i in range(6 - scout_amount)])

        st.divider()

        if st.button(
            "Set Scouters",
            type="primary",
            use_container_width=True,
            key=f"set_scouters",
        ):
            st.session_state.assigned = scout_list

            with open("src\\pickles\\scouts.pickle", "wb") as f:
                pickle.dump([scouts, scout_list], f, pickle.HIGHEST_PROTOCOL)

            st.toast("Successfully set scouters! Please refresh...", icon="✅")

if __name__ == "__main__":
    main()
