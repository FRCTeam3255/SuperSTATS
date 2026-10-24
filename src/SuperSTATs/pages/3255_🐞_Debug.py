from pathlib import Path

import pandas as pd
import streamlit as st

from SuperSTATs.utils import constants, forms, gsheets, scouting, tba

page_name = Path(__file__).stem.split("_", 1)[1].replace("_", " ")
st.title(page_name)
col_a, col_b = st.columns(2)
if col_a.button("Clear Sheets Caches & Reload", type="primary", width="stretch"):
    gsheets.clear_cache()
    st.rerun()
if col_b.button("Clear Event Data (teams, photos)", width="stretch"):
    tba.clear_event_cache()
    st.rerun()
st.divider()
print(f"{page_name} loaded:")

# ==== Event & Constants ====
with st.expander("Event", expanded=False):
    col1, col2, col3 = st.columns(3)
    col1.metric("Event Key", constants.DEFAULT_EVENT_KEY)
    col2.metric("Team Number", constants.DEFAULT_TEAM_NUMBER)
    col3.metric("Year", constants.CURRENT_YEAR)

# ==== Config ====
with st.expander("Config (Google Sheet)", expanded=False):
    try:
        configs = gsheets.get_configs()
        st.dataframe(
            pd.DataFrame(
                {
                    "Config": list(configs),
                    "Value": [", ".join(v) for v in configs.values()],
                }
            ).set_index("Config"),
            width="stretch",
        )
    except Exception as e:
        st.error(f"Failed to load configs: {e}")

# ==== Data Sources ====
sources = {
    "Data: Stats inputs": lambda: gsheets.get_stats_inputs(),
    "Data: Available/picked": gsheets.get_available,
    "Data: Scouts": lambda: pd.DataFrame({"Assigned": gsheets.get_scouts()[1]}),
    "Data: TBA teams": tba.get_teams,
    "Data: TBA matches": lambda: tba.get_matches(as_simple=True),
    "Data: TBA rankings": tba.get_rankings,
}
for label, fetch in sources.items():
    with st.expander(label, expanded=False):
        try:
            data = fetch()
            st.caption(f"{len(data)} rows × {len(data.columns)} columns")
            st.dataframe(data.astype(str), width="stretch")
        except Exception as e:
            st.error(f"Failed: {e}")

# ==== Stats Form Entries ====
with st.expander("Stats Form Entries", expanded=False):
    try:
        set_entries, phase_entries = forms.get_stats_form_entries(
            (*gsheets.PHASES, "COMMENT")
        )
        st.caption(
            "Scraped from the Google Form and cached until restart. "
            "Identifier entries are filled by the app, phase entries come from the form inputs."
        )
        st.markdown("**Identifier entries**")
        st.dataframe(
            pd.DataFrame(
                {"Question": list(set_entries), "Entry ID": list(set_entries.values())}
            ),
            hide_index=True,
            width="stretch",
        )
        st.markdown("**Phase entries**")
        st.dataframe(
            pd.DataFrame(
                {
                    "Question": list(phase_entries),
                    "Phase": [q.split("_")[0] for q in phase_entries],
                    "Entry ID": list(phase_entries.values()),
                }
            ),
            hide_index=True,
            width="stretch",
        )
    except Exception as e:
        st.error(f"Failed: {e}")

# ==== Submissions ====
with st.expander("Submissions", expanded=False):
    try:
        counts = gsheets.get_submission_counts()
        pending = (
            gsheets.get_pending_submissions()
        )  # read after counts, which prunes it
        st.caption(
            f"Cache TTLs: sheets {constants.GSHEET_DATA_CACHE_TTL}, "
            "team list & robot photos 1 day, TBA follows its own Cache-Control headers"
        )
        submissions = pd.DataFrame(
            {
                "Match": list(counts),
                "Teams scouted": list(counts.values()),
                "Pending (not in sheet yet)": [
                    ", ".join(map(str, pending.get(m, []))) for m in counts
                ],
            }
        ).set_index("Match")
        st.dataframe(submissions, width="stretch")
    except Exception as e:
        st.error(f"Failed: {e}")

# ==== Scout Rotation ====
with st.expander("Scout Rotation", expanded=False):
    try:
        _, assigned = gsheets.get_scouts()
        rotation = int(gsheets.get_configs()["Scouting Rotations"][0])
        tba_matches = tba.get_matches(as_simple=True).drop_duplicates("Match Name")
        teams = scouting.match_teams(tba_matches)
        rotation_scouts = scouting.get_all_match_scouts(
            assigned, teams.index.to_list(), rotation
        )
        slots = [
            f"{c} {i + 1}" for c in ("🔴", "🔵") for i in range(constants.ALLIANCE_SIZE)
        ]
        st.caption(f"Rotation: {rotation} matches, {len(assigned)} assigned scouts")
        st.dataframe(
            pd.DataFrame.from_dict(
                rotation_scouts, orient="index", columns=slots
            ).rename_axis("Match"),
            width="stretch",
        )
    except Exception as e:
        st.error(f"Failed: {e}")
