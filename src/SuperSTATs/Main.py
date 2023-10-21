import SuperSTATs.loader as load
import streamlit as st


# [NOTE]
# from SuperSTATs.app import *
# df = load.download_sheets_raw("st.secrets['GID_RAW']")
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


def main():
    load.init_page()

    main_title = st.empty()

    main_title.title("INITIALIZING...")

    # if "team_info_dict" not in st.session_state:
    #     st.session_state.team_info_dict = download_team_info()

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
