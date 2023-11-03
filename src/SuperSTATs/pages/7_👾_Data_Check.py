import SuperSTATs.loader as load
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="[STATS] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
    layout="wide",
)

df = load.download_sheets_raw(st.secrets["GID_RAW"]).dropna(subset="Timestamp")

def show_raw(match_num, match_info):
    try:
        if st.checkbox("📊 Show RAW Data", key=f"{match_num}_RAW"):
            st.write(match_info["RAW Data"])
    except:
        pass


def main():
    load.init_page()

    st.markdown(
        "<h1 style='text-align: center;'>👾 Data Check 👾</h1>",
        unsafe_allow_html=True,
    )
    st.title("")

    grouped = df.groupby("Match")
    df_matches = {match: group for match, group in grouped}

    filters = [
        "❓ Missing Teams", "💭 Missing Comments", "🔄️ [WIP] Wrong Entry Amount", "📈 [TODO] Score Outliers"
    ]

    selected_filters = st.multiselect("Filters:", filters)

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
                "RAW Data": current_match_df
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
                    
                    col_1.subheader("Data")
                    col_1.write(teams_data)
                    
                    col_2.subheader("Actual")
                    col_2.write(teams_actual)


            if "💭 Missing Comments" in selected_filters:
                comment_df = df[["Team", "Match", "COMMENT_GENERAL_1"]]
                comment_df = comment_df[comment_df["Match"] == match_num].drop("Match", axis=1)
                comment_df = comment_df[comment_df['COMMENT_GENERAL_1'].isnull()]
                
                if not comment_df.empty:
                    show_raw(match_num, match_info)
                    st.header("Missing Comments")
                    st.write(comment_df)

            if "🔄️ [WIP] Wrong Entry Amount" in selected_filters:
                entries_df = df[["Team", "Match"]]
                entries_df = entries_df[entries_df["Match"] == match_num].drop("Match", axis=1)
                entries_length = len(entries_df)

                if entries_length != 6:
                    show_raw(match_num, match_info)
                    team_entries = []
                    st.header("Wrong Entry Amount")

                    for entry in entries_df.values:
                        team_entries.append(int(entry))

                    output = f"{entries_length}/6 Entries : {team_entries}"
                    st.write(output)

if __name__ == "__main__":
    main()
