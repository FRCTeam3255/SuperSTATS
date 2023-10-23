import SuperSTATs.loader as load
import streamlit as st
import json, os

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
        pass_input = display.text_input("Password", type="password")

        if pass_input == password:
            st.session_state.signed_in = True

    if st.session_state.signed_in:
        display.button("Update Page", type="primary", use_container_width=True)

        # presets_folder = "src\\SuperSTATs\\presets"

        # presets = [
        #     file.split(".")[0]
        #     for file in os.listdir(presets_folder)
        #     if os.path.isfile(os.path.join(presets_folder, file))
        # ]

        # preset_choice = st.selectbox("Preset Choice:", ["None"] + presets)
        # if preset_choice == "None":
        #     pass
        # else:
        #     with open(f"{presets_folder}\\{preset_choice}.json", "r") as json_file:
        #         st.write(json.load(json_file))
        #     if st.button("Delete Preset"):
        #         os.remove(f"{presets_folder}\\{preset_choice}.json")
        #         st.warning("Please Reload Page")

    if "presets" not in st.session_state:
        st.session_state.presets = {}

    uploaded_file = st.file_uploader("Upload Preset")
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        bytes_formatted = bytes_data.decode("utf-8")

        json_data = json.loads(bytes_formatted)
        # st.write(json_data)

    if st.button("Upload Preset"):
        st.session_state.presets[(json_data["preset_name"]).split(".")[0]] = json_data

    st.write(st.session_state.presets)

    preset_choice = st.selectbox(
        "Preset Choice:", ["None"] + list(st.session_state.presets.keys())
    )

    if preset_choice != "None":
        st.write("Selected Preset Value:")
        st.write(st.session_state.presets[preset_choice])

    # json_data = json.dumps(json_data)
    # json_encoded = json_data.encode("utf-8")
    # st.download_button(
    #     "Download Data", json_encoded, file_name=f"preset_{uploaded_file.name}"
    # )


if __name__ == "__main__":
    main()
