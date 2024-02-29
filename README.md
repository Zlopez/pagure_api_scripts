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

## get_statistics
This script is retrieving various useful data from specified pagure repository.

### Usage
`python pagure_api_scripts_cli.py closed-issues <repository>`

This will retrieve all closed issues in the last 30 days from the `repository` and print aggregated data.

`python pagure_api_scripts_cli.py closed-issues <repository> --days-ago 5`

This will retrieve all closed issues in the last 5 days from the `repository` and print aggregated data.

`python pagure_api_scripts_cli.py closed-issues <repository> --days-ago 5 --till 11.05.2022`

This will retrieve all closed issues in the last 5 days till 11.05.2022 from the `repository`
and print aggregated data.

`python pagure_api_scripts_cli.py open-issues <repository>`

This will retrieve all open issues in the last 30 days from the `repository` and print aggregated data.

`python pagure_api_scripts_cli.py open-issues <repository> --days-ago 5`

This will retrieve all open issues in the last 5 days from the `repository` and print aggregated data.

`python pagure_api_scripts_cli.py open-issues <repository> --days-ago 5 --till 11.05.2022`

This will retrieve all open issues in the last 5 days till 11.05.2022 from the `repository`
and print aggregated data.
