import click
import os
import subprocess
from datetime import datetime
from crontab import CronTab
from cron_descriptor import get_description

@click.group()
def main():
    pass

@main.command()
@click.argument("time", type=str)
@click.option("--dir", "-d", default=".", help="Directory path to create markdown files")
def setup(time, dir):
    """
    Setup a cron job to create a daily markdown journal.
    
    TIME is the cron schedule format (e.g., '0 9 * * *' for 9 AM).
    """
    setup_cron_job(time, dir)
    expression = get_description(time)
    click.echo(f"Cron job set to create daily journal at {expression} in directory {dir}")

@main.command()
def remove():
    """Remove the previously created cron job"""
    remove_cron_job()
    click.echo("Cron job removed")

def create_markdown_file(dir):
    now = datetime.now()
    filename = os.path.join(dir, now.strftime("%Y-%m-%d") + "_journal.md")
    heading = "# " + now.strftime("%B %d, %Y") + " Working Journal\n"
    
    with open(filename, "w") as f:
        f.write(heading)
    
    open_text_editor(filename)

def setup_cron_job(schedule, output_dir):
    cron = CronTab(user=os.getlogin())
    command = f'python "{os.path.abspath(__file__)}" work_journal --output-dir "{output_dir}"'
    job = cron.new(command=command)
    job.setall(schedule)
    cron.write()

def remove_cron_job():
    cron = CronTab(user=os.getlogin())
    for job in cron:
        if "work_journal" in job.command:
            cron.remove(job)
            cron.write()
            return

def open_text_editor(filename):
    try:
        # Replace 'editor_command' with the command to open your preferred text editor
        editor_command = "gedit"
        subprocess.run([editor_command, filename])
    except Exception as e:
        click.echo(f"Error opening text editor: {e}")

if __name__ == "__main__":
    main()
