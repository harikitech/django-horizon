==============
Django Horizon
==============


.. image:: https://img.shields.io/pypi/v/django_horizon.svg
        :target: https://pypi.python.org/pypi/django_horizon

.. image:: https://img.shields.io/travis/uncovertruth/django_horizon.svg
        :target: https://travis-ci.org/uncovertruth/django_horizon

.. image:: https://readthedocs.org/projects/django-horizon/badge/?version=latest
        :target: https://django-horizon.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/uncovertruth/django_horizon/shield.svg
     :target: https://pyup.io/repos/github/uncovertruth/django_horizon/
     :alt: Updates

Purpose
-------

Simple database sharding (horizontal partitioning) library for Django applications.


* Free software: MIT license
* Documentation: https://django-horizon.readthedocs.io.
* Inspired by django-sharding_. Thank you so much for your cool solution :)

.. _django-sharding: https://github.com/JBKahn/django-sharding

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

Add database router configuration in your `settings.py`:

Horizontal database groups and metadata store
"""""""""""""""""""""""""""""""""""""""""""""

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

In the example, metadata store keep user's pk and that index of horizontal database (`1`, `2` or `3`).

Shard database
""""""""""""""

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
            horizontal_key = 'user'  # Group key

In many cases use UUIDField_ field for `id`.
The `AbstractHorizontalModel` uses UUIDField_ as a them id field in default.

.. _UUIDField: https://docs.djangoproject.com/en/dev/ref/models/fields/#uuidfield

Using model
"""""""""""

.. code-block:: python

    from django.contrib.auth import get_user_model


    user_model = get_user_model()
    user = user_model.objects.get(pk=1)

    # Get by foreign instance
    SomeLargeModel.objects.filter(uses=user)

    # Get by foreign id
    SomeLargeModel.objects.filter(uses_id=user.id)

    # django.db.utils.IntegrityError occured when not specify horizontal key field to filter
    SomeLargeModel.objects.all()

Model limitation
""""""""""""""""

.. code-block:: python

    # django.db.utils.IntegrityError occured when not specify horizontal key field to filter
    SomeLargeModel.objects.all()

.. code-block:: python

    # Cannot lookup by foreign key field, cause there are other (like `default`) DBs
    list(self.user.somelargemodel_set.all())
