import getpass
import os

import click
from crontab import CronTab
from croniter import croniter
from datetime import datetime

from work_journal.setup import JournalSetter
from work_journal.run import create_markdown_file


@click.group()
def main():
    pass


@main.command()
@click.argument("schedule", type=str)
@click.option(
    "--dir",
    "-d",
    "journal_folder",
    default=".",
    help="Directory for creating journals, current working directory is set as default.",
)
@click.option(
    "--job-comment",
    "-c",
    default="work_journal",
    help="Label the job with job comment, default is work_journal. Duplicated job comment is not allowed",
)
def setup(schedule, journal_folder, job_comment):
    """
    Setup a cron job to create a markdown journal on schedule.

    TIME is the cron schedule format (e.g., '0 9 * * *' for 9 AM).
    """
    new_journal = JournalSetter()

    new_journal.cron_expression = schedule
    if journal_folder == ".":
        current_folder = os.path.dirname(os.path.abspath(__file__))
        new_journal.journal_folder = current_folder
    else:
        new_journal.journal_folder = journal_folder
    new_journal.job_comment = job_comment

    new_journal.setup_new_journal()


@main.command()
@click.option(
    "--dir",
    "journal_folder",
    default=".",
    help="Directory for creating journals, current working directory is set as default.",
)
@click.option(
    "--overwrite",
    "allow_overwrite",
    is_flag=True,
    default=False,
    help="Allow overwriting the existing journal, set to False as default.",
)
def run(journal_folder, allow_overwrite):
    """create a journal and start writing immediately."""

    create_markdown_file(journal_folder, allow_overwrite)


@main.command()
@click.option(
    "--job-comment",
    "-c",
    default="work_journal",
    help="Specify the job with job comment, work_journal is set as default.",
)
def remove(job_comment):
    """Remove the previously created work_journal cron job"""
    cron = CronTab(user=getpass.getuser())
    job = next(cron.find_comment(job_comment), None)
    if job is None:
        click.echo(f"No cron job found with comment {job_comment}.")
        raise click.exceptions.Exit(code=1)
    else:
        cron.remove(job)
        cron.write()
        click.echo(f"Cron job {job_comment} removed.")
    


@main.command()
@click.option(
    "--job-comment",
    "-c",
    default="work_journal",
    help="Specify the job with job comment, work_journal is set as default.",
)
def next_run(job_comment):
    """Show when the next journal will be created."""

    cron = CronTab(user=getpass.getuser())
    job = next(cron.find_comment(job_comment), None)
    if job is None:
        click.echo(f"No cron job found with comment {job_comment}.")
    else:
        croniter_ = croniter(str(job.slices))
        next_run_time = croniter_.get_next(datetime)
        click.echo(f"Next run time for job {job_comment} is {next_run_time}.")
        

if __name__ == "__main__":
    main()
