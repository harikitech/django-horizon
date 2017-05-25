# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.db.models import Model
from django.db.models.query import QuerySet
from django.db.utils import ProgrammingError


class HorizontalQuerySet(QuerySet):
    def __init__(self, model=None, **kwargs):
        super(HorizontalQuerySet, self).__init__(model=model, **kwargs)
        self._horizontal_key = None

    @classmethod
    def _get_horizontal_key_from_lookup_value(cls, lookup_value):
        if not lookup_value:
            return
        if isinstance(lookup_value, Model):
            return lookup_value.pk
        return lookup_value

    def _set_horizontal_key_from_params(self, kwargs):
        if self._horizontal_key is not None:
            return

        key_field = self.model._meta.get_field(self.model._meta.horizontal_key)
        lookup_value = kwargs.get(key_field.attname, None) or kwargs.get(key_field.name, None)
        self._horizontal_key = self._get_horizontal_key_from_lookup_value(lookup_value)

    def _create_object_from_params(self, lookup, params):
        self._set_horizontal_key_from_params(lookup)
        return super(HorizontalQuerySet, self)._create_object_from_params(lookup, params)

    def _extract_model_params(self, defaults, **kwargs):
        self._set_horizontal_key_from_params(kwargs)
        return super(HorizontalQuerySet, self)._extract_model_params(defaults, **kwargs)

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
        if self._db:
            return self._db

        if self._horizontal_key is None:
            raise ProgrammingError("Missing horizontal key field's filter")

        self._add_hints(horizontal_key=self._horizontal_key)
        return super(HorizontalQuerySet, self).db
