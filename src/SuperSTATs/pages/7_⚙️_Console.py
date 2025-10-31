import SuperSTATs.analytics as analytics
import SuperSTATs.load as load
import streamlit as st
import pickle
import json


def main():
    load.app_init()
    analytics.collect_analytics("page_change", "console")

    presets_path = "src\\pickles\\presets.pickle"
    colors_path = "src\\pickles\\colors.pickle"

    st.title("⚙️ Console ⚙️")

    st.button(
        "Update Page",
        type="primary",
        use_container_width=True,
        key=f"update_page",
        on_click=analytics.button_press,
        args=("update_page",),
    )
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

        st.divider()

        if st.button(
            "Update Configs",
            type="primary",
            use_container_width=True,
            key=f"update_configs",
            on_click=analytics.button_press,
            args=("update_configs",),
        ):
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
            st.error(f"⚠️ Not enough scouters ({scout_amount}/6)")
            scout_list.extend([f"N/A {i}" for i in range(6 - scout_amount)])

        st.divider()

        if st.button(
            "Set Scouters",
            type="primary",
            use_container_width=True,
            key=f"set_scouters",
            on_click=analytics.button_press,
            args=("set_scouters",),
        ):
            st.session_state.assigned = scout_list

            with open("src\\pickles\\scouts.pickle", "wb") as f:
                pickle.dump([scouts, scout_list], f, pickle.HIGHEST_PROTOCOL)

            st.toast("Successfully set scouters! Please refresh...", icon="✅")

    with st.expander("Presets"):
        uploaded_file = st.file_uploader("Override Presets:", ".json")

        if uploaded_file is not None:
            st.divider()

            if st.button(
                "Set Presets",
                type="primary",
                use_container_width=True,
                key=f"set_presets",
                on_click=analytics.button_press,
                args=("set_presets",),
            ):
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
                    "Delete Selected",
                    type="primary",
                    use_container_width=True,
                    key=f"delete_selected",
                    on_click=analytics.button_press,
                    args=("delete_selected",),
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

            if st.button(
                "Set Colors",
                type="primary",
                use_container_width=True,
                key=f"set_colors",
                on_click=analytics.button_press,
                args=("set_colors",),
            ):
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

    if st.session_state.console["collect_analytics"]:
        with st.expander("Analytics"):
            columns = st.columns(4)

            updated_analytics = {}

            for i, analytic in enumerate(st.session_state.analytics_settings):
                updated_analytics[analytic] = columns[i % 4].toggle(
                    analytic.title().replace("_", " "),
                    st.session_state.analytics[analytic],
                )

            if st.button(
                "Update Analytics",
                type="primary",
                use_container_width=True,
                key=f"update_analytics",
                on_click=analytics.button_press,
                args=("update_analytics",),
            ):
                st.session_state.analytics = updated_analytics


if __name__ == "__main__":
    main()
