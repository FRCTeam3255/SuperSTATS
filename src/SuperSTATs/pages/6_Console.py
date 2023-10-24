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

    if "signed_in" not in st.session_state:
        st.session_state.signed_in = False

    if not st.session_state.signed_in:
        pass_input = display.text_input("Password:", type="password")

        if pass_input == password:
            st.session_state.signed_in = True

    if st.session_state.signed_in:
        display.button("Update Page", type="primary", use_container_width=True)

        uploaded_file = st.file_uploader("Override Presets:")

        if uploaded_file is not None:
            if st.button("Set Presets", use_container_width=True):
                bytes_data = uploaded_file.getvalue()
                bytes_formatted = bytes_data.decode("utf-8")
                data = json.loads(bytes_formatted)

                with open("data.pickle", "wb") as f:
                    pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
                st.success("Successfully Updated Presets!")

        st.download_button(
            "Download Presets",
            json.dumps(st.session_state.presets).encode("utf-8"),
            "Presets.json",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
