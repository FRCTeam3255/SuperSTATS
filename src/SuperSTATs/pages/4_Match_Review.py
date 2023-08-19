import SuperSTATs.Main as stats
import streamlit as st
import tbapy

st.set_page_config(
    page_title="[REVIEW] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="collapsed",
)

tba = tbapy.TBA(st.secrets["TBA_API"])


def check_uni(rp):
    if rp == 4:
        return " 🦄"
    else:
        return ""


def main():
    stats.set_font()

    st.title("⏳ Match Review ⌛")

    matches = tba.event_matches("2023casd")
    unique_matches = {}
    unique_team_numbers = set()

    for match in matches:
        match_number = match["match_number"]
        if match_number not in unique_matches:
            unique_matches[match_number] = match
            unique_team_numbers.update(
                [team[3:] for team in match["alliances"]["red"]["team_keys"]]
            )
            unique_team_numbers.update(
                [team[3:] for team in match["alliances"]["blue"]["team_keys"]]
            )

    sorted_match_numbers = sorted(unique_matches.keys())

    selected_team = st.selectbox(
        "Select Team Number", ["Show All Matches"] + sorted(unique_team_numbers)
    )

    for match_number in sorted_match_numbers:
        match_info = unique_matches[match_number]

        red_teams = [team[3:] for team in match_info["alliances"]["red"]["team_keys"]]
        blue_teams = [team[3:] for team in match_info["alliances"]["blue"]["team_keys"]]
        if (
            selected_team == "Show All Matches"
            or selected_team in red_teams + blue_teams
        ):
            with st.expander(f"Match {match_number}", expanded=False):
                st.title("")

                red_alliance = match_info["alliances"]["red"]
                blue_alliance = match_info["alliances"]["blue"]

                st.write(f"🔴 Red Alliance - {' || '.join(red_teams)}")
                st.write(f"Alliance: Score: {red_alliance['score']}")

                red_rp = match_info["score_breakdown"]["red"]["rp"]

                st.write(f"Ranking Points: {red_rp} / 4{check_uni(red_rp)}")

                st.title("")

                st.write(f"🔵 Blue Alliance - {' || '.join(blue_teams)}")
                st.write(f"Score: {blue_alliance['score']}")

                blue_rp = match_info["score_breakdown"]["blue"]["rp"]
                st.write(f"Ranking Points: {blue_rp} / 4{check_uni(blue_rp)}")


if __name__ == "__main__":
    main()
