# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.db.models.query import QuerySet
# from django.db import IntegrityError


class HorizontalQuerySet(QuerySet):
    def __init__(self, **kwargs):
        super(HorizontalQuerySet, self).__init__(**kwargs)
        self._horizontal_index = None

    def _filter_or_exclude(self, negate, *args, **kwargs):
        return super(HorizontalQuerySet, self)._filter_or_exclude(negate, *args, **kwargs)

    @property
    def db(self):
        # if not self._horizontal_index:
        #     raise IntegrityError("Missing horizontal key field's filter")
        self._add_hints(horizontal_index=self._horizontal_index)
        return super(HorizontalQuerySet, self).db
