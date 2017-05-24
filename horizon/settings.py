# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.utils.lru_cache import lru_cache


CONFIG_DEFAULTS = {
    'GROUPS': {},
    'METADATA_MODEL': None,
}


@lru_cache()
def get_config():
    USER_CONFIG = getattr(settings, 'HORIZONTAL_CONFIG', {})

    CONFIG = CONFIG_DEFAULTS.copy()
    CONFIG.update(USER_CONFIG)

    for name, horizontal_group in CONFIG['GROUPS'].items():
        horizontal_group['DATABASE_SET'] = set()
        for key, member in horizontal_group['DATABASES'].items():
            horizontal_group['DATABASE_SET'].add(member['write'])
            horizontal_group['DATABASE_SET'].update(member.get('read', []))

            if 'read' not in member:
                member['read'] = [member['write']]

        if 'PICKABLES' not in horizontal_group:
            horizontal_group['PICKABLES'] = [int(i) for i in horizontal_group['DATABASES'].keys()]

    return CONFIG
