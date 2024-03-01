"""
This script is a command line client for pagure_api_scripts module.
"""
import arrow
import click

import pagure_api_scripts.get_statistics as get_statistics
import pagure_api_scripts.google_docs as google_docs


@click.group()
def cli():
    pass


@click.command()
@click.option("--days-ago", default=30, help="How many days ago to look for open issues.")
@click.option("--till", default=None, help="Show results till this date. Expects date in DD.MM.YYYY format (31.12.2021).")
@click.argument('repository')
def open_issues(days_ago: int, till: str, repository: str):
    """
    Get open issues from the repository and print their count.

    Params:
      days_ago: How many days ago to look for the issues
      till: Limit results to the day set by this argument. Default None will be replaced by `arrow.utcnow()`.
      repository: Repository namespace to check
    """
    if till:
        till = arrow.get(till, "DD.MM.YYYY")
    else:
        till = arrow.utcnow()
    since_arg = till.shift(days=-days_ago)

    click.echo("Retrieving open issues from {} opened in last {} days ({}) till {}".format(
        repository, days_ago, since_arg.format("DD.MM.YYYY"), since_arg.shift(days=+days_ago).format("DD.MM.YYYY")))

    data = get_statistics.open_issues(till, since_arg, repository)

    click.echo("Total number of retrieved issues: {}".format(data["total"]))

    click.echo("Already closed: {}".format(data["closed"]))

    click.echo("")
    click.echo("Close Resolution:")
    for key, value in data["resolution"].items():
        click.echo("* {}: {}".format(key, value))

    click.echo("")
    click.echo("Gain:")
    for key, value in data["gain"].items():
        click.echo("* {}: {}".format(key, value))

    click.echo("")
    click.echo("Trouble:")
    for key, value in data["trouble"].items():
        click.echo("* {}: {}".format(key, value))

    click.echo("")
    click.echo("Ops: {}".format(data["ops"]))
    click.echo("Dev: {}".format(data["dev"]))


@click.command()
@click.option("--days-ago", default=30, help="How many days ago to look for closed issues.")
@click.option("--till", default=None, help="Show results till this date. Expects date in DD.MM.YYYY format (31.12.2021).")
@click.argument('repository')
def closed_issues(days_ago: int, till: str, repository: str):
    """
    Get closed issues from the repository and print their count.

    Params:
      days_ago: How many days ago to look for the issues
      till: Limit results to the day set by this argument. Default None will be replaced by `arrow.utcnow()`.
      repository: Repository namespace to check
    """
    if till:
        till = arrow.get(till, "DD.MM.YYYY")
    else:
        till = arrow.utcnow()
    since_arg = till.shift(days=-days_ago)

    click.echo("Retrieving closed issues from {} updated in last {} days ({}) till {}".format(
        repository, days_ago, since_arg.format("DD.MM.YYYY"), since_arg.shift(days=+days_ago).format("DD.MM.YYYY")))

    data = get_statistics.closed_issues(till, since_arg, repository)

    click.echo("Total number of retrieved issues: {}".format(data["total"]))

    click.echo("")
    click.echo("Time to Close:")
    click.echo("* Maximum: {}".format(data["maximum_ttc"]))
    click.echo("* Minimum: {}".format(data["minimum_ttc"]))
    click.echo("* Average: {}".format(data["average_ttc"]))
    click.echo("* Median: {}".format(data["median_ttc"]))

    click.echo("")
    click.echo("Resolution:")
    for key, value in data["resolution"].items():
        click.echo("* {}: {}".format(key, value))

    click.echo("")
    click.echo("Gain:")
    for key, value in data["gain"].items():
        click.echo("* {}: {}".format(key, value))

    click.echo("")
    click.echo("Trouble:")
    for key, value in data["trouble"].items():
        click.echo("* {}: {}".format(key, value))

    click.echo("")
    click.echo("Ops: {}".format(data["ops"]))
    click.echo("Dev: {}".format(data["dev"]))


@click.command()
@click.option("--days-ago", default=7, help="How many days ago to look for closed issues.")
@click.option("--till", default=None, help="Show results till this date. Expects date in DD.MM.YYYY format (31.12.2021).")
@click.argument("google_spreadsheet")
@click.argument("repositories", nargs=-1)
def update_google_spreadsheet(
        days_ago: int, till: str, google_spreadsheet: str, repositories: tuple
):
    """
    Update google spreadsheet by statistics from specified repositories.

    Params:
      days_ago: How many days ago to look for the issues
      till: Limit results to the day set by this argument. Default None will be replaced by `arrow.utcnow()`.
      repository: Repository namespace to check
    """
    if till:
        till = arrow.get(till, "DD.MM.YYYY")
    else:
        till = arrow.utcnow()
    since_arg = till.shift(days=-days_ago)

    click.echo("Retrieving open and closed issues from {} updated in last {} days ({}) till {}".format(
        ", ".join(repositories), days_ago, since_arg.format("DD.MM.YYYY"), since_arg.shift(days=+days_ago).format("DD.MM.YYYY")))

    data = {}
    data["since"] = since_arg
    data["till"] = till
    data["repositories"] = {}
    for repository in repositories:
        data["repositories"][repository] = {}
        repository_data = get_statistics.open_issues(till, since_arg, repository)
        data["repositories"][repository]["Opened issues"] = repository_data["total"]
        repository_data = get_statistics.closed_issues(till, since_arg, repository)
        data["repositories"][repository]["Closed issues"] = repository_data

    click.echo("Data retrieved. Updating google spreadsheet 'https://docs.google.com/spreadsheets/d/{}/edit'".format(google_spreadsheet))
    google_docs.add_new_sheet(data, google_spreadsheet)


if __name__ == "__main__":
    cli.add_command(closed_issues)
    cli.add_command(open_issues)
    cli.add_command(update_google_spreadsheet)
    cli()
