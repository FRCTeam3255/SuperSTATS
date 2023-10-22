import streamlit as st

# [PRESETS]
# Delete
# Rename
# Compare

# [STATS INPUT]
# Stat Taker List

# [SCOUTING]
# Uncollected Teams

password = st.secrets["ADMIN_PASSWORD"]

if "signed_in" not in st.session_state:
    st.session_state.signed_in = False

if not st.session_state.signed_in:
    pass_input = st.text_input("Password", type="password")

    if pass_input == password:
        st.session_state.signed_in = True
else:
    st.title("Signed in: True")
