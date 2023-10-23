import SuperSTATs.loader as load
import streamlit as st
import json

# [PRESETS]
# Delete
# Rename
# Compare

# [STATS INPUT]
# Stat Taker List

# [SCOUTING]
# Uncollected Teams

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

        with st.expander("View Presets Dict"):
            presets_json = json.dumps(st.session_state.presets)
            presets_bytes = presets_json.encode("utf-8")
            st.download_button(
                "Download Dictionary", presets_bytes, file_name=f"presets.json"
            )

            st.write(st.session_state.presets)

            uploaded_file = st.file_uploader("Override Dictionary")

            if uploaded_file is not None:
                if st.button("Override Presets"):
                    bytes_data = uploaded_file.getvalue()
                    bytes_formatted = bytes_data.decode("utf-8")
                    st.session_state.presets = json.loads(bytes_formatted)
                    st.success("Presets Successfully Overridden")


if __name__ == "__main__":
    main()
