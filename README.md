# pagure_api_scripts
This repository contains scripts using API calls to work with pagure


## Quick start
1. Clone this repository
  `git clone https://github.com/Zlopez/pagure_api_scripts.git`
2. Enter the directory
  `cd pagure_api_scripts`
3. Create a python virtual env
  `python -m venv .venv`
4. Activate the virtual env
  `source .venv/bin/activate`
5. Install requirements
  `pip install -r requirements`
6. Start the script
  `python pagure_api_scripts_cli.py closed-issues fedora-infra`

## Usage

## closed-issues command
This command is retrieving useful data about closed issues from specified pagure repository.

`python pagure_api_scripts_cli.py closed-issues <repository>`

This will retrieve all closed issues in the last 30 days from the `repository` and print aggregated data.

`python pagure_api_scripts_cli.py closed-issues <repository> --days-ago 5`

This will retrieve all closed issues in the last 5 days from the `repository` and print aggregated data.

`python pagure_api_scripts_cli.py closed-issues <repository> --days-ago 5 --till 11.05.2022`

This will retrieve all closed issues in the last 5 days till 11.05.2022 from the `repository`
and print aggregated data.

## open-issues command
This command is retrieving useful data about open issues from specified pagure repository.

`python pagure_api_scripts_cli.py open-issues <repository>`

This will retrieve all open issues in the last 30 days from the `repository` and print aggregated data.

`python pagure_api_scripts_cli.py open-issues <repository> --days-ago 5`

This will retrieve all open issues in the last 5 days from the `repository` and print aggregated data.

`python pagure_api_scripts_cli.py open-issues <repository> --days-ago 5 --till 11.05.2022`

This will retrieve all open issues in the last 5 days till 11.05.2022 from the `repository`
and print aggregated data.

## update-google-spreadsheet command
This command updates specified Google Spreadsheet with the data about closed/open issues from
pagure repositories. Spreadsheet is identified by `spreadsheetId` which could be obtained from
document url `https://docs.google.com/spreadsheets/d/<spreadsheetId/edit`.

`python pagure_api_scripts_cli.py update-google-spreadsheet <spreadsheet_id> <repository>`

This will retrieve all open/closed issues in the last 7 days from the `repository` and saves aggregated data to Google Spreadsheet.

`python pagure_api_scripts_cli.py update-google-spreadsheet --days-ago 5 <spreadsheet_id> <repository>`

This will retrieve all open/closed issues in the last 5 days from the `repository` and saves aggregated data to Google Spreadsheet.

`python pagure_api_scripts_cli.py update-google-spreadsheet --days-ago 5 --till 11.05.2022 <spreadsheet_id> <repository>`

This will retrieve all open/closed issues in the last 5 days till 11.05.2022 from the `repository`
and saves aggregated data to Google Spreadsheet.

`python pagure_api_scripts_cli.py update-google-spreadsheet <spreadsheet_id> <repository1> <repository2>`

This will retrieve all open/closed issues in the last 7 days from the `repository1`, `repository2` and saves aggregated data to Google Spreadsheet. You can specify unlimited number of repositories, but the repositories need to be last argument for the command.
