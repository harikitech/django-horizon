# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import uuid

from django.core import checks
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.migrations import state
from django.db.migrations.operations import models as migrate_models
from django.db.models import options
from django.utils.functional import cached_property

from .manager import HorizontalManager
from .utils import (
    get_config_from_model,
    get_group_from_model,
    get_key_field_name_from_model,
    get_or_create_index,
)


_HORIZON_OPTIONS = (
    'horizontal_group',
    'horizontal_key',
)


# Monkey patch to add horizontal options in to models and database migrations
options.DEFAULT_NAMES += _HORIZON_OPTIONS
state.DEFAULT_NAMES += _HORIZON_OPTIONS
migrate_models.AlterModelOptions.ALTER_OPTION_KEYS += list(_HORIZON_OPTIONS)


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

        errors.extend(cls._check_horizontal_group(**kwargs))
        errors.extend(cls._check_horizontal_key(**kwargs))
        return errors

    @classmethod
    def _check_horizontal_meta(cls, **kwargs):
        errors = []
        if not get_group_from_model(cls):
            errors.append(
                checks.Error(
                    "'horizontal_group' not configured.",
                    obj=cls,
                    id='horizon.E001',
                )
            )
        if not get_key_field_name_from_model(cls):
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
        if get_config_from_model(cls):
            return []
        return [
            checks.Error(
                "'horizontal_group' '%s' does not defined in settings."
                % get_group_from_model(cls),
                obj=cls,
                id='horizon.E002',
            ),
        ]

    @classmethod
    def _check_horizontal_key(cls, **kwargs):
        try:
            cls._meta.get_field(get_key_field_name_from_model(cls))
            return []
        except FieldDoesNotExist:
            return [
                checks.Error(
                    "'horizontal_key' refers to the non-existent field '%s'."
                    % get_key_field_name_from_model(cls),
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
                    unique_fields_for_exclude.append(
                        (model_class, (name, )),
                    )
                    unique_fields_with_horizontal_key.append(
                        (model_class, (get_key_field_name_from_model(self), name)),
                    )
        unique_checks, date_checks = super(AbstractHorizontalModel, self) \
            ._get_unique_checks(exclude=exclude)
        for unique_check in unique_checks:
            if unique_check in unique_fields_for_exclude:
                continue
            unique_fields_with_horizontal_key.append(unique_check)
        return unique_fields_with_horizontal_key, date_checks

    @cached_property
    def _horizontal_key(self):
        key_field = self._meta.get_field(get_key_field_name_from_model(self))
        return getattr(self, key_field.attname)

    @cached_property
    def _horizontal_database_index(self):
        return get_or_create_index(self, self._horizontal_key)

    class Meta(object):
        abstract = True
        horizontal_group = None
        horizontal_key = None
