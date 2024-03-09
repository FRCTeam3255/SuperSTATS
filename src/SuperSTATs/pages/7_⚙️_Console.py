import SuperSTATs.load as load
import streamlit as st
import pickle
import json


def main():
    load.app_init()

    presets_path = "src\\pickles\\presets.pickle"
    colors_path = "src\\pickles\\colors.pickle"

    import SuperSTATs.styles as style

    st.markdown(style.shimmer("#b9b9b9"), unsafe_allow_html=True)
    st.markdown("<div class='shimmer'>⚙️ Console ⚙️</div>", unsafe_allow_html=True)

    st.title("")

    st.button("Update Page", type="primary", use_container_width=True)
    st.divider()

    with st.expander("Config"):
        updated_configs = {}

        columns = st.columns(4)

        for i, (config, status) in enumerate(st.session_state.console.items()):
            updated_configs[config] = columns[i % 4].toggle(
                config.title().replace("_", " "), status
            )

        settings_raw = [
            f"{key}={str(value).lower()}" for key, value in updated_configs.items()
        ]

        st.divider()

        if st.button("Update Configs", type="primary", use_container_width=True):
            st.session_state.configs["Console"] = settings_raw
            st.session_state.console = updated_configs

            with open("src\\pickles\\configs.pickle", "wb") as f:
                pickle.dump(st.session_state.configs, f, pickle.HIGHEST_PROTOCOL)

            st.toast("Successfully updated configs! Please refresh...", icon="✅")

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
            st.error(f"⚠️ Not enough scouters! ({scout_amount}/6)")
            scout_list.extend([f"N/A {i}" for i in range(6 - scout_amount)])

        st.divider()

        if st.button("Set Scouters", type="primary", use_container_width=True):
            st.session_state.assigned = scout_list

            with open("src\\pickles\\scouts.pickle", "wb") as f:
                pickle.dump([scouts, scout_list], f, pickle.HIGHEST_PROTOCOL)

            st.toast("Successfully set scouters! Please refresh...", icon="✅")

    with st.expander("Presets"):
        uploaded_file = st.file_uploader("Override Presets:", ".json")

        if uploaded_file is not None:
            st.divider()

            if st.button("Set Presets", type="primary", use_container_width=True):
                bytes_data = uploaded_file.getvalue()
                bytes_formatted = bytes_data.decode("utf-8")
                data = json.loads(bytes_formatted)

                st.session_state.presets = data
                with open(presets_path, "wb") as f:
                    pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

                st.toast("Successfully updated presets! Please refresh...", icon="✅")

        with open(presets_path, "rb") as f:
            presets = pickle.load(f)

        has_presets = len(presets) != 0

        if has_presets:
            st.download_button(
                f"Download Presets",
                json.dumps(presets).encode("utf-8"),
                "presets.json",
                type="primary",
                use_container_width=True,
            )

        if has_presets:
            delete_all = False
            if st.checkbox("Delete All", False):
                delete_all = True

        try:
            with open(presets_path, "rb") as f:
                presets = pickle.load(f)

            deleted_presets = []

            for name, value in presets.items():
                if st.checkbox(name, delete_all, help=str(value)):
                    deleted_presets.append(name)

            if has_presets:
                st.divider()

                if st.button(
                    "Delete Selected", type="primary", use_container_width=True
                ):
                    for preset in deleted_presets:
                        presets.pop(preset)

                    with open(presets_path, "wb") as f:
                        pickle.dump(presets, f, pickle.HIGHEST_PROTOCOL)

                    st.toast(
                        "Successfully deleted presets! Please refresh...", icon="🗑️"
                    )

            else:
                st.error("⚠️ No Presets Found")

        except:
            st.error("⚠️ No Presets Found")

    with st.expander("Colors"):
        uploaded_file = st.file_uploader("Upload Team Colors:", ".json")

        if uploaded_file is not None:
            st.divider()

            if st.button("Set Colors", type="primary", use_container_width=True):
                bytes_data = uploaded_file.getvalue()
                bytes_formatted = bytes_data.decode("utf-8")
                data = json.loads(bytes_formatted)

                with open(colors_path, "wb") as f:
                    pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

                st.session_state.team_colors = data
                load.get_team_colors.clear()

                st.toast("Successfully updated colors! Please refresh...", icon="✅")

        try:
            with open(colors_path, "rb") as f:
                colors = pickle.load(f)

            st.download_button(
                f"Download colors",
                json.dumps(colors).encode("utf-8"),
                "colors.json",
                type="primary",
                use_container_width=True,
            )
        except:
            pass


if __name__ == "__main__":
    main()
