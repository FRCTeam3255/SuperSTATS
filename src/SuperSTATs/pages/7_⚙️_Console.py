import SuperSTATs.loader as load
import streamlit as st
import pickle, json

# [STATS INPUT]
# Stat Taker List

st.set_page_config(
    page_title="[CONSOLE] SN Stats",
    page_icon="⚙️",
    initial_sidebar_state="expanded",
    layout="wide",
)


def main():
    load.init_page()

    display = st.empty()

    password = st.secrets["ADMIN_PASSWORD"]

    if not st.session_state.admin_signed_in:
        pass_input = display.text_input("Admin Password:", type="password")

        if pass_input == password:
            st.session_state.admin_signed_in = True

    if st.session_state.admin_signed_in:
        display.button("Update Page", type="primary", use_container_width=True)

        st.write("""---""")

        with st.expander("Set Presets"):
            uploaded_file = st.file_uploader("Override Presets:")

            if uploaded_file is not None:
                if st.button("Set Presets", use_container_width=True):
                    bytes_data = uploaded_file.getvalue()
                    bytes_formatted = bytes_data.decode("utf-8")
                    data = json.loads(bytes_formatted)

                    with open("presets.pickle", "wb") as f:
                        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
                    st.success("Successfully Updated Presets!")

            st.markdown("""---""")

            st.download_button(
                "Download Presets",
                json.dumps(st.session_state.presets).encode("utf-8"),
                "Presets.json",
                use_container_width=True,
            )

        with st.expander("Delete Presets"):
            try:
                with open("presets.pickle", "rb") as f:
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

                        with open("presets.pickle", "wb") as f:
                            pickle.dump(presets, f, pickle.HIGHEST_PROTOCOL)
                        st.success("Successfully Deleted Presets!")

                else:
                    st.error("No Presets Found")

            except:
                st.error("No Presets Found")


if __name__ == "__main__":
    main()
