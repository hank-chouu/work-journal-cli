import sys
import getpass
from crontab import CronTab
import os
import click
from cron_descriptor import get_description
from datetime import datetime

from work_journal.config import PYTHON_PATH


class JournalSetter:
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

    def _log_maker(selfs):
        home_dir = os.path.expanduser("~")
        date = datetime.today().strftime("%Y%m%d")
        os.makedirs(os.path.join(home_dir, ".work_journal"), exist_ok=True)
        return f">>{home_dir}/.work_journal/{date}.log 2>&1"

    def _send_finishing_msg(self):
        expression = get_description(self._schedule)
        msg = f"Journal is scheduled at {expression} with name {self._journal_name}, and will be saved at {self._journal_folder}."
        click.echo(msg)

    def setup_new_journal(self):
        cli = f"{os.path.dirname(__file__)}/cli.py"
        command = f"DISPLAY=:1 {PYTHON_PATH} {cli} run {self._journal_folder} {self._log_maker()}"
        job = self._cron.new(
            command=command, comment=f"work_journal_{self._journal_name}"
        )
        job.setall(self._schedule)
        self._cron.write()
        self._send_finishing_msg()
