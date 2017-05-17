# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.apps import apps
from .settings import get_config


class HorizontalRouter(object):
    def _get_horizontal_group(self, model):
        return getattr(model._meta, 'horizontal_group', None)

    def db_for_read(self, model, **hints):
        horizontal_group = self._get_horizontal_group(model)
        if not horizontal_group:
            return

    def db_for_write(self, model, **hints):
        horizontal_group = self._get_horizontal_group(model)
        if not horizontal_group:
            return

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

        if db in get_config()['GROUPS'][horizontal_group]['MIGRATE']:
            return True
