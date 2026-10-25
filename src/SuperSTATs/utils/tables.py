"""Shared mobile-first team stats table used by the Stats and Preview pages."""
from typing import Literal

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from matplotlib import colormaps

GREENS = colormaps["Greens"]
REDS = colormaps["Reds"]


def format_trend(value: float) -> str:
    if value > 0:
        return f"▲ {value:.1f}"
    if value < 0:
        return f"▼ {-value:.1f}"
    return "–"


def shade_column(column: pd.Series, scale: pd.Series | None = None) -> list[str]:
    """Green gradient for positives and red gradient for negatives, per column.

    `scale` (default: the column itself) sets the range the shading is relative to.
    """
    scale = column if scale is None else scale
    max_positive = scale.clip(lower=0).max()
    max_negative = (-scale).clip(lower=0).max()
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


def _ordered_matches(raw_sn_df: pd.DataFrame, sn_df: pd.DataFrame) -> pd.DataFrame:
    """Per-match rows for the selected metrics, oldest scouting entry first."""
    match_times = pd.to_datetime(raw_sn_df[("METADATA", "Timestamp")], errors="coerce")
    return sn_df.loc[match_times.sort_values(kind="stable").index]


def team_stats_table(
    agg_data: pd.DataFrame,
    raw_sn_df: pd.DataFrame,
    sn_df: pd.DataFrame,
    tba_rank: pd.DataFrame,
    sn_avail: pd.DataFrame,
    chart_type: str,
    trend_matches: int,
    hide_identifiers: bool = False,
    selectable: bool = False,
    groups: dict[int, str] | None = None,
    team_names: pd.Series | None = None,
    key: str | None = None,
    selection_mode: Literal["single-row", "multi-row"] = "single-row",
) -> None:
    """Render the shaded team table for the teams in `agg_data`.

    With `selectable`, selecting rows shows their match-by-match breakdowns below.
    `groups` maps team -> label (e.g. an alliance emoji); rows are kept together
    by group, in the order the groups first appear, ranked within each group.
    """
    if agg_data.empty:
        st.info("No scouting data for these teams yet.")
        return

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

    # Recent form: average of the last few matches minus the team's overall average
    ordered_sn_df = _ordered_matches(raw_sn_df, sn_df)
    match_totals = ordered_sn_df.sum(axis=1)
    by_team = match_totals.groupby("Team")
    recent_avg = by_team.apply(lambda totals: totals.tail(trend_matches).mean())
    # Teams with no earlier matches to compare against have no trend
    has_history = by_team.size() > trend_matches
    display_data["Trend"] = (recent_avg - by_team.mean()).where(has_history)

    display_data = display_data[
        ["Avail", "Our Rank", "TBA Rank", "Total", "Trend"] + metric_columns
    ].sort_values("Our Rank")

    if groups:
        group_order = {label: i for i, label in enumerate(dict.fromkeys(groups.values()))}
        display_data["Group"] = display_data.index.map(groups)
        display_data = display_data.iloc[
            display_data["Group"].map(group_order).argsort(kind="stable")
        ]

    shaded_columns = ["Total"] + metric_columns
    table_data = display_data.drop(columns="Avail")
    if groups:
        table_data.insert(0, "Group", table_data.pop("Group"))
    table_data.index = (
        display_data["Avail"] + " " + display_data.index.astype(str)
    ).rename("Team")
    def style_rows(rows: pd.DataFrame):
        return (
            rows.style.apply(
                lambda col: shade_column(col, table_data[col.name]),
                axis=0,
                subset=shaded_columns,
            )
            .format("{:.1f}", subset=shaded_columns)
            .format("{:d}", subset=["Our Rank", "TBA Rank"], na_rep="–")
            .format(format_trend, subset=["Trend"], na_rep="–")
            .map(
                lambda value: (
                    "color: #2ca02c"
                    if value > 0
                    else "color: #d62728" if value < 0 else ""
                ),
                subset=["Trend"],
            )
            .set_properties(subset=["Total"], **{"font-weight": "bold"})
        )

    styled_data = style_rows(table_data)
    column_config = {
        "_index": st.column_config.Column("Team", width=80),
        "Group": st.column_config.Column("", width=40, alignment="center"),
        "Our Rank": st.column_config.Column("SN", width=40, alignment="center"),
        "TBA Rank": st.column_config.Column("TBA", width=48, alignment="center"),
        "Trend": st.column_config.Column(
            "Trend",
            width=64,
            alignment="center",
            help=f"Average of the last {trend_matches} matches vs. the team's overall average",
        ),
    }
    visible_columns = [
        col
        for col in table_data.columns
        if not (hide_identifiers and col == "TBA Rank")
    ]

    caption = (
        "Total is the sum of the metrics shown. Green is positive and red is "
        "negative; darker means larger within each column. Swipe to see more metrics."
    )
    if selectable:
        caption += " Tap a row for a match-by-match breakdown."
    st.caption(caption)

    selection = st.dataframe(
        styled_data,
        key=key,
        on_select="rerun" if selectable else "ignore",
        selection_mode=selection_mode,
        hide_index=hide_identifiers,
        column_order=visible_columns,
        column_config=column_config,
        width="stretch",
        height="content",
    )

    if not selectable:
        return
    selected_rows = selection.selection.rows
    if selected_rows:
        match_totals_by_level = ordered_sn_df.T.groupby(level=chart_type).sum().T
        selected_teams = [display_data.index[row] for row in selected_rows]
        breakdowns = [
            (
                team,
                team_names.get(team) if team_names is not None else None,
                match_totals_by_level.xs(team, level="Team"),
            )
            for team in selected_teams
        ]
        values = pd.concat([matches.stack() for _, _, matches in breakdowns]).dropna()
        low = min(float(values.min()), 0) if not values.empty else 0
        high = max(float(values.max()), 0) if not values.empty else 0
        if low == high:
            low, high = low - 1, high + 1
        y_domain = [low, high]
        for team, name, matches in breakdowns:
            _team_breakdown(
                matches,
                team,
                name,
                chart_type,
                y_domain,
                lambda position=display_data.index.get_loc(team): st.dataframe(
                    style_rows(table_data.iloc[[position]]),
                    column_order=visible_columns,
                    column_config=column_config,
                    hide_index=True,
                    width="stretch",
                    height="content",
                ),
            )


