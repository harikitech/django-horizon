# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.core import checks
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import options
from django.utils.functional import cached_property

from .manager import HorizontalManager
from .settings import get_config
from .utils import get_metadata_model


OPTION_NAMES = (
    'horizontal_group',
    'horizontal_key',
)
options.DEFAULT_NAMES += OPTION_NAMES


class AbstractHorizontalMetadata(models.Model):
    group = models.CharField(max_length=8)
    key = models.CharField(max_length=120)
    index = models.PositiveSmallIntegerField()

    class Meta(object):
        abstract = True
        unique_together = (
            ('group', 'key'),
        )


class AbstractHorizontalModel(models.Model):
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
        for option_name in OPTION_NAMES:
            if not getattr(cls._meta, option_name, None):
                errors.append(
                    checks.Error(
                        "'%s' not configured." % option_name,
                        obj=cls,
                        id='horizon.E001',
                    )
                )
        return errors

    @classmethod
    def _check_horizontal_group(cls, **kwargs):
        if cls._meta.horizontal_group in get_config()['GROUPS']:
            return []
        return [
            checks.Error(
                "'horizontal_group' '%s' does not defined in settings."
                % cls._meta.horizontal_group,
                obj=cls,
                id='horizon.E002',
            ),
        ]

    @classmethod
    def _check_horizontal_key(cls, **kwargs):
        try:
            cls._meta.get_field(cls._meta.horizontal_key)
            return []
        except FieldDoesNotExist:
            return [
                checks.Error(
                    "'horizontal_key' refers to the non-existent field '%s'."
                    % cls._meta.horizontal_key,
                    obj=cls,
                    id='horizon.E003',
                ),
            ]

    @cached_property
    def _horizontal_key(self):
        key_field = self._meta.get_field(self._meta.horizontal_key)
        return getattr(self, key_field.attname)

    @cached_property
    def _horizontal_database_index(self):
        metadata_model = get_metadata_model()
        return metadata_model.objects.get(
            group=self._meta.horizontal_group,
            key=self._horizontal_key,
        ).index

    @classmethod
    def _get_horizontal_database_set(cls):
        return get_config()['GROUPS'][cls._meta.horizontal_group]['DATABASE_SET']

    class Meta(object):
        abstract = True
        horizontal_group = None
        horizontal_key = None
