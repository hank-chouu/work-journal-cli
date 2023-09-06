# Work Journal CLI Tool

Some people consider it's a good practice to make work journal on a daily basis, to remind what you have achieved every day. In this CLI tool, we utitlize the Linux built-in tool crontab and set a schedule, to create a work journal in markdown file automatically. 

The idea is to pop up the editor window every day before leaving work, make it effortless to maintain the habit.

This project is bulit on Linux Ubuntu, and is presumed to be only run on a Linux system, with text editor `gedit` installed.

## Setup 

1. Clone the repo.

```
git clone https://github.com/hank-chouu/work-journal-cli.git
cd work-journal-cli
```

2. Make sure your machine has `virtualenv` on it.

```
pip install virtualenv
```

3. Make a virtual enviroment, activate it, and install the dependencies. Note that once you successfully activated your virtual enviroment, your terminal should be marked with your env's name.

```
virtualenv venv
source ./venv/bin/activate
(venv) pip install -r requirements.txt
```

4. Run this command, and you should be good to go!

```
(venv) pip install --editable .
```


## Usage 

After finishing the above steps, you may run the following commands to setup your journaling schedule:

```
(venv) work-journal setup "0 18 * * 1,2,3,4,5" --dir /home/user/path/for/journals
```

In this `setup` command, you need to pass a [cron schedule expression](https://crontab.guru/) to initiate. In the example, the expression means it's scheduled to pop out the editor every workday at 6pm. You can specify the directory you wnat the journals to be saved. If `--dir` is not specified, it will be the directory where the source file (`cli.py`) is located on default.

If you want to modify or remove the previous created job, simply run

```
(venv) work-journal remove
```

and setup a new job if you want. 

To check for the existing job, you can run 

```
crontab -l
```

the cron job made with this tool will have a comment with `#cron_journal`.