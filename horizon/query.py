# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.db.models import Model
from django.db.models.query import QuerySet
from django.db.utils import IntegrityError


class HorizontalQuerySet(QuerySet):
    def __init__(self, **kwargs):
        super(HorizontalQuerySet, self).__init__(**kwargs)
        self._horizontal_key = None

    def _set_horizontal_key_from_params(self, kwargs):
        key_field = self.model._meta.get_field(self.model._meta.horizontal_key)
        lookup_value = kwargs.get(key_field.attname, None) or kwargs.get(key_field.name, None)
        if lookup_value:
            if isinstance(lookup_value, Model):
                self._horizontal_key = lookup_value.pk
            else:
                self._horizontal_key = lookup_value

    def _filter_or_exclude(self, negate, *args, **kwargs):
        self._set_horizontal_key_from_params(kwargs)
        return super(HorizontalQuerySet, self)._filter_or_exclude(negate, *args, **kwargs)

    def create(self, **kwargs):
        self._set_horizontal_key_from_params(kwargs)
        return super(HorizontalQuerySet, self).create(**kwargs)

    def _clone(self, **kwargs):
        clone = super(HorizontalQuerySet, self)._clone(**kwargs)
        clone._horizontal_key = self._horizontal_key
        return clone

    @property
    def db(self):
        if self._horizontal_key is None:
            raise IntegrityError("Missing horizontal key field's filter")
        self._add_hints(horizontal_key=self._horizontal_key)
        return super(HorizontalQuerySet, self).db
