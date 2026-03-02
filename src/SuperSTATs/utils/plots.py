import plotly.express as px
import streamlit as st
from SuperSTATs.utils import constants


def hbar(df):
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
