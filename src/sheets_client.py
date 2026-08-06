import os
from google.oauth2.service_account import Credentials
import gspread

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def _authenticate():
    credentials = Credentials.from_service_account_file(filename="credentials.json",
    scopes=SCOPES)
    gc = gspread.authorize(credentials)
    return gc

def _open_spreadsheet():
    gc = _authenticate()
    spreadsheet = gc.open_by_key(os.getenv("GOOGLE_SHEETS_ID"))
    sheet = spreadsheet.sheet1
    return sheet

def save_transaction(data):
    sheet = _open_spreadsheet()
    row = [
        data.get("name", "Not identified"), 
        data.get("date", "Not identified"),
        data.get("amount", "Not identified"), 
        data.get("receiver", "Not identified"),
    ]
    sheet.append_row(row)