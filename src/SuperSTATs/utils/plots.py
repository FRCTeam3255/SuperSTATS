import plotly.express as px
import streamlit as st
from SuperSTATs.utils import constants


def hbar(df, show_y_labels=True):
    fig = px.bar(df, orientation="h")

    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True

    chart_height = max(len(df) * constants.PIXEL_PER_TEAM, constants.MIN_HEIGHT)

    fig.update_traces(
        hovertemplate=None,
    )
    fig.update_yaxes(showticklabels=show_y_labels)
    fig.update_layout(
        hovermode="y unified",
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
    )
    st.plotly_chart(fig, height=chart_height)
