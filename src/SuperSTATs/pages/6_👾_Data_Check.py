import SuperSTATs.loader as load
import streamlit as st
import tbapy

st.set_page_config(
    page_title="[STATS] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
    layout="wide",
)

df = load.download_sheets_raw(st.secrets["GID_RAW"]).dropna(subset="Timestamp")
tba = tbapy.TBA(st.secrets["TBA_API"])
sections = load.get_match_sections(df)


def show_raw(match_num, match_info):
    try:
        if st.checkbox("📊 Show RAW Data", key=f"{match_num}_RAW"):
            st.write(match_info["RAW Data"])
    except:
        pass


def calc_score(df, team_num, sections):
    df = df.drop("COMMENT_GENERAL_1", axis=1)
    df_plot = df.loc[(df["Team"] == team_num)]

    mask = df.columns == "Match"
    for section in sections:
        mask = mask | df.columns.str.startswith(f"{section}_")

    df_plot = df_plot.loc[:, mask]

    df_split = []
    for list in df.columns.str.split("_"):
        if len(list) > 1:
            df_split.append(list)

    points = {}
    for value in df_split:
        points.update({f"{value[0]}_{value[1]}_{value[2]}": int(value[2])})

    for col, point in points.items():
        if col in df_plot.columns:
            df_plot[col] *= point

    for score_type in sections:
        columns = [col for col in df_plot.columns if col.startswith(score_type)]
        df_plot[f"{score_type.strip('_').title()} Score"] = df_plot[columns].sum(axis=1)

    excluded_cols = ["Match"]
    sum_cols = [f"{section.title()} Score" for section in sections]
    all_columns = excluded_cols + sum_cols

    df_plot["Total Score"] = df_plot.drop(columns=all_columns, axis=1).sum(axis=1)

    return df_plot["Total Score"]


