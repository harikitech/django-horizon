#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'tests.test_settings')


def runtests():
    import django
    from django.conf import settings
    from django.test.utils import get_runner

    if hasattr(django, 'setup'):
        django.setup()

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    failures = test_runner.run_tests(['tests'])
    sys.exit(bool(failures))


if __name__ == "__main__":
    runtests()
