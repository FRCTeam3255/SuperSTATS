import SuperSTATs.build as build
import SuperSTATs.load as load
import streamlit as st


def main():
    load.app_init()

    import SuperSTATs.styles as style

    st.markdown(style.shimmer("#ffe8ad"), unsafe_allow_html=True)
    st.markdown("<div class='shimmer'>🏆 NURD Stats 🏆</div>", unsafe_allow_html=True)

    st.title("")

    if st.button("Update Page", type="primary", use_container_width=True):
        df = load.download_sheets_raw(st.secrets["GID_RAW"]).dropna(
            subset=["Timestamp"]
        )
        df = df.sort_values(["Match", "Timestamp"], ascending=[True, True])
        df = df.drop_duplicates(subset=["Team", "Match Type", "Match"])
        df = df[df["Event Key"] == st.secrets["DEFAULT_EVENT_KEY"]]
        st.session_state.df = df

    st.divider()

    build.gen_bar(st.session_state.df)


if __name__ == "__main__":
    main()
