import SuperSTATs.build_chart as build
import SuperSTATs.Main as stats
import streamlit as st

st.set_page_config(
    page_title="[STATS] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
)

df = stats.download_sheets_raw(st.secrets["GID_RAW"]).dropna(subset="Timestamp")
df_picked = stats.download_sheets_raw(st.secrets["GID_PICKED"])
df = df.merge(df_picked, on="Team", how="left")


def main():
    stats.set_font()

    st.header("🏆 NURD Stats 🏆")

    col1, col2, col3, col4 = st.columns(4)

    groupFilters = col1.checkbox("Group Filters", True)
    hide_teams = col3.checkbox("Hide Teams", False)
    hide_picked = col2.checkbox("Hide Picked", False)
    wide_chart = col4.checkbox("Wide Mode", False)

    if groupFilters:
        agg_type = st.selectbox("Aggregation Type:", ("Mean", "Median", "Sum")).lower()
        filter_cols = ["Autonomous", "Teleop", "Endgame", "Info"]
    else:
        agg_type = st.selectbox(
            "Aggregation Type:", ("Mean", "Median", "Sum", "Count")
        ).lower()
        filter_cols = [
            col
            for col in df.columns
            if col.startswith(tuple(["AUTO", "TELE", "END", "INFO"]))
        ]

    selected_filters = st.multiselect("Filters:", filter_cols, default=filter_cols)

    if selected_filters:
        st.altair_chart(
            build.custom_bar_chart(
                build.config_chart(df, selected_filters, agg_type, hide_picked),
                hide_teams,
                wide_chart,
                1500,
            )
        )
    else:
        st.error("Please select at least one filter")


if __name__ == "__main__":
    main()
