import pandas as pd

from SuperSTATs.utils import gsheets, tba
import streamlit as st
import plotly.express as px

points = gsheets.get_stats_inputs(as_points=True)
r = tba.get_rankings()


meanpoints = (
    points[gsheets.PHASES]
    .T.groupby(level=0)
    .sum()
    .T.groupby("Team")
    .mean()
    .assign(
        sn_rank=lambda x: (
            x[gsheets.PHASES].sum(axis=1).rank(ascending=False).astype(int)
        )
    )
)
meanpoints = meanpoints.join(r, how="left")
meanpoints["team_num_ranks"] = (
    meanpoints.index.astype(str)
    + " | T"
    + meanpoints["rank"].astype(str).str.zfill(2)
    + " | S"
    + meanpoints["sn_rank"].astype(str).str.zfill(2)
)
meanpoints = meanpoints.set_index("team_num_ranks").sort_values(
    "sn_rank", ascending=False
)
meanpoints

# ==== CHART 2: RANKINGS VS POINTS ====

chart_df = (
    meanpoints[gsheets.PHASES]
    .reset_index()
    .melt(id_vars="team_num_ranks", var_name="Phase", value_name="Points")
)

fig = px.bar(
    chart_df,
    x="Points",
    y="team_num_ranks",
    color="Phase",
    title="Points by Phase",
    orientation="h",
    hover_data={
        "Points": ":.2f",
        "team_num_ranks": False,
        "Phase": True,
    },
)
fig.update_yaxes(type="category")
fig.layout.xaxis.fixedrange = True
fig.layout.yaxis.fixedrange = True

num_teams = chart_df["team_num_ranks"].nunique()
chart_height = num_teams * 30

fig.update_layout(hovermode="y unified", height=chart_height)
st.plotly_chart(
    fig,
    use_container_width=True,
)
