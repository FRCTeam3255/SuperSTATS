from streamlit_gsheets import GSheetsConnection
import streamlit as st

st.title("2023 Stats Table")

conn = st.experimental_connection("gsheets", type=GSheetsConnection)
df = conn.read(worksheet="Stats")

st.dataframe(df)