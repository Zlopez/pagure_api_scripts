# pagure_api_scripts
This repository contains scripts using API calls to work with pagure


## get_statistics
This script is retrieving various useful data from specified pagure repository.

### Usage
`python get_statistics.py closed-issues <repository>`

This will retrieve all closed issues in the last 30 days from the `repository` and print aggregated data.

`python get_statistics.py closed-issues <repository> --days-ago 5`

This will retrieve all closed issues in the last 5 days from the `repository` and print aggregated data.
