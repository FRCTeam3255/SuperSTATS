import SuperSTATs.Main as stats
import streamlit as st

st.set_page_config(
    page_title="[PREVIEW] SN Stats",
    page_icon="🤖",
    initial_sidebar_state="expanded",
)


def main():
    stats.set_font()

    st.header("🔮 Match Preview 🔮")


if __name__ == "__main__":
    main()
