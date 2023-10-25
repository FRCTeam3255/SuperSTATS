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


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    color_int = int(hex_color, 16)
    red = (color_int >> 16) & 255
    green = (color_int >> 8) & 255
    blue = color_int & 255
    return red, green, blue


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

    teams = {}
    teams_raw = st.session_state.team_info_dict.items()

    for team in teams_raw:
        teams[team[1]] = int(team[0])

    team_options = [
        f"{team_name} | {team_num}" for team_name, team_num in teams.items()
    ]

    col_1, col_2 = st.columns(2)
    selected_team = col_1.selectbox("Select Team:", sorted(team_options))
    team_num = int(selected_team.split(" | ")[1])
    team_1_color = hex_to_rgb(col_2.color_picker("Team Color:", value="#910000"))

    df = load.download_sheets_raw(st.secrets["GID_RAW"]).dropna(subset="Timestamp")
    df = df.loc[(df["Team"] == team_num)]
    sections = load.get_match_sections(df)

    section_cols = [
        col
        for col in df.columns
        if any(col.startswith(section) for section in sections)
    ]
    df = df[section_cols].reset_index(drop=True)

    column_values = {}
    for column in df:
        column_value = int(column.split("_")[2])
        sum_value = int(df[column].sum()) * column_value
        column_values[column] = sum_value

    sum_values = ["AUTO", "TELE", "END"]

    radar_r = []
    radar_t = []

    for sum_for in sum_values:
        value_sum = sum(
            value for key, value in column_values.items() if key.startswith(sum_for)
        )
        radar_r.append(value_sum)
        radar_t.append(sum_for)

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
        paper_bgcolor="#141414",
    )

    radar_chart.update_traces(
        fill="toself",
        fillcolor=f"rgba({team_1_color[0]}, {team_1_color[1]}, {team_1_color[2]}, 0.5)",
        line=dict(
            color="#000000",
            width=2,
        ),
    )

    st.plotly_chart(radar_chart)

    if st.checkbox("Show Raw Data"):
        st.dataframe(df)


if __name__ == "__main__":
    main()
