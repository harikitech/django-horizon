"""Django settings for tests."""

SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'tests',
]


DATABASES = {
    'default': {'ENGINE': 'django.db.backends.sqlite3'},
    'a1-primary': {'ENGINE': 'django.db.backends.sqlite3'},
    'a1-replica-1': {'ENGINE': 'django.db.backends.sqlite3'},
    'a1-replica-2': {'ENGINE': 'django.db.backends.sqlite3'},
    'a2-primary': {'ENGINE': 'django.db.backends.sqlite3'},
    'a2-replica': {'ENGINE': 'django.db.backends.sqlite3'},
    'a3': {'ENGINE': 'django.db.backends.sqlite3'},
    'b1-primary': {'ENGINE': 'django.db.backends.sqlite3'},
    'b1-replica-1': {'ENGINE': 'django.db.backends.sqlite3'},
    'b1-replica-2': {'ENGINE': 'django.db.backends.sqlite3'},
    'b2-primary': {'ENGINE': 'django.db.backends.sqlite3'},
    'b2-replica': {'ENGINE': 'django.db.backends.sqlite3'},
    'b3': {'ENGINE': 'django.db.backends.sqlite3'},
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
