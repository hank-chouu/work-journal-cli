from setuptools import setup, find_packages

setup(
    name='work-journal-cli',
    version='v1.1',
    packages=find_packages(),
    install_requires=[
        'click',
        'python-crontab',
    ],
    entry_points={
        'console_scripts': [
            'work-journal = cli:main',
        ],
    },
)
