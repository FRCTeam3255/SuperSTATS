import io

import pandas as pd
import requests
import streamlit as st

from SuperSTATs.utils.constants import DEFAULT_GSHEET_DOC_ID, GSHEET_DATA_CACHE_TTL


# Reusing connections avoids a new TLS handshake for each hop of Google's export redirect
_session = requests.Session()


def _download(sheet_id: str, doc_id: str) -> pd.DataFrame:
    print("\t⬇️ Fetching Google Sheets data")
    sheet_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={sheet_id}"
    response = _session.get(sheet_url, timeout=10)
    response.raise_for_status()
    df = pd.read_csv(io.BytesIO(response.content))
    df.columns = (
        df.columns.str.lstrip()
        .str.replace("[", repl="", regex=False)
        .str.replace("]", repl="", regex=False)
    )
    return df


@st.cache_data(ttl=GSHEET_DATA_CACHE_TTL, show_spinner=False)
def get_data(sheet_id: str, doc_id: str = DEFAULT_GSHEET_DOC_ID) -> pd.DataFrame:
    """Download a Google Sheet tab as a DataFrame (cached, shared across users)."""
    return _download(sheet_id, doc_id)


def clear() -> None:
    get_data.clear()
