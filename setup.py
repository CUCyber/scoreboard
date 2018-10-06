#!/usr/bin/env python3
from setuptools import setup, find_packages


setup(
    name='snakeboi',
    version='0.0.1',
    description='a scoreboard for verifying and scoring red vs. blue services',
    license='MIT',
    author='CU Cyber',
    author_email='cyber@clemson.edu',
    install_requires=['fooster-web', 'dnspython', 'python-ldap', 'mysqlclient', 'paramiko'],
    packages=find_packages(),
    package_data={'': ['html/*.*']},
    entry_points={'console_scripts': ['snakeboi = snakeboi.main:main']},
)