import streamlit as st
import pandas as pd

no_pick_url = f"https://docs.google.com/spreadsheets/d/{st.secrets['GSHEET_DOC_ID']}/edit#gid=1962951229"

def build_sheet_url(url):
    doc_id, sheet_id = url.split("/")[5:7]
    sheet_id = sheet_id.split("gid=")[1]
    return f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={sheet_id}"

def download_sheets_raw():
    url = f"https://docs.google.com/spreadsheets/d/{st.secrets['GSHEET_DOC_ID']}/edit#gid=1657585295"
    return pd.read_csv(build_sheet_url(url))