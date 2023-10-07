import SuperSTATs.Main as stats
import streamlit as st
import altair as alt
import pandas as pd

st.set_page_config(
    page_title="[RANKS] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
)

auto_cols = [
    "Auton Mobility",
    "Auton Top",
    "Auton Middle",
    "Auton Bottom",
    "Auton Docked NOT engaged",
    "Auton Docked ENGAGED",
]

teleop_cols = [
    "Top Row",
    "Middle Row",
    "Bottom Row",
]

end_game_cols = [
    "Parked",
    "Docked NOT engaged",
    "Docked ENGAGED",
]


def custom_bar_chart(data):
    chart = (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X("value:Q", title="Sum Value"),
            y=alt.Y(
                "Team:N",
                sort=alt.EncodingSortField(field="rank", order="ascending"),
                title="Team Number",
            ),
            color=alt.Color("variable:N", title=" "),
            tooltip=["Team:N", "value:Q", "variable:N"],
        )
        .properties(height=1500)
    )
    return chart


def config_chart(column):
    df = stats.download_sheets_raw("1318549794")
    sum_df = df.groupby("Team")[column].sum()
    sum_df["sum"] = sum_df.sum(axis=1)
    sum_df["rank"] = sum_df["sum"].rank(ascending=False).astype(int)
    sum_df.reset_index(inplace=True)
    row_sum = pd.melt(
        sum_df,
        id_vars=["Team", "rank"],
        value_vars=column,
        var_name="variable",
        value_name="value",
    )
    return row_sum


def main():
    stats.set_font()

    st.header("🏆 Ranks 🏆")

    with st.expander("[ Auto ]"):
        selected_auto_cols = st.multiselect("Filters:", auto_cols, default=auto_cols)

        if selected_auto_cols:
            st.altair_chart(custom_bar_chart(config_chart(selected_auto_cols)))
        else:
            st.error("Please select at least one filter for autonomous")

    with st.expander("[ Teleop ]"):
        selected_teleop_cols = st.multiselect(
            "Filters:", teleop_cols, default=teleop_cols
        )

        if selected_teleop_cols:
            st.altair_chart(custom_bar_chart(config_chart(selected_teleop_cols)))
        else:
            st.error("Please select at least one filter for teleop")

    with st.expander("[ End Game ]"):
        selected_end_game_cols = st.multiselect(
            "Filters:", end_game_cols, default=end_game_cols
        )

        if selected_end_game_cols:
            st.altair_chart(custom_bar_chart(config_chart(selected_end_game_cols)))
        else:
            st.error("Please select at least one filter for end game")


if __name__ == "__main__":
    main()
