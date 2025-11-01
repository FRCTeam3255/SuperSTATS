import SuperSTATs.analytics as analytics
import SuperSTATs.build as build
import SuperSTATs.load as load
import streamlit as st


def main():
    load.app_init()
    analytics.collect_analytics("page_change", "stats")

    st.title("🏆 NURD Stats 🏆")

    if st.button(
        "Update Page",
        type="primary",
        use_container_width=True,
        key="update_page",
        on_click=analytics.button_press,
        args=("update_page",),
    ):
        st.session_state.df = load.organize_df(
            load.download_sheets_raw(st.secrets["GID_RAW"]).dropna(subset=["Timestamp"])
        )

        st.session_state.picked = load.get_picked()
        st.session_state.tba_ranks = load.get_tba_ranks()
        st.session_state.presets = load.get_presets()

    st.divider()

    build.gen_bar(
        st.session_state.df, st.session_state.picked, st.session_state.tba_ranks
    )


if __name__ == "__main__":
    main()
