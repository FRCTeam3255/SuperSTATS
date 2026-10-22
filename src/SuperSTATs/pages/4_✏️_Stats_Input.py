import re
import zlib
from pathlib import Path

import requests
import streamlit as st

from SuperSTATs.utils import constants, forms, gsheets, scouting, tba

page_name = Path(__file__).stem.split("_", 1)[1].replace("_", " ")
print(f"{page_name} loaded:")

PHASE_TITLES = {
    "AUTO": "🤖 Autonomous",
    "TELE": "🎮 Teleop",
    "END": "🏁 Endgame",
    "INFO": "📝 Info & Comments",
}
FORM_PHASES = (*gsheets.PHASES, "COMMENT")
ALLIANCE = constants.ALLIANCE_SIZE
UPCOMING_MATCHES = 5

# Big tap targets, no column stacking on phones, and a header that stays on screen
st.markdown(
    """
    <style>
    .block-container { padding: 3.5rem 0.9rem 6rem; max-width: 640px; }
    /* Sticky elements stick within their parent, so the banner's own element wrapper
       (a direct child of the page) sticks for the whole page, while each phase header
       (first child of its section) only sticks until the next section starts */
    div[data-testid="stElementContainer"]:has(.banner) {
        position: sticky; top: 3.75rem; z-index: 1000;
    }
    [class*="st-key-phase_"] { margin-top: 1rem; }
    [class*="st-key-phase_"] > :first-child {
        position: sticky; top: 8.4rem; z-index: 900;
    }
    .phase-title { text-align: center; font-size: 1.4rem; font-weight: 700; color: #fff;
                   border-radius: 0.5rem; padding: 0.35rem 0; margin-bottom: 0.5rem; }
    .phase-AUTO { background: #b8860b; }
    .phase-TELE { background: #2e7d32; }
    .phase-END { background: #6a1b9a; }
    .phase-INFO { background: #455a64; }
    .banner { text-align: center; border-radius: 0.75rem; padding: 0.5rem 0.25rem;
              line-height: 1.25; color: #fff; }
    .banner.red { background: #8f1d1c; border: 2px solid #f8312f; }
    .banner.blue { background: #0a4f7a; border: 2px solid #0074ba; }
    .banner .team { font-size: 1.5rem; font-weight: 700; }
    .banner .sub { font-size: 0.85rem; opacity: 0.85; }
    [class*="st-key-ctr_"] [data-testid="stHorizontalBlock"],
    [class*="st-key-tgl_"] [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; }
    [class*="st-key-ctr_"] [data-testid="stHorizontalBlock"] > *,
    [class*="st-key-tgl_"] [data-testid="stHorizontalBlock"] > * {
        min-width: 0 !important; width: auto !important; flex: 1 1 0 !important; }
    [class*="st-key-ctr_"] button { min-height: 3.5rem; font-size: 1.6rem; }
    .count { text-align: center; font-size: 2.4rem; font-weight: 700; line-height: 3.5rem; }
    .ctr-label { font-size: 1.05rem; margin-top: 0.5rem; text-align: center; }
    /* Counters and toggles pick up their phase color; negative-point items are tinted red */
    [class*="st-key-ctr_"], [class*="st-key-tgl_"] {
        border: 2px solid rgba(250, 250, 250, 0.85) !important; border-radius: 0.75rem !important;
        padding: 0 0.5rem 0.5rem !important; margin-bottom: 0.5rem; box-sizing: border-box; }
    [class*="st-key-tgl_"] { padding: 0.5rem !important; }
    [class*="st-key-tgl_"] .ctr-label { margin: 0; height: 3.5rem; display: flex;
        align-items: center; justify-content: center; }
    [class*="st-key-tgl_"] [data-testid="stMarkdownContainer"] { margin: 0 !important; }
    [class*="st-key-tgl_"] [data-testid="stMarkdownContainer"] p { margin: 0; }
    [class*="st-key-ctr_auto-"], [class*="st-key-tgl_auto-"] { border-color: #e6a817 !important; }
    [class*="st-key-ctr_tele-"], [class*="st-key-tgl_tele-"] { border-color: #4caf50 !important; }
    [class*="st-key-ctr_end-"], [class*="st-key-tgl_end-"] { border-color: #ba68c8 !important; }
    [class*="st-key-ctr_info-"], [class*="st-key-tgl_info-"] { border-color: #90a4ae !important; }
    [class*="-neg-"] { background: rgba(248, 49, 47, 0.14); }
    .count.zero { opacity: 0.35; }
    [class*="st-key-ctr_auto-"] .count.set { color: #e6a817; }
    [class*="st-key-ctr_tele-"] .count.set { color: #4caf50; }
    [class*="st-key-ctr_end-"] .count.set { color: #ba68c8; }
    [class*="st-key-ctr_info-"] .count.set { color: #90a4ae; }
    [class*="st-key-tgl_"] button { min-height: 3.5rem; font-size: 1.6rem; }
    [class*="st-key-tgl_"] button[kind="primary"] { color: #fff; }
    [class*="st-key-tgl_auto-"] button[kind="primary"] { background: #b8860b; border-color: #b8860b; }
    [class*="st-key-tgl_tele-"] button[kind="primary"] { background: #2e7d32; border-color: #2e7d32; }
    [class*="st-key-tgl_end-"] button[kind="primary"] { background: #6a1b9a; border-color: #6a1b9a; }
    [class*="st-key-tgl_info-"] button[kind="primary"] { background: #455a64; border-color: #455a64; }
    [class*="st-key-tgl_"][class*="-neg-"] button[kind="primary"] { background: #c62828; border-color: #c62828; }
    [class*="-neg-"] .count.set { color: #f8312f !important; }
    .st-key-submit button { min-height: 4rem; font-size: 1.3rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

if flash := st.session_state.pop("flash", None):
    st.balloons()
    st.toast(flash, icon="✅")


# === Page Specific Data ===
configs = gsheets.get_configs()
all_scouts, assigned_scouts = gsheets.get_scouts()
tba_team_info = tba.get_teams()
tba_matches = tba.get_matches(as_simple=True)
if tba_matches.empty:
    st.error("⚠️ No match schedule available from TBA")
    st.stop()
match_teams = scouting.match_teams(tba_matches.drop_duplicates("Match Name"))
match_list = match_teams.index.to_list()
rotation = int(configs["Scouting Rotations"][0])
all_match_scouts = scouting.get_all_match_scouts(assigned_scouts, match_list, rotation)
submission_counts = gsheets.get_submission_counts()
tba_played = set(tba_matches.loc[tba_matches["🔴 Score"].notna(), "Match Name"])
unplayed = [
    m
    for m in match_list
    if submission_counts.get(m, 0) < ALLIANCE and m not in tba_played
]
set_entries, phase_entries = forms.get_stats_form_entries(FORM_PHASES)
features = configs["Features"]


def nickname_of(team: int) -> str:
    return tba_team_info.loc[team, "nickname"] if team in tba_team_info.index else ""


# ==== Scout & Match Setup (name first, the rest loads once it's chosen) ====
name = st.selectbox(
    "Your name:",
    assigned_scouts + ["Sub"],
    index=None,
    placeholder="Select your name",
    key="scout_name",
)
substitute = None
if name == "Sub":
    name = st.selectbox("Original scout:", assigned_scouts, key="sub_original")
    substitute = st.selectbox("Substitute:", all_scouts, key="sub_name")

selected_match = team = color = None
practice_mode = False
if name:
    practice_mode = st.toggle("Practice mode", False, key="practice_mode")
    if practice_mode:
        match_options = [f"Prac {i + 1}" for i in range(50)]
    else:
        match_options = [m for m in unplayed if name in all_match_scouts[m]]
        match_options.append("Other")
    # No keys here: a changing options list should reset the selection
    selected_match = st.selectbox("Match:", match_options)
    if selected_match == "Other":
        selected_match = st.selectbox("Match [OTHER]:", match_list)

    if selected_match in match_teams.index and not practice_mode:
        teams = match_teams.loc[selected_match].to_list()
        scouts = all_match_scouts[selected_match]
        if name in scouts:
            slot = scouts.index(name)
            team, color = teams[slot], "R" if slot < ALLIANCE else "B"
        else:
            team = st.selectbox("Team:", teams)
            color = "R" if teams.index(team) < ALLIANCE else "B"
    else:
        team = st.selectbox(
            "Team:",
            tba_team_info.index.to_list(),
            format_func=lambda t: f"{t} | {nickname_of(t)}",
        )
        color = st.radio("Color:", ["R", "B"], horizontal=True)

if not name:
    st.info("👆 Select your name to start scouting")
    st.stop()
if not selected_match or team is None:
    st.warning("⚠️ No match available to scout")
    st.stop()
match_type, match_number = selected_match.split()
recorded_name = (
    f"{substitute} [⇄] {name}" if substitute and substitute != name else name
)

# ==== Sticky Team Header ====
st.markdown(
    f"""
    <div class="banner {"red" if color == "R" else "blue"}">
        <div class="team">{"🔴" if color == "R" else "🔵"} {team} | {nickname_of(team)}</div>
        <div class="sub">{selected_match} · {recorded_name}{" · PRACTICE" if practice_mode else ""}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

photo_expander = st.expander("Robot Image", False, on_change="rerun")
if photo_expander.open:
    # Only fetch the photo once the expander is opened, to save mobile data
    with photo_expander:
        photo_url = tba.get_robot_photo_url(team)
        if photo_url:
            st.image(photo_url, caption=f"Team {team} Robot", width="stretch")
        else:
            st.warning("⚠️ No robot photo available")

if not practice_mode:
    with st.expander("Upcoming scouts", False):
        search = st.text_input("Find match:", "", placeholder="e.g. Quals 12").lower()
        if search:
            shown = [m for m in match_list if search in m.lower()]
        else:
            shown = unplayed[:UPCOMING_MATCHES]
        for match in shown:
            row = []
            for icon, part in (("🔴", slice(0, ALLIANCE)), ("🔵", slice(ALLIANCE, None))):
                pairs = zip(all_match_scouts[match][part], match_teams.loc[match][part])
                row.append(icon + " " + " · ".join(f"{s} ({t})" for s, t in pairs))
            st.markdown(f"**{match}**  \n" + "  \n".join(row))
else:
    st.error("⚠️ Practice mode enabled")


# ==== Stats Form ====
def slug(text: str) -> str:
    # The hash keeps keys unique when different entries reduce to the same text
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_") + f"_{zlib.crc32(text.encode()):x}"


def step_counter(state_key: str, delta: int) -> None:
    st.session_state[state_key] = max(0, st.session_state.get(state_key, 0) + delta)


def flip(state_key: str) -> None:
    st.session_state[state_key] = not st.session_state.get(state_key, False)


def render_counter(ctx: str, entry: str, label: str, tag: str) -> int:
    state_key = f"{ctx}|{entry}"
    value = st.session_state.setdefault(state_key, 0)
    with st.container(key=f"ctr_{tag}-{slug(state_key)}"):
        st.markdown(f'<div class="ctr-label">{label}</div>', unsafe_allow_html=True)
        minus, count, plus = st.columns([1, 1, 1], vertical_alignment="center")
        minus.button(
            "➖",
            key=f"dec_{slug(state_key)}",
            on_click=step_counter,
            args=(state_key, -1),
            width="stretch",
        )
        count.markdown(
            f'<div class="count {"set" if value else "zero"}">{value}</div>',
            unsafe_allow_html=True,
        )
        plus.button(
            "➕",
            key=f"inc_{slug(state_key)}",
            on_click=step_counter,
            args=(state_key, 1),
            width="stretch",
        )
    return value


def render_phase_inputs(ctx: str, phase: str, responses: dict) -> None:
    for entry in (e for e in phase_entries if e.startswith(phase)):
        parts = entry.split("_")
        # Key tag drives the CSS: phase color, plus "neg" for negative-point entries
        sign = "neg" if parts[-1].startswith("-") else "pos"
        tag = f"{phase.lower()}-{sign}"
        label = parts[1].title().replace("Rsl", "RSL")
        kind = next((p for p in parts[2:] if p in ("INT", "STR", "BOOL")), None)
        if kind == "INT":
            responses[entry] = render_counter(ctx, entry, label, tag)
        elif kind == "STR":
            picked = st.pills(
                f"{label}:",
                features,
                selection_mode="multi",
                key=f"{ctx}|{entry}",
            )
            responses[entry] = ", ".join(picked or [])
        elif kind == "BOOL":
            state_key = f"{ctx}|{entry}"
            on = st.session_state.setdefault(state_key, False)
            with st.container(key=f"tgl_{tag}-{slug(state_key)}"):
                text, control = st.columns([1, 1], vertical_alignment="center")
                text.markdown(f'<div class="ctr-label">{label}</div>', unsafe_allow_html=True)
                control.button(
                    "YES ✓" if on else "NO",
                    key=f"btn_{slug(state_key)}",
                    type="primary" if on else "secondary",
                    on_click=flip,
                    args=(state_key,),
                    width="stretch",
                )
            responses[entry] = int(on)


# Only this part reruns on taps, so phone interactions stay light
@st.fragment
def stats_form(identifiers: list, match_name: str, team_number: int) -> None:
    # A new generation after each submit gives fresh, empty inputs
    ctx = f"{match_name}|{team_number}|{st.session_state.get('form_gen', 0)}"
    responses: dict = {}
    for phase, title in PHASE_TITLES.items():
        with st.container(border=True, key=f"phase_{phase}"):
            st.markdown(
                f'<div class="phase-title phase-{phase}">{title}</div>',
                unsafe_allow_html=True,
            )
            render_phase_inputs(ctx, phase, responses)
            if phase == "INFO":
                render_phase_inputs(ctx, "COMMENT", responses)

    st.divider()
    with st.container(key="submit"):
        submitted = st.button("Submit", type="primary", width="stretch")
    if not submitted:
        return

    values = dict(zip(set_entries, identifiers)) | responses
    url = forms.build_submit_url(set_entries | phase_entries, values)
    try:
        ok = requests.get(url, timeout=10).status_code == 200
    except requests.exceptions.RequestException:
        ok = False
    if ok:
        gsheets.record_submission(match_name, team_number)
        st.session_state["form_gen"] = st.session_state.get("form_gen", 0) + 1
        st.session_state["flash"] = f"Submitted {match_name} · Team {team_number}"
        st.rerun()
    else:
        st.error("⚠️ Submission failed. Scan the QR code from another device")
        st.image(scouting.gen_qr(url), width="stretch")


stats_form(
    [
        recorded_name,
        match_number,
        match_type,
        color,
        team,
        constants.DEFAULT_EVENT_KEY,
    ],
    selected_match,
    team,
)

if st.button("Refresh data", width="stretch"):
    gsheets.clear_cache()
    st.rerun()
