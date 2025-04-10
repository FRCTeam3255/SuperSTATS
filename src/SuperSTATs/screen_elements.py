import datetime
import pandas as pd
import streamlit as st
import styles as style
import SuperSTATs.load as load


@st.cache_data(show_spinner=False, persist=True)
def robot_photo_dropdown(input_team):
    """
    Displays a dropdown with the robot photo for a given team.
    Args:
        input_team (int): The team number for which the robot photo is to be displayed.
    Retrieves the robot photo URL for the specified team and competition year using The Blue Alliance API.
    If a photo is available, it is displayed in an expander with the caption "Team {input_team} Robot".
    If no photo is available, a warning message is shown.
    Note:
        The function assumes that `st` (Streamlit) and `tba` (The Blue Alliance API client) are already imported and configured.
        The function also assumes that `get_event_year` is a predefined function that retrieves the event year.
    Raises:
        KeyError: If the "DEFAULT_EVENT_KEY" is not found in `st.secrets`.
        IndexError: If the media list does not contain at least two elements.
    """
    team_key = f"frc{input_team}"
    competition_year = load.DataInitializer.get_event_year(st.secrets["DEFAULT_EVENT_KEY"])

    if competition_year != None:
        media = st.session_state.tba.team_media(team_key, competition_year)
        robot_photo_url = media[1]["direct_url"] if len(media) > 1 else None
        with st.expander("Robot Image", False):
            if robot_photo_url:
                st.image(
                    robot_photo_url,
                    caption=f"Team {input_team} Robot",
                    use_container_width=True,
                )
            else:
                st.warning("⚠️ No robot photo available")

def display_header(title):
    """
    Displays a styled header with a rainbow effect.
    Args:
        title (str): The text to display as the header.
    Notes:
        - This function uses Streamlit's `st.markdown` to render HTML content.
        - The `style.rainbow()` function is assumed to provide the necessary CSS for the rainbow effect.
        - The `unsafe_allow_html=True` parameter is used to allow rendering of raw HTML.
    """

    st.markdown(style.rainbow(), unsafe_allow_html=True)
    st.markdown(f"<div class='rainbow'>{title}</div>", unsafe_allow_html=True)


def display_event_link(event_key):
    """
    Displays a clickable link to an event on The Blue Alliance website using Streamlit's markdown.
    Args:
        event_key (str): The unique identifier for the event. This will be used to construct
                         the URL for the event on The Blue Alliance website.
    Notes:
        - The link is styled to appear centered, with a font size of 1.5em, white text color,
          and no underline.
        - This function uses Streamlit's `st.markdown` with `unsafe_allow_html=True` to render
          custom HTML.
    """

    st.markdown(
        f"<div style='text-align: center; font-size: 1.5em;'><a href='https://www.thebluealliance.com/event/{event_key}' style='color: #ffffff; text-decoration: none;'>Current Dataframe: {event_key}</a></div>",
        unsafe_allow_html=True,
    )


def get_team_selection(teams):
    """
    Creates a Streamlit UI element for team selection.
    Parameters:
        teams (list): A list of team names to populate the selection dropdown.
    Returns:
        tuple: A tuple containing:
            - team (str): The selected team from the dropdown. Defaults to "All Matches" if no specific team is selected.
            - columns (list): A list of Streamlit column objects used for layout.
    """

    columns = st.columns(2)
    team = columns[0].selectbox("Team Selection:", ["All Matches"] + teams)
    return team, columns


def display_scoreboard(matches, team, columns):
    """
    Displays a scoreboard for matches with scores and optional team filtering.
    Args:
        matches (pd.DataFrame): A DataFrame containing match data. Must include a "Match" column.
        team (str): The team to filter matches by. Use "All Matches" to display all matches.
        columns (list): A list of Streamlit column objects for UI interactions.
    Raises:
        KeyError: If the expected keys are missing in the match data's "score_breakdown".
        Exception: For any other errors encountered during processing.
    Notes:
        - The function merges match data with session state data to retrieve score breakdowns.
        - Scores are displayed with red (🔴) and blue (🔵) indicators, and a trophy (🏆) for the winning team.
        - If team filtering is enabled, matches involving the specified team are highlighted.
        - The function uses Streamlit's `st.dataframe` to display the processed match data.
    """

    try:
        # Merge match data
        matches = pd.merge(
            matches,
            st.session_state.match_data[["Match Name", "score_breakdown"]],
            left_on="Match",
            right_on="Match Name",
            how="left",
        )

        # Update scores
        for match_name in matches["Match"]:
            data = matches[matches["Match"] == match_name]["score_breakdown"].to_list()[
                0
            ]
            try:
                red_score = int(data["red"]["totalPoints"])
                blue_score = int(data["blue"]["totalPoints"])

                red_data = f"🔴 {red_score:3}" + (
                    " 🏆" if red_score > blue_score else ""
                )
                blue_data = f"🔵 {blue_score:3}" + (
                    " 🏆" if blue_score > red_score else ""
                )
            except KeyError:
                red_data = blue_data = "🕑 N/A"

            matches.loc[matches["Match"] == match_name, "Red Score"] = red_data
            matches.loc[matches["Match"] == match_name, "Blue Score"] = blue_data

        matches = matches.drop(columns=["Match Name", "score_breakdown"])

        # Filter matches by team
        if team != "All Matches":
            team_id = int(str(team).split(" | ")[0])
            use_team_colors = columns[1].toggle("Use Team Colors")
            team_colors = st.session_state.team_colors[str(team_id)]

            if use_team_colors:
                if team_colors[0] == "003255" or team_colors[1] == "003255":
                    columns[1].toggle("Use Secondary Color", disabled=True)
                    st.warning("⚠️ Team Colors Not Found")
                    team_color = "#ffffff"
                else:
                    if columns[1].toggle("Use Secondary Color"):
                        team_color = team_colors[1]
                    else:
                        team_color = team_colors[0]
            else:
                columns[1].toggle("Use Secondary Color", disabled=True)
                team_color = "#ffffff"

            team_cols = [
                col
                for col in matches.columns
                if col not in ["Match", "Red Score", "Blue Score"]
            ]

            matches = matches[matches[team_cols].isin([team_id]).any(axis=1)].astype(
                str
            )

            matches = matches.style.map(
                lambda cell: (
                    f"color: {team_color}" if cell == str(team_id) else "color: #808080"
                ),
                subset=pd.IndexSlice[:, team_cols],
            )
        else:
            matches = matches.astype(str)

        # Display matches
        st.dataframe(
            matches.set_index("Match") if team == "All Matches" else matches,
            use_container_width=True,
        )

    except Exception as e:
        st.error(f"⚠️ Error processing matches: {e}")


