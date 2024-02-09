import SuperSTATs.build as build
import SuperSTATs.load as load
import streamlit as st


def main():
    load.app_init()

    import SuperSTATs.styles as style

    st.markdown(style.shimmer("#ffe8ad"), unsafe_allow_html=True)
    st.markdown("<div class='shimmer'>🏆 NURD Stats 🏆</div>", unsafe_allow_html=True)

    st.title("")

    st.button("Update Page", type="primary", use_container_width=True)
    st.divider()

    build.gen_bar()


if __name__ == "__main__":
    main()
