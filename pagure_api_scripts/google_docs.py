"""Script for working with google docs with pagure_api_scripts."""
import os.path

import arrow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Ticket resolutions that are considered positive
POSITIVE_RESOLUTION = [
    "Fixed",
    "Fixed with Explanation",
    "Initiative Worthy",
    "It's all good",
    "To resubmit as CPE initiative"
]

# Ticket resolutions that are considered negative
NEGATIVE_RESOLUTION = [
    "Invalid",
    "Will Not/Can Not fix",
    "Duplicate",
    "Upstream",
    "Insufficient data",
    "Spam",
    "Can't Fix",
    "Get back later",
    "Wrong tracker",
]


def authenticate():
    """
    Authenticate using google API
    """
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def add_new_sheet(data: dict, spreadsheet: str):
    """
    Add new sheet with provided data to document.

    Params:
      data: Data to put in the new sheet
      spreadsheet: Spreadsheet to update
    """
    creds = authenticate()
    try:
        service = build("sheets", "v4", credentials=creds)

        requests = []

        # Create a new sheet
        requests.append(
            {
                "addSheet": {
                    "properties": {
                        "title": (
                            data["since"].format("DD.MM.") + "-" +
                            data["till"].format("DD.MM.YYYY")
                        )
                    }
                }
            }
        )
        body = {"requests": requests}

        response = (
            service.spreadsheets()
            .batchUpdate(spreadsheetId=spreadsheet, body=body)
            .execute()
        )
        for reply in response.get("replies"):
            if "addSheet" in reply:
                sheetId = reply.get("addSheet").get("properties").get("sheetId")

        requests = []

        # Merge A1:B1
        requests.append(
            {
                "mergeCells": {
                    "range": {
                        "sheetId": sheetId,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 2
                    }
                }
            }
        )

        # Merge E1:F1
        requests.append(
            {
                "mergeCells": {
                    "range": {
                        "sheetId": sheetId,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 4,
                        "endColumnIndex": 6
                    }
                }
            }
        )

        # Merge I1:J1
        requests.append(
            {
                "mergeCells": {
                    "range": {
                        "sheetId": sheetId,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 8,
                        "endColumnIndex": 10
                    }
                }
            }
        )

        body = {"requests": requests}

        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet, body=body).execute()

    except HttpError as err:
        print(err)
