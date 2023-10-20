import getpass
import os
import sys
from cron_descriptor import get_description
import subprocess

import click
from crontab import CronTab, CronSlices
from croniter import croniter
from datetime import datetime

class JournalSetter:
    def __init__(self) -> None:
        self._cron_expression = None
        self._journal_folder = None
        self._job_comment = None
        self._cron = CronTab(user=getpass.getuser())

    @property
    def cron_expression(self):
        return self._cron_expression

    @cron_expression.setter
    def cron_expression(self, cron_expression):
        if not CronSlices.is_valid(cron_expression):
            click.echo("Error: schedule is not valid.")
            raise click.exceptions.Exit(code=1)
        self._cron_expression = cron_expression

    @property
    def journal_folder(self):
        return self._journal_folder

    @journal_folder.setter
    def journal_folder(self, path):
        if not os.path.exists(path):
            click.echo(f"Warning: directory not found. Making a a folder at {path}...")
            try:
                os.makedirs(path)
                click.echo("Succeeded.")
            except PermissionError:
                click.echo(
                    "Error: you don't have permission to make a new folder."
                )
                raise click.exceptions.Exit(code=1)

        self._journal_folder = path

    @property
    def job_comment(self):
        return self._job_comment

    @job_comment.setter
    def job_comment(self, job_comment):
        self._job_comment = job_comment

    def _job_comment_used(self):
        job_comment_is_used = False

        result = self._cron.find_comment(self._job_comment)
        if len(list(result)) != 0:
            job_comment_is_used = True
        return job_comment_is_used

    def _log_maker(selfs):
        cwd = os.path.dirname(os.path.abspath(__file__))
        return f">> {cwd}/cronlog.log 2>&1"

    def _send_finishing_msg(self):
        expression = get_description(self._cron_expression)
        msg = f"Journal is scheduled at {expression} with job comment {self._job_comment}, and will be saved at {self._journal_folder}."
        click.echo(msg)

    def setup_new_journal(self):
        if self._job_comment_used():
            click.echo(f"Job comment {self._job_comment} is already used. Exiting ...")
            raise click.exceptions.Exit(code=1)
        compiler_path = f"{sys.prefix}/bin/python"
        cli = f"{os.path.dirname(__file__)}/cli.py"
        command = f'DISPLAY=:1 {compiler_path} {cli} run --dir "{self._journal_folder}"{self._log_maker()}'
        job = self._cron.new(command=command, comment=self._job_comment)
        job.setall(self._cron_expression)
        self._cron.write()
        self._send_finishing_msg()

def create_markdown_file(journal_folder, allow_overwrite):
    now = datetime.now()
    current_year_and_month = now.strftime("%Y-%m")
    current_date = now.strftime("%Y-%m-%d")

    # make monthly folder
    monthly_folder_path = os.path.join(journal_folder, current_year_and_month)
    if not os.path.exists(monthly_folder_path):
        os.makedirs(monthly_folder_path)

    # check if journal for today already existed
    journal_to_be_created = os.path.join(
        monthly_folder_path, current_date + "-journal.md"
    )
    if os.path.exists(journal_to_be_created) and not allow_overwrite:
        click.echo("Journal for today is already created. Exiting...")
        raise click.exceptions.Exit(code=1)

    # create journal
    with open(journal_to_be_created, "w") as f:
        heading = f"# {now.strftime('%B %d, %Y')} Working Journal\n\n"
        f.write(heading)

    open_text_editor(journal_to_be_created)


def open_text_editor(filename):
    try:
        editor_command = "/usr/bin/gedit"
        subprocess.run([editor_command, filename])
    except Exception as e:
        click.echo(f"An error occurred: {e}")


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
