# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.apps import apps


class HorizontalRouter(object):
    def _get_horizontal_group(self, model):
        return getattr(model._meta, 'horizontal_group', None)

    def _get_database_for_instance(self, instance):
        return instance._state.db or instance._()

    def db_for_read(self, model, **hints):
        horizontal_group = self._get_horizontal_group(model)
        if not horizontal_group:
            return

    def db_for_write(self, model, **hints):
        horizontal_group = self._get_horizontal_group(model)
        if not horizontal_group:
            return

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
