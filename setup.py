from setuptools import setup, find_packages

setup(
    name='work-journal-tool',
    version='0.1',
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
