import SuperSTATs.build_chart as build
import SuperSTATs.loader as load
import streamlit as st

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

    col1, col2, col3 = st.columns(3)

    group_filters = col1.checkbox("Group Filters", True)
    hide_picked = col2.checkbox("Hide Picked Teams", False)
    hide_teams = col3.checkbox("Hide Team Numbers", False)

    col1, col2 = st.columns(2)

    if group_filters:
        agg_type = col1.selectbox(
            "Aggregation Type:", ("Mean", "Median", "Sum")
        ).lower()
        filter_cols = sections
    else:
        agg_type = col1.selectbox(
            "Aggregation Type:", ("Mean", "Median", "Sum", "Count")
        ).lower()

        filter_cols = [col for col in df.columns if col.startswith(tuple(sections))]

        # TODO: Make the sorting types in numerical order for sorting
        # sort_type = st.radio("Sorting Type:", ["NONE"] + sections, horizontal=True)
        sort_type = st.radio(
            "Sorting Type:", ["NONE", "AUTO", "TELE", "END"], horizontal=True
        )

        if sort_type == "NONE":
            filter_cols = [col for col in df.columns if col.startswith(tuple(sections))]
        else:
            filter_cols = sort_cols(sort_type)

    match_filters = col2.multiselect(
        "Match Types:", ["Prac", "Quals", "Playoffs"], default=["Quals", "Playoffs"]
    )

    if match_filters:
        pass
    else:
        match_filters = ["Prac", "Quals", "Playoffs"]

    selected_filters = st.multiselect("Filters:", filter_cols, default=filter_cols)

    if selected_filters:
        st.altair_chart(
            build.custom_bar_chart(
                build.config_chart(
                    df, selected_filters, agg_type, hide_picked, match_filters
                ),
                hide_teams,
            ),
            use_container_width=True,
        )
    else:
        st.error("Please select at least one filter")

    st.button("Reload Chart", use_container_width=True)


if __name__ == "__main__":
    main()
