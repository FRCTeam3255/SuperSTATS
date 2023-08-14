import streamlit as st
import pandas as pd

# from SuperSTATs.supernurds.stats_data import *
# df = download_sheets_raw()
# df = df.dropna(subset="Timestamp")
# df.loc[(df["Team"]==3255) | (df["Team"]==254)]
# df.loc[df["Team"]==3255].sum(numeric_only=True)
# df.groupby("Team").sum(numeric_only=True)
# df.sort_values("match", ascending=False)

no_pick_url = f"https://docs.google.com/spreadsheets/d/{st.secrets['GSHEET_DOC_ID']}/edit#gid=1962951229"


def build_sheet_url(url):
    doc_id, sheet_id = url.split("/")[5:7]
    sheet_id = sheet_id.split("gid=")[1]
    return f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={sheet_id}"


def download_sheets_raw():
    url = f"https://docs.google.com/spreadsheets/d/{st.secrets['GSHEET_DOC_ID']}/edit#gid=1657585295"
    return pd.read_csv(build_sheet_url(url)).dropna(subset="Timestamp")


def view_matches(team: int):
    df = download_sheets_raw()
    df = df.dropna(subset="Timestamp")

    color_mapping = {"R": "🔴", "B": "🔵"}
    df["color"] = df["color"].map(color_mapping)

    return (
        df.loc[(df["Team"] == team), ["Team", "color", "match"]]
        .reset_index(drop=True)
        .astype({"Team": int, "match": int})
    )


def main():
    st.title("Row Types Per Match")

    df = download_sheets_raw()

    teams = df["Team"].unique().astype(int)
    selected_team = st.sidebar.selectbox(
        "Select Team:", teams, index=teams.tolist().index(3255)
    )

    selected_team_df = df[df["Team"] == selected_team]
    st.dataframe(selected_team_df[["Top Row", "Middle Row", "Bottom Row"]])

    row_types = ["Top Row", "Middle Row", "Bottom Row"]

    selected_row_types = []
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.checkbox(row_types[0], value=True):
            selected_row_types.append(row_types[0])

    with col2:
        if st.checkbox(row_types[1], value=True):
            selected_row_types.append(row_types[1])

    with col3:
        if st.checkbox(row_types[2], value=True):
            selected_row_types.append(row_types[2])

    if not selected_row_types:
        st.error("Please select at least one row type.")
        return

    match_values = selected_team_df["match"].tolist()

    chart_data = pd.DataFrame({"Match": match_values})

    for row_type in selected_row_types:
        row_values = selected_team_df[row_type].tolist()
        chart_data[row_type] = row_values

    chart_data = chart_data.set_index("Match")
    st.line_chart(chart_data)


if __name__ == "__main__":
    main()
