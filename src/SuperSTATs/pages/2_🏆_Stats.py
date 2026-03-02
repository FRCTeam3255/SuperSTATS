import pandas as pd

from SuperSTATs.utils import gsheets, tba
import streamlit as st
import altair as alt

points = gsheets.get_stats_inputs(as_points=True)
r = tba.get_rankings()

points
r

meanpoints = points[gsheets.PHASES].T.groupby(level=0).sum().T.groupby("Team").mean()
meanpoints


# ============= CHART =============
chart_data = meanpoints.reset_index().melt(
    id_vars="Team", var_name="Phase", value_name="Points"
)
# chart_data
# chart = (
#     alt.Chart(meanpoints)
#     .mark_bar()
#     .encode(
#         y=alt.Y("Team:N", sort="-x"),
#         x=alt.X("Points:Q"),
#         color=alt.Color("Phase:N"),
#         tooltip=["Team", "Phase", "Points"],
#     )
#     .properties(width="container", height=400)
#     .configure_mark(
#         # Make touch targets bigger
#         size=60
#     )
#     .configure_axis(
#         labelFontSize=14,  # Bigger labels for touch
#         titleFontSize=16,
#     )
# )

# st.altair_chart(chart, use_container_width=True)


# # Prepare data for stacked bar chart
chart_data = meanpoints.reset_index().melt(
    id_vars="Team", var_name="Phase", value_name="Points"
)
# Create horizontal stacked bar chart
chart = (
    alt.Chart(chart_data)
    .mark_bar()
    .encode(
        y=alt.Y("Team:N", sort="-x"),
        x=alt.X("Points:Q"),
        color=alt.Color("Phase:N"),
        tooltip=["Team", "Phase", "Points"],
    )
    .configure_mark(
        # Make touch targets bigger
        size=60
    )
    .configure_axis(
        labelFontSize=14,  # Bigger labels for touch
        titleFontSize=16,
    )
)

st.altair_chart(chart, use_container_width=True)


# ==== CHART 2: RANKINGS VS POINTS ====
import plotly.express as px

chart_df = meanpoints.reset_index().melt(
    id_vars="Team", var_name="Phase", value_name="Points"
)

# Sort teams by total points (descending)
team_order = (
    chart_df.groupby("Team")["Points"].sum().sort_values(ascending=False).index.tolist()
)

fig = px.bar(
    chart_df,
    x="Points",
    y="Team",
    color="Phase",
    title="Points by Phase",
    orientation="h",
    category_orders={"Team": team_order},
    hover_data={
        "Points": ":.2f",
        "Team": False,
        "Phase": True,
    },
)
fig.update_yaxes(type="category")
fig.layout.xaxis.fixedrange = True
fig.layout.yaxis.fixedrange = True

fig.update_layout(hovermode="y unified")
st.plotly_chart(
    fig,
    height="stretch",
    width="stretch",
)
