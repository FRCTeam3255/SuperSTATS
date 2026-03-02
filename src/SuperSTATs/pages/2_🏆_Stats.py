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

# ==== CHART 2: RANKINGS VS POINTS ====
fig = px.bar(
    meanpoints.reset_index(),
    x=gsheets.PHASES,
    y="team_num_ranks",
    orientation="h",
)

fig.layout.xaxis.fixedrange = True
fig.layout.yaxis.fixedrange = True

num_teams = meanpoints.index.nunique()
chart_height = num_teams * 30

fig.update_traces(
    hovertemplate=None,
)
fig.update_layout(
    hovermode="y unified",
    height=chart_height,
    legend=dict(
        orientation="h",
        yanchor="top",
        y=1.02,
        xanchor="left",
        title=None,
        x=0,
    ),
)
st.plotly_chart(fig)
