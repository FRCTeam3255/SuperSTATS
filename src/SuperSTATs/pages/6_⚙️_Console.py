import SuperSTATs.load as load
import streamlit as st
import pickle
import json


def main():
    load.app_init()

    presets_path = "src\\pickles\\presets.pickle"

    import SuperSTATs.styles as style

    st.markdown(style.shimmer("#b9b9b9"), unsafe_allow_html=True)
    st.markdown("<div class='shimmer'>⚙️ Console ⚙️</div>", unsafe_allow_html=True)

    st.title("")

    st.button("Update Page", type="primary", use_container_width=True)
    st.markdown("""---""")

    with st.expander("Initialization"):
        if st.button("Clear Team Info Cache", type="primary", use_container_width=True):
            load.get_team_info.clear()

        if st.button("Refresh Team Colors", type="primary", use_container_width=True):
            load.check_team_colors()

    st.markdown("""---""")

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
            st.error(f"Not enough scouters! ({scout_amount}/6)")
            scout_list = scout_list + ["N/A"] * (6 - scout_amount)

        st.markdown("""---""")

        if st.button("Set Scouters", type="primary", use_container_width=True):
            st.session_state.assigned = scout_list

            with open("src\\pickles\\scouts.pickle", "wb") as f:
                pickle.dump([scouts, scout_list], f, pickle.HIGHEST_PROTOCOL)

            st.success("Successfully Set Scouters!")

    st.markdown("""---""")

    with st.expander("Set Presets"):
        uploaded_file = st.file_uploader("Override Presets:")

        if uploaded_file is not None:
            st.markdown("""---""")

            if st.button("Set Presets", use_container_width=True):
                bytes_data = uploaded_file.getvalue()
                bytes_formatted = bytes_data.decode("utf-8")
                data = json.loads(bytes_formatted)

                with open(presets_path, "wb") as f:
                    pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

                st.success("Successfully Updated Presets!")

        with open(presets_path, "rb") as f:
            presets = pickle.load(f)

        has_presets = len(presets) != 0

        if has_presets:
            st.download_button(
                f"Download Presets",
                json.dumps(presets).encode("utf-8"),
                "presets.json",
                use_container_width=True,
            )

        st.markdown("""---""")

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
                st.markdown("""---""")

                if st.button("Delete Selected", use_container_width=True):
                    for preset in deleted_presets:
                        presets.pop(preset)

                    with open(presets_path, "wb") as f:
                        pickle.dump(presets, f, pickle.HIGHEST_PROTOCOL)

                    st.success("Successfully Deleted Presets!")

            else:
                st.error("No Presets Found")

        except:
            st.error("No Presets Found")


if __name__ == "__main__":
    main()