def _team_breakdown(
    team_matches: pd.DataFrame,
    team: int,
    name: str | None,
    chart_type: str,
    y_domain: list[float],
    show_row,
) -> None:
    st.subheader(f"{team} {name}" if name else f"Team {team}")
    show_row()
    chart_data = team_matches.reset_index().melt(
        id_vars="Match Name", var_name=chart_type, value_name="Points"
    )
    match_order = team_matches.index.to_list()
    y_scale = alt.Scale(domain=y_domain)
    x_axis = alt.X(
        "Match Name:N", sort=match_order, title=None, axis=alt.Axis(labelAngle=-45)
    )
    bars = (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=x_axis,
            y=alt.Y("Points:Q", title=None, scale=y_scale),
            color=alt.Color(
                f"{chart_type}:N", legend=alt.Legend(orient="bottom", title=None)
            ),
            tooltip=["Match Name", chart_type, "Points"],
        )
    )
    # Fitted linear trend through each match's total
    totals = team_matches.sum(axis=1).rename("Total").reset_index()
    if len(totals) > 1:
        slope, intercept = np.polyfit(range(len(totals)), totals["Total"], 1)
        totals["Trend"] = intercept + slope * np.arange(len(totals))
    else:
        totals["Trend"] = totals["Total"]
    trend_line = (
        alt.Chart(totals)
        .mark_line(color="#e6a817", size=3)
        .encode(x=x_axis, y=alt.Y("Trend:Q", scale=y_scale))
    )
    with st.expander("Chart", expanded=False):
        st.altair_chart(
            (bars + trend_line).properties(height=280),
            width="stretch",
        )
        st.caption("Gold: trend line through match totals")
    with st.expander("Data", expanded=False):
        st.dataframe(
            team_matches.assign(Total=team_matches.sum(axis=1)).style.format("{:.1f}"),
            width="stretch",
            height="content",
        )


def alliance_table(alliance_data: dict[str, pd.DataFrame], actual: dict[str, int]) -> None:
    """One row per alliance with each metric summed across its teams."""
    rows = {
        label: data.drop(columns="sn_rank").sum().rename_axis(None)
        for label, data in alliance_data.items()
    }
    table = pd.DataFrame(rows).T
    metric_columns = list(table.columns)
    table.insert(0, "Projected", table.sum(axis=1))
    table.insert(1, "Actual", pd.Series(actual))
    table.index.name = "Alliance"
    shaded_columns = ["Projected"] + metric_columns
    st.dataframe(
        table.style.apply(shade_column, axis=0, subset=shaded_columns)
        .format("{:.1f}", subset=shaded_columns)
        .format("{:d}", subset=["Actual"], na_rep="–")
        .set_properties(subset=["Projected"], **{"font-weight": "bold"}),
        column_config={
            "_index": st.column_config.Column("", width=40, alignment="center"),
            "Actual": st.column_config.Column(width=60, alignment="center"),
        },
        width="stretch",
        height="content",
    )
