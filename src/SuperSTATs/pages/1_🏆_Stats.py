import SuperSTATs.build as build
import SuperSTATs.load as load
import streamlit as st
import pandas as pd


def main():
    load.app_init()

    df = pd.DataFrame(st.session_state.df)

    st.markdown(
        "<h1 style='text-align: center;'>🏆 NURD Stats 🏆</h1>", unsafe_allow_html=True
    )
    st.title("")

    st.button("Update Page", type="primary", use_container_width=True)
    st.markdown("""---""")

    build.gen_bar()


if __name__ == "__main__":
    main()
