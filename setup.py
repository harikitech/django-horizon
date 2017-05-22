#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

import horizon

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Django>=1.8',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='django-horizon',
    version=horizon.__version__,
    description=(
        "Simple database sharding (horizontal partitioning) library for Django applications."
    ),
    long_description=readme + '\n\n' + history,
    author=horizon.__author__,
    author_email=horizon.__email__,
    url='https://github.com/uncovertruth/django-horizon',
    packages=find_packages(exclude=('tests', 'docs')),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='django-horizon, django, sharding, horizontal partitioning, database',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',  # Allow failure because SQLite is too old
        'Programming Language :: Python :: 2.7',  # Allow failure because SQLite is too old
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='runtests.runtests',
    tests_require=test_requirements
)
