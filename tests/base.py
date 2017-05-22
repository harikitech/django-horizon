# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.test import TransactionTestCase


class HorizontalBaseTestCase(TransactionTestCase):
    """Base test case for horizonta."""

    multi_db = True
