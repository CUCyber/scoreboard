#!/usr/bin/env python3
from setuptools import setup, find_packages


setup(
    name='scoreboard',
    version='0.4.1',
    description='a scoreboard for verifying and scoring services in a red vs. blue competition',
    license='MIT',
    author='CU Cyber',
    author_email='cyber@clemson.edu',
    install_requires=['fooster-web', 'dnspython', 'python-ldap', 'mysqlclient', 'paramiko'],
    packages=find_packages(),
    package_data={'': ['html/*.*']},
    entry_points={'console_scripts': ['scoreboard = scoreboard.__main__:main']},
)
