import streamlit as st
import pandas as pd
import tbapy

# [NOTE]
# from SuperSTATs.app import *
# df = stats.download_sheets_raw("st.secrets['GID_RAW']")
# df = df.dropna(subset="Timestamp")
# df.loc[(df["Team"]==3255) | (df["Team"]==254)]
# df.loc[df["Team"]==3255].sum(numeric_only=True)
# df.groupby("Team").sum(numeric_only=True)
# df.sort_values("match", ascending=False)
# df = df.drop(columns=df.filter(regex=".1").columns)
# df.filter(regex="Auto").sum(axis=1)

st.set_page_config(
    page_title="SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
    menu_items={"About": "Developed by FRC Team 3255 - SuperNURDs"},
)

tba = tbapy.TBA(st.secrets["TBA_API"])


def build_sheet_url(url):
    doc_id, sheet_id = url.split("/")[5:7]
    sheet_id = sheet_id.split("gid=")[1]
    return f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={sheet_id}"


def download_sheets_raw(gid):
    url = f"https://docs.google.com/spreadsheets/d/{st.secrets['GSHEET_DOC_ID']}/edit#gid={gid}"
    df = pd.read_csv(build_sheet_url(url))
    df.columns = (
        df.columns.str.lstrip()
        .str.replace("[", repl="", regex=False)
        .str.replace("]", repl="", regex=False)
    )
    return df


def get_team(team):
    return tba.team(f"frc{int(team)}", True)


@st.cache_data
def download_team_info():
    df = download_sheets_raw(st.secrets["GID_RAW"])
    local_team_info_dict = {}
    for team in df["Team"].unique():
        local_team_info_dict[team] = get_team(team).get("nickname", "N/A")
    return local_team_info_dict


def get_match_sections(df):
    filtered_columns = []
    for column in df.columns:
        if any(c.isdigit() for c in column.split("_")[-1]):
            filtered_columns.append(column)

    sections = []
    for column in filtered_columns:
        column = column.split("_")[0]
        sections.append(column)

    return sorted(list(set(sections)))


def set_font():
    streamlit_style = """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100&display=swap');

            html, body, [class*="css"]  {
            font-family: 'Roboto', sans-serif;
            }
            </style>
            """
    st.markdown(streamlit_style, unsafe_allow_html=True)


def main():
    set_font()

    main_title = st.empty()

    main_title.title("INITIALIZING...")

    if "team_info_dict" not in st.session_state:
        st.session_state.team_info_dict = download_team_info()

    main_title.markdown(
        "<div style='display: flex; justify-content: center; font-size: 40px;'><b>🤖 SuperSTATs 🤖</b></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="display: flex; flex-direction: column; align-items: center; text-align: center;">
            <a href="https://docs.google.com/spreadsheets/d/1KboyFTIZJiIW_33Z9_ea8jtYkV3T-fuS659ezwsXYmY/edit#gid=1878511843" style="color: #0070E0; font-size: 25px;">Raw Data Sheet</a>
            <a href="https://www.supernurds.com/statsinput" style="color: #0070E0; font-size: 25px;">Stats Input Form</a>
            <a href="https://docs.google.com/forms/d/1P32axMIgTIkHJUZuP4BPpiVX1-CMNHobgsAW-aZkse4" style="color: #0070E0; font-size: 25px;">Scouting Form</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    logo_path = "src/SuperSTATs/images/SN_Logo.png"

    st.title("")
    st.image(logo_path)

    st.title("")


if __name__ == "__main__":
    main()
