==============
Django Horizon
==============

.. image:: https://travis-ci.org/uncovertruth/django-horizon.svg?branch=master
    :target: https://travis-ci.org/uncovertruth/django-horizon

.. image:: https://codecov.io/gh/uncovertruth/django-horizon/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/uncovertruth/django-horizon

.. image:: https://readthedocs.org/projects/django-horizon/badge/?version=latest
    :target: http://django-horizon.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://pyup.io/repos/github/uncovertruth/django-horizon/shield.svg
    :target: https://pyup.io/repos/github/uncovertruth/django-horizon/
    :alt: Updates

.. image:: https://pyup.io/repos/github/uncovertruth/django-horizon/python-3-shield.svg
    :target: https://pyup.io/repos/github/uncovertruth/django-horizon/
    :alt: Python 3

.. image:: https://img.shields.io/pypi/v/django-horizon.svg
    :target: https://pypi.python.org/pypi/django-horizon


Purpose
-------

Simple database sharding (horizontal partitioning) library for Django applications.


* Free software: MIT license
* Documentation: https://django-horizon.readthedocs.io.
* Inspired by django-sharding_. Thank you so much for your cool solution :)

.. _django-sharding: https://github.com/JBKahn/django-sharding


.. image:: https://raw.githubusercontent.com/uncovertruth/django-horizon/master/docs/_static/logo.jpg
    :alt: Logo


Features
--------

* Shard (horizontal partitioning) by some ForeignKey_ field like user account.

.. _ForeignKey: https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.ForeignKey

Installation
------------

To install Django Horizon, run this command in your terminal:

.. code-block:: console

    $ pip install django-horizon

This is the preferred method to install Django Horizon, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

Usage
-----

Setup
^^^^^

Add database router configuration in your ``settings.py``:

Horizontal database groups and a metadata store
"""""""""""""""""""""""""""""""""""""""""""""""

.. code-block:: python

    HORIZONTAL_CONFIG = {
        'GROUPS': {
            'group1': {  # The name of database horizontal partitioning group
                'DATABASES': {
                    1: {
                        'write': 'member1-primary',
                        'read': ['member1-replica-1', 'member1-replica-2'],  # Pick randomly by router
                    },
                    2: {
                        'write': 'member2-primary',
                        'read': ['member2-replica'],
                    },
                    3: {
                        'write': 'a3',  # Used by 'read' too
                    },
                },
                'PICKABLES': [2, 3],  # Group member keys to pick new database
            },
        },
        'METADATA_MODEL': 'app.HorizontalMetadata',  # Metadata store for horizontal partition key and there database
    }

Database router
"""""""""""""""

.. code-block:: python

    DATABASE_ROUTERS = (
        'horizon.routers.HorizontalRouter',
        ...
    )

Example models
^^^^^^^^^^^^^^

Horizontal partitioning by user

Metadata store
""""""""""""""

.. code-block:: python

    from horizon.models import AbstractHorizontalMetadata

    class HorizontalMetadata(AbstractHorizontalMetadata):
        pass

In the example, metadata store save followings.

- ``group``: Group name for horizontal partitioning.
- ``key``: Determines the distribution of the table's records amoung the horizontal partitioning group.
- ``index``: Choosed database index in horizontal partitioning groups.

Sharded model
"""""""""""""

.. code-block:: python

    from django.conf import settings

    from horizon.manager import HorizontalManager  # For Django<1.10
    from horizon.models import AbstractHorizontalModel


    class SomeLargeModel(AbstractHorizontalModel):
        user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
        ...

        objects = HorizontalManager()  # For Django<1.10

        class Meta(object):
            horizontal_group = 'group1'  # Group name
            horizontal_key = 'user'  # Field name to use group key

In many cases use UUIDField_ field for ``id``.
The ``AbstractHorizontalModel`` uses UUIDField_ as a them id field in default.

.. _UUIDField: https://docs.djangoproject.com/en/dev/ref/models/fields/#uuidfield

Using a model
"""""""""""""

.. code-block:: python

    from django.contrib.auth import get_user_model


    user_model = get_user_model()
    user = user_model.objects.get(pk=1)

    # Get by foreign instance
    SomeLargeModel.objects.filter(uses=user)

    # Get by foreign id
    SomeLargeModel.objects.filter(uses_id=user.id)

Model limitations
"""""""""""""""""

* ``django.db.utils.IntegrityError`` occured when not specify horizontal key field to filter

    .. code-block:: python

        SomeLargeModel.objects.all()

* Cannot lookup by foreign key field, cause there are other (like ``default``) database

    .. code-block:: python

        list(user.somelargemodel_set.all())
