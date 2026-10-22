from SuperSTATs.utils import constants, gsheets, scouting, tba
import pandas as pd
import streamlit as st

ALLIANCE = constants.ALLIANCE_SIZE

st.markdown(
    """
    <style>
    .match-table { width: 100%; table-layout: fixed; text-align: center;
                   border-collapse: collapse; margin-bottom: 0.5rem;
                   border-bottom: 1px solid rgba(250, 250, 250, 0.25); }
    .match-table td { padding: 0.1rem 0.2rem; overflow-wrap: anywhere; line-height: 1.2; }
    .match-table td span:not(.win) { font-size: 0.8rem; }
    .match-table .head td { text-align: left; font-weight: 700; padding-top: 0.3rem; }
    .match-table .win { background: #e6a817; color: #1a1a1a; font-weight: 700;
                        border-radius: 0.4rem; padding: 0 0.4rem; }
    .match-table .side { width: 3.5rem; font-size: 0.85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)
st.header(f"🕗 Matches for {constants.DEFAULT_EVENT_KEY}")
raw_matches = tba.get_matches(as_simple=True)
matches = raw_matches.set_index("Match Name")[
    ["🔴 Teams", "🔵 Teams", "🔴 Score", "🔵 Score", "🏆", "Start Time"]
]

# Scout assignments follow the same rotation as the Stats Input page
configs = gsheets.get_configs()
_, assigned_scouts = gsheets.get_scouts()
match_list = scouting.match_teams(raw_matches.drop_duplicates("Match Name")).index.to_list()
scouts = scouting.get_all_match_scouts(
    assigned_scouts, match_list, int(configs["Scouting Rotations"][0])
)
show = st.segmented_control(
    "Show", ["Upcoming", "Played", "All"], default="Upcoming", label_visibility="collapsed"
) or "Upcoming"
scout_col, team_col = st.columns(2)
me = scout_col.selectbox("Scout:", assigned_scouts, index=None, placeholder="Any scout")
all_teams = sorted({t for r in matches[["🔴 Teams", "🔵 Teams"]].itertuples() for ts in r[1:] for t in ts})
team_filter = team_col.selectbox("Team:", all_teams, index=None, placeholder="Any team")
search = st.text_input("Find match:", "", placeholder="e.g. Quals 12").lower()

cards = []
for match, row in matches.iterrows():
    played = pd.notna(row["🔴 Score"])
    if (show == "Upcoming" and played) or (show == "Played" and not played):
        continue
    if search and search not in match.lower():
        continue
    if me and me not in scouts.get(match, []):
        continue
    if team_filter and team_filter not in list(row["🔴 Teams"]) + list(row["🔵 Teams"]):
        continue
    rows = f'<tr class="head"><td colspan="{ALLIANCE + 1}">{match} · {row["Start Time"]}</td></tr>'
    for color, part in (("🔴", slice(0, ALLIANCE)), ("🔵", slice(ALLIANCE, None))):
        score = f"{row[f'{color} Score']:.0f}" if played else ""
        won = played and row["🏆"] == color
        score_html = f'<span class="win">{score}</span>' if won else score
        cells = ""
        for t, n in zip(row[f"{color} Teams"], scouts.get(match, [])[part]):
            mark = "🔎 " if t == team_filter else ""
            name = f"<b>{n}</b>" if n == me else n
            cells += f"<td><b>{mark}{t}</b><br><span>{name}</span></td>"
        rows += f'<tr><td class="side">{color}<br>{score_html}</td>{cells}</tr>'
    cards.append(f'<table class="match-table{" played" if played else ""}">{rows}</table>')
st.markdown("".join(cards), unsafe_allow_html=True)
