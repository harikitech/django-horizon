# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.utils.lru_cache import lru_cache


CONFIG_DEFAULTS = {
    'GROUPS': {},
    'METADATA_STORE': None,
}


@lru_cache()
def get_config():
    USER_CONFIG = getattr(settings, 'HORIZONTAL_CONFIG', {})

    CONFIG = CONFIG_DEFAULTS.copy()
    CONFIG.update(USER_CONFIG)

    for name, horizontal_group in CONFIG['GROUPS'].items():
        horizontal_group['MIGRATE'] = set()
        for key, member in horizontal_group['DATABASES'].items():
            horizontal_group['MIGRATE'].add(member['write'])
            horizontal_group['MIGRATE'].update(member.get('read', []))

    return CONFIG
