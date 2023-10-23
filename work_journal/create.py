from datetime import datetime
import os
import click
import subprocess

from work_journal.config import EDITOR_CMD

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
