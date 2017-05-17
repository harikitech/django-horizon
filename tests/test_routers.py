# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase

from horizon.routers import HorizontalRouter
from .models import HorizonA, HorizonB, HorizontalMetadata


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
        self.assertIsNone(self.router._get_horizontal_group(user_modle))

    def test_allow_migrate(self):
        for expected_database in ('a1-primary', 'a1-replica-1', 'a1-replica-2', 'a2-primary',
                                  'a2-replica', 'a3'):
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'HorizonA', model=HorizonA))

        for expected_database in ('b1-primary', 'b1-replica-1', 'b1-replica-2', 'b2-primary',
                                  'b2-replica', 'b3'):
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'HorizonB', model=HorizonB))

    def test_not_allow_migrate(self):
        self.assertIsNone(
            self.router.allow_migrate('default', 'tests', 'HorizonA', model=HorizonA),
            "Other database",
        )
        self.assertIsNone(
            self.router.allow_migrate('default', 'tests', 'HorizonB', model=HorizonB),
            "Other database",
        )
        self.assertIsNone(
            self.router.allow_migrate(
                'default', user_modle._meta.app_label, 'User', model=user_modle),
            "Not configured for horizontal database groups",
        )
        self.assertIsNone(
            self.router.allow_migrate(
                'a1-primary', user_modle._meta.app_label, 'User', model=user_modle),
            "Not configured for horizontal database groups",
        )

    def test_allow_migrate_without_hints(self):
        for expected_database in ('a1-primary', 'a1-replica-1', 'a1-replica-2', 'a2-primary',
                                  'a2-replica', 'a3'):
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'HorizonA'))

        for expected_database in ('b1-primary', 'b1-replica-1', 'b1-replica-2', 'b2-primary',
                                  'b2-replica', 'b3'):
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'HorizonB'))

    def test_not_allow_migrate_without_hints(self):
        self.assertIsNone(
            self.router.allow_migrate('default', 'tests', 'HorizonA'),
            "Other database",
        )
        self.assertIsNone(
            self.router.allow_migrate('default', 'tests', 'HorizonB'),
            "Other database",
        )
        self.assertIsNone(
            self.router.allow_migrate('default', user_modle._meta.app_label, 'User'),
            "Not configured for horizontal database groups",
        )
        self.assertIsNone(
            self.router.allow_migrate('b1-primary', user_modle._meta.app_label, 'User'),
            "Not configured for horizontal database groups",
        )

    def test_allow_relation(self):
        user = user_modle.objects.create_user('spam')
        a1 = HorizonA.objects.using('a1-primary').create(user=user, spam='1st')
        a2 = HorizonA.objects.using('a1-primary').create(user=user, spam='2nd')
        self.assertTrue(self.router.allow_relation(a1, a2))

    def test_not_allow_relation(self):
        user_a = user_modle.objects.create_user('spam')
        user_b = user_modle.objects.create_user('egg')
        HorizontalMetadata.objects.create(group='a', key=user_a.id, index=1)
        HorizontalMetadata.objects.create(group='a', key=user_b.id, index=2)
        a1 = HorizonA.objects.using('a1-primary').create(user=user_a, spam='1st')
        a2 = HorizonA.objects.using('a2-primary').create(user=user_a, spam='2nd')
        a3 = HorizonA.objects.using('a2-primary').create(user=user_b, spam='3rd')
        self.assertTrue(self.router.allow_relation(a1, a2))
        self.assertIsNone(self.router.allow_relation(a1, a3), "Other shard")
