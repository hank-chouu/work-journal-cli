# Work Journal CLI Tool

Some people consider it's a good practice to write work journals on a daily basis, to remind what you have achieved every day. In this CLI tool, we utitlize the Linux built-in tool crontab and set a schedule, to create a work journal in markdown format automatically. 

The idea is to create a text file and pop up an editor window every day before leaving work, make it effortless to maintain the habit.

Linux/UNIX are theoretically all supported if you have these programs:

1. which
2. crontab
3. python/python3

These programs should be installed for the user and can be invoked through command line. Otherwise, the tool may has unpredictable behaviors. 

## Install 

```
pip install work-journal-cli
```

## Usage 

```
Usage: work-journal [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  config  Show configurations.
  info    Show the details of the scheduled info.
  new     Create a cron job for scheduling a journal.
  remove  Remove the previously created work-journal cron job.
  run     Make a journal and start writing immediately.

```

To schedule a new journal, run

```
work-journal new
```

The terminal will prompt you to input the required fields.

```
$ work-journal new
Journal name [#]: test
Schedule: 0 18 * * 1,2,3,4,5
Folder path for saving journals [/home/user/work_journals]: 
Journal is scheduled at At 06:00 PM, only on Monday, Tuesday, Wednesday, Thursday, and Friday with name test, and will be saved at /home/user/work_journals.
```

You need to pass a [cron expression](https://crontab.guru/) for the schedule. In the example, the expression means it's scheduled to pop out the editor every workday at 6pm. You can specify the directory you want the journals to be saved. 

You can also assign the text editor you preferred, using the following line:

```
work-journal config --set-editor gedit
```

In the example, `gedit` is the command for calling the GNOME GUI text editor.