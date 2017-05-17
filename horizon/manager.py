# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.db.models.manager import BaseManager

from .query import HorizontalQuerySet


class HorizontalManager(BaseManager.from_queryset(HorizontalQuerySet)):
    pass
