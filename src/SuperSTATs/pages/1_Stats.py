import SuperSTATs.Main as stats
import streamlit as st
import altair as alt
import pandas as pd
import tbapy

st.set_page_config(
    page_title="[RANKS] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
)


def add_cols(org_df, reg, filter):
    org_df = stats.download_sheets_raw()
    org_df = org_df.drop(columns=org_df.filter(regex=".1").columns)
    org_df[filter] = org_df.filter(regex=reg).sum(axis=1)
    return org_df[filter]


filter_cols = [
    "autonomous",
    "teleop",
    "endgame"
    # "Auton Mobility",
    # "Auton Top",
    # "Auton Middle",
    # "Auton Bottom",
    # "Auton Docked NOT engaged",
    # "Auton Docked ENGAGED",
    # "Top Row",
    # "Middle Row",
    # "Bottom Row",
    # "Parked",
    # "Docked NOT engaged",
    # "Docked ENGAGED",
]


def custom_bar_chart(data):
    chart = (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X("value:Q", title=" "),
            y=alt.Y(
                "Team:N",
                sort=alt.EncodingSortField(field="rank", order="ascending"),
                title="",
            ),
            color=alt.Color("variable:N", title=" "),
            tooltip=["Team:N", "value:Q", "variable:N"],
        )
        .properties(height=1500)
    )
    return chart


def config_chart(column):
    df = stats.download_sheets_raw()

    df["autonomous"] = add_cols(df, "Auton", "autonomous")
    df["teleop"] = add_cols(df, "Row", "teleop")
    df["endgame"] = add_cols(df, r"(^Docked|^Parked)", "endgame")

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

    st.header("NURD Stats")

    # with st.expander("SN Stats"):
    selected_filters = st.multiselect("Filters:", filter_cols, default=filter_cols)

    if selected_filters:
        st.altair_chart(custom_bar_chart(config_chart(selected_filters)))
    else:
        st.error("Please select at least one filter")


if __name__ == "__main__":
    main()
