import streamlit as st
import styles as style

def display_header(title):
    st.markdown(style.rainbow(), unsafe_allow_html=True)
    st.markdown(f"<div class='rainbow'>{title}</div>", unsafe_allow_html=True)

def display_event_link(event_key):
    st.markdown(
        f"<div style='text-align: center; font-size: 1.5em;'><a href='https://www.thebluealliance.com/event/{event_key}' style='color: #ffffff; text-decoration: none;'>Current Dataframe: {event_key}</a></div>",
        unsafe_allow_html=True,
    )
