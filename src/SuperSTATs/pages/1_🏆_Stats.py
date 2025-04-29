import streamlit as st
import SuperSTATs.load as load
import SuperSTATs.styles as style
import SuperSTATs.screen_elements as ui
import pandas as pd


def gen_bar(
    df=st.session_state.df,
    picked=st.session_state.picked,
    tba_ranks=st.session_state.tba_ranks,
    key=0,
    use_presets=True,
    use_group_filters=True,
    use_show_available=True,
    use_show_nums=True,
    use_inline_legend=True,
    use_features=True,
    use_local_rank=True,
    use_agg_type=True,
    use_filter_selection=True,
    use_max_size=True,
    displayed_teams=[],
    compared_teams=[],
    x_range=[],
    expanders=True,
):
    """
    Generates a bar chart based on the given parameters.

    Parameters:
    - df (DataFrame): The DataFrame containing the data.
    - picked (str): The picked value.
    - tba_ranks (str): The TBA ranks value.
    - key (int): The key value.
    - use_presets (bool): Whether to use presets or not.
    - use_group_filters (bool): Whether to use group filters or not.
    - use_show_available (bool): Whether to show availability or not.
    - use_show_nums (bool): Whether to show team numbers or not.
    - use_inline_legend (bool): Whether to use inline legend or not.
    - use_features (bool): Whether to use features or not.
    - use_local_rank (bool): Whether to use local rank or not.
    - use_agg_type (bool): Whether to use aggregation type or not.
    - use_filter_selection (bool): Whether to use filter selection or not.
    - use_max_size (bool): Whether to use maximum size or not.
    - displayed_teams (list): The list of displayed teams.
    - compared_teams (list): The list of compared teams.
    - x_range (list): The range of x-axis values.
    - expanders (bool): Whether to use expanders or not.

    Returns:
    - None
    """
    phases = st.session_state.phases

    variables = [
        "group_filters" if use_group_filters else None,
        "inline_legend" if use_inline_legend else None,
        "show_available" if use_show_available else None,
        "show_nums" if use_show_nums else None,
        "features" if use_features else None,
        "local_rank" if use_local_rank else None,
    ]

    variables = [var for var in variables if var != None]

    if use_presets:
        presets = st.session_state.presets
        preset_columns = st.columns(2)

        preset_choice = preset_columns[0].selectbox(
            "Preset Choice:",
            ["None"] + list(preset for preset in presets.keys() if preset != "Custom"),
        )

        preset_json = preset_columns[1].text_input("JSON Preset:", placeholder="{}")

        if preset_choice != "None":
            st.header(
                f"Selected Preset: {preset_choice}",
                False,
                help=json.dumps(presets[preset_choice]),
            )
            preset = presets[preset_choice]
        elif preset_json:
            try:
                preset_choice = "Custom"
                presets[preset_choice] = json.loads(preset_json)
                st.header(
                    f"Selected Preset: Custom",
                    False,
                    help=json.dumps(presets[preset_choice]),
                )
                preset = presets[preset_choice]
            except:
                st.error("⚠️ Invalid JSON")
    else:
        preset_choice = "None"

    if len(variables) != 0:
        columns = st.columns(len(variables))

    var_count = 0

    def gen_toggle(var_name, var_count, box_name, default, key, disabled):
        """
        Generate a toggle variable based on the given parameters.

        Args:
            var_name (str): The name of the variable.
            var_count (int): The current count of variables.
            box_name (str): The name of the toggle box.
            default (bool): The default value of the toggle.
            key (str): The key used to identify the toggle.
            disabled (bool): Whether the toggle is disabled or not.

        Returns:
            list: A list containing the generated toggle variable and the updated variable count.
        """
        if var_name in variables:
            variable = columns[var_count].toggle(
                box_name, default, key=f"{var_name}_{key}", disabled=disabled
            )
            var_count += 1
        else:
            variable = default

        return [variable, var_count]

    if preset_choice == "None":
        show_nums, var_count = gen_toggle(
            "show_nums", var_count, "Team Numbers", True, key, False
        )

        show_available, var_count = gen_toggle(
            "show_available", var_count, "Availability", show_nums, key, not show_nums
        )

        features, var_count = gen_toggle(
            "features", var_count, "Features", False, key, False
        )

        use_local_rank, var_count = gen_toggle(
            "local_rank", var_count, "Local Rank", False, key, False
        )

        group_filters, var_count = gen_toggle(
            "group_filters", var_count, "Group Filters", True, key, False
        )

        inline_legend, var_count = gen_toggle(
            "inline_legend",
            var_count,
            "Inline Legend",
            not group_filters,
            key,
            group_filters,
        )

        if use_agg_type:
            agg_type = st.selectbox(
                "Aggregation Type:", ("Mean", "Median", "Sum"), key=f"agg_type_{key}"
            ).lower()
        else:
            agg_type = "mean"

        if not group_filters:
            selected_phases = st.multiselect("Phases:", phases, default=phases, key=key)
            phases = [
                col
                for col in df.columns
                if any(col.startswith(f"{phase}_") for phase in selected_phases)
            ]
            selected_filters = phases
            filter_choices = phases
        else:
            filter_choices = phases
    else:
        show_nums = preset["show_nums"]
        show_available = preset["show_available"]
        features = preset["use_features"]
        use_local_rank = preset["use_local_rank"]
        group_filters = preset["group_filters"]
        filter_choices = preset["selected_filters"]
        inline_legend = preset["inline_legend"]
        agg_type = preset["agg_type"]
        phases = preset["phases"]

    comment_df = df
    df = df.drop("COMMENT_GENERAL_STR_1", axis=1)

    for i in range(len(phases)):
        df.loc[:, phases[i]] = load.add_cols(
            df,
            phases[i],
        )

    if not use_inline_legend:
        inline_legend = False

    if displayed_teams:
        df = df[df["Team"].isin(displayed_teams + compared_teams)]
    else:
        df = df

    if df.empty:
        df.loc[0] = 0
        no_data = True
    else:
        no_data = False

    feature_list = list(
        comment_df["COMMENT_GENERAL_STR_1"].dropna().str.split(", ").explode().unique()
    )

    df_scouting = st.session_state.scouting
    dt_types = df_scouting["Drivetrain Type"].unique().tolist() + ["Unknown Drivetrain"]

    feature_choices = []

    for filter in feature_list + dt_types:
        if str(filter) == "nan":
            pass
        else:
            feature_choices.append(filter)

    if preset_choice == "None":
        selected_features = (
            st.multiselect(
                "Features:",
                feature_choices,
                default=[],
                key=f"selected_features_{key}",
            )
            if use_features and features
            else feature_choices
        )

    df = df.merge(
        df_scouting[
            ["Team #", "Drivetrain Type", "Frame Size LENGTH", "Frame Size WIDTH"]
        ].fillna("Unknown Drivetrain"),
        left_on="Team",
        right_on="Team #",
        how="left",
    ).drop(columns=["Team #"])

    df["Drivetrain Type"] = df["Drivetrain Type"].fillna("Unknown Drivetrain")

    selected_features = (
        preset["selected_features"] if preset_choice != "None" else selected_features
    )

    if any(dt in selected_features for dt in dt_types):
        df = df[(df["Drivetrain Type"].isin(selected_features))]

    all_team_features = {}
    kept_teams = []

    def has_features(team):
        """
        Check if a team has all the required features.

        Args:
            team (str): The name of the team.

        Returns:
            bool: True if the team has all the required features, False otherwise.
        """
        if not features:
            return True

        for feature in selected_features:
            if feature not in all_team_features[team] + dt_types:
                return False

        return True

    for team in comment_df["Team"]:
        comment_df = comment_df.dropna()
        team_values = comment_df.loc[
            comment_df["Team"] == team, "COMMENT_GENERAL_STR_1"
        ].tolist()

        team_features = [value.split(", ") for value in team_values]
        team_features = list(
            set([feature for sublist in team_features for feature in sublist])
        )

        all_team_features[team] = team_features

        if has_features(team):
            kept_teams.append(team)

    df = df[df["Team"].isin(kept_teams)]

    if preset_choice == "None":
        if use_filter_selection:
            selected_filters = st.multiselect(
                "Filters:",
                filter_choices,
                default=filter_choices,
                key=f"selected_filters_{key}",
            )
        else:
            selected_filters = filter_choices
    else:
        selected_filters = preset["selected_filters"]

    selected_filters = (
        preset["selected_filters"] if preset_choice != "None" else selected_filters
    )

    if "COMMENT_GENERAL_STR_1" in selected_filters:
        selected_filters.remove("COMMENT_GENERAL_STR_1")

    rank_df = df.groupby("Team")[
        [
            filter_item
            for filter_item in selected_filters
            if filter_item != "COMMENT_GENERAL_STR_1"
        ]
    ].agg(agg_type)
    rank_df["rank"] = rank_df.sum(axis=1).rank(ascending=False).astype(int)
    rank_df.reset_index(inplace=True)

    if use_max_size and features:
        min_size = df[["Frame Size LENGTH", "Frame Size WIDTH"]].min().min()
        max_size = df[["Frame Size LENGTH", "Frame Size WIDTH"]].max().max()
        unscouted_size = max_size + 0.5

        if preset_choice == "None":
            size_limit = st.slider(
                "Max Size:",
                min_value=min_size,
                max_value=unscouted_size,
                value=unscouted_size,
                step=0.5,
                key=f"size_limit_{key}",
            )
        else:
            size_limit = preset["size_limit"]

        if size_limit == unscouted_size:
            st.toast("Viewing unscouted teams", icon="⚠️")

        df["Frame Size LENGTH"] = df["Frame Size LENGTH"].fillna(unscouted_size)
        df["Frame Size WIDTH"] = df["Frame Size WIDTH"].fillna(unscouted_size)

        df = df[
            (df["Frame Size LENGTH"] <= size_limit)
            & (df["Frame Size WIDTH"] <= size_limit)
        ]
    else:
        size_limit = None

    calc_df = df.groupby("Team")[selected_filters].agg(agg_type)
    calc_df["rank"] = calc_df.sum(axis=1).rank(ascending=False).astype(int)
    calc_df.reset_index(inplace=True)
    data = pd.melt(
        calc_df,
        id_vars=["Team", "rank"],
        value_vars=selected_filters,
        var_name="variable",
        value_name="value",
    )

    calc_df["Score Sum"] = calc_df[selected_filters].sum(axis=1)

    if preset_choice is not "None":
        x_range = preset["x_range"]
    else:
        try:
            x_min = (
                math.floor(calc_df.min().min()) - 2
                if calc_df.min().min() < 0
                else math.floor(calc_df.min().min())
            )
        except:
            st.error("⚠️ No bots found with selected features")
            st.stop()

        x_range = (
            x_range if x_range else [x_min, (round(calc_df["Score Sum"].max()) + 2)]
        )

    x_min, x_max = x_range

    data = data[~data["Team"].isin(compared_teams)]

    def rgba_to_hex(rgba):
        """
        Converts an RGBA color value to its corresponding hexadecimal representation.

        Args:
            rgba (tuple): A tuple containing the red, green, blue, and alpha values of the color.

        Returns:
            str: The hexadecimal representation of the color.
        """
        r, g, b, a = rgba
        return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))

    def gen_cmap(
        length,
        cmap_name=(
            "Blues" if not st.session_state.console["colorblind_mode"] else "OrRd"
        ),
    ):
        """
        Generate a color map with the specified length and colormap name.

        Parameters:
        - length (int): The number of colors to generate in the color map.
        - cmap_name (str): The name of the colormap to use. Defaults to "Blues" if colorblind mode is disabled, otherwise defaults to "OrRd".

        Returns:
        - colors (list): A list of colors in hexadecimal format.
        """
        cmap = plt.get_cmap(cmap_name)
        colors = [rgba_to_hex(cmap(i)) for i in np.linspace(0, 0.8, length)]
        return colors

    def format_y(team, show_available, picked):
        """
        Formats the team information based on the given parameters.

        Args:
            team (int): The team number.
            show_available (bool): Flag indicating whether to show availability status.
            picked (dict): A dictionary containing the picked teams.

        Returns:
            str: The formatted team information.

        """
        if show_available:
            picked = (
                "💎"
                if team == st.secrets["TEAM_NUMBER"]
                else "🚫" if team in picked["Team"].values else "🟢"
            )
        else:
            picked = ""

        if use_local_rank:
            rank = str(calc_df.loc[calc_df["Team"] == team, "rank"].to_list()[0]).zfill(
                2
            )
        else:
            rank = str(tba_ranks.get(str(int(team)), "NA")).zfill(2)

        return f"{picked} {str(int(team)).rjust(5)} [{rank}]"

    ranked_data = data.copy()

    ranked_data["Team"] = ranked_data["Team"].apply(
        lambda team: format_y(team, show_available, picked)
    )

    # TODO: Fix scaling to be more dynamic

    if displayed_teams:
        chart_height = 60 * len(displayed_teams)
    else:
        chart_height = 37 * len(ranked_data["Team"].unique())

    chart = (
        alt.Chart(
            ranked_data,
            height=chart_height,
        )
        .mark_bar()
        .encode(
            x=alt.X("value:Q", title=" ", scale=alt.Scale(domain=[x_min, x_max])),
            y=alt.Y(
                "Team:N",
                sort=alt.EncodingSortField(field="rank", order="ascending"),
                title="",
                axis=alt.Axis(labels=show_nums),
            ),
            color=alt.Color(
                "variable:N",
                title=" ",
                scale=alt.Scale(
                    domain=selected_filters,
                    range=gen_cmap(len(data["variable"].unique())),
                ),
                legend=alt.Legend(
                    title=None,
                    orient=(
                        "bottom-right"
                        if inline_legend and not group_filters
                        else "bottom"
                    ),
                    symbolType="circle",
                    labelBaseline="alphabetic",
                    labelLimit=0,
                    offset=5,
                    padding=0,
                    rowPadding=0,
                    labelFontSize=(10.5 if inline_legend and not group_filters else 14),
                ),
            ),
            stroke=alt.value("#141414"),
            strokeWidth=alt.value(2),
            tooltip=["value:Q", "variable:N"],
        )
    )

    if selected_filters:
        if not no_data:
            st.divider()
            st.altair_chart(chart, use_container_width=True)
        else:
            st.error("⚠️ Not enough data")
    else:
        st.error("⚠️ Please select at least one filter")

    if use_presets:
        if preset_choice == "None":
            preset_name = st.text_input("New Preset Name:")

            preset_data = {
                "agg_type": agg_type,
                "group_filters": group_filters,
                "inline_legend": inline_legend,
                "phases": phases,
                "selected_features": selected_features,
                "selected_filters": selected_filters,
                "size_limit": size_limit,
                "use_local_rank": use_local_rank,
                "show_available": show_available,
                "show_nums": show_nums,
                "use_features": features,
                "x_range": x_range,
            }

            if preset_name.replace(" ", ""):
                if preset_name.lower() == "custom":
                    pass
                elif preset_name not in presets.keys():
                    presets[preset_name] = preset_data

                    with open("src\\pickles\\presets.pickle", "wb") as f:
                        pickle.dump(presets, f, pickle.HIGHEST_PROTOCOL)
                    st.toast("Successfully added preset!", icon="✅")
                else:
                    st.toast("Preset name already exists!", icon="⚠️")

        if st.button(
            "Generate JSON",
            use_container_width=True,
            key=f"gen_json",
            on_click=analytics.button_press,
            args=("gen_json",),
        ):
            if preset_choice != "None":
                preset_data = preset
            st.code(
                json.dumps(preset_data) if preset_data else json.dumps(preset),
                language="json",
            )

    if expanders:
        if st.toggle("Ranked Expanders"):
            with st.container(border=True):
                start_time = time.time()

                rank_df = rank_df.sort_values(by="rank")
                for _, row in rank_df.iterrows():
                    team_num = row["Team"]

                    all_team_features = {
                        str(float(k)): v for k, v in all_team_features.items()
                    }

                    formatted_features = all_team_features[str(team_num)]

                    scouting_expander(
                        df=st.session_state.scouting,
                        team_num=int(team_num),
                        team_features=formatted_features,
                        rank_info=[
                            rank_df.loc[rank_df["Team"] == team_num, "rank"].to_list()[
                                0
                            ],
                            tba_ranks[str(int(team_num))],
                        ],
                    )

                st.markdown(
                    f"<span style='font-size: small; color: #808080;'>Loaded in {round(time.time() - start_time, 2)} seconds...</span>",
                    unsafe_allow_html=True,
                )

    return ranked_data

def main() -> None:
    load.initialise_app()

    st.markdown(style.shimmer("#ffe8ad"), unsafe_allow_html=True)
    st.markdown("<div class='shimmer'>🏆 NURD Stats 🏆</div>", unsafe_allow_html=True)

    st.title("")

    if st.button(
        "Update Page",
        type="primary",
        use_container_width=True,
        key="update_page",
    ):
        st.session_state.df = load.organize_df(
            load.download_sheets_raw(st.secrets["GID_RAW"]).dropna(subset=["Timestamp"])
        )

        st.session_state.picked = load.get_picked()
        st.session_state.tba_ranks = load.get_tba_ranks()
        st.session_state.presets = load.get_presets()

    st.divider()

    gen_bar(
        st.session_state.df, st.session_state.picked, st.session_state.tba_ranks
    )


if __name__ == "__main__":
    main()
