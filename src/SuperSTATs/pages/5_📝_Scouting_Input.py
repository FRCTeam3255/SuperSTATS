import SuperSTATs.analytics as analytics
import SuperSTATs.load as load
import requests, pickle
import streamlit as st
import qrcode
import io


def main():
    load.app_init()
    analytics.collect_analytics("page_change", "scouting_input")


    st.title("📝 Scouting Input 📝")

    if st.button(
        "Update Page",
        type="primary",
        use_container_width=True,
        key=f"update_page",
        on_click=analytics.button_press,
        args=("update_page",),
    ):
        st.session_state.scouting = load.download_sheets_raw(st.secrets["GID_SCOUTING"])

    st.divider()

    # Add css to increase button width
    st.markdown(
        """
        <style>
        .st-emotion-cache-nnubno {
            width: 100px;
        }
        svg {
            transform: scale(2);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    entries = st.session_state.forms["SCOUTING_FORM"]["set"]

    df = st.session_state.scouting

    scouted_teams = df["Team #"].unique()

    unscouted_teams_raw = [
        team for team in st.session_state.team_info if team not in scouted_teams
    ]

    teams_raw = st.session_state.team_info.items()

    if len(unscouted_teams_raw) == 0:
        st.success("All teams have scouting info!")
        st.balloons()
        st.stop()

    submitted = False

    with st.form("Scouting Input", clear_on_submit=True, border=False):
        unscouted_teams = []
        for num, name in teams_raw:
            if num in unscouted_teams_raw:
                unscouted_teams.append(f"{num} | {name}")

        team_num = st.selectbox("Team:", unscouted_teams)
        team_num = team_num.split(" | ")[0]

        top_columns = st.columns(2)
        bot_columns = st.columns(2)

        length = top_columns[0].number_input(
            "Frame Size LENGTH [NO BUMPERS]:", step=0.5, min_value=0.0
        )

        width = top_columns[1].number_input(
            "Frame Size WIDTH [NO BUMPERS]:", step=0.5, min_value=0.0
        )

        weight = bot_columns[0].number_input(
            "Weight [NO BATTERY]:", step=0.5, min_value=0.0
        )

        dt_type = bot_columns[1].radio(
            "Drivetrain Type:",
            ["Swerve", "Westcoast", "Mecanum", "Other"],
            horizontal=True,
        )

        comments = st.text_input("Additional Comments:")

        gen_combined = {
            "Team #": team_num,
            "Frame Size LENGTH": length,
            "Frame Size WIDTH": width,
            "Weight": weight,
            "Drivetrain Type": dt_type,
            "Comments": comments.replace(" ", "+"),
        }

        form_entries = [
            f"&entry.{entries[entry]}={gen_combined[entry]}" for entry in gen_combined
        ]

        prefill_url = f"{st.secrets['SCOUTING_FORM'].split('/viewform')[0]}/formResponse?usp=pp_url{''.join(form_entries)}&submit=Submit"

        submitted = st.form_submit_button(
            "Submit", type="primary", use_container_width=True
        )

    if submitted:
        req = requests.get(prefill_url)
        if req.status_code == 200:
            st.balloons()
            st.toast("Submission successful!", icon="✅")
        else:
            st.toast("Submission unsuccessful! Use QR Code...", icon="⚠️")

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
            )

            qr.add_data(prefill_url)
            qr.make(fit=True)

            img = qr.make_image(fill_color="#ffffff", back_color="#141414")

            byte_stream = io.BytesIO()

            img.save(byte_stream, format="JPEG")
            bytes_image = byte_stream.getvalue()

            st.image(bytes_image, use_container_width=True)

    st.write("""---""")

    with st.expander("Pit Map"):
        pit_map = st.file_uploader("Upload Map: ", type=["png", "jpg"])
        if pit_map:
            with open("src\\pickles\\map.pickle", "wb") as f:
                pickle.dump(pit_map, f, pickle.HIGHEST_PROTOCOL)
        else:
            try:
                with open("src\\pickles\\map.pickle", "rb") as f:
                    pit_map = pickle.load(f)
                st.image(pit_map, use_container_width=True)
            except:
                pass


if __name__ == "__main__":
    main()
