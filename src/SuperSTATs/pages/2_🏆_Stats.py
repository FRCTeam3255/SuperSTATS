import pandas as pd

import streamlit as st
from SuperSTATs.utils import gsheets, tba
from pathlib import Path

from matplotlib import colormaps

GREENS = colormaps["Greens"]
REDS = colormaps["Reds"]

page_name = Path(__file__).stem.split("_", 1)[1].replace("_", " ")
st.title(page_name)
if st.button("Update Page", type="primary", width="stretch"):
    gsheets.clear_cache()
    st.rerun()
st.divider()
print(f"{page_name} loaded:")


def shade_column(column: pd.Series) -> list[str]:
    """Green gradient for positives and red gradient for negatives, per column."""
    max_positive = column.clip(lower=0).max()
    max_negative = (-column).clip(lower=0).max()
    styles = []
    for value in column:
        if value > 0 and max_positive > 0:
            intensity, cmap = value / max_positive, GREENS
        elif value < 0 and max_negative > 0:
            intensity, cmap = -value / max_negative, REDS
        else:
            styles.append("")
            continue
        # Start past the near-white end of the colormap so small values stay visible
        red, green, blue, _ = cmap(0.1 + 0.8 * intensity)
        text = "white" if intensity > 0.6 else "black"
        styles.append(
            f"background-color: rgb({red * 255:.0f}, {green * 255:.0f}, {blue * 255:.0f}); "
            f"color: {text}"
        )
    return styles


# === Page Specific Data ===
sn_avail = gsheets.get_available()


# ==== Settings UI =====
settings_and_filter_expander = st.expander("Settings & Filters", expanded=False)
with settings_and_filter_expander:
    col1, col2, col3, col4 = st.columns(4)
    hide_identifiers = col1.toggle("Hide Identifiers", False)
    chart_type = col2.radio("View by:", gsheets.COLUMN_LEVELS, horizontal=True, index=1)
    as_points = (
        col3.radio("View as:", ["Points", "Counts"], horizontal=True) == "Points"
    )
    agg_type = col4.selectbox(
        "Aggregation Type:",
        ["min", "mean", "50%", "75%", "90%", "95%", "99%", "max"],
        format_func=str.capitalize,
        index=1,
    )

# ==== DATA Download ====
raw_sn_df = gsheets.get_stats_inputs(as_points=as_points)
tba_rank = tba.get_rankings()

# ==== Filters UI ====
with settings_and_filter_expander:
    selected_phases = st.multiselect("Phase:", gsheets.PHASES, default=gsheets.PHASES)
    metrics = raw_sn_df[selected_phases].columns.get_level_values("Metric").unique()
    selected_metrics = st.multiselect("Metric:", metrics, default=metrics)
    selected_phases_and_metrics = pd.IndexSlice[selected_phases, selected_metrics]

# ==== Data Processing ====
sn_df = raw_sn_df.loc[:, selected_phases_and_metrics]
agg_data = gsheets.aggregate_team_performance(
    df=sn_df,
    level=chart_type,
    agg_type=agg_type,
)

# ==== Outputs ====
# Best team first; the team column stays pinned while the rest scrolls sideways
metric_columns = list(agg_data.columns.drop("sn_rank"))
display_data = (
    agg_data.rename(columns={"sn_rank": "Our Rank"})
    .join(tba_rank["rank"].rename("TBA Rank"), how="left")
    .join(sn_avail["emoji"].rename("Avail"), how="left")
    .rename_axis("Team")
)
display_data["Avail"] = display_data["Avail"].fillna("🟢")
display_data["TBA Rank"] = display_data["TBA Rank"].astype("Int64")
display_data.insert(0, "Total", display_data[metric_columns].sum(axis=1))
display_data = display_data[
    ["Avail", "Our Rank", "TBA Rank", "Total"] + metric_columns
].sort_values("Our Rank")

shaded_columns = ["Total"] + metric_columns
styled_data = (
    display_data.style.apply(shade_column, axis=0, subset=shaded_columns)
    .format("{:.1f}", subset=shaded_columns)
    .format("{:d}", subset=["Our Rank", "TBA Rank"], na_rep="–")
    .set_properties(subset=["Total"], **{"font-weight": "bold"})
)
st.caption(
    "Total is the sum of the metrics shown. Green is positive and red is "
    "negative; darker means larger within each column. Swipe to see more metrics."
)
identifier_columns = ["Avail", "TBA Rank"]
visible_columns = [
    col
    for col in display_data.columns
    if not (hide_identifiers and col in identifier_columns)
]
st.dataframe(
    styled_data,
    hide_index=hide_identifiers,
    column_order=visible_columns,
    column_config={
        "_index": st.column_config.Column("Team", width=60),
        "Avail": st.column_config.Column("", width=40, alignment="center"),
        "Our Rank": st.column_config.Column("SN", width=40, alignment="center"),
        "TBA Rank": st.column_config.Column("TBA", width=48, alignment="center"),
    },
    width="stretch",
    height="content",
)
