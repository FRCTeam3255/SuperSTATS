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
        if phase in use_phases:
            team_averages[phase] = round(score / match_count)

    match_scores = team_df.loc[team_df["Match Name"] == match_name]

    team_scores = match_scores.drop(columns=["Match Name"])
    team_scores = team_scores.sum()
    team_scores["TOTAL"] = team_scores.sum()

    match_score = {}

    for phase, score in team_scores.items():
        if phase in use_phases:
            match_score[phase] = score

    for i, phase in enumerate(phases):
        columns[i].subheader(f"{match_score[phase]}/{team_averages[phase]}")

    df = pd.DataFrame(
        {
            "Phase": use_phases,
            "Average": list(team_averages.values()),
            "Match": list(match_score.values()),
        }
    )

    chart = (
        alt.Chart(df.melt("Phase"))
        .mark_bar()
        .encode(
            alt.X("variable:N", axis=alt.Axis(title="")),
            alt.Y("value:Q", axis=alt.Axis(title="Team Average vs Match", grid=False)),
            color=alt.Color(
                "variable:N",
                scale=alt.Scale(
                    domain=["Average", "Match"],
                    range=["#f8312f", "#0074ba"],
                ),
                legend=alt.Legend(title=" "),
            ),
            column="Phase:O",
        )
        .configure_view(stroke="transparent")
        .configure_axis(labelAngle=0)
    )

    alt_size = st.columns(len(use_phases) + 1)
    with alt_size[0].container():
        st.altair_chart(chart, use_container_width=True)


if __name__ == "__main__":
    main()
