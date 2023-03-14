from __future__ import print_function

import pygsheets
import os.path
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

os.system('cls')
username = os.getlogin()

credOrigin = "C:\\Users\ " + username + "\Sheet_API_Creds\ " + "credentials.json"
credPath = credOrigin.replace(" ", "")

tokenOrigin = "C:\\Users\ " + username + "\Sheet_API_Creds\ " + "token.json"
tokenPath = tokenOrigin.replace(" ", "")

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

SAMPLE_SPREADSHEET_ID = '1BESNawhGsaBgJi5erxkbdp5yib7a7BUWm5cdeL5ak-M'
# All Teams : SAMPLE_RANGE_NAME = 'TeamList!A2:C8015'
SAMPLE_RANGE_NAME = 'TeamList!A2:C8015'

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
            print('No data found.')
            return

        for row in values:
            print('Team %s - %s - %s' % (row[0], row[1], row[2]))
    except HttpError as err:
        print(err)

if __name__ == '__main__':
    main()