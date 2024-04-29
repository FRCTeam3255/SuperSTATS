import SuperSTATs.form as form
import streamlit as st


def log(event, content):
    analytics_form = st.secrets["ANALYTICS_FORM"]

    entries = form.get_entries(analytics_form)[0]

    entry_pairs = {
        "UID": st.session_state.uid,
        "Page": st.session_state.page.title().replace("_", " "),
        "Event": event,
        "Content": content,
    }

    form_entries = [
        f"&entry.{entries[entry]}={entry_pairs[entry]}" for entry in entry_pairs
    ]

    prefill_url = f"{analytics_form.split('/viewform')[0]}/formResponse?usp=pp_url{''.join(form_entries)}&submit=Submit"

    st.html(f'<p><img style="display: none;"src="{prefill_url}" /></p>')


def page_change(page):
    if st.session_state.page != page:
        st.session_state.page = page
        log("Page Changed", None)
    elif st.session_state.analytics["page_update"]:
        log("Page Updated", None)


def collect_analytics(func, args):
    if (
        st.session_state.console["collect_analytics"]
        and st.session_state.analytics[func]
    ):
        if func == "page_change":
            page_change(args)
