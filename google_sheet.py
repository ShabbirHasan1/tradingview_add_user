from googleapiclient.discovery import build
from google.oauth2 import service_account

from config import google_account_api_path

SAMPLE_RANGE_NAME = 'A1:AA1000000'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def get_google_sheet_value(sheet_id):
    credentials = service_account.Credentials.from_service_account_file(google_account_api_path, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=SAMPLE_RANGE_NAME).execute()
    return result.get('values', [])
