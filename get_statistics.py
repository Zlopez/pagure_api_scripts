"""
This script will obtains issues from the specified issue tracker
and print some interesting statistics from those data.
"""
import json

import arrow
import click
import requests

PAGURE_URL="https://pagure.io/"

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
    url = PAGURE_URL + "api/0/" + repository + "/issues?status=Closed&since=" + str(since.int_timestamp)
    r = requests.get(url)

    # click.echo(json.dumps(r.json(), indent=4, sort_keys=True))

    if r.status_code == 200:
        data = r.json()
        per_page = data["pagination"]["per_page"]
        pages = data["pagination"]["pages"]
        r = requests.get(data["pagination"]["last"])
        if r.status_code == 200:
            data = r.json()
            total_issues = per_page * (pages - 1) + data["total_issues"]
        else:
            click.echo("Status code: {}".format(r.status_code))
            raise click.UsageError("Pagure API call for url {} returned error".format(data["pagination"]["last"]))

        click.echo("Total issues: {}".format(total_issues))
    else:
        click.echo("Status code: {}".format(r.status_code))
        raise click.UsageError("Pagure API call for url {} returned error".format(url))

if __name__ == "__main__":
    cli.add_command(closed_issues)
    cli()
