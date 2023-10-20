from datetime import datetime
import os
import click
import subprocess


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
        editor_command = "xdg-open"
        subprocess.run([editor_command, filename])
    except Exception as e:
        click.echo(f"An error occurred: {e}")
