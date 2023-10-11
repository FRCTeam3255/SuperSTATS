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

    st.header("NURD Stats")

    hidePicked = st.checkbox("Hide Picked Teams", False)

    col1, col2 = st.columns(2)
    groupFilters = col2.checkbox("Group Filters", True)

    if groupFilters:
        aggType = col1.selectbox("Aggregation Type", ("Mean", "Median", "Sum")).lower()
    else:
        aggType = col1.selectbox(
            "Aggregation Type", ("Mean", "Median", "Sum", "Count")
        ).lower()

    if groupFilters:
        filter_cols = ["Autonomous", "Teleop", "Endgame", "Info"]
    else:
        filter_cols = [
            col
            for col in df.columns
            if col.startswith(tuple(["AUTON", "TELEOP", "END", "INFO"]))
        ]

    selected_filters = st.multiselect("Filters", filter_cols, default=filter_cols)

    wide_chart = col2.checkbox("Wide Mode", False)
    if selected_filters:
        st.altair_chart(
            build.custom_bar_chart(
                build.config_chart(df, selected_filters, aggType, hidePicked),
                wide_chart,
                1500,
            )
        )
    else:
        st.error("Please select at least one filter")


if __name__ == "__main__":
    main()