def main():
    load.init_page()

    st.markdown(
        "<h1 style='text-align: center;'>👾 Data Check 👾</h1>",
        unsafe_allow_html=True,
    )
    st.title("")

    tba_scores = {}
    tba_info = tba.event_matches(st.secrets["DEFAULT_EVENT_KEY"])

    calc_excess = st.checkbox("Calculate Excess")
    for data in tba_info:
        if calc_excess:
            excess_points = (
                data["score_breakdown"]["red"]["foulPoints"]
                + data["score_breakdown"]["red"]["linkPoints"]
                + data["score_breakdown"]["blue"]["foulPoints"]
                + data["score_breakdown"]["blue"]["linkPoints"]
            )
        match_num = data["match_number"]
        if calc_excess:
            total_score = (
                data["alliances"]["blue"]["score"] + data["alliances"]["red"]["score"]
            ) - excess_points
            tba_scores[match_num] = total_score
        total_score = (
            data["alliances"]["blue"]["score"] + data["alliances"]["red"]["score"]
        )
        tba_scores[match_num] = total_score

    grouped = df.groupby("Match")
    df_matches = {match: group for match, group in grouped}

    st.button("Update Page", use_container_width=True, type="primary")

    filters = [
        "❓ Missing Teams",
        "💭 Missing Comments",
        "🔄️ Incorrect Entry Amount",
        "🚨 TBA Score Variation",
        # "📈 Score Outliers",
    ]

    selected_filters = st.multiselect(
        "Filters:", filters, ["❓ Missing Teams", "🔄️ Incorrect Entry Amount"]
    )

    st.write("""---""")

    if not selected_filters:
        st.error("No Filters Selected")

    all_data = {}

    for match_num, match_info in df_matches.items():
        current_match_df = df[df["Match"] == match_num]

        team_nums = []
        for team in current_match_df["Team"]:
            team_nums.append(team)

        team_comments = {}
        for index, row in current_match_df.iterrows():
            team = row["Team"]
            comment = row["COMMENT_GENERAL_1"]

            if team not in team_comments:
                team_comments[team] = []

            team_comments[team].append(comment)

        data = {
            "Match Number": match_num,
            "Match Type": match_info["Match Type"].max(),
            "Team Count": len(team_nums),
            "Teams": team_nums,
            "Comments": team_comments,
            "RAW Data": current_match_df,
        }

        all_data[match_num] = data

    match_df = st.session_state.global_match_df

    match_teams = {}
    for match in match_df.values:
        match_teams[match[0]] = list(match[1:])

    for match_num, match_info in all_data.items():
        match_name = f"{match_info['Match Type']} {match_info['Match Number']}"

        with st.expander(match_name):
            if "❓ Missing Teams" in selected_filters:
                teams_actual = sorted(list(map(int, match_teams[match_name])))
                teams_data = sorted(match_info["Teams"])

                if teams_actual != teams_data:
                    show_raw(match_num, match_info)
                    st.header("Missing Teams")
                    col_1, col_2 = st.columns(2)

                    col_1.subheader("NURD Data")
                    col_1.write(teams_data)

                    col_2.subheader("TBA Data")
                    col_2.write(teams_actual)

            if "💭 Missing Comments" in selected_filters:
                comment_df = df[["Team", "Match", "COMMENT_GENERAL_1"]]
                comment_df = comment_df[comment_df["Match"] == match_num].drop(
                    "Match", axis=1
                )
                comment_df = comment_df[comment_df["COMMENT_GENERAL_1"].isnull()]

                if not comment_df.empty:
                    show_raw(match_num, match_info)
                    st.header("Missing Comments")
                    st.write(comment_df)

            if "🔄️ Incorrect Entry Amount" in selected_filters:
                entries_df = df[["Team", "Match"]]
                entries_df = entries_df[entries_df["Match"] == match_num].drop(
                    "Match", axis=1
                )
                entries_length = len(entries_df)

                if entries_length != 6:
                    show_raw(match_num, match_info)
                    team_entries = []
                    st.header("Incorrect Entry Amount")

                    team_entries = [
                        int(sub_entry)
                        for entry in entries_df.values
                        for sub_entry in entry
                    ]

                    entries_count = f"{entries_length}/6 Entries : {team_entries}"
                    st.write(entries_count)

            if "🚨 TBA Score Variation" in selected_filters:
                # tolerance = st.slider(
                #     "Score Tolerance:", 0, 100, value=25, key=f"{match_num}_Tolerance"
                # )

                tba_score = tba_scores[match_num]

                match_teams = st.session_state.global_match_df
                match_teams = match_teams.loc[(match_teams["Match"] == match_name)]
                match_teams = match_teams.drop("Match", axis=1).astype(int)

                team_list = match_teams.iloc[0].tolist()

                data_score = []
                for team in team_list:
                    data = calc_score(df, team, sections).mean()
                    try:
                        data_score.append(int(data))
                    except:
                        data_score.append(data)

                data_score = sum(data_score)

                # TODO: Add Tolerance

                if tba_score > data_score:
                    tba_score_text = (
                        f"<font color='limegreen'>TBA Score: {tba_score}</font>"
                    )
                    data_score_text = (
                        f"<font color='red'>Our Data Score: {data_score}</font>"
                    )
                elif tba_score < data_score:
                    tba_score_text = f"<font color='red'>TBA Score: {tba_score}</font>"
                    data_score_text = (
                        f"<font color='limegreen'>Our Data Score: {data_score}</font>"
                    )
                else:
                    tba_score_text = (
                        f"<font color='yellow'>TBA Score: {tba_score}</font>"
                    )
                    data_score_text = (
                        f"<font color='yellow'>Our Data Score: {data_score}</font>"
                    )

                show_raw(match_num, match_info)
                st.subheader("TBA Score Variation")
                col_1, col_2 = st.columns(2)
                col_1.markdown(tba_score_text, unsafe_allow_html=True)
                col_2.markdown(data_score_text, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
