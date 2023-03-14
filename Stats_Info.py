from __future__ import print_function

import streamlit as st
import tbapy, os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

username = os.getlogin()

fileOrigin = "C:\\Users\ " + username + "\encryption.txt"
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

with st.form("Teams"):
    btnResult = st.form_submit_button('Show Teams (BETA)')

if btnResult:
    try:
        os.system('cls')
        username = os.getlogin()

        credOrigin = "C:\\Users\ " + username + "\Sheet_API_Creds\ " + "credentials.json"
        credPath = credOrigin.replace(" ", "")

        tokenOrigin = "C:\\Users\ " + username + "\Sheet_API_Creds\ " + "token.json"
        tokenPath = tokenOrigin.replace(" ", "")

        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

        SAMPLE_SPREADSHEET_ID = '1BESNawhGsaBgJi5erxkbdp5yib7a7BUWm5cdeL5ak-M'
        # All Teams : SAMPLE_RANGE_NAME = 'TeamList!A2:C8015'
        SAMPLE_RANGE_NAME = 'TeamList!A2:C85'

        # https://gsheets.readthedocs.io/en/stable/
        # https://www.thebluealliance.com/teams/

        def main():
                creds = None
                if os.path.exists(tokenPath):
                        creds = Credentials.from_authorized_user_file(tokenPath, SCOPES)
                if not creds or not creds.valid:
                        if creds and creds.expired and creds.refresh_token:
                                creds.refresh(Request())
                        else:
                                flow = InstalledAppFlow.from_client_secrets_file(
                                credPath, SCOPES)
                                creds = flow.run_local_server(port=0)
                        with open(tokenPath, 'w') as token:
                                token.write(creds.to_json())

                try:
                        service = build('sheets', 'v4', credentials=creds)
                        sheet = service.spreadsheets()
                        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                                range=SAMPLE_RANGE_NAME).execute()
                        values = result.get('values', [])

                        if not values:
                                st.write('No data found.')
                                return

                        for row in values:
                                st.write('Team %s - %s - %s' % (row[0], row[1], row[2]))
                except HttpError as err:
                        print(err)

        if __name__ == '__main__':
                main()
    except:
        print('rip')