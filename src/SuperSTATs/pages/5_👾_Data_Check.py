import SuperSTATs.load as load
import streamlit as st
import json


st.set_page_config(
    page_title="[STATS] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
    layout="wide",
)


def show_raw(match_num, match_info, match_key):
    try:
        if st.checkbox("📊 Show RAW Data", key=f"{match_num}_RAW"):
            st.write(match_info)
        st.markdown(
            f"<span style='font-size: small;'>[{match_key.replace('_', '-')}](https://www.thebluealliance.com/match/{match_key})</span>",
            unsafe_allow_html=True,
        )
    except:
        pass


def main():
    load.app_init()

    import SuperSTATs.build as build

    st.markdown(
        "<h1 style='text-align: center;'>👾 Data Check 👾</h1>", unsafe_allow_html=True
    )
    st.title("")

    st.button("Update Page", type="primary", use_container_width=True)
    st.markdown("""---""")

    df = st.session_state.df

    phases = ["AUTO", "TELE", "END"]

    for i in range(len(phases)):
        df.loc[:, phases[i]] = build.add_cols(
            df,
            phases[i],
        )

    df["Score Sum"] = df[phases].sum(axis=1)

    filters = [
        "❓ Missing Teams",
        "💭 Missing Comments",
        "🚨 TBA Score Variation",
    ]

    selected_filters = st.multiselect("Filters:", filters, [filters[0], filters[2]])

    default_threshold = 25
    min_threshold = 0
    max_threshold = 50

    if filters[2] in selected_filters:
        with st.form("Threshold Slider", clear_on_submit=False):
            variance_threshold = st.slider(
                "Variance Threshold:",
                min_threshold,
                max_threshold,
                default_threshold,
                1,
            )
            st.form_submit_button(
                "Set Threshold", type="primary", use_container_width=True
            )

    matches = st.session_state.matches

    df["Match Name"] = df["Match Type"] + " " + df["Match"].astype(str)

    grouped = df.groupby("Match Name")
    df_matches = {match: group for match, group in grouped}

    if not selected_filters:
        st.error("No Filters Selected")

    def sort_key(match):
        parts = match.split(" ")
        match_order = {"Quals": 1, "Playoffs": 2, "Finals": 3}
        return (match_order.get(parts[0], 4), int(parts[1]))

    sorted_matches = sorted(df_matches.keys(), key=sort_key)
    df_matches = {match: df_matches[match] for match in sorted_matches}

    match_keys = {}
    match_data = st.session_state.match_data
    match_keys = match_data.set_index("Match Name")["key"].to_dict()

    for match_name, match_info in df_matches.items():
        current_match = df_matches[match_name]
        team_nums = current_match["Team"].tolist()
        match_teams = matches.loc[matches["Match"] == match_name]
        match_teams = match_teams.drop(columns=["Match"])
        tba_values = match_teams.values.tolist()[0]

        with st.expander(match_name):
            data_variance = False

            if filters[0] in selected_filters:
                if sorted(team_nums) != sorted(tba_values):
                    st.subheader(f"Team Count: {len(team_nums)}/6")

                    columns = st.columns(2)

                    columns[0].subheader("SN Data")
                    columns[0].write(team_nums)

                    columns[1].subheader("TBA Data")
                    columns[1].write(tba_values)

                    data_variance = True

            if filters[1] in selected_filters:
                comment_df = df[["Team", "Match Name", "COMMENT_GENERAL_STR_1"]]
                comment_df = comment_df[comment_df["Match Name"] == match_name].drop(
                    "Match Name", axis=1
                )
                comment_df = comment_df[comment_df["COMMENT_GENERAL_STR_1"].isnull()]

                if not comment_df.empty:
                    no_comm_teams = []
                    for team in comment_df["Team"]:
                        no_comm_teams.append(str(team))
                    no_comm_teams = ", ".join(no_comm_teams)

                    st.subheader(f"💭 {no_comm_teams}")
                    data_variance = True

            if filters[2] in selected_filters:
                score_breakdown = match_data[match_data["Match Name"] == match_name][
                    "score_breakdown"
                ]

                score_breakdown = score_breakdown.to_json(orient="records")
                data = json.loads(score_breakdown)

                red_data = data[0]["red"]
                blue_data = data[0]["blue"]

                red_tba_score = (
                    red_data["totalPoints"]
                    - red_data["linkPoints"]
                    - red_data["foulPoints"]
                )
                blue_tba_score = (
                    blue_data["totalPoints"]
                    - blue_data["linkPoints"]
                    - blue_data["foulPoints"]
                )

                def get_variance(color, tba_score):
                    team_df = match_info[match_info["Team Color"] == color[0]]
                    team_score = int(team_df["Score Sum"].sum())
                    team_variance = abs(tba_score - team_score)
                    text_color = "#f8312f" if color[0] == "R" else "#0074ba"

                    if team_variance >= variance_threshold:
                        colored_header = f"<span style='color: {text_color}; font-size: 2em;'>[{color}]</span>"
                        default_header = f"<span style='color: white; font-size: 2em;'> Point Variance: {team_variance} ({team_score}/{tba_score})</span>"

                        st.markdown(
                            f"{colored_header}{default_header}",
                            unsafe_allow_html=True,
                        )

                        st.write(team_df[["Team", "AUTO", "TELE", "END", "Score Sum"]])

                        nonlocal data_variance
                        data_variance = True

                get_variance("RED", red_tba_score)
                get_variance("BLUE", blue_tba_score)

            if data_variance:
                show_raw(match_name, match_info, match_keys[match_name])


if __name__ == "__main__":
    main()
