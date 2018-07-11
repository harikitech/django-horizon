#!/usr/bin/env python

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'tests.test_settings')


def runmigrations():
    import django
    from django.core.management import call_command

    if hasattr(django, 'setup'):
        django.setup()

    call_command('makemigrations', 'tests')


if __name__ == "__main__":
    runmigrations()
