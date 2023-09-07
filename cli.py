import click
import os
import sys
import getpass
import subprocess
from datetime import datetime
from croniter import croniter
from crontab import CronTab
from cron_descriptor import get_description

###################################################################

# command group

###################################################################

@click.group()
def main():
    pass

###################################################################

# work-journal setup

###################################################################

@main.command()
@click.argument("time", type=str)
@click.option("--dir", "-d", "journal_folder", 
              default=".", help="Directory for creating journals, current working directory is set as default.")
@click.option("--job-comment", "-c", 
              default="cron_journal", help="Labelling the job with job comment, cron_journal is set as default (duplicated comments are not allowed).")
def setup(time, journal_folder, job_comment):
    """
    Setup a cron job to create a markdown journal on schedule.
    
    TIME is the cron schedule format (e.g., '0 9 * * *' for 9 AM).
    """
    cwd = os.path.dirname(os.path.abspath(__file__))
    if journal_folder == '.':
        journal_folder = cwd
    setup_cron_job(time, journal_folder, job_comment)
    expression = get_description(time)
    click.echo(f"Daily-journaling is scheduled at {expression} in directory {journal_folder} with job comment {job_comment}.")

def setup_cron_job(schedule, journal_folder, job_comment):

    cron = CronTab(user=getpass.getuser())
    venv_path = sys.prefix
    cwd = os.path.dirname(os.path.abspath(__file__))

    # check unique job comment
        
    if job_comment_used(job_comment):
        click.echo(f'Job comment {job_comment} is already used. Exiting ...')
        raise click.exceptions.Exit(code=1)

    # check directory exist

    if not os.path.exists(journal_folder):
        try:
            click.echo(f'Directory not found. A new directory {journal_folder} has been created.')
            os.makedirs(journal_folder)
        except PermissionError:
            click.echo('You don\'t have permission to the directory. Exiting...')
            raise click.exceptions.Exit(code=1)

    command = f'DISPLAY=:1 {venv_path}/bin/python {os.path.abspath(__file__)} run --dir "{journal_folder}">> {cwd}/cron.log 2>&1'
    job = cron.new(command=command, comment=job_comment)
    job.setall(schedule)
    cron.write()

def job_comment_used(job_comment):

    cron = CronTab(user=getpass.getuser())
    
    job_comment_is_used = False
    for job in cron:
        if job_comment == job.comment:
            job_comment_is_used = True

    return job_comment_is_used

###################################################################

# work-journal run

###################################################################

@main.command()
@click.option("--dir", "-d", "journal_folder", 
               default='.', help="Directory for creating journals, current working directory is set as default.")
@click.option("--overwrite", "--o", "allow_overwrite", 
              is_flag=True, default=False,help="Allow overwriting the existing journal, set to False as default.")
def run(journal_folder, allow_overwrite):
    """Initiate a journal immediately."""

    create_markdown_file(journal_folder, allow_overwrite)

def create_markdown_file(journal_folder, allow_overwrite):

    now = datetime.now()
    current_year_and_month = now.strftime('%Y-%m')
    current_date = now.strftime('%Y-%m-%d')

    # make monthly folder

    monthly_folder_path = os.path.join(journal_folder, current_year_and_month)
    if not os.path.exists(monthly_folder_path):
        os.makedirs(monthly_folder_path)

    # check if journal for today already existed

    journal_to_be_created = os.path.join(monthly_folder_path, current_date + "-journal.md")
    if os.path.exists(journal_to_be_created) and not allow_overwrite:
        click.echo('Journal for today is already created. Exiting...')
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
        click.echo(f"Error opening text editor: {e}")

###################################################################

# work-journal remove

###################################################################

@main.command()
@click.option("--job-comment", "-c", 
    default='cron_journal',help="Specify the job with job comment, cron_journal is set as default.")
def remove(job_comment):
    """Remove the previously created work-journal cron job"""
    remove_cron_journal(job_comment)

def remove_cron_journal(job_comment):

    cron = CronTab(user=getpass.getuser())

    # check if job can be found

    no_job_found = True
    for job in cron:
        if job_comment in job.comment:
            no_job_found = False

    if no_job_found:
        click.echo(f'No cron job found with job comment {job_comment}. Exiting...')
        raise click.exceptions.Exit(code=1)

    # reomve the job with given job comment   
    
    for job in cron:
        if job_comment == job.comment:
            cron.remove(job)
            cron.write()
            click.echo(f"Cron job {job_comment} removed.")

###################################################################

# work-journal next-run

###################################################################

@main.command()
@click.option('--job-comment', '-c', 
              default='cron_journal', help='Specify the job with job comment, cron_journal is set as default.')
def next_run(job_comment):
    """Show when the next journal will be created."""

    cron = CronTab(user=getpass.getuser())
    no_job_found = True

    for job in cron:
        if job_comment == job.comment:
            no_job_found = False
            next_run_time = get_next_run_time(str(job.slices))
            click.echo(f'Next run time for job {job_comment} is {next_run_time}.')

    if no_job_found:
        click.echo(f'No job found with comment {job_comment}.')
            

def get_next_run_time(cron_expression: str):

    if not isinstance(cron_expression, str):
        raise TypeError('Pass the cron expression as a string.')

    now = datetime.now()

    cron = croniter(cron_expression, now)
    next_run_time = cron.get_next(datetime)

    return next_run_time

###################################################################

# execute

###################################################################        

if __name__ == "__main__":
    main()    
