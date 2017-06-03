# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import logging

from django.apps import apps
from django.db.utils import IntegrityError

from .utils import (
    get_config_from_model,
    get_db_for_read_from_model_index,
    get_db_for_write_from_model_index,
    get_group_from_model,
    get_or_create_index,
)


logger = logging.getLogger(__name__)


class HorizontalRouter(object):
    def _get_horizontal_index(self, model, hints):
        horizontal_group = get_group_from_model(model)
        if not horizontal_group:
            return

        horizontal_key = hints.get('horizontal_key', None)
        if not horizontal_key:
            instance = hints.get('instance', None)
            if instance and isinstance(instance, model):
                return instance._horizontal_database_index
            return None

        if not horizontal_key:
            raise IntegrityError("Missing 'horizontal_key'")
        return get_or_create_index(model, horizontal_key)

    def db_for_read(self, model, **hints):
        horizontal_index = self._get_horizontal_index(model, hints)
        if horizontal_index is None:
            return
        database = get_db_for_read_from_model_index(model, horizontal_index)
        logger.debug("'%s' read from '%s'", model, database)
        return database

    def db_for_write(self, model, **hints):
        horizontal_index = self._get_horizontal_index(model, hints)
        if horizontal_index is None:
            return
        database = get_db_for_write_from_model_index(model, horizontal_index)
        logger.debug("'%s' read from '%s'", model, database)
        return database

    def allow_relation(self, obj1, obj2, **hints):
        horizontal_group_1 = get_group_from_model(obj1._meta.model)
        horizontal_group_2 = get_group_from_model(obj2._meta.model)
        if not horizontal_group_1 or not horizontal_group_2:
            return

        if horizontal_group_1 != horizontal_group_2:
            return

        if obj1._state.db == obj2._state.db:
            return True

        if obj1._horizontal_database_index == obj2._horizontal_database_index:
            return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if 'model' in hints:
            model = hints['model']
        elif model_name:
            model = apps.get_model(app_label, model_name)
        else:
            return

        if db in get_config_from_model(model).get('DATABASE_SET', []):
            return True
