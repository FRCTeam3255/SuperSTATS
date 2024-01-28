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

    with st.expander("Set Presets"):
        uploaded_file = st.file_uploader("Override Presets:")

        if uploaded_file is not None:
            if st.button("Set Presets", use_container_width=True):
                bytes_data = uploaded_file.getvalue()
                bytes_formatted = bytes_data.decode("utf-8")
                data = json.loads(bytes_formatted)

                with open(presets_path, "wb") as f:
                    pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
                st.success("Successfully Updated Presets!")

        st.markdown("""---""")

        with open(presets_path, "rb") as f:
            presets = pickle.load(f)

        st.download_button(
            "Download Presets",
            json.dumps(presets).encode("utf-8"),
            "presets.json",
            use_container_width=True,
        )

    with st.expander("Delete Presets"):
        try:
            with open(presets_path, "rb") as f:
                presets = pickle.load(f)

            deleted_presets = []
            for name, value in presets.items():
                if st.checkbox(name, False, help=str(value)):
                    deleted_presets.append(name)

            if presets != {}:
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

    st.markdown("""---""")

    with st.expander("Scouts"):
        columns = st.columns(2)

        columns[0].subheader("All Scouts", False)
        columns[0].write(st.session_state.scouts)

        columns[1].subheader("Assigned Scouts", False)
        columns[1].write(st.session_state.assigned)


if __name__ == "__main__":
    main()
