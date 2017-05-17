# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase

from horizon.routers import HorizontalRouter
from .models import HorizonA, HorizonB


user_modle = get_user_model()


class HorizontalModelTestCase(TestCase):
    def setUp(self):
        self.router = HorizontalRouter()

    def test_get_horizontal_group(self):
        self.assertEqual(
            'a',
            self.router._get_horizontal_group(HorizonA),
        )
        self.assertEqual(
            'b',
            self.router._get_horizontal_group(HorizonB),
        )

    def test_get_horizontal_group_for_default(self):
        self.assertEqual(
            None,
            self.router._get_horizontal_group(user_modle),
        )

    def test_allow_migrate(self):
        for expected_database in ('a1-primary', 'a1-replica-1', 'a1-replica-2', 'a2-primary',
                                  'a2-replica', 'a3'):
            self.assertEqual(
                True,
                self.router.allow_migrate(expected_database, 'tests', 'HorizonA', model=HorizonA),
            )

        for expected_database in ('b1-primary', 'b1-replica-1', 'b1-replica-2', 'b2-primary',
                                  'b2-replica', 'b3'):
            self.assertEqual(
                True,
                self.router.allow_migrate(expected_database, 'tests', 'HorizonB', model=HorizonB),
            )

    def test_not_allow_migrate(self):
        self.assertIsNone(
            self.router.allow_migrate('default', 'tests', 'HorizonA', model=HorizonA),
        )
        self.assertIsNone(
            self.router.allow_migrate('default', 'tests', 'HorizonB', model=HorizonB),
        )
        self.assertIsNone(
            self.router.allow_migrate(
                'default', user_modle._meta.app_label, 'User', model=user_modle),
        )
        self.assertIsNone(
            self.router.allow_migrate(
                'a1-primary', user_modle._meta.app_label, 'User', model=user_modle),
        )

    def test_allow_migrate_without_hints(self):
        for expected_database in ('a1-primary', 'a1-replica-1', 'a1-replica-2', 'a2-primary',
                                  'a2-replica', 'a3'):
            self.assertEqual(
                True,
                self.router.allow_migrate(expected_database, 'tests', 'HorizonA'),
            )

        for expected_database in ('b1-primary', 'b1-replica-1', 'b1-replica-2', 'b2-primary',
                                  'b2-replica', 'b3'):
            self.assertEqual(
                True,
                self.router.allow_migrate(expected_database, 'tests', 'HorizonB'),
            )

    def test_not_allow_migrate_without_hints(self):
        self.assertIsNone(
            self.router.allow_migrate('default', 'tests', 'HorizonA'),
        )
        self.assertIsNone(
            self.router.allow_migrate('default', 'tests', 'HorizonB'),
        )
        self.assertIsNone(
            self.router.allow_migrate('default', user_modle._meta.app_label, 'User'),
        )
        self.assertIsNone(
            self.router.allow_migrate('b1-primary', user_modle._meta.app_label, 'User'),
        )
