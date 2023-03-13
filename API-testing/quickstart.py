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

credOrigin = "C:\\Users\ " + username + "\OneDrive\ " + "Documents\ " + "api\ " + "credentials.json"
credPath = credOrigin.replace(" ", "")

tokenOrigin = "C:\\Users\ " + username + "\OneDrive\ " + "Documents\ " + "api\ " + "token.json"
tokenPath = tokenOrigin.replace(" ", "")

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1BESNawhGsaBgJi5erxkbdp5yib7a7BUWm5cdeL5ak-M'
SAMPLE_RANGE_NAME = 'Sheet1!A2:C'

column_start = 0
column_end = 3

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
            print('Team %s : %s' % (row[column_start], row[column_end]))
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    try:
        main()
    except:
        column_end = column_end - 1
        main()