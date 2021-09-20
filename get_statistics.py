"""
This script will obtains issues from the specified issue tracker
and print some interesting statistics from those data.
"""
import json

import arrow
import click
import requests

PAGURE_URL="https://pagure.io/"

GAIN_VALUES = [
    "low-gain",
    "medium-gain",
    "high-gain"
]

TROUBLE_VALUES = [
    "low-trouble",
    "medium-trouble",
    "high-trouble"
]

@click.group()
def cli():
    pass

@click.command()
@click.option("--days-ago", default=30, help="How many days ago to look for closed issues.")
@click.argument('repository')
def closed_issues(days_ago: int, repository: str):
    """
    Get closed issues from the repository and print their count.

    Params:
      days_ago: How many days ago to look for the issues
      repository: Repository namespace to check
    """
    since = arrow.utcnow().shift(days=-days_ago)
    next_page = PAGURE_URL + "api/0/" + repository + "/issues?status=Closed&since=" + str(since.int_timestamp)
    data = {
        "issues": [],
        "total": 0,
    }

    click.echo("Retrieving closed issue from {} updated in last {} days".format(repository, days_ago))

    while next_page:
        page_data = get_page_data(next_page)
        # click.echo(json.dumps(page_data, indent=4))
        data["issues"] = data["issues"] + page_data["issues"]
        data["total"] = data["total"] + page_data["total"]
        next_page = page_data["next_page"]

    click.echo("Total number of retrieved issues: {}".format(data["total"]))


def get_page_data(url: str):
    """
    Gets data from the current page returned by pagination.
    It does some calculations, like time to close etc.

    Params:
      url: Url for the page

    Returns:
      Dictionary containing issues with data we care about.

      {
        "issues": [
          {
            0: { # Id of the issue
              "time_to_close": 10, # Time to close in days
              "resolution": "fixed", # Resolution of the ticket
              "gain": "low-gain", # Issue gain value tag
              "trouble": "low-trouble", # Issue trouble value tag
              "ops": True, # Issue has ops tag
              "dev": True, # Issue has dev tag
            },
          },
        ],
        "total": 1, # Number of issues on the page
        "next_page": "https://pagure.io/next_page" # URL for next page
      }
    """
    r = requests.get(url)
    data = {
        "issues": [],
        "total": 0,
        "next_page": None,
    }

    if r.status_code == requests.codes.ok:
        page = r.json()
        for issue in page["issues"]:
            entry = {
                issue["id"]: {
                    "time_to_close": (arrow.Arrow.fromtimestamp(issue["closed_at"]) - arrow.Arrow.fromtimestamp(issue["date_created"])).days,
                    "resolution": issue["close_status"],
                    "gain": [tag for tag in issue["tags"] if tag in GAIN_VALUES],
                    "trouble": [tag for tag in issue["tags"] if tag in TROUBLE_VALUES],
                    "ops": "ops" in issue["tags"],
                    "dev": "dev" in issue["tags"],
                }
            }
            data["issues"].append(entry)
        data["total"] = len(data["issues"])
        data["next_page"] = page["pagination"]["next"]
    else:
        click.echo("Status code '{}' returned for url '{}'. Skipping...".format(r.status_code, url))

    return data


if __name__ == "__main__":
    cli.add_command(closed_issues)
    cli()
