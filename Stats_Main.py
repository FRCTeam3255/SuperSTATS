import streamlit as st
import tbapy, os

# TODO List:
# - Make secrets file
#       - API Key
#       - Upload Password
#   - Teleop

tba = tbapy.TBA('cTuS1j02TIfz40I1riOZTLaAR3OwhN88os8JJzvNN56bj8zuDrcdJvN1Cy8vLOQR')

st.set_page_config(
        page_title="Super Stats",
        page_icon="https://github.com/FRCTeam3255/GraphicsYearly/blob/main/Exports/SN%20Logos/favicon.png?raw=true",
        layout="wide",
)

def sendError(error, origin):
    st.error('{Error : ' + error + ' : ' + ' "' + origin + '"}')

st.title("FRC Stats Collector 2023")

# Team Selection

with st.form("Input"):
    teamInput = st.text_input("Team Number:", placeholder='3255', max_chars=4)
    btnResult = st.form_submit_button('Submit')

if btnResult:
    try:
        int(teamInput)
        team = tba.team(int(teamInput))
        teamName = ('%s' % (team.nickname))
        st.markdown(":green[*Team Updated Successfully - " + teamName + "*]")
    except:
        try:
            int(teamInput)
            st.markdown(":red[*Team **NOT** updated successfully*]")
            sendError("Team does not exist", teamInput)
        except:
            st.markdown(":red[*Team **NOT** updated successfully*]")
            sendError('Invalid team input', teamInput)

# Autonomous

st.header("Autonomous")

autoColumn1, autoColumn2, autoColumn3 = st.columns(3)

with autoColumn1:
    mobility = st.checkbox('Mobility')

    if mobility:
        autoMobility = True
        st.text('Mobility: ' + str(autoMobility))
    else:
        autoMobility = False
        st.text('Mobility: ' + str(autoMobility))

with autoColumn2:
    autoDock = st.checkbox('Docking')

    if autoDock:
        autoDocking = True
        st.text('Docked: ' + str(autoDocking))
    else:
        autoDocking = False
        st.text('Docked: ' + str(autoDocking))

with autoColumn3:
    autoEngage = st.checkbox('Engage')

    if autoEngage:
        autoEngaging = True
        st.text('Engaged: ' + str(autoEngaging))
    else:
        autoEngaging = False
        st.text('Engaged: ' + str(autoEngaging))

st.write("---")

# Teleop

st.header("Teleop")

st.write("---")

# Comments

st.header("Comments")

with st.form("Comments"):
    commentsInput = st.text_input("Comments:", placeholder='Example: "Robot tipped in middle of field 40 seconds into match"', max_chars=None)
    btnResult = st.form_submit_button('Submit')

if btnResult:
    if(autoEngaging == True):
        autoDocking = True

    st.markdown(":green[*Updated Successfully*]")

st.write("---")

# Password Protection

with st.form("Password"):
    passwordInput = st.text_input("Insert Password:", placeholder=':D', max_chars=None)
    btnResult = st.form_submit_button('Upload')

if btnResult:
    if(passwordInput.lower() == 'susan'):
        if(autoEngaging == True):
            autoDocking = True

        username = os.getlogin()
        path = "C:\\Users\ " + username + "\Documents\ " + 'SN_Stats\ ' + teamInput + "_stats.txt"
        newPath = path.replace(" ", "")

        if os.path.exists(newPath):
            os.remove(newPath)
            print(newPath)

        f = open(newPath, "x")
        f = open(newPath, "a")

        team = tba.team(int(teamInput))
        teamName = ('%s' % (team.nickname))

        if(commentsInput == ''):
            commentsInput = 'None'

        os.system('cls')
        f.write('[Team]')
        f.write('\nTeam Number: ' + teamInput)
        f.write('\nName: ' + teamName)
        f.write('\n\n[Autonomous]')
        f.write('\nMobility: ' + str(autoMobility))
        f.write('\nDock: ' + str(autoDocking))
        f.write('\nEngage: ' + str(autoEngaging))
        f.write('\n\n[Teleop]')
        f.write('\n\n[Comments]')
        f.write('\n' + commentsInput)

        f.close()

        st.success('Successfully Submitted')
    else:
        st.error('Incorrect Password')