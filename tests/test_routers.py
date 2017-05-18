# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from unittest import skip

from django.contrib.auth import get_user_model
from django.test import TestCase

from horizon.routers import HorizontalRouter
from .models import AnotherGroup, HorizonChild, HorizonParent, HorizontalMetadata


user_modle = get_user_model()


class HorizontalRouterMigrationTestCase(TestCase):
    def setUp(self):
        self.router = HorizontalRouter()

    def test_get_horizontal_group(self):
        self.assertEqual(
            'a',
            self.router._get_horizontal_group(HorizonParent),
        )
        self.assertEqual(
            'a',
            self.router._get_horizontal_group(HorizonChild),
        )
        self.assertEqual(
            'b',
            self.router._get_horizontal_group(AnotherGroup),
        )

    def test_get_horizontal_group_for_default(self):
        self.assertIsNone(self.router._get_horizontal_group(user_modle))

    def test_allow_migrate(self):
        for expected_database in ('a1-primary', 'a1-replica-1', 'a1-replica-2', 'a2-primary',
                                  'a2-replica', 'a3'):
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'HorizonParent',
                                          model=HorizonParent))
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'HorizonChild',
                                          model=HorizonParent))

        for expected_database in ('b1-primary', 'b1-replica-1', 'b1-replica-2', 'b2-primary',
                                  'b2-replica', 'b3'):
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'AnotherGroup',
                                          model=AnotherGroup))

    def test_allow_migrate_without_hints(self):
        for expected_database in ('a1-primary', 'a1-replica-1', 'a1-replica-2', 'a2-primary',
                                  'a2-replica', 'a3'):
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'HorizonParent'))
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'HorizonChild'))

        for expected_database in ('b1-primary', 'b1-replica-1', 'b1-replica-2', 'b2-primary',
                                  'b2-replica', 'b3'):
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'AnotherGroup'))

    def test_not_allow_migrate(self):
        for horizontal_model in (HorizonParent, HorizonChild, AnotherGroup):
            self.assertIsNone(
                self.router.allow_migrate('default', 'tests', horizontal_model.__name__,
                                          model=horizontal_model),
                "Other database",
            )

        self.assertIsNone(
            self.router.allow_migrate('a1-primary', user_modle._meta.app_label, user_modle.__name__,
                                      model=user_modle),
            "Not configured for horizontal database groups",
        )
        self.assertIsNone(
            self.router.allow_migrate('a1-primary', 'tests', AnotherGroup.__name__,
                                      model=AnotherGroup),
            "Another horizontal group",
        )

    def test_not_allow_migrate_without_hints(self):
        for horizontal_model in ('HorizonParent', 'HorizonChild', 'AnotherGroup'):
            self.assertIsNone(
                self.router.allow_migrate('default', 'tests', horizontal_model),
                "Other database",
            )

        self.assertIsNone(
            self.router.allow_migrate(
                'a1-primary', user_modle._meta.app_label, 'User', model=user_modle),
            "Not configured for horizontal database groups",
        )
        self.assertIsNone(
            self.router.allow_migrate(
                'a1-primary', 'tests', 'AnotherGroup', model=AnotherGroup),
            "Another horizontal group",
        )


class HorizontalRouterRelationTestCase(TestCase):
    def setUp(self):
        self.router = HorizontalRouter()
        self.user_a = user_modle.objects.create_user('spam')
        self.user_b = user_modle.objects.create_user('egg')

    def test_allow_relation_in_same_database(self):
        HorizontalMetadata.objects.create(group='a', key=self.user_a.id, index=1)
        HorizontalMetadata.objects.create(group='a', key=self.user_b.id, index=1)
        p1 = HorizonParent.objects.create(user=self.user_a, spam='1st')
        p2 = HorizonParent.objects.create(user=self.user_b, spam='2nd')
        self.assertTrue(self.router.allow_relation(p1, p2))

    def test_disallow_other_database(self):
        HorizontalMetadata.objects.create(group='a', key=self.user_a.id, index=1)
        HorizontalMetadata.objects.create(group='a', key=self.user_b.id, index=2)
        p1 = HorizonParent.objects.create(user=self.user_a, spam='1st')
        p2 = HorizonParent.objects.create(user=self.user_b, spam='2nd')
        self.assertIsNone(self.router.allow_relation(p1, p2), "Other shard")

    def test_allow_relation_to_forein(self):
        p = HorizonParent.objects.create(user=self.user_a, spam='1st')
        c = HorizonChild.objects.create(user=self.user_a, parent=p)
        self.assertTrue(self.router.allow_relation(p, c))

    def test_disallow_default_database(self):
        p = HorizonParent.objects.create(user=self.user_a, spam='1st')
        self.assertFalse(self.router.allow_relation(p, self.user_a))


class HorizontalRouterReadWriteTestCase(TestCase):
    def setUp(self):
        self.router = HorizontalRouter()

    def test_db_for_read(self):
        user = user_modle.objects.create_user('spam')
        HorizonParent.objects.using('a1-primary').create(user=user, spam='1st')
