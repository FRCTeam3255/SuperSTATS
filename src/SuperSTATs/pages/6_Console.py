import SuperSTATs.loader as load
import plotly.express as px
import streamlit as st
import pickle, json
import pandas as pd

# [STATS INPUT]
# Stat Taker List

st.set_page_config(
    page_title="[CONSOLE] SN Stats",
    page_icon="⚙️",
    initial_sidebar_state="expanded",
    layout="wide",
)


def main():
    load.init_page()

    display = st.empty()

    password = st.secrets["ADMIN_PASSWORD"]

    if "admin_signed_in" not in st.session_state:
        st.session_state.admin_signed_in = False

    if not st.session_state.admin_signed_in:
        pass_input = display.text_input("Password:", type="password")

        if pass_input == password:
            st.session_state.admin_signed_in = True

    if st.session_state.admin_signed_in:
        display.button("Update Page", type="primary", use_container_width=True)

        with st.expander("Set Presets"):
            uploaded_file = st.file_uploader("Override Presets:")

            if uploaded_file is not None:
                if st.button("Set Presets", use_container_width=True):
                    bytes_data = uploaded_file.getvalue()
                    bytes_formatted = bytes_data.decode("utf-8")
                    data = json.loads(bytes_formatted)

                    with open("presets.pickle", "wb") as f:
                        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
                    st.success("Successfully Updated Presets!")

        with st.expander("Delete Presets"):
            for preset in st.session_state.presets.keys():
                st.checkbox(preset, False)
            # if st.button("Set Presets", use_container_width=True):
            #     bytes_data = uploaded_file.getvalue()
            #     bytes_formatted = bytes_data.decode("utf-8")
            #     data = json.loads(bytes_formatted)

            #     with open("presets.pickle", "wb") as f:
            #         pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
            #     st.success("Successfully Updated Presets!")

        st.download_button(
            "Download Presets",
            json.dumps(st.session_state.presets).encode("utf-8"),
            "Presets.json",
            use_container_width=True,
        )

        # df = pd.DataFrame(
        #     dict(
        #         r=[1, 5, 2, 2, 3],
        #         theta=sections,
        #     )
        # )
        # radar_chart = px.line_polar(df, r="r", theta="theta", line_close=True)

        with st.expander("Radio Chart:"):
            teams = {}
            teams_raw = st.session_state.team_info_dict.items()

            for team in teams_raw:
                teams[team[1]] = int(team[0])

            team_options = [
                f"{team_name} | {team_num}" for team_name, team_num in teams.items()
            ]

            selected_team = st.selectbox("Select Team:", sorted(team_options))
            team_num = int(selected_team.split(" | ")[1])

            df = load.download_sheets_raw(st.secrets["GID_RAW"]).dropna(
                subset="Timestamp"
            )
            df = df.loc[(df["Team"] == team_num)]

            sections = load.get_match_sections(df)

            radar_r = []
            radar_t = []

            for section in sections:
                section_cols = [col for col in df.columns if col.startswith(section)]

                col_sum = df[section_cols].sum().sum()
                radar_r.append(abs(col_sum))
                radar_t.append(section)

            # st.write(f"R: {radar_r}")
            # st.write(f"T: {radar_t}")
            radar_df = pd.DataFrame(
                {
                    "r": radar_r,
                    "theta": radar_t,
                }
            )

            radar_chart = px.line_polar(radar_df, r="r", theta="theta", line_close=True)
            radar_chart.update_traces(fill="toself")

            radar_chart.update_layout(
                polar_bgcolor="#212121",
                polar_radialaxis_visible=False,
                polar_angularaxis_showline=False,
                paper_bgcolor="#141414",
            )

            radar_chart.update_traces(
                fill="toself",
                fillcolor="#141414",
                line=dict(
                    color="#000000",
                    width=2,
                ),
            )

            st.plotly_chart(radar_chart)

            # for score_type in sections:
            #     columns = [col for col in df.columns if col.startswith(score_type)]
            #     df[f"{score_type.strip('_').title()} Score"] = df[columns].sum(axis=1)
            #     st.write(df[f"{score_type.strip('_').title()} Score"])


if __name__ == "__main__":
    main()
