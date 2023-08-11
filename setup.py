from setuptools import setup, find_packages

setup(
    name='work-journal-cli',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'click',
        'python-crontab',
    ],
    entry_points={
        'console_scripts': [
            'wjournal = cli:main',
        ],
    },
)
