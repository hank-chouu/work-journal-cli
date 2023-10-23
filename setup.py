from setuptools import setup, find_packages

setup(
    name='work-journal-cli',
    version='0.2.0',
    packages=find_packages(),
    package_data={"work_journal": ["*.ini"]},
    install_requires=[
        'click',
        'python-crontab',
        'cron-descriptor',
        'croniter'
    ],
    entry_points={
        'console_scripts': [
            'work-journal = work_journal.cli:main',
        ],
    },
)
