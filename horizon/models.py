# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import random
import uuid

from django.core import checks
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import options
from django.utils.functional import cached_property

from .manager import HorizontalManager
from .settings import get_config
from .utils import get_metadata_model


options.DEFAULT_NAMES += (
    'horizontal_group',
    'horizontal_key',
)


class AbstractHorizontalMetadata(models.Model):
    group = models.CharField(max_length=15)
    key = models.CharField(max_length=32)
    index = models.PositiveSmallIntegerField()

    class Meta(object):
        abstract = True
        unique_together = (
            ('group', 'key'),
        )


class AbstractHorizontalModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    objects = HorizontalManager()

    @classmethod
    def check(cls, **kwargs):
        errors = super(AbstractHorizontalModel, cls).check(**kwargs)
        clash_errors = cls._check_horizontal_meta(**kwargs)
        if clash_errors:
            errors.extend(clash_errors)
            return errors

        errors.extend(cls._check_horizontal_key(**kwargs))
        return errors

    @classmethod
    def _check_horizontal_meta(cls, **kwargs):
        errors = []
        if not cls._get_horizontal_group():
            errors.append(
                checks.Error(
                    "'horizontal_group' not configured.",
                    obj=cls,
                    id='horizon.E001',
                )
            )
        if not cls._get_horizontal_key():
            errors.append(
                checks.Error(
                    "'horizontal_key' not configured.",
                    obj=cls,
                    id='horizon.E001',
                )
            )
        return errors

    @classmethod
    def _check_horizontal_group(cls, **kwargs):
        if cls._get_horizontal_group() in get_config()['GROUPS']:
            return []
        return [
            checks.Error(
                "'horizontal_group' '%s' does not defined in settings."
                % cls._get_horizontal_group(),
                obj=cls,
                id='horizon.E002',
            ),
        ]

    @classmethod
    def _check_horizontal_key(cls, **kwargs):
        try:
            cls._meta.get_field(cls._get_horizontal_key())
            return []
        except FieldDoesNotExist:
            return [
                checks.Error(
                    "'horizontal_key' refers to the non-existent field '%s'."
                    % cls._get_horizontal_key(),
                    obj=cls,
                    id='horizon.E003',
                ),
            ]

    def _get_unique_checks(self, exclude=None):
        if exclude is None:
            exclude = []

        fields_with_class = [(self.__class__, self._meta.local_fields)]
        for parent_class in self._meta.get_parent_list():
            fields_with_class.append((parent_class, parent_class._meta.local_fields))

        # Exclude default field's unique check and add field's unique check with horizontal key
        unique_fields_for_exclude = []
        unique_fields_with_horizontal_key = []
        for model_class, fields in fields_with_class:
            for f in fields:
                name = f.name
                if name in exclude:
                    continue
                if f.unique:
                    unique_fields_for_exclude.append(name)
                    unique_fields_with_horizontal_key.append(
                        (model_class, (self._get_horizontal_key(), name)),
                    )

        unique_checks, date_checks = super(AbstractHorizontalModel, self)._get_unique_checks(
            exclude=exclude + unique_fields_for_exclude,
        )
        return unique_checks + unique_fields_with_horizontal_key, date_checks

    @classmethod
    def _get_horizontal_config(cls):
        return get_config()['GROUPS'][cls._get_horizontal_group()]

    @classmethod
    def _get_horizontal_group(cls):
        horizontal_group = getattr(cls._meta, 'horizontal_group', None)
        if horizontal_group:
            return horizontal_group

        for parent_class in cls._meta.get_parent_list():
            horizontal_group = getattr(parent_class._meta, 'horizontal_group', None)
            if horizontal_group:
                return horizontal_group

    @classmethod
    def _get_horizontal_key(cls):
        horizontal_key = getattr(cls._meta, 'horizontal_key', None)
        if horizontal_key:
            return horizontal_key

        for parent_class in cls._meta.get_parent_list():
            horizontal_key = getattr(parent_class._meta, 'horizontal_key', None)
            if horizontal_key:
                return horizontal_key

    @classmethod
    def _get_horizontal_db_for_read(cls, index):
        return random.choice(cls._get_horizontal_config()['DATABASES'][index]['read'])

    @classmethod
    def _get_horizontal_db_for_write(cls, index):
        return cls._get_horizontal_config()['DATABASES'][index]['write']

    @classmethod
    def _get_or_create_horizontal_index(cls, horizontal_key):
        metadata_model = get_metadata_model()
        metadata, created = metadata_model.objects.get_or_create(
            group=cls._get_horizontal_group(),
            key=horizontal_key,
            defaults={
                'index': random.choice(cls._get_horizontal_config()['PICKABLES'])
            },
        )
        return metadata.index

    @cached_property
    def _horizontal_key(self):
        key_field = self._meta.get_field(self._get_horizontal_key())
        return getattr(self, key_field.attname)

    @cached_property
    def _horizontal_database_index(self):
        return self._get_or_create_horizontal_index(self._horizontal_key)

    class Meta(object):
        abstract = True
        horizontal_group = None
        horizontal_key = None
