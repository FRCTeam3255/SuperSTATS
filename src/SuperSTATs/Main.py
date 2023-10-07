import streamlit as st
import pandas as pd
import tbapy

# [NOTE]
# from SuperSTATs.app import *
# df = stats.download_sheets_raw("1318549794")
# df = df.dropna(subset="Timestamp")
# df.loc[(df["Team"]==3255) | (df["Team"]==254)]
# df.loc[df["Team"]==3255].sum(numeric_only=True)
# df.groupby("Team").sum(numeric_only=True)
# df.sort_values("match", ascending=False)
# df = df.drop(columns=df.filter(regex=".1").columns)
# df.filter(regex="Auton").sum(axis=1)

st.set_page_config(
    page_title="SN Stats",
    page_icon="🤖",
    initial_sidebar_state="collapsed",
    menu_items={"About": "Developed by FRC Team 3255 - SuperNURDs"},
)

tba = tbapy.TBA(st.secrets["TBA_API"])


def build_sheet_url(url):
    doc_id, sheet_id = url.split("/")[5:7]
    sheet_id = sheet_id.split("gid=")[1]
    return f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={sheet_id}"


def download_sheets_raw(gid):
    url = f"https://docs.google.com/spreadsheets/d/{st.secrets['GSHEET_DOC_ID_ALT']}/edit#gid={gid}"
    return pd.read_csv(build_sheet_url(url))


def get_team(team):
    return tba.team(f"frc{int(team)}", True)


@st.cache_data
def download_team_info():
    df = download_sheets_raw("1318549794")
    local_team_info_dict = {}
    for team in df["Team"].unique():
        local_team_info_dict[team] = get_team(team)["nickname"]
    return local_team_info_dict


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
        "<div style='display: flex; justify-content: center; font-size: 4em;'>🤖 SuperSTATs 🤖</div>",
        unsafe_allow_html=True,
    )

    logo_path = "src/SuperSTATs/images/SN_Logo.png"

    st.title("")
    st.image(logo_path, use_column_width=True)

    st.title("")
    st.markdown(
        """
        <div style="display: flex; flex-direction: column; align-items: center; text-align: center;">
            <a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ/" style="color: #ffffff; font-size: 2em;">SuperNURDs Website</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
