import getpass
import os
import re
from datetime import datetime

import click
from croniter import croniter
from crontab import CronItem, CronTab

from work_journal.config import config_file, config_file_path, is_valid_cmd
from work_journal.create import create_markdown_file
from work_journal.setter import JournalSetter


@click.group()
def main():
    pass


@main.command()
def create():
    """
    Create a cron job for scheduling a journal.
    """
    new_journal = JournalSetter()

    journal_name = click.prompt("Journal name", type=str, default="#")
    while new_journal.is_name_duplicated(journal_name) is True:
        click.echo("Journal name must not be duplicated.")
        journal_name = click.prompt("Journal name", type=str, default="#")
    new_journal.journal_name = journal_name

    schedule = click.prompt("Schedule", type=str)
    while not croniter.is_valid(schedule):
        click.echo("Schedule is not valid. Please consult the cron expression online.")
        schedule = click.prompt("Schedule", type=str)
    new_journal.schedule = schedule

    journal_folder = click.prompt(
        "Folder path for saving journals",
        default=os.path.join(os.path.expanduser("~"), "work_journals"),
    )
    while True:
        if os.path.isdir(journal_folder):
            break
        try:
            click.echo(f"Folder not found. Making folder {journal_folder}.")
            os.makedirs(journal_folder)
            click.echo("Succeeded.")
            break
        except PermissionError:
            click.echo(
                f"Error: you don't have permission to make a new folder at {journal_folder}."
            )
            journal_folder = click.prompt(
                "Folder path for saving journals",
                default=os.path.join(os.path.expanduser("~"), "work_journals"),
            )
    new_journal.journal_folder = journal_folder

    new_journal.setup_new_journal()


@main.command()
@click.argument("folder")
@click.option(
    "--overwrite",
    "allow_overwrite",
    is_flag=True,
    default=False,
    help="Allow overwriting the existing journal, set to False as default.",
)
def run(folder, allow_overwrite):
    """Make a journal and start writing immediately."""
    create_markdown_file(folder, allow_overwrite)


def _get_jobs(cron: CronTab):
    return cron.find_comment(re.compile(r"^work_journal_.*"))


@main.command()
@click.option("--name", default=None, help="Pass special characters in quotations.")
def remove(name: None | str):
    """Remove the previously created work_journal cron job"""
    cron = CronTab(user=getpass.getuser())

    if next(_get_jobs(cron), None) is None:
        click("There is no scheduled journal.")
    elif name is None:
        if click.confirm(
            "This will remove all scheduled journals. Proceed?", abort=True
        ):
            for job in _get_jobs(cron):
                cron.remove(job)
                journal_name = re.sub(r"^work_journal_", "", job.comment)
                click.echo(f"Journal {journal_name} removed.")
            cron.write()
            click.echo("Removed all scheduled journals.")
    else:
        name = name.strip()
        job = next(
            cron.find_comment(
                f"work_journal_{name}",
            ),
            None,
        )
        if job is None:
            click.echo(f"No journal named {name} found.")
        else:
            if click.confirm(f"Journal {name} found. Remove?", abort=True):
                cron.remove(job)
                cron.write()
                click.echo(f"Journal {name} removed.")


def _format_journal_info(job: CronItem):
    name = re.sub(r"^work_journal_", "", job.comment)
    folder = re.search(r"run\s+([^>]+)", job.command).group(1)
    schedule = str(job.slices)
    croniter_ = croniter(schedule)
    next_run_time = croniter_.get_next(datetime)

    msg = f"""
    Journal name: {name}
    Folder: {folder}
    Schedule: {schedule}
    Next run: {next_run_time}
    """
    return msg


@main.command()
@click.option("--name", default=None, help="Pass special characters in quotations.")
def info(name: None | str):
    """Show the details of the scheduled info."""

    cron = CronTab(user=getpass.getuser())
    if next(_get_jobs(cron), None) is None:
        click.echo("There is no scheduled journal.")
        return
    elif name is None:
        for job in _get_jobs(cron):
            msg = _format_journal_info(job)
            click.echo(msg)
    else:
        name = name.strip()
        job = next(
            cron.find_comment(
                f"work_journal_{name}",
            ),
            None,
        )
        if job is None:
            click.echo(f"No journal named {name} found.")
        else:
            msg = _format_journal_info(next(job))
            click.echo(msg)


@main.command
@click.option("--set-editor", type=str)
def config(set_editor):
    if set_editor is None:
        for key, value in config_file["PREFERENCES"].items():
            click.echo(f"{key} = {value}")
        return
    if is_valid_cmd(set_editor):
        config_file.set("PREFERENCES", "EDITOR", set_editor)
        with open(config_file_path, "w") as f:
            config_file.write(f)
        click.echo(f"Set journal editor to {set_editor}.")
    else:
        click.echo("Error: invalid editor command.")


if __name__ == "__main__":
    main()
