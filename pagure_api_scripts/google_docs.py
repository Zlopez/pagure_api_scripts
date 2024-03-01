"""Script for working with google docs with pagure_api_scripts."""
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Pagure URL
PAGURE_URL = "https://pagure.io/"

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

        # Merge cells
        column = 0
        for repository in data["repositories"]:
            # Repository name
            requests.append(
                {
                    "mergeCells": {
                        "range": {
                            "sheetId": sheetId,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": column,
                            "endColumnIndex": column + 2
                        }
                    }
                }
            )
            # Time to close
            requests.append(
                {
                    "mergeCells": {
                        "range": {
                            "sheetId": sheetId,
                            "startRowIndex": 4,
                            "endRowIndex": 5,
                            "startColumnIndex": column,
                            "endColumnIndex": column + 2
                        }
                    }
                }
            )
            # Resolution
            requests.append(
                {
                    "mergeCells": {
                        "range": {
                            "sheetId": sheetId,
                            "startRowIndex": 10,
                            "endRowIndex": 11,
                            "startColumnIndex": column,
                            "endColumnIndex": column + 2
                        }
                    }
                }
            )
            # Gain
            requests.append(
                {
                    "mergeCells": {
                        "range": {
                            "sheetId": sheetId,
                            "startRowIndex": 21,
                            "endRowIndex": 22,
                            "startColumnIndex": column,
                            "endColumnIndex": column + 2
                        }
                    }
                }
            )
            # Trouble
            requests.append(
                {
                    "mergeCells": {
                        "range": {
                            "sheetId": sheetId,
                            "startRowIndex": 27,
                            "endRowIndex": 28,
                            "startColumnIndex": column,
                            "endColumnIndex": column + 2
                        }
                    }
                }
            )
            column += 4

        column = 0
        # Prepare the ranges with the data
        for repository in data["repositories"]:
            # Repository name with link
            requests.append(
                {
                    "updateCells": {
                        "range": {
                            "sheetId": sheetId,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": column,
                            "endColumnIndex": column + 2
                        },
                        "fields": "*",
                        "rows": [
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "formulaValue": f"=HYPERLINK(\"{PAGURE_URL + repository + '/issues'}\", \"{repository}\")",
                                        },
                                        "userEnteredFormat": {
                                            "textFormat": {
                                                "bold": True,
                                            },
                                            "horizontalAlignment": "CENTER"
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            )
            # Total Open/Closed issues
            requests.append(
                {
                    "updateCells": {
                        "range": {
                            "sheetId": sheetId,
                            "startRowIndex": 1,
                            "endRowIndex": 3,
                            "startColumnIndex": column,
                            "endColumnIndex": column + 2
                        },
                        "fields": "*",
                        "rows": [
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "Opened issues",
                                        },
                                    },
                                    {
                                        "userEnteredValue": {
                                            "numberValue": data["repositories"][repository]["Opened issues"],
                                        },
                                    },
                                ]
                            },
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "Closed issues",
                                        },
                                    },
                                    {
                                        "userEnteredValue": {
                                            "numberValue": data["repositories"][repository]["Closed issues"]["total"],
                                        },
                                    },
                                ]
                            },
                        ]
                    }
                }
            )
            # Time to close
            requests.append(
                {
                    "updateCells": {
                        "range": {
                            "sheetId": sheetId,
                            "startRowIndex": 4,
                            "endRowIndex": 10,
                            "startColumnIndex": column,
                            "endColumnIndex": column + 2
                        },
                        "fields": "*",
                        "rows": [
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "Time to Close (days):",
                                        },
                                        "userEnteredFormat": {
                                            "textFormat": {
                                                "bold": True,
                                            },
                                        }
                                    }
                                ]
                            },
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "Maximum",
                                        },
                                    },
                                    {
                                        "userEnteredValue": {
                                            "numberValue": data["repositories"][repository]["Closed issues"]["maximum_ttc"],
                                        },
                                    },
                                ]
                            },
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "Minimum",
                                        },
                                    },
                                    {
                                        "userEnteredValue": {
                                            "numberValue": data["repositories"][repository]["Closed issues"]["minimum_ttc"],
                                        },
                                    },
                                ]
                            },
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "Average",
                                        },
                                    },
                                    {
                                        "userEnteredValue": {
                                            "numberValue": data["repositories"][repository]["Closed issues"]["average_ttc"],
                                        },
                                    },
                                ]
                            },
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "Median",
                                        },
                                    },
                                    {
                                        "userEnteredValue": {
                                            "numberValue": data["repositories"][repository]["Closed issues"]["median_ttc"],
                                        },
                                    },
                                ]
                            },
                        ]
                    }
                }
            )

            # Resolution
            requests.append(
                {
                    "updateCells": {
                        "range": {
                            "sheetId": sheetId,
                            "startRowIndex": 10,
                            "endRowIndex": 11,
                            "startColumnIndex": column,
                            "endColumnIndex": column + 2
                        },
                        "fields": "*",
                        "rows": [
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "Resolution",
                                        },
                                        "userEnteredFormat": {
                                            "textFormat": {
                                                "bold": True,
                                            },
                                        }
                                    }
                                ]
                            },
                        ]
                    }
                }
            )

            row = 11
            # Positive resolutions
            for resolution in data["repositories"][repository]["Closed issues"]["resolution"]:
                if resolution in POSITIVE_RESOLUTION:
                    requests.append(
                        {
                            "updateCells": {
                                "range": {
                                    "sheetId": sheetId,
                                    "startRowIndex": row,
                                    "endRowIndex": row + 1,
                                    "startColumnIndex": column,
                                    "endColumnIndex": column + 2
                                },
                                "fields": "*",
                                "rows": [
                                    {
                                        "values": [
                                            {
                                                "userEnteredValue": {
                                                    "stringValue": resolution,
                                                },
                                                "userEnteredFormat": {
                                                    "backgroundColor": {
                                                        "green": 0.9,
                                                        "red": 0.7,
                                                        "blue": 0.7
                                                    },
                                                }
                                            },
                                            {
                                                "userEnteredValue": {
                                                    "numberValue": data["repositories"][repository]["Closed issues"]["resolution"][resolution],
                                                },
                                                "userEnteredFormat": {
                                                    "backgroundColor": {
                                                        "green": 0.9,
                                                        "red": 0.7,
                                                        "blue": 0.7
                                                    },
                                                }
                                            },
                                        ]
                                    },
                                ]
                            }
                        }
                    )
                    row += 1

            # Negative resolutions
            for resolution in data["repositories"][repository]["Closed issues"]["resolution"]:
                if resolution in NEGATIVE_RESOLUTION:
                    requests.append(
                        {
                            "updateCells": {
                                "range": {
                                    "sheetId": sheetId,
                                    "startRowIndex": row,
                                    "endRowIndex": row + 1,
                                    "startColumnIndex": column,
                                    "endColumnIndex": column + 2
                                },
                                "fields": "*",
                                "rows": [
                                    {
                                        "values": [
                                            {
                                                "userEnteredValue": {
                                                    "stringValue": resolution,
                                                },
                                                "userEnteredFormat": {
                                                    "backgroundColor": {
                                                        "green": 0.8,
                                                        "red": 1.0,
                                                        "blue": 0.8
                                                    },
                                                }
                                            },
                                            {
                                                "userEnteredValue": {
                                                    "numberValue": data["repositories"][repository]["Closed issues"]["resolution"][resolution],
                                                },
                                                "userEnteredFormat": {
                                                    "backgroundColor": {
                                                        "green": 0.8,
                                                        "red": 1.0,
                                                        "blue": 0.8
                                                    },
                                                }
                                            },
                                        ]
                                    },
                                ]
                            }
                        }
                    )
                    row += 1

            # Gain
            requests.append(
                {
                    "updateCells": {
                        "range": {
                            "sheetId": sheetId,
                            "startRowIndex": 21,
                            "endRowIndex": 26,
                            "startColumnIndex": column,
                            "endColumnIndex": column + 2
                        },
                        "fields": "*",
                        "rows": [
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "Gain",
                                        },
                                        "userEnteredFormat": {
                                            "textFormat": {
                                                "bold": True,
                                            },
                                        }
                                    }
                                ]
                            },
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "no_tag",
                                        },
                                    },
                                    {
                                        "userEnteredValue": {
                                            "numberValue": data["repositories"][repository]["Closed issues"]["gain"]["no_tag"],
                                        },
                                    },
                                ]
                            },
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "low-gain",
                                        },
                                    },
                                    {
                                        "userEnteredValue": {
                                            "numberValue": data["repositories"][repository]["Closed issues"]["gain"]["low-gain"],
                                        },
                                    },
                                ]
                            },
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "medium-gain",
                                        },
                                    },
                                    {
                                        "userEnteredValue": {
                                            "numberValue": data["repositories"][repository]["Closed issues"]["gain"]["medium-gain"],
                                        },
                                    },
                                ]
                            },
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "high-gain",
                                        },
                                    },
                                    {
                                        "userEnteredValue": {
                                            "numberValue": data["repositories"][repository]["Closed issues"]["gain"]["high-gain"],
                                        },
                                    },
                                ]
                            },
                        ]
                    }
                }
            )

            # Trouble
            requests.append(
                {
                    "updateCells": {
                        "range": {
                            "sheetId": sheetId,
                            "startRowIndex": 27,
                            "endRowIndex": 32,
                            "startColumnIndex": column,
                            "endColumnIndex": column + 2
                        },
                        "fields": "*",
                        "rows": [
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "Trouble",
                                        },
                                        "userEnteredFormat": {
                                            "textFormat": {
                                                "bold": True,
                                            },
                                        }
                                    }
                                ]
                            },
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "no_tag",
                                        },
                                    },
                                    {
                                        "userEnteredValue": {
                                            "numberValue": data["repositories"][repository]["Closed issues"]["trouble"]["no_tag"],
                                        },
                                    },
                                ]
                            },
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "low-trouble",
                                        },
                                    },
                                    {
                                        "userEnteredValue": {
                                            "numberValue": data["repositories"][repository]["Closed issues"]["trouble"]["low-trouble"],
                                        },
                                    },
                                ]
                            },
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "medium-trouble",
                                        },
                                    },
                                    {
                                        "userEnteredValue": {
                                            "numberValue": data["repositories"][repository]["Closed issues"]["trouble"]["medium-trouble"],
                                        },
                                    },
                                ]
                            },
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "high-trouble",
                                        },
                                    },
                                    {
                                        "userEnteredValue": {
                                            "numberValue": data["repositories"][repository]["Closed issues"]["trouble"]["high-trouble"],
                                        },
                                    },
                                ]
                            },
                        ]
                    }
                }
            )

            # Ops/Dev
            requests.append(
                {
                    "updateCells": {
                        "range": {
                            "sheetId": sheetId,
                            "startRowIndex": 33,
                            "endRowIndex": 35,
                            "startColumnIndex": column,
                            "endColumnIndex": column + 2
                        },
                        "fields": "*",
                        "rows": [
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "Ops",
                                        },
                                    },
                                    {
                                        "userEnteredValue": {
                                            "numberValue": data["repositories"][repository]["Closed issues"]["ops"],
                                        },
                                    },
                                ]
                            },
                            {
                                "values": [
                                    {
                                        "userEnteredValue": {
                                            "stringValue": "Dev",
                                        },
                                    },
                                    {
                                        "userEnteredValue": {
                                            "numberValue": data["repositories"][repository]["Closed issues"]["dev"],
                                        },
                                    },
                                ]
                            },
                        ]
                    }
                }
            )
            column += 4

        requests.append(
            {
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": sheetId,
                        "dimension": "COLUMNS",
                    }
                }
            }
        )

        body = {"requests": requests}

        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet, body=body).execute()

    except HttpError as err:
        print(err)
