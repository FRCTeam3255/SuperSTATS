from bs4 import BeautifulSoup
import streamlit as st
import requests


def get_entries(url):
    """
    Retrieves entries from a given form URL and returns two dictionaries: set_entries and gen_entries.

    Args:
        url (str): The URL to retrieve the entries from.

    Returns:
        tuple: A tuple containing two dictionaries:
            - set_entries: A dictionary of entries that do not start with any phase in st.session_state.phases.
            - gen_entries: A dictionary of entries that start with any phase in st.session_state.phases.
    """
    response = requests.get(url)
    html = BeautifulSoup(response.content, "html.parser")

    found = "FB_PUBLIC_LOAD_DATA_ ="

    split_html = str(html).split(found)[1]
    split_html = str(split_html).split("]],[")

    first_val = split_html[0].split("[[")[2].split(",")[0]

    split_html.insert(
        0,
        (split_html[0].split("[[")[1].split(",null,")[0])
        + f",null,0,[[{first_val},null,1]],null,",
    )
    split_html = [line for line in split_html if line[0].isdigit()]

    entries_dict = {}

    for html in split_html:
        if "]],null," in html:
            num_raw = html.split("[[")[1]
            entries_dict[html.split('"')[1]] = num_raw.split(",")[0]

    gen_entries = {
        name: id
        for name, id in entries_dict.items()
        if any(name.startswith(phase) for phase in st.session_state.phases)
    }

    set_entries = {
        name: id for name, id in entries_dict.items() if name not in gen_entries
    }

    return set_entries, gen_entries


@st.cache_data(show_spinner=False)
def cache_forms(forms):
    form_data = {}

    for form in forms:
        set_entries, gen_entries = get_entries(st.secrets[form])
        form_data[form] = {"set": set_entries, "gen": gen_entries}

    return form_data
