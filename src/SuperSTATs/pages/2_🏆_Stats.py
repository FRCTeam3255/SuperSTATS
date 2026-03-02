from SuperSTATs.utils import gsheets, tba, constants
import streamlit as st
import plotly.express as px

points = gsheets.get_stats_inputs(as_points=True)
r = tba.get_rankings()

df = (
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
df = df.join(r, how="left")
df["team_num_ranks"] = (
    df.index.astype(str)
    + " | T"
    + df["rank"].astype(str).str.zfill(2)
    + " | S"
    + df["sn_rank"].astype(str).str.zfill(2)
)
df = df.set_index("team_num_ranks").sort_values("sn_rank", ascending=False)
df = df[gsheets.PHASES]
df
# ==== CHART 2: RANKINGS VS POINTS ====
fig = px.bar(df, orientation="h")

fig.layout.xaxis.fixedrange = True
fig.layout.yaxis.fixedrange = True

chart_height = len(df) * constants.PIXEL_PER_TEAM

fig.update_traces(
    hovertemplate=None,
)
fig.update_layout(
    hovermode="y unified",
    height=chart_height,
    legend=dict(
        orientation="h",
        yanchor="top",
        y=1.025,
        xanchor="left",
        title=None,
        x=0,
    ),
    xaxis_title=None,
    yaxis_title=None,
)
st.plotly_chart(fig)
