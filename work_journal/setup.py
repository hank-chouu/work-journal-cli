import sys
import getpass
from crontab import CronTab, CronSlices
import os
import click
from cron_descriptor import get_description


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
        return f">{cwd}/cronlog.log 2>&1"

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
        command = f'DISPLAY=:1 {compiler_path} {cli} run --dir "{self._journal_folder}"{self._log_maker()}"'
        job = self._cron.new(command=command, comment=self._job_comment)
        job.setall(self._cron_expression)
        self._cron.write()
        self._send_finishing_msg()
