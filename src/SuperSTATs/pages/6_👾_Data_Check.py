import SuperSTATs.analytics as analytics
import SuperSTATs.load as load
from datetime import datetime
import streamlit as st
import pandas as pd
import requests
import json
import time


def show_raw(match_num, match_info, match_key):
    """
    Display the raw data for a given match through a dataframe.

    Parameters:
    - match_num (int): The match number.
    - match_info (str): The raw data for the match.
    - match_key (str): The key of the match.

    Returns:
    None
    """
    try:
        if st.toggle("📊 Show RAW Data", key=f"{match_num}_RAW"):
            st.write(match_info)
        st.markdown(
            f"<span style='font-size: small;'>[{match_key.replace('_', '-')}](https://www.thebluealliance.com/match/{match_key})</span>",
            unsafe_allow_html=True,
        )
    except:
        pass


def main():
    load.app_init()
    analytics.collect_analytics("page_change", "data_check")

    import SuperSTATs.styles as style

    st.markdown(style.shimmer("#c18aff"), unsafe_allow_html=True)
    st.markdown("<div class='shimmer'>👾 Data Check 👾</div>", unsafe_allow_html=True)

    st.title("")

    if st.button(
        "Update Page",
        type="primary",
        use_container_width=True,
        key=f"update_page",
        on_click=analytics.button_press,
        args=("update_page",),
    ):
        st.session_state.df = load.organize_df(
            load.download_sheets_raw(st.secrets["GID_RAW"]).dropna(subset=["Timestamp"])
        )

    st.divider()

    df = st.session_state.df

    phases = ["AUTO", "TELE", "END"]

    for i in range(len(phases)):
        df.loc[:, phases[i]] = load.add_cols(
            df,
            phases[i],
        )

    df["Score Sum"] = df[phases].sum(axis=1)

    scout = st.selectbox(
        "Scout:",
        ["None"]
        + [scout for scout in st.session_state.scouts if scout in df["Name"].unique()],
    )

    if scout != "None":
        df_raw = load.download_sheets_raw(st.secrets["GID_RAW"]).dropna(
            subset=["Timestamp"]
        )
        df_raw = df_raw.sort_values(["Match", "Timestamp"], ascending=[True, True])
        df_raw = df_raw[df_raw["Event Key"] == st.secrets["DEFAULT_EVENT_KEY"]]
        df_raw = df_raw.drop_duplicates(subset=["Team", "Match Type", "Match"])

        match_type, match_num = st.selectbox(
            "Match:", df[df["Name"] == scout]["Match Name"]
        ).split()

        st.divider()

        scout_match = df_raw[
            (df_raw["Name"] == scout)
            & (df_raw["Match Type"] == match_type)
            & (df_raw["Match"] == float(match_num))
        ]

        edited_match = st.data_editor(scout_match.T, use_container_width=True)
        match_dict = list(edited_match.to_dict().values())[0]

        form_ = st.session_state.forms["STATS_FORM"]
        set_entries = form_["set"]
        gen_entries = form_["gen"]

        entries = {**set_entries, **gen_entries}

        for entry, value in match_dict.items():
            if entry in entries:
                set_entries[entry] = value

        form_entries = [
            f"&entry.{entries[entry]}={set_entries[entry]}" for entry in entries
        ]

        prefill_url = f"{st.secrets['STATS_FORM'].split('/viewform')[0]}/formResponse?usp=pp_url{''.join(form_entries)}&submit=Submit"

        if st.button(
            "Submit",
            type="primary",
            use_container_width=True,
            key=f"submit_data",
            on_click=analytics.button_press,
            args=("submit_data",),
        ):
            requests.get(prefill_url)
            st.balloons()

        st.stop()

    st.divider()

    filters = [
        "❓ Missing Teams",
        "💭 Missing Comments",
        "🚨 TBA Score Variation",
    ]

    selected_filters = st.multiselect("Filters:", filters, [filters[0]])

    start_time = time.time()

    thresholds_raw = st.session_state.configs["Variance Slider Thresholds"]
    thresholds = {}

    for config in thresholds_raw:
        config = config.split("=")
        thresholds[config[0]] = int(config[1])

    if filters[2] in selected_filters:
        with st.form("Threshold Slider", clear_on_submit=False):
            variance_threshold = st.slider(
                "Variance Threshold:",
                value=thresholds["default"],
                min_value=thresholds["min"],
                max_value=thresholds["max"],
                step=1,
            )
            st.form_submit_button(
                "Set Threshold", type="primary", use_container_width=True
            )

    matches = st.session_state.matches

    df["Match Name"] = df["Match Type"] + " " + df["Match"].astype(int).astype(str)

    grouped = df.groupby("Match Name")
    df_matches = {match: group for match, group in grouped}

    if not selected_filters:
        st.error("⚠️ No Filters Selected")

    def sort_key(match):
        """
        Returns a key used for sorting matches.

        The key is a tuple containing two elements:
        - The first element is a numeric value representing the match type order.
            The order is defined as follows:
                - "Quals" matches have the lowest order (1).
                - "Playoffs" matches have a higher order (2).
                - "Finals" matches have the highest order (3).
                - Any other match type has the highest order (4).
        - The second element is the match number as an integer.

        Parameters:
        match (str): The match string in the format "<match_type> <match_number>".

        Returns:
        tuple: A tuple containing the match type order and the match number.
        """
        parts = match.split()
        match_order = {"Quals": 1, "Playoffs": 2, "Finals": 3}
        return (match_order.get(parts[0], 4), int(parts[1]))

    sorted_matches = sorted(df_matches.keys(), key=sort_key)
    df_matches = {match: df_matches[match] for match in sorted_matches}

    match_keys = {}
    match_data = st.session_state.match_data

    try:
        match_keys = match_data.set_index("Match Name")["key"].to_dict()
    except:
        st.error("⚠️ Event not started")
        st.stop()

    tba_json = load.download_sheets_raw(st.secrets["GID_TBA_JSON"])
    tba_columns = {row["TBA"]: row["Column"] for _, row in tba_json.iterrows()}

    df_cols = load.download_sheets_raw(st.secrets["GID_RAW"]).dropna(
        subset=["Timestamp"]
    )
    df_cols = df_cols.sort_values(["Match", "Timestamp"], ascending=[True, True])
    df_cols = df_cols.drop_duplicates(subset=["Team", "Match Type", "Match"])
    df_cols = df_cols[df_cols["Event Key"] == st.secrets["DEFAULT_EVENT_KEY"]]
    row_columns = df_cols.columns.to_list()

    for match_name, match_info in df_matches.items():
        current_match = df_matches[match_name]
        match_teams = matches.loc[matches["Match"] == match_name]
        match_teams = match_teams.drop(columns=["Match"])

        team_nums = current_match["Team"].tolist()
        tba_teams = match_teams.values.tolist()[0]

        with st.expander(match_name):
            data_variance = False

            if filters[0] in selected_filters:
                sorted_team_nums = sorted(team_nums)
                sorted_tba_teams = sorted(tba_teams)
                missing_teams = list(set(sorted_tba_teams).difference(sorted_team_nums))

                if sorted_team_nums != sorted_tba_teams:
                    st.subheader(f"Team Count: {len(team_nums)}/6", False)

                    columns = st.columns(3)

                    columns[0].subheader("SN Teams", False)
                    columns[0].write(sorted_team_nums)

                    columns[1].subheader("TBA Teams", False)
                    columns[1].write(sorted_tba_teams)

                    columns[2].subheader("Missing Teams", False)
                    columns[2].write(sorted(missing_teams))

                    score_breakdown = match_data[
                        match_data["Match Name"] == match_name
                    ]["score_breakdown"].to_list()[0]

                    calc_teams = {}

                    for team in missing_teams:
                        column_name = None

                        for column in match_teams.columns:
                            for value in match_teams[column]:
                                if team == value:
                                    column_name = column
                                    break

                            if column_name:
                                break

                        alliance_color, alliance_num = column_name.split()
                        calc_teams[team] = {
                            "color": alliance_color,
                            "number": alliance_num,
                        }

                    blue_missing, red_missing = (
                        sum(1 for team in calc_teams.values() if team["color"] == color)
                        for color in ["Blue", "Red"]
                    )

                    try:
                        if blue_missing == 1 or red_missing == 1:
                            all_data = []

                            for team in calc_teams:
                                alliance_counts = {}
                                tba_counts = {}
                                calc_values = {}

                                for tba, col in tba_columns.items():
                                    tba_counts[tba] = score_breakdown[
                                        calc_teams[team]["color"].lower()
                                    ][tba]

                                team_color = calc_teams[team]["color"]

                                alliance_df = match_info[
                                    match_info["Team Color"] == team_color[0]
                                ]

                                for tba, col in tba_columns.items():
                                    alliance_counts[col] = alliance_df[col].sum()

                                for i in range(len(tba_counts.keys())):
                                    tba_count = list(tba_counts.values())[i]
                                    alliance_count = list(alliance_counts.values())[i]
                                    count_diff = tba_count - alliance_count

                                    calc_values[list(alliance_counts.keys())[i]] = (
                                        count_diff if count_diff > 0 else 0
                                    )

                                match_split = match_name.split()

                                custom_fields = {
                                    "Timestamp": datetime.now().strftime(
                                        "%m/%d/%Y %H:%M:%S"
                                    ),
                                    "Name": "Calc",
                                    "Match Type": match_split[0],
                                    "Match": match_split[1],
                                    "Team Color": team_color[0],
                                    "Team": team,
                                    "Event Key": st.secrets["DEFAULT_EVENT_KEY"],
                                    "COMMENT_GENERAL_STR_1": "",
                                }

                                calc_df = pd.concat(
                                    [
                                        pd.DataFrame(custom_fields, index=[0]),
                                        pd.DataFrame(calc_values, index=[0]),
                                    ],
                                    axis=1,
                                )

                                for col in row_columns:
                                    if col not in calc_df:
                                        calc_df[col] = 0

                                calc_df = calc_df[row_columns]

                                if team_color == "Red" and red_missing > 1:
                                    pass
                                elif team_color == "Blue" and blue_missing > 1:
                                    pass
                                else:
                                    all_data.append(calc_df)

                            all_calc = (
                                pd.concat(all_data, ignore_index=True)
                                .set_index(df.columns[0])
                                .astype(str)
                            )

                            st.data_editor(all_calc)
                    except:
                        st.error("⚠️ No TBA data")

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

                    st.subheader(f"💭 {no_comm_teams}", False)
                    data_variance = True

            if filters[2] in selected_filters:
                try:
                    score_breakdown = match_data[
                        match_data["Match Name"] == match_name
                    ]["score_breakdown"]

                    score_breakdown = score_breakdown.to_json(orient="records")
                    data = json.loads(score_breakdown)

                    red_data = data[0]["red"]
                    blue_data = data[0]["blue"]

                    red_tba_score = red_data["totalPoints"] - red_data["foulPoints"]
                    blue_tba_score = blue_data["totalPoints"] - blue_data["foulPoints"]

                    def get_variance(color, tba_score):
                        """
                        Calculates the variance between the given team's score and the TBA score.

                        Parameters:
                        - color (str): The color of the team ("R" for red, "B" for blue).
                        - tba_score (int): The TBA score to compare against.

                        Returns:
                        None
                        """
                        team_df = match_info[match_info["Team Color"] == color[0]]
                        team_score = int(team_df["Score Sum"].sum())
                        team_variance = tba_score - team_score
                        text_color = "#f8312f" if color[0] == "R" else "#0074ba"

                        if abs(team_variance) >= variance_threshold:
                            colored_header = f"<span style='color: {text_color}; font-size: 2em;'>[{color}]</span>"
                            default_header = f"<span style='color: white; font-size: 2em;'> Point Variance: {-team_variance} ({team_score}/{tba_score})</span>"

                            st.markdown(
                                f"{colored_header}{default_header}",
                                unsafe_allow_html=True,
                            )

                            st.write(
                                team_df[["Team", "AUTO", "TELE", "END", "Score Sum"]]
                            )

                            nonlocal data_variance
                            data_variance = True

                    get_variance("RED", red_tba_score)
                    get_variance("BLUE", blue_tba_score)

                    if st.toggle("Show TBA JSON", False):
                        with st.container(border=True):
                            st.json(data[0])
                except:
                    st.error("⚠️ Invalid TBA Match Data")

            if data_variance:
                show_raw(match_name, match_info, match_keys[match_name])

    st.markdown(
        f"<span style='font-size: small; color: #808080;'>Loaded in {round(time.time() - start_time, 2)} seconds...</span>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
