import streamlit as st
import pandas as pd
import tbapy

tba = tbapy.TBA(st.secrets["TBA_API"])

def download_team_data(team):
    print(tba.team(('frc' + str(team)), True))

# from SuperSTATs.tba.team_data import test_team_data
def test_team_data(team):
    import streamlit as st
    import pandas as pd
    import tbapy

    tba = tbapy.TBA(st.secrets["TBA_API"])

    print(tba.team(('frc' + str(team)), True))