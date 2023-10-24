import SuperSTATs.build_chart as build
import SuperSTATs.loader as load
import streamlit as st
import pickle

st.set_page_config(
    page_title="[STATS] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
    layout="wide",
    menu_items={"About": "Errorz Was Here 🐢"},
)

df = load.download_sheets_raw(st.secrets["GID_RAW"]).dropna(subset="Timestamp")
df_picked = load.download_sheets_raw(st.secrets["GID_PICKED"])
df = df.merge(df_picked, on="Team", how="left")

sections = load.get_match_sections(df)


def sort_cols(starts_with):
    filter_cols = []
    cols = [col for col in df.columns if col.startswith(starts_with)]
    filter_cols.extend(cols)
    return filter_cols


def main():
    load.init_page()

    st.markdown(
        "<h1 style='text-align: center;'>🏆 NURD Stats 🏆</h1>", unsafe_allow_html=True
    )
    st.title("")

    if st.button("Update Page", type="primary", use_container_width=True):
        try:
            with open("presets.pickle", "rb") as f:
                st.session_state.presets = pickle.load(f)
        except:
            pass

    st.markdown("""---""")

    preset_choice = st.selectbox(
        "Preset Choice:", ["None"] + list(st.session_state.presets.keys())
    )

    if preset_choice != "None":
        st.header(f"Selected Preset: {preset_choice}")

    def check_preset(variable):
        data = st.session_state.presets[preset_choice]
        return data[variable]

    col_1, col_2, col_3 = st.columns(3)

    if preset_choice == "None":
        group_filters = col_1.checkbox("Group Filters", True)
        hide_picked = col_2.checkbox("Hide Picked Teams", False)
        hide_team_nums = col_3.checkbox("Hide Team Numbers", False)
    else:
        group_filters = check_preset("group_filters")
        hide_picked = check_preset("hide_picked")
        hide_team_nums = check_preset("hide_team_nums")

    col_1, col_2 = st.columns(2)

    if group_filters:
        if preset_choice == "None":
            agg_type = col_1.selectbox(
                "Aggregation Type:", ("Mean", "Median", "Sum")
            ).lower()
        else:
            agg_type = check_preset("agg_type")

        filter_cols = sections
    else:
        if preset_choice == "None":
            agg_type = col_1.selectbox(
                "Aggregation Type:", ("Mean", "Median", "Sum", "Count")
            ).lower()
        else:
            agg_type = check_preset("agg_type")

        filter_cols = [col for col in df.columns if col.startswith(tuple(sections))]

        # TODO: Make the sorting types in numerical order for sorting
        # sort_type = st.radio("Sorting Type:", ["NONE"] + sections, horizontal=True)
        if preset_choice == "None":
            sort_type = st.radio(
                "Sorting Type:", ["NONE", "AUTO", "TELE", "END"], horizontal=True
            )

            if sort_type == "NONE":
                filter_cols = [
                    col for col in df.columns if col.startswith(tuple(sections))
                ]
            else:
                filter_cols = sort_cols(sort_type)

    if preset_choice == "None":
        match_filters = col_2.multiselect(
            "Match Types:", ["Prac", "Quals", "Playoffs"], default=["Quals", "Playoffs"]
        )
    else:
        match_filters = check_preset("match_filters")

    if match_filters:
        pass
    else:
        match_filters = ["Prac", "Quals", "Playoffs"]

    if preset_choice == "None":
        selected_filters = st.multiselect("Filters:", filter_cols, default=filter_cols)
    else:
        selected_filters = check_preset("selected_filters")

    if selected_filters:
        st.altair_chart(
            build.custom_bar_chart(
                build.config_chart(
                    df, selected_filters, agg_type, hide_picked, match_filters
                ),
                hide_team_nums,
            ),
            use_container_width=True,
        )
    else:
        st.error("Please select at least one filter")

    preset_name = st.text_input("New Preset Name:")

    if preset_name:
        if st.button("Add Preset", use_container_width=True):
            data = {
                "group_filters": group_filters,
                "selected_filters": selected_filters,
                "agg_type": agg_type,
                "match_filters": match_filters,
                "hide_picked": hide_picked,
                "hide_team_nums": hide_team_nums,
            }

            presets = st.session_state.presets
            presets[preset_name] = data
            with open("presets.pickle", "wb") as f:
                pickle.dump(presets, f, pickle.HIGHEST_PROTOCOL)
            st.success("Successfully Added Preset!")


if __name__ == "__main__":
    main()
