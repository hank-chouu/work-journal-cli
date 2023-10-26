import getpass
import os
import subprocess
from datetime import datetime

import click
from cron_descriptor import get_description
from crontab import CronTab

from work_journal.config import EDITOR_CMD, PYTHON_PATH


class JournalCreator:
    def __init__(self) -> None:
        self._schedule = None
        self._journal_folder = None
        self._journal_name = None
        self._cron = CronTab(user=getpass.getuser())

    @property
    def schedule(self):
        return self._schedule

    @schedule.setter
    def schedule(self, schedule):
        self._schedule = schedule

    @property
    def journal_folder(self):
        return self._journal_folder

    @journal_folder.setter
    def journal_folder(self, path):
        self._journal_folder = path

    @property
    def journal_name(self):
        return self._journal_name

    @journal_name.setter
    def journal_name(self, journal_name):
        self._journal_name = journal_name.strip()

    @property
    def cron(self):
        return self._cron

    def is_name_duplicated(self, journal_name):
        job_comment = f"work_journal_{journal_name}".strip()
        find_job = self._cron.find_comment(job_comment)
        if next(find_job, None) is None:
            return False
        return True

    def _log_maker(self):
        home_dir = os.path.expanduser("~")
        os.makedirs(os.path.join(home_dir, ".work-journal-cli"), exist_ok=True)
        return f">>{home_dir}/.work-journal-cli/work-journal-{self._journal_name}.log 2>&1"

    def _send_finishing_msg(self):
        expression = get_description(self._schedule)
        msg = f"Journal is scheduled at {expression} with name {self._journal_name}, and will be saved at {self._journal_folder}."
        click.echo(msg)

    def setup_new_journal(self):
        cli = f"{os.path.dirname(__file__)}/cli.py"
        command = (
            f"DISPLAY=:1 {PYTHON_PATH} {cli} run {self._journal_folder} {self._log_maker()}"
        )
        job = self._cron.new(command=command, comment=f"work-journal-{self._journal_name}")
        job.setall(self._schedule)
        self._cron.write()
        self._send_finishing_msg()


def _open_text_editor(filename):
    try:
        subprocess.run([EDITOR_CMD, filename])
    except Exception as e:
        click.echo(f"An error occurred: {e}")


def create_markdown_file(journal_folder, allow_overwrite):
    today = datetime.today()

    year_and_month = today.strftime("%Y-%m")
    monthly_folder = os.path.join(journal_folder, year_and_month)
    if not os.path.exists(monthly_folder):
        os.makedirs(monthly_folder)

    today_date = today.strftime("%Y-%m-%d")
    new_journal_path = os.path.join(monthly_folder, f"{today_date}-journal.md")
    if os.path.exists(new_journal_path) and not allow_overwrite:
        click.echo("Journal for today exists, and allowing overwrite is set to False.")
        raise click.exceptions.Exit(code=1)

    # create journal
    with open(new_journal_path, "w") as f:
        heading = f"# {today.strftime('%B %d, %Y')} Working Journal\n\n"
        f.write(heading)

    _open_text_editor(new_journal_path)
