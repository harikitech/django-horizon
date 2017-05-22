# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import django
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured

from .settings import get_config


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