def display_nexus_data():
    """
    Displays Nexus data in a Streamlit application.
    This function retrieves Nexus data from the Streamlit session state and
    displays it in an expandable section. It includes information about the
    currently playing item, queue status, the next match, and the alliance color.
    The displayed information includes:
    - "Now Playing": The current item being played.
    - "Queue Status": The status of the queue (e.g., READY, WAITING).
    - "Next Match": Details of the next scheduled match, if available.
    - "Alliance Color": The color of the alliance for the next match.
    If no Nexus data or scheduled matches are found, appropriate messages are displayed.
    Dependencies:
    - Requires `st.session_state.nexus_data` to contain the Nexus data.
    - Requires `st.session_state.console["practice_mode"]` for the expander label.
    Note:
    - This function is designed to be used within a Streamlit application.
    """

    nexus_data = st.session_state.nexus_data

    if nexus_data:
        with st.expander("Nexus Data", st.session_state.console["practice_mode"]):
            st.subheader("Now Playing")
            st.write(nexus_data["now_playing"])

            st.subheader("Queue Status")
            queue_status = nexus_data.get("queue_status", "").upper()
            next_match = nexus_data.get("next_match")
            alliance_color = nexus_data.get("alliance_color")

            if next_match:
                st.write(f"[{queue_status}] {next_match} on {alliance_color} alliance")
            else:
                st.write("No scheduled matches found")


def display_event_keys():
    """
    Displays a Streamlit UI component for viewing and selecting event keys.
    This function creates an expandable section in a Streamlit app where users
    can input a year, view a list of events for that year, and optionally select
    an event to display its key. If no specific event is selected, all event keys
    for the given year are displayed.
    The function uses the following:
    - A number input for the user to specify the year.
    - A selectbox for searching and selecting events.
    - Displays the selected event's key or all event keys for the year.
    Behavior:
    - If a specific event is selected, its key and name are displayed as a subheader.
    - If "All Events" is selected, all event keys and names are listed.
    - If no events are found for the given year, an error message is displayed.
    Dependencies:
    - `st.expander`: Used to create an expandable section.
    - `st.columns`: Used to create two columns for year input and event selection.
    - `st.session_state`: Accesses session state for practice mode and event data.
    - `st.number_input`: Used for year input.
    - `st.selectbox`: Used for event selection.
    - `st.subheader` and `st.text`: Used for displaying event information.
    - `st.error`: Used for displaying error messages.
    Note:
    - The function assumes `st.session_state.tba.events(year)` returns a list of
      events, where each event is a dictionary containing "name" and "key".
    - The default year is set to the current year using `datetime.datetime.now().year`.
    """

    with st.expander("Event Keys"):
        columns = st.columns(2)
        year = columns[0].number_input(
            "Year:", min_value=0, step=1, value=datetime.datetime.now().year
        )
        events = st.session_state.tba.events(year)
        event_keys = {event["name"]: event["key"] for event in events}
        searched_event = columns[1].selectbox(
            "Search Events", ["All Events"] + list(event_keys.keys())
        )
        if searched_event != "All Events":
            selected_key = event_keys.get(searched_event, "")
            st.subheader(f"[{selected_key}] {searched_event}")
        else:
            for name, key in event_keys.items():
                st.text(f"[{key}] {name}")
            if len(event_keys) == 0:
                st.error(f"⚠️ No keys found for {year}")


def generate_qr(contents):
    """
    Generates a QR code image from the given contents and returns it as a byte stream.
    Args:
        contents (str): The data to encode in the QR code.
    Returns:
        bytes: The QR code image in JPEG format as a byte stream.
    """

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
    )

    qr.add_data(contents)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#ffffff", back_color="#141414")

    byte_stream = io.BytesIO()

    img.save(byte_stream, format="JPEG")
    bytes_image = byte_stream.getvalue()

    return bytes_image