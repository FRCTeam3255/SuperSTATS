import json
import pickle
import SuperSTATs.load as load
import streamlit as st
import SuperSTATs.screen_elements as ui

def save_console_configs(
        settings_raw: dict,
        updated_configs: dict
    ) -> None:
    """
    Updates and saves the console configuration settings.
    This function updates the Streamlit session state with the provided 
    console settings and saves the updated configurations to a pickle file. 
    A success message is displayed to the user upon completion.
    Args:
        settings_raw (dict): The raw console settings to be saved in the session state.
        updated_configs (dict): The updated console configurations to be saved in the session state.
    Side Effects:
        - Updates `st.session_state.configs["Console"]` with `settings_raw`.
        - Updates `st.session_state.console` with `updated_configs`.
        - Saves the updated `st.session_state.configs` to a pickle file at 
          "src\\pickles\\configs.pickle".
        - Displays a toast notification to the user.
    Raises:
        Any exceptions raised during file operations or pickling will propagate.
    Note:
        The user is advised to refresh the application after the configurations 
        are updated to ensure the changes take effect.
    """

    st.session_state.configs["Console"] = settings_raw
    st.session_state.console = updated_configs

    with open("src\\pickles\\configs.pickle", "wb") as f:
        pickle.dump(st.session_state.configs, f, pickle.HIGHEST_PROTOCOL)

    st.toast("Successfully updated configs! Please refresh...", icon="✅")

def save_scouts(
        scout_list: list,
        scouts: list
    ) -> None:
    """
    Save the list of scouts and their assignments to a pickle file and update the session state.
    Args:
        scout_list (list): A list of assigned scouts.
        scouts (list): A list of all scouts.
    Side Effects:
        - Updates the `st.session_state.assigned` with the provided `scout_list`.
        - Saves the `scouts` and `scout_list` data to a pickle file at "src\\pickles\\scouts.pickle".
        - Displays a toast notification indicating successful operation.
    Note:
        The function assumes the use of the Streamlit library for session state and toast notifications.
    """

    st.session_state.assigned = scout_list

    with open("src\\pickles\\scouts.pickle", "wb") as f:
        pickle.dump([scouts, scout_list], f, pickle.HIGHEST_PROTOCOL)

    st.toast("Successfully set scouters! Please refresh...", icon="✅")

def save_presets(uploaded_file: str, presets_path: str) -> None:
    """
    Saves user-uploaded presets to the session state and a local file.
    This function processes a file uploaded by the user, decodes its content,
    parses it as JSON, and stores the resulting data both in the Streamlit 
    session state and as a serialized pickle file on disk. A success message 
    is displayed to the user upon completion.
    Side Effects:
        - Updates `st.session_state.presets` with the parsed data.
        - Writes the parsed data to a file specified by `presets_path` in 
          binary format using pickle.
        - Displays a success toast message in the Streamlit app.
    Raises:
        - Any exceptions raised by `uploaded_file.getvalue()`, `json.loads()`, 
          or file I/O operations will propagate.
    Note:
        The user is advised to refresh the application after updating presets 
        to ensure changes take effect.
    """

    bytes_data = uploaded_file.getvalue()
    bytes_formatted = bytes_data.decode("utf-8")
    data = json.loads(bytes_formatted)

    st.session_state.presets = data
    with open(presets_path, "wb") as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

    st.toast("Successfully updated presets! Please refresh...", icon="✅")

def delete_selected_presets(deleted_presets: list, presets: dict, presets_path: str) -> None:
    """
    Deletes the selected presets from the presets dictionary and updates the
    presets file. Displays a success message upon completion.
    This function iterates through the `deleted_presets` list, removes the
    corresponding entries from the `presets` dictionary, and saves the updated
    dictionary to a file specified by `presets_path` using the pickle module.
    Finally, it displays a toast notification to inform the user that the
    presets have been successfully deleted and suggests refreshing the page.
    Note:
        - Ensure `deleted_presets`, `presets`, and `presets_path` are defined
          and accessible in the current scope.
        - The `st.toast` function is used for displaying the notification, so
          the Streamlit library must be imported and properly configured.
    """

    for preset in deleted_presets:
        presets.pop(preset)

    with open(presets_path, "wb") as f:
        pickle.dump(presets, f, pickle.HIGHEST_PROTOCOL)

    st.toast(
        "Successfully deleted presets! Please refresh...", icon="🗑️"
    )

def set_colors(uploaded_file: str, colors_path: str) -> None:
    """
    Updates the team colors by processing an uploaded file containing color data.
    This function reads the uploaded file, decodes its content, and parses it as JSON.
    The parsed data is then saved to a specified file path using pickle for persistence.
    It also updates the session state with the new team colors and clears the cache
    for the `load.get_team_colors` function to ensure the changes take effect.
    Finally, a success message is displayed to the user, prompting them to refresh.
    Raises:
        AttributeError: If `uploaded_file` is not properly defined or does not have a `getvalue` method.
        json.JSONDecodeError: If the uploaded file content is not valid JSON.
        IOError: If there is an issue writing to the `colors_path` file.
    Side Effects:
        - Updates `st.session_state.team_colors` with the new color data.
        - Clears the cache for the `load.get_team_colors` function.
        - Displays a toast message in the Streamlit app.
    """

    bytes_data = uploaded_file.getvalue()
    bytes_formatted = bytes_data.decode("utf-8")
    data = json.loads(bytes_formatted)

    with open(colors_path, "wb") as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

    st.session_state.team_colors = data
    load.get_team_colors.clear()

    st.toast("Successfully updated colors! Please refresh...", icon="✅")

def display_config_dropdown() -> None:
    """
    Displays a dropdown interface for configuring console settings in a Streamlit app.
    This function creates an expandable section labeled "Config" where users can toggle
    various console settings. The updated configurations are saved to the session state
    and persisted to a pickle file upon user confirmation.
    Functionality:
    - Displays toggle switches for each configuration item in a grid layout.
    - Updates the session state with the new configuration values.
    - Saves the updated configurations to a pickle file.
    - Displays a success message upon successful update.
    Notes:
    - The function assumes `st.session_state.console` contains the current console settings
      as a dictionary with configuration names as keys and their statuses as values.
    - The updated configurations are stored in `st.session_state.configs["Console"]`.
    Dependencies:
    - Requires the `streamlit` library for UI components.
    - Requires the `pickle` module for saving configurations.
    Raises:
    - KeyError: If `st.session_state.console` or `st.session_state.configs` is not properly initialized.
    """

    with st.expander("Config"):
        updated_configs = {}

        columns = st.columns(4)

        for i, (config, status) in enumerate(st.session_state.console.items()):
            updated_configs[config] = columns[i % 4].toggle(
                config.title().replace("_", " ").replace("Tba", "TBA"), status
            )

        settings_raw = [
            f"{key}={str(value).lower()}" for key, value in updated_configs.items()
        ]

        if st.button(
            "Update Configs",
            type="primary",
            use_container_width=True,
            key=f"update_configs",
        ):
            st.session_state.configs["Console"] = settings_raw
            st.session_state.console = updated_configs

            with open("src\\pickles\\configs.pickle", "wb") as f:
                pickle.dump(st.session_state.configs, f, pickle.HIGHEST_PROTOCOL)

            st.toast("Successfully updated configs! Please refresh...", icon="✅")

def display_scout_dropdown() -> None:
    """
    Displays a dropdown interface for selecting scouts and assigns them to a list.
    This function uses Streamlit components to create an interactive UI where users
    can toggle scouts from a list. It ensures that at least six scouts are selected,
    filling in placeholders if necessary. The selected scouts are saved to the session
    state and persisted to a pickle file.
    Functionality:
    - Displays an expander containing scout toggles.
    - Ensures a minimum of six scouts are selected, adding placeholders if needed.
    - Saves the selected scouts to the session state and a pickle file.
    - Displays a success toast upon saving.
    Raises:
        ValueError: If the number of selected scouts is less than six.
    Streamlit Components:
        - `st.expander`: Used to group scout toggles under a collapsible section.
        - `st.columns`: Used to arrange scout toggles in a grid layout.
        - `st.error`: Displays an error message if fewer than six scouts are selected.
        - `st.divider`: Adds a visual divider in the UI.
        - `st.button`: Triggers the saving of selected scouts.
        - `st.toast`: Displays a success message upon saving.
    Side Effects:
        - Updates `st.session_state.assigned` with the selected scouts.
        - Writes the scouts and their assignments to a pickle file.
    Note:
        This function assumes that `st.session_state.scouts` and `st.session_state.assigned`
        are pre-populated lists available in the Streamlit session state.
    """

    with st.expander("Scouts"):
        scouts = st.session_state.scouts
        assigned = st.session_state.assigned

        columns = st.columns(4)

        scout_list = []

        for i, scout in enumerate(scouts):
            initial_state = True if scout in assigned else False

            toggled_state = columns[i % 4].toggle(scout, initial_state)

            if toggled_state:
                scout_list.append(scout)

        scout_amount = len(scout_list)

        if scout_amount < 6:
            st.error(f"⚠️ Not enough scouters ({scout_amount}/6)")
            scout_list.extend([f"N/A {i}" for i in range(6 - scout_amount)])

        st.divider()

        if st.button(
            "Set Scouters",
            type="primary",
            use_container_width=True,
            key=f"set_scouters",
        ):
            st.session_state.assigned = scout_list

            with open("src\\pickles\\scouts.pickle", "wb") as f:
                pickle.dump([scouts, scout_list], f, pickle.HIGHEST_PROTOCOL)

            st.toast("Successfully set scouters! Please refresh...", icon="✅")

def display_presets_dropdown(presets_path) -> None:
    with st.expander("Presets"):
        presets_path = "src\\pickles\\presets.pickle"

        uploaded_file = st.file_uploader("Override Presets:", ".json")

        if uploaded_file is not None:
            st.divider()

            if st.button(
                "Set Presets",
                type="primary",
                use_container_width=True,
                key=f"set_presets",
                args=(uploaded_file, presets_path),
            ):
                save_presets()

        with open(presets_path, "rb") as f:
            presets = pickle.load(f)

        has_presets = len(presets) != 0

        if has_presets:
            st.download_button(
                f"Download Presets",
                json.dumps(presets).encode("utf-8"),
                "presets.json",
                type="primary",
                use_container_width=True,
            )

        if has_presets:
            delete_all = False
            if st.checkbox("Delete All", False):
                delete_all = True

        try:
            with open(presets_path, "rb") as f:
                presets = pickle.load(f)

            deleted_presets = []

            for name, value in presets.items():
                if st.checkbox(name, delete_all, help=str(value)):
                    deleted_presets.append(name)

            if has_presets:
                st.divider()

                if st.button(
                    "Delete Selected",
                    type="primary",
                    use_container_width=True,
                    key=f"delete_selected",
                    args=(deleted_presets, presets, presets_path),
                ):
                    delete_selected_presets()

            else:
                st.error("⚠️ No Presets Found")

        except:
            st.error("⚠️ No Presets Found")

def display_colors_dropdown(colors_path: str) -> None:
    """
    Displays a dropdown interface for managing team colors in a Streamlit application.
    This function provides an expandable section labeled "Colors" where users can:
    - Upload a JSON file containing team colors.
    - Set the uploaded colors using a button.
    - Download the current colors as a JSON file.
    The function handles the following:
    - File upload via a file uploader widget.
    - Button click to trigger the `set_colors` function and log the action using `analytics.button_press`.
    - Loading existing colors from a file and providing a download button for them.
    Note:
    - The `colors_path` variable is expected to point to the file storing the current colors.
    - The `set_colors` function and `analytics.button_press` are external dependencies that must be defined elsewhere.
    - Errors during file operations are silently ignored.
    Raises:
        None
    """

    with st.expander("Colors"):
        uploaded_file = st.file_uploader("Upload Team Colors:", ".json")

        if uploaded_file is not None:
            st.divider()

            if st.button(
                "Set Colors",
                type="primary",
                use_container_width=True,
                key=f"set_colors",
                args=(uploaded_file, colors_path),
            ):
                set_colors()

        try:
            with open(colors_path, "rb") as f:
                colors = pickle.load(f)

            st.download_button(
                f"Download colors",
                json.dumps(colors).encode("utf-8"),
                "colors.json",
                type="primary",
                use_container_width=True,
            )
        except:
            pass

def update_button(button_name, key="update_page") -> None:
    """
    Renders an "Update Page" button on the Streamlit app interface.
    This function adds a divider above and below the button for visual separation.
    The button is styled as a primary button and spans the full width of its container.
    Parameters:
        None
    Returns:
        None
    """

    st.divider()
    st.button(
        button_name,
        type="primary",
        use_container_width=True,
        key=key,
    )
    st.divider()


def main() -> None:
    load.initialise_app()

    presets_path = "src\\pickles\\presets.pickle"
    colors_path = "src\\pickles\\colors.pickle"

    ui.display_header("⚙️ Console ⚙️")
    update_button("Update Page")

    display_config_dropdown()
    display_scout_dropdown()
    display_presets_dropdown(presets_path)
    display_colors_dropdown(colors_path)

if __name__ == "__main__":
    main()
