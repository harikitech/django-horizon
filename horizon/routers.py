# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.apps import apps
from django.db.utils import IntegrityError


class HorizontalRouter(object):
    def _get_horizontal_group(self, model):
        return getattr(model._meta, 'horizontal_group', None)

    def _get_horizontal_index(self, model, hints):
        horizontal_group = self._get_horizontal_group(model)
        if not horizontal_group:
            return

        horizontal_key = hints.get('horizontal_key', None)
        if not horizontal_key:
            instance = hints.get('instance', None)
            if instance:
                # From foreign field
                horizontal_key = instance.pk

        if not horizontal_key:
            raise IntegrityError("Missing 'horizontal_key'")
        return model._get_or_create_horizontal_index(horizontal_key)

    def db_for_read(self, model, **hints):
        horizontal_index = self._get_horizontal_index(model, hints)
        if not horizontal_index:
            return
        return model._get_horizontal_db_for_read(horizontal_index)

    def db_for_write(self, model, **hints):
        horizontal_index = self._get_horizontal_index(model, hints)
        if not horizontal_index:
            return
        return model._get_horizontal_db_for_write(horizontal_index)

    def allow_relation(self, obj1, obj2, **hints):
        horizontal_group_1 = self._get_horizontal_group(obj1._meta.model)
        horizontal_group_2 = self._get_horizontal_group(obj2._meta.model)
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

        horizontal_group = self._get_horizontal_group(model)
        if not horizontal_group:
            return

        if db in model._get_horizontal_config()['DATABASE_SET']:
            return True
