import SuperSTATs.Main as stats
import streamlit as st
import altair as alt
import pandas as pd
import tbapy

st.set_page_config(
    page_title="[STATS_ALT] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
)


def add_cols(org_df, reg, filter):
    org_df[filter] = org_df.filter(regex=reg).sum(axis=1)
    return org_df[filter]


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
        .properties(width=700, height=1500)
    )
    return chart


def config_chart(column, agg):
    df = stats.download_sheets_raw()

    df_split = []
    for list in df.columns.str.split("_"):
        if len(list) > 1:
            df_split.append(list)

    points = {}
    for value in df_split:
        points.update({f"{value[0]}_{value[1]}": int(value[2])})

    for col, point in points.items():
        df[f"{col}_{point}"] *= point

    df["Autonomous"] = add_cols(
        df,
        r"AUTON_",
        "autonomous",
    )

    df["Teleop"] = add_cols(
        df,
        r"TELEOP_",
        "teleop",
    )

    df["Endgame"] = add_cols(
        df,
        r"END_",
        "endgame",
    )

    calc_df = df.groupby("Team")[column].agg(agg)
    calc_df["rank"] = calc_df.sum(axis=1).rank(ascending=False).astype(int)
    calc_df.reset_index(inplace=True)
    calc_row = pd.melt(
        calc_df,
        id_vars=["Team", "rank"],
        value_vars=column,
        var_name="variable",
        value_name="value",
    )
    return calc_row


def main():
    stats.set_font()

    st.header("NURD Stats")

    aggType = st.selectbox("Aggregation Type", ("Mean", "Median", "Sum")).lower()
    groupFilters = st.checkbox("Group Filters", True)

    if groupFilters:
        filter_cols = ["Autonomous", "Teleop", "Endgame"]
    else:
        filter_cols = [
            # "INFO_NOTES",
            # "INFO_DEFENSE",
            # "INFO_PENALTY",
            # "INFO_BRICK",
            # "AUTON_MOBILITY",
            # "AUTON_BOTTOM",
            # "AUTON_MIDDLE",
            # "AUTON_TOP",
            # "AUTON_DOCKED NOT ENGAGED",
            # "AUTON_DOCKED AND ENGAGED",
            "TELEOP_BOTTOM_2",
            "TELEOP_MIDDLE_3",
            "TELEOP_TOP_5",
            # "END_PARKED",
            # "END_DOCKED NOT ENGAGED",
            # "END_DOCKED AND ENGAGED",
        ]

    selected_filters = st.multiselect("Filters", filter_cols, default=filter_cols)

    if selected_filters:
        st.altair_chart(custom_bar_chart(config_chart(selected_filters, aggType)))
    else:
        st.error("Please select at least one filter")


if __name__ == "__main__":
    main()
