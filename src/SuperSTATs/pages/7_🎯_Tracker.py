import SuperSTATs.load as load
import streamlit as st
import altair as alt
import pandas as pd


def main():
    load.app_init()

    import SuperSTATs.styles as style
    import SuperSTATs.build as build

    st.markdown(style.shimmer("#ff5b5a"), unsafe_allow_html=True)
    st.markdown("<div class='shimmer'>🎯 Team Tracker 🎯</div>", unsafe_allow_html=True)

    st.title("")

    st.button("Update Page", type="primary", use_container_width=True)
    st.markdown("""---""")

    df = st.session_state.df
    match_df = st.session_state.matches
    phases = st.session_state.phases + ["TOTAL"]

    columns = st.columns(2)

    teams = []

    for num, name in st.session_state.team_info.items():
        teams.append(f"{num} | {name}")

    team = columns[0].selectbox("Team:", teams)

    team_num = int(team.split(" | ")[0])
    team_cols = [f"Red {i}" for i in range(1, 4)] + [f"Blue {i}" for i in range(1, 4)]

    match_df = match_df[match_df[team_cols].isin([team_num]).any(axis=1)]
    matches = match_df["Match"].to_list()

    match_name = columns[1].selectbox("Match:", matches)

    st.markdown("""---""")

    team_df = df[df["Team"] == team_num]
    match_count = len(team_df)

    team_df = build.calc_projected([team_num], True)
    team_scores = team_df.drop(columns=["Match Name"])

    team_scores = team_scores.sum()
    team_scores["TOTAL"] = team_scores.sum()

    columns = st.columns(len(phases))

    skip_phases = ["INFO", "COMMENT"]
    use_phases = []

    for i, phase in enumerate(phases):
        use = columns[i].toggle(phase.title(), False if phase in skip_phases else True)
        if use:
            use_phases.append(phase)

    st.markdown("""---""")

    team_averages = {}

    for phase, score in team_scores.items():
        team_averages[phase] = round(score / match_count)

    match_scores = team_df.loc[team_df["Match Name"] == match_name]

    team_scores = match_scores.drop(columns=["Match Name"])
    team_scores = team_scores.sum()
    team_scores["TOTAL"] = team_scores.sum()

    match_score = {}

    for phase, score in team_scores.items():
        match_score[phase] = score

    for i, phase in enumerate(phases):
        columns[i].markdown(
            f"<span style='color: #0074ba; font-size: 2em;'>{match_score[phase]}</span>"
            f"<span style='color: #ffffff; font-size: 2em;'>/</span>"
            f"<span style='color: #f8312f; font-size: 2em;'>{team_averages[phase]}</span>",
            unsafe_allow_html=True,
        )

    df = pd.DataFrame(
        {
            "Phase": use_phases,
            "Average": [team_averages[phase] for phase in use_phases],
            "Match": [match_score[phase] for phase in use_phases],
        }
    )

    chart = (
        alt.Chart(df.melt("Phase"))
        .mark_bar()
        .encode(
            alt.X("variable:N", axis=alt.Axis(title=""), sort=["Match", "Average"]),
            alt.Y(
                "value:Q",
                axis=alt.Axis(title=f"{match_name} vs {team_num} Average", grid=False),
            ),
            color=alt.Color(
                "variable:N",
                scale=alt.Scale(
                    domain=["Match", "Average"],
                    range=["#0074ba", "#f8312f"],
                ),
                legend=alt.Legend(title=None, symbolType="circle"),
            ),
            column="Phase:O",
        )
        .properties(height=250)
        .configure_axis(labelAngle=0)
    )

    alt_size = st.columns(len(use_phases) + 1)
    with alt_size[0].container():
        st.altair_chart(chart, use_container_width=True)


if __name__ == "__main__":
    main()
