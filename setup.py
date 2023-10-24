from setuptools import setup, find_packages
with open("README.md") as f:
    long_description = f.read()

setup(
    name='work-journal-cli',
    version='2.0.0',
    packages=find_packages(),
    package_data={"work_journal": ["*.ini"]},
    install_requires=["click", "python-crontab", "cron-descriptor", "croniter"],
    description="A CLI tool to schedule for writing a work journal with cron.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Heng-Tse Chou",
    author_email="hengtse.me@gmail.com",
    url="https://github.com/hank-chouu/work-journal-cli",
    license="MIT",
    keywords="Cron CLI",
    entry_points={
        "console_scripts": [
            "work-journal = work_journal.cli:main",
        ],
    },
)
