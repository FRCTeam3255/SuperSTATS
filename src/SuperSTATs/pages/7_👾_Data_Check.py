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
# df = df.drop("Timestamp", axis=1)


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
        "❓ Missing Team", "💭 Missing Comments", "⚠️ Duplicate Team Numbers", "❌ Wrong Number of Entries", "📈 Score Outliers", "📊 Show RAW Data"
    ]

    selected_filters = st.multiselect("Filters:", filters)

    st.write("""---""")

    all_data = {}

    for match_num, match_info in df_matches.items():
        current_match_df = df[df["Match"] == match_num]
        # st.write(current_match_df)

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
                "Show RAW Data": current_match_df
                }
        
        all_data[match_num] = data

    display_info = []
    
    if "❓ Missing Team" in selected_filters:
        display_info.append("Teams")
    
    if "📊 Show RAW Data" in selected_filters:
        display_info.append("Show RAW Data")

    match_df = st.session_state.global_match_df

    match_teams = {}
    for match in match_df.values:
        match_teams[match[0]] = list(match[1:])

    for match_num, match_info in all_data.items():

        match_name = (f"{match_info['Match Type']} {match_info['Match Number']}")
        teams_actual = sorted(list(map(int, match_teams[match_name])))
        teams_data = sorted(match_info["Teams"])

        if teams_actual != teams_data:
            with st.expander(f"{match_info['Match Type']} {match_num}"):
                col_1, col_2 = st.columns(2)
                
                col_1.subheader("Data")
                col_1.write(teams_data)
                
                col_2.subheader("Actual")
                col_2.write(teams_actual)

if __name__ == "__main__":
    main()
