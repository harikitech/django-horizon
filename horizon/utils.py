# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import logging
import random

import django
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured

from .settings import get_config


logger = logging.getLogger(__name__)


def get_metadata_model():
    try:
        if (1, 11) > django.VERSION:
            return apps.get_model(get_config()['METADATA_MODEL'])
        else:
            return apps.get_model(get_config()['METADATA_MODEL'], require_ready=False)

    except ValueError:
        raise ImproperlyConfigured("METADATA_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "METADATA_MODEL refers to model '%s' that has not been installed"
            % get_config()['METADATA_MODEL']
        )


def get_group_from_model(model):
    horizontal_group = getattr(model._meta, 'horizontal_group', None)
    if horizontal_group:
        return horizontal_group

    for parent_class in model._meta.get_parent_list():
        horizontal_group = getattr(parent_class._meta, 'horizontal_group', None)
        if horizontal_group:
            return horizontal_group


def get_key_field_name_from_model(model):
    horizontal_key = getattr(model._meta, 'horizontal_key', None)
    if horizontal_key:
        return horizontal_key

    for parent_class in model._meta.get_parent_list():
        horizontal_key = getattr(parent_class._meta, 'horizontal_key', None)
        if horizontal_key:
            return horizontal_key


def get_config_from_group(horizontal_group):
    if horizontal_group not in get_config()['GROUPS']:
        return {}
    return get_config()['GROUPS'][horizontal_group]


def get_config_from_model(model):
    horizontal_group = get_group_from_model(model)
    if not horizontal_group:
        return {}
    return get_config_from_group(horizontal_group)


def get_db_for_read_from_model_index(model, index):
    config = get_config_from_model(model)
    return random.choice(config['DATABASES'][index]['read'])


def get_db_for_write_from_model_index(model, index):
    config = get_config_from_model(model)
    return config['DATABASES'][index]['write']


def get_or_create_index(model, horizontal_key):
    metadata_model = get_metadata_model()
    horizontal_group = get_group_from_model(model)
    metadata, created = metadata_model.objects.get_or_create(
        group=get_group_from_model(model),
        key=horizontal_key,
        defaults={
            'index': random.choice(get_config_from_group(horizontal_group)['PICKABLES'])
        },
    )
    if created:
        logger.info("Assign new index to '%s': %s", horizontal_group, metadata.index)
    return metadata.index
