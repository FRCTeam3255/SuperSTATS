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

    col1, col2 = st.columns(2)

    groupFilters = col2.checkbox("Group Filters", True)

    if groupFilters:
        agg_type = col1.selectbox("Aggregation Type", ("Mean", "Median", "Sum")).lower()
    else:
        agg_type = col1.selectbox(
            "Aggregation Type", ("Mean", "Median", "Sum", "Count")
        ).lower()

    if groupFilters:
        filter_cols = ["Autonomous", "Teleop", "Endgame", "Info"]
    else:
        filter_cols = [
            col
            for col in df.columns
            if col.startswith(tuple(["AUTO", "TELE", "END", "INFO"]))
        ]

    hide_picked = col2.checkbox("Hide Picked Teams", False)

    wide_chart = st.checkbox("Wide Mode", False)
    selected_filters = st.multiselect("Filters", filter_cols, default=filter_cols)

    if selected_filters:
        st.altair_chart(
            build.custom_bar_chart(
                build.config_chart(df, selected_filters, agg_type, hide_picked),
                wide_chart,
                1500,
            )
        )
    else:
        st.error("Please select at least one filter")


if __name__ == "__main__":
    main()
