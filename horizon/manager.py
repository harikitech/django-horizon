# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.db.models.manager import Manager

from .query import HorizontalQuerySet


class HorizontalManager(Manager):
    use_for_related_fields = True
    use_in_migrations = True

    def __init__(self):
        super(HorizontalManager, self).__init__()
        self.name = 'horizontal'

    def get_queryset(self):
        """For old django"""
        return HorizontalQuerySet(model=self.model, using=self._db, hints=self._hints)
