"""
This script will obtains issues from the specified issue tracker
and print some interesting statistics from those data.
"""
import json
import statistics

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

    aggregated_data = aggregate_stats(data)

    click.echo("")
    click.echo("Time to Close:")
    click.echo("* Maximum: {}".format(aggregated_data["maximum_ttc"]))
    click.echo("* Minimum: {}".format(aggregated_data["minimum_ttc"]))
    click.echo("* Average: {}".format(aggregated_data["average_ttc"]))
    click.echo("* Median: {}".format(aggregated_data["median_ttc"]))

    click.echo("")
    click.echo("Resolution:")
    for key, value in aggregated_data["resolution"].items():
        click.echo("* {}: {}".format(key, value))

    click.echo("")
    click.echo("Gain:")
    for key, value in aggregated_data["gain"].items():
        click.echo("* {}: {}".format(key, value))

    click.echo("")
    click.echo("Trouble:")
    for key, value in aggregated_data["trouble"].items():
        click.echo("* {}: {}".format(key, value))

    click.echo("")
    click.echo("Ops: {}".format(aggregated_data["ops"]))
    click.echo("Dev: {}".format(aggregated_data["dev"]))

def aggregate_stats(data: dict):
    """
    Aggregate informative statistics from the data.

    Params:
      data: Data to sift through.

    Returns:
      Dict with statistics from the data.

    Example output::
      {
        "maximum_ttc": 100, # Maximum time to close
        "minimum_ttc": 1, # Minimum time to close
        "average_ttc": 10, # Average time to close
        "median_ttc": 10, # Average time to close
        "resolution": { # Contains all types of resolutions and their count
          "fixed": 5,
          ...
        },
        "gain": { # Contains all gain tags and their count
          "low-gain": 10,
          ...
        },
        "trouble": { # Contains all trouble tags and their count
          "low-trouble": 10,
          ...
        },
        "ops": 10, # How many ops issues were closed
        "dev": 10, # How many dev issues were closed
      }
    """
    aggregated_data = {
        "maximum_ttc": 0,
        "minimum_ttc": 0,
        "average_ttc": 0,
        "median_ttc": 0,
        "resolution": {},
        "gain": {
            "no_tag": 0,
        },
        "trouble": {
            "no_tag": 0
        },
        "ops": 0,
        "dev": 0,
    }
    time_to_close_list = []

    for issue_dict in data["issues"]:
        for issue in issue_dict.values():
            # time to close
            time_to_close_list.append(issue["time_to_close"])

            # resolution
            if issue["resolution"] in aggregated_data["resolution"]:
                aggregated_data["resolution"][issue["resolution"]] = aggregated_data["resolution"][issue["resolution"]] + 1
            else:
                aggregated_data["resolution"][issue["resolution"]] = 1

            # gain
            if issue["gain"]:
                if issue["gain"][0] in aggregated_data["gain"]:
                    aggregated_data["gain"][issue["gain"][0]] = aggregated_data["gain"][issue["gain"][0]] + 1
                else:
                    aggregated_data["gain"][issue["gain"][0]] = 1
            else:
                aggregated_data["gain"]["no_tag"] = aggregated_data["gain"]["no_tag"] + 1

            # trouble
            if issue["trouble"]:
                if issue["trouble"][0] in aggregated_data["trouble"]:
                    aggregated_data["trouble"][issue["trouble"][0]] = aggregated_data["trouble"][issue["trouble"][0]] + 1
                else:
                    aggregated_data["trouble"][issue["trouble"][0]] = 1
            else:
                aggregated_data["trouble"]["no_tag"] = aggregated_data["trouble"]["no_tag"] + 1

            # ops
            if issue["ops"]:
                aggregated_data["ops"] = aggregated_data["ops"] + 1

            # dev
            if issue["dev"]:
                aggregated_data["dev"] = aggregated_data["dev"] + 1

    # Get data from time to close list
    aggregated_data["maximum_ttc"] = max(time_to_close_list)
    aggregated_data["minimum_ttc"] = min(time_to_close_list)
    aggregated_data["average_ttc"] = sum(time_to_close_list) / len(time_to_close_list)
    aggregated_data["median_ttc"] = statistics.median(time_to_close_list)

    return aggregated_data

def get_page_data(url: str):
    """
    Gets data from the current page returned by pagination.
    It does some calculations, like time to close etc.

    Params:
      url: Url for the page

    Returns:
      Dictionary containing issues with data we care about.

    Example output::
      {
        "issues": [
          {
            0: { # Id of the issue
              "time_to_close": 10, # Time to close in days
              "resolution": "fixed", # Resolution of the ticket
              "gain": ["low-gain"], # Issue gain value tag
              "trouble": ["low-trouble"], # Issue trouble value tag
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
            # Skip the ticket if any on the dates is not filled
            if not issue["closed_at"] or not issue["date_created"]:
                continue

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
        click.secho(click.style("Status code '{}' returned for url '{}'. Skipping...".format(r.status_code, url), fg="red"))

    return data


if __name__ == "__main__":
    cli.add_command(closed_issues)
    cli()
