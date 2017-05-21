"""Django settings for tests."""

SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'tests',
]


DATABASES = {
    'default': {
        'NAME': 'default',
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST': {
            'NAME': 'file:memorydb_default?mode=memory&cache=shared',
        },
    },
    'a1-primary': {
        'NAME': 'a1-primary',
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST': {
            'NAME': 'file:memorydb_a1-primary?mode=memory&cache=shared',
        },
    },
    'a1-replica-1': {
        'NAME': 'a1-replica-1',
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST': {
            'MIRROR': 'a1-primary',
        },
    },
    'a1-replica-2': {
        'NAME': 'a1-replica-2',
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST': {
            'MIRROR': 'a1-primary',
        },
    },
    'a2-primary': {
        'NAME': 'a2-primary',
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST': {
            'NAME': 'file:memorydb_a2-primary?mode=memory&cache=shared',
        },
    },
    'a2-replica': {
        'NAME': 'a2-replica',
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST': {
            'MIRROR': 'a2-primary',
        },
    },
    'a3': {
        'NAME': 'a3',
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST': {
            'NAME': 'file:memorydb_a3?mode=memory&cache=shared',
        },
    },
    'b1-primary': {
        'NAME': 'b1-primary',
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST': {
            'NAME': 'file:memorydb_b1-primary?mode=memory&cache=shared',
        },
    },
    'b1-replica-1': {
        'NAME': 'b1-replica-1',
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST': {
            'MIRROR': 'b1-primary',
        },
    },
    'b1-replica-2': {
        'NAME': 'b1-replica-2',
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST': {
            'MIRROR': 'b1-primary',
        },
    },
    'b2-primary': {
        'NAME': 'b2-primary',
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST': {
            'NAME': 'file:memorydb_b2-primary?mode=memory&cache=shared',
        },
    },
    'b2-replica': {
        'NAME': 'b2-replica',
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST': {
            'MIRROR': 'b2-primary',
        },
    },
    'b3': {
        'NAME': 'b3',
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST': {
            'NAME': 'file:memorydb_b3?mode=memory&cache=shared',
        },
    },
}
DATABASE_ROUTERS = (
    'horizon.routers.HorizontalRouter',
)


HORIZONTAL_CONFIG = {
    'GROUPS': {
        'a': {
            'DATABASES': {
                1: {
                    'write': 'a1-primary',
                    'read': ['a1-replica-1', 'a1-replica-2'],
                },
                2: {
                    'write': 'a2-primary',
                    'read': ['a2-replica'],
                },
                3: {
                    'write': 'a3',
                },
            },
        },
        'b': {
            'DATABASES': {
                1: {
                    'write': 'b1-primary',
                    'read': ['b1-replica-1', 'b1-replica-2'],
                },
                2: {
                    'write': 'b2-primary',
                    'read': ['b2-replica'],
                },
                3: {
                    'write': 'b3',
                },
            },
            'PICKABLES': [2, 3],
        },
    },
    'METADATA_MODEL': 'tests.HorizontalMetadata',
}
