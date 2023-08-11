import click
import os
import sys
import getpass
import subprocess
from datetime import datetime
from crontab import CronTab
from cron_descriptor import get_description

@click.group()
def main():
    pass

@main.command()
@click.argument("time", type=str)
@click.option("--dir", default=".", help="Directory path to create markdown files")
def setup(time, dir):
    """
    Setup a cron job to create a daily markdown journal.
    
    TIME is the cron schedule format (e.g., '0 9 * * *' for 9 AM).
    """
    cwd = os.path.dirname(os.path.abspath(__file__))
    if dir == '.':
        dir = cwd
    setup_cron_job(time, dir)
    expression = get_description(time)
    click.echo(f"Cron job set to create daily journal at {expression} in directory {dir}")

@main.command()
def remove():
    """Remove the previously created cron job"""
    remove_cron_job()
    click.echo("Cron job removed")


@main.command()
@click.option("--dir", default='.')
def run(dir):

    create_markdown_file(dir)



def open_text_editor(filename):
    try:
        editor_command = "/usr/bin/gedit"
        subprocess.run([editor_command, filename])
    except Exception as e:
        click.echo(f"Error opening text editor: {e}")

def create_markdown_file(dir):
    now = datetime.now()
    filename = os.path.join(dir, now.strftime("%Y-%m-%d") + "-journal.md")
    heading = "# " + now.strftime("%B %d, %Y") + " Working Journal\n\n"
    
    with open(filename, "w") as f:
        f.write(heading)
    
    open_text_editor(filename)

def setup_cron_job(schedule, output_dir):
    cron = CronTab(user=getpass.getuser())
    venv_path = sys.prefix
    cwd = os.path.dirname(os.path.abspath(__file__))
    command = f'DISPLAY=:1 {venv_path}/bin/python {os.path.abspath(__file__)} run --dir "{output_dir}">> {cwd}/cron.log 2>&1'
    job = cron.new(command=command, comment='cron_journal')
    job.setall(schedule)
    cron.write()

def remove_cron_job():
    cron = CronTab(user=getpass.getuser())
    for job in cron:
        if 'cron_journal' in job.comment:
            cron.remove(job)
            cron.write()
            return
        

if __name__ == "__main__":
    main()
