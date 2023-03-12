import streamlit as st
import tbapy, os

fileOrigin = "C:\\Users\ " + username + "\Documents\ " + "encryption.txt"
filename = fileOrigin.replace(" ", "")

with open(filename) as file:
    lines = [line.rstrip() for line in file]

tba = tbapy.TBA(lines[0])

def sendError(error, origin):
    st.error('{Error : ' + error + ' : ' + ' "' + origin + '"}')

st.set_page_config(
        page_title="FRC Team Search",
        page_icon="https://github.com/FRCTeam3255/GraphicsYearly/blob/main/Exports/SN%20Logos/favicon.png?raw=true",
        layout="wide",
)

st.title('FRC Team Info Search')

with st.form("Search"):
    teamInput = st.text_input("Search Team:", placeholder='3255', max_chars=4)
    btnResult = st.form_submit_button('Submit')

if btnResult:
    try:
        int(teamInput)
        team = tba.team(int(teamInput))

        st.markdown(':red[**[Results for team %s]**]' % (team.team_number))
        st.write('Team Name: %s' % (team.nickname))
        st.write('Team School: %s' % (team.school_name))
        st.write('Team City: %s' % (team.city))
        st.write('Team State: %s' % (team.state_prov))
        st.write('Team Country: %s' % (team.country))
        st.write('Team Rookie Year: %s' % (team.rookie_year))
        st.write('Team Website: %s' % (team.website))
    except:
        try:
            int(teamInput)
            sendError("Team does not exist", teamInput)
        except:
            sendError('Invalid team input', teamInput)

showCode = st.checkbox('Show Source Code')

if showCode:
        showCode = True
        code = '''
import streamlit as st
import tbapy, os

tba = tbapy.TBA('<TBA Auth Key>')

def sendError(error, origin):
        st.error('{Error : ' + error + ' : ' + ' "' + origin + '"}')

st.set_page_config(
        page_title="FRC Team Search",
        page_icon="<Icon Link>",
        layout="wide",
)

st.title('FRC Team Info Search')
with st.form("Search"):
        teamInput = st.text_input("Search Team:", placeholder='3255', max_chars=4)
        btnResult = st.form_submit_button('Submit')

if btnResult:
try:
        int(teamInput)
        team = tba.team(int(teamInput))

        st.markdown(':red[**[Results for team %s]**]' % (team.team_number))
        st.write('Team Name: %s' % (team.nickname))
        st.write('Team School: %s' % (team.school_name))
        st.write('Team City: %s' % (team.city))
        st.write('Team State: %s' % (team.state_prov))
        st.write('Team Country: %s' % (team.country))
        st.write('Team Rookie Year: %s' % (team.rookie_year))
        st.write('Team Website: %s' % (team.website))
except:
        try:
                int(teamInput)
                sendError("Team does not exist", teamInput)
        except:
                sendError('Invalid team input', teamInput)

showCode = st.checkbox('Show Source Code')

if showCode:
        showCode = True
        code = (3 of ')

        <code>
        
        (3 of ')
        st.code(code, language='python')
else:
        showCode = False

                '''
        st.code(code, language='python')
else:
        showCode = False