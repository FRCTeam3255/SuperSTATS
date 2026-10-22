import requests
import streamlit as st
from bs4 import BeautifulSoup

from SuperSTATs.utils import constants


def _scrape_entries(url: str) -> dict[str, str]:
    """Scrape {question name: entry id} from a Google Form's public HTML."""
    html = BeautifulSoup(requests.get(url, timeout=10).content, "html.parser")
    split_html = str(html).split("FB_PUBLIC_LOAD_DATA_ =")[1].split("]],[")

    first_val = split_html[0].split("[[")[2].split(",")[0]
    split_html.insert(
        0,
        (split_html[0].split("[[")[1].split(",null,")[0])
        + f",null,0,[[{first_val},null,1]],null,",
    )

    entries = {}
    for chunk in (c for c in split_html if c and c[0].isdigit()):
        if "]],null," in chunk:
            entries[chunk.split('"')[1]] = chunk.split("[[")[1].split(",")[0]
    return entries


@st.cache_data(show_spinner=False)
def get_stats_form_entries(phases: tuple[str, ...]) -> tuple[dict, dict]:
    """Returns (identifier entries, phase entries) for the stats form."""
    entries = _scrape_entries(constants.STATS_FORM_URL)
    phase_entries = {k: v for k, v in entries.items() if k.startswith(phases)}
    set_entries = {k: v for k, v in entries.items() if k not in phase_entries}
    return set_entries, phase_entries


def build_submit_url(entries: dict[str, str], values: dict) -> str:
    """Build a formResponse URL from {question: entry id} and {question: value}."""
    base = constants.STATS_FORM_URL.split("/viewform")[0]
    params = "".join(
        f"&entry.{entry_id}={requests.utils.quote(str(values[name]), safe='')}"
        for name, entry_id in entries.items()
        if name in values
    )
    return f"{base}/formResponse?usp=pp_url{params}&submit=Submit"
