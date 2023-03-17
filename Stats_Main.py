import streamlit as st
import tbapy, os

# TODO List:
# - Make secrets file
#       - API Key
#       - Upload Password
#   - Teleop

username = os.getlogin()

fileOrigin = "C:\\Users\ " + username + "\encryption.txt"
filename = fileOrigin.replace(" ", "")

with open(filename) as file:
    lines = [line.rstrip() for line in file]

tba = tbapy.TBA(lines[0])

cones = 0
cubes = 0
hybrids = 0

css = r'''
    <style>
        [data-testid="stForm"] {border: 0px}
    </style>
'''

st.set_page_config(
        page_title="Super Stats",
        page_icon="https://github.com/FRCTeam3255/GraphicsYearly/blob/main/Exports/SN%20Logos/favicon.png?raw=true",
        layout="wide",
)

st.markdown(css, unsafe_allow_html=True)

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

st.write("---")

# Autonomous

st.header("Autonomous")

autoColumn1, autoColumn2, autoColumn3, autoColumn4, autoColumn5 = st.columns(5)

# with autoColumn1:
#     if 'cones' not in st.session_state:
#         st.session_state.cones = 0

#     addCone = st.button('Add Cone')
#     if addCone:
#         st.session_state.cones += 1

#     cones = st.session_state.cones
#     st.write('Cones = ', str(cones))

# with autoColumn2:
#     if 'cubes' not in st.session_state:
#         st.session_state.cubes = 0

#     addCube = st.button('Add Cube')
#     if addCube:
#         st.session_state.cubes += 1

#     cubes = st.session_state.cubes
#     st.write('Cones = ', str(cubes))

if 'cones' not in st.session_state:
    st.session_state.cones = 0

if 'cubes' not in st.session_state:
    st.session_state.cubes = 0

if 'hybrids' not in st.session_state:
    st.session_state.hybrids = 0

with autoColumn1:
    with st.form("highCone"):
        btnResult = st.form_submit_button('▲ High Cone ▲')
    if btnResult:
        st.session_state.cones += 1

    with st.form("midCone"):
        btnResult = st.form_submit_button('▲ Mid Cone ▲')
    if btnResult:
        st.session_state.cones += 1

    with st.form("hybridLeft"):
        btnResult = st.form_submit_button('※~ Hybrid ~※')
    if btnResult:
        st.session_state.hybrids += 1

with autoColumn2:
    with st.form("highCube"):
        btnResult = st.form_submit_button(' ■ High Cube ■')
    if btnResult:
        st.session_state.cubes += 1

    with st.form("midCube"):
        btnResult = st.form_submit_button('■ Mid Cube ■')
    if btnResult:
        st.session_state.cubes += 1

    with st.form("hybridRight"):
        btnResult = st.form_submit_button('※~ Hybrid ~※')
    if btnResult:
        st.session_state.hybrids += 1

with autoColumn3:
    mobility = st.checkbox('Mobility')

    if mobility:
        autoMobility = True
        st.text('Mobility: ' + str(autoMobility))
    else:
        autoMobility = False
        st.text('Mobility: ' + str(autoMobility))

with autoColumn4:
    autoDock = st.checkbox('Docking')

    if autoDock:
        autoDocking = True
        st.text('Docked: ' + str(autoDocking))
    else:
        autoDocking = False
        st.text('Docked: ' + str(autoDocking))

with autoColumn5:
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
    passwordInput = st.text_input("Insert Password:", placeholder='Password', max_chars=None)
    btnResult = st.form_submit_button('Upload')

if btnResult:
    if(passwordInput.lower() == lines[1]):
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
        f.write('\nCones: ' + cones)
        f.write('\nCubes: ' + cubes)
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

# text_contents = 'Team Number: ' + teamInput
# st.download_button('Download some text', text_contents)