# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.db.models.manager import Manager

from .query import HorizontalQuerySet


class HorizontalManager(Manager.from_queryset(HorizontalQuerySet)):
    use_for_related_fields = True
    use_in_migrations = True
    silence_use_for_related_fields_deprecation = True  # For Django<1.10

    def __init__(self):
        super(HorizontalManager, self).__init__()
