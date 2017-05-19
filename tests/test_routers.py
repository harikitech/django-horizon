# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from unittest import skip
from mock import patch

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
        self.user_a = user_modle.objects.create_user('spam')
        self.user_b = user_modle.objects.create_user('egg')
        self.user_c = user_modle.objects.create_user('sushi')
        HorizontalMetadata.objects.create(group='a', key=self.user_a.id, index=1)
        HorizontalMetadata.objects.create(group='a', key=self.user_b.id, index=2)
        HorizontalMetadata.objects.create(group='a', key=self.user_c.id, index=3)

    def test_db_for_write(self):
        with patch.object(HorizontalRouter, 'db_for_write', wraps=self.router.db_for_write) as mock_db_for_write:
            HorizonParent.objects.create(user=self.user_a, spam='1st')
            mock_db_for_write.assert_any_call(HorizonParent, horizontal_key=self.user_a.id)
            self.assertEqual(
                'a1-primary',
                self.router.db_for_write(HorizonParent, horizontal_key=self.user_a.id),
            )

        with patch.object(HorizontalRouter, 'db_for_write', wraps=self.router.db_for_write) as mock_db_for_write:
            HorizonParent.objects.create(user=self.user_b, spam='2nd')
            mock_db_for_write.assert_any_call(HorizonParent, horizontal_key=self.user_b.id)
            self.assertEqual(
                'a2-primary',
                self.router.db_for_write(HorizonParent, horizontal_key=self.user_b.id),
            )

        with patch.object(HorizontalRouter, 'db_for_write', wraps=self.router.db_for_write) as mock_db_for_write:
            HorizonParent.objects.create(user=self.user_c, spam='1st')
            mock_db_for_write.assert_any_call(HorizonParent, horizontal_key=self.user_c.id)
            self.assertEqual(
                'a3',
                self.router.db_for_write(HorizonParent, horizontal_key=self.user_c.id),
            )

    def test_db_for_write_by_id(self):
        with patch.object(HorizontalRouter, 'db_for_write', wraps=self.router.db_for_write) as mock_db_for_write:
            HorizonParent.objects.create(user_id=self.user_a.id, spam='1st')
            mock_db_for_write.assert_any_call(HorizonParent, horizontal_key=self.user_a.id)
            self.assertEqual(
                'a1-primary',
                self.router.db_for_write(HorizonParent, horizontal_key=self.user_a.id),
            )

    def test_db_for_write_other_databases(self):
        with patch.object(HorizontalRouter, 'db_for_write', wraps=self.router.db_for_write) as mock_db_for_write:
            new_user = user_modle.objects.create_user('pizza')
            mock_db_for_write.assert_any_call(user_modle, instance=new_user)
            self.assertIsNone(self.router.db_for_write(user_modle, instance=new_user))

    def test_db_for_read(self):
        with patch.object(HorizontalRouter, 'db_for_read', wraps=self.router.db_for_read) as mock_db_for_read:
            list(HorizonParent.objects.filter(user=self.user_a))
            mock_db_for_read.assert_any_call(HorizonParent, horizontal_key=self.user_a.id)
            self.assertIn(
                self.router.db_for_read(HorizonParent, horizontal_key=self.user_a.id),
                ['a1-replica-1', 'a1-replica-2'],
            )

        with patch.object(HorizontalRouter, 'db_for_read', wraps=self.router.db_for_read) as mock_db_for_read:
            list(HorizonParent.objects.filter(user=self.user_b))
            mock_db_for_read.assert_any_call(HorizonParent, horizontal_key=self.user_b.id)
            self.assertIn(
                self.router.db_for_read(HorizonParent, horizontal_key=self.user_b.id),
                ['a2-replica'],
            )

        with patch.object(HorizontalRouter, 'db_for_read', wraps=self.router.db_for_read) as mock_db_for_read:
            list(HorizonParent.objects.filter(user=self.user_c))
            mock_db_for_read.assert_any_call(HorizonParent, horizontal_key=self.user_c.id)
            self.assertIn(
                self.router.db_for_read(HorizonParent, horizontal_key=self.user_c.id),
                ['a3'],
            )

    def test_db_for_read_by_id(self):
        with patch.object(HorizontalRouter, 'db_for_read', wraps=self.router.db_for_read) as mock_db_for_read:
            list(HorizonParent.objects.filter(user_id=self.user_a.id))
            mock_db_for_read.assert_any_call(HorizonParent, horizontal_key=self.user_a.id)
            self.assertIn(
                self.router.db_for_read(HorizonParent, horizontal_key=self.user_a.id),
                ['a1-replica-1', 'a1-replica-2'],
            )

    def test_db_for_read_other_databases(self):
        with patch.object(HorizontalRouter, 'db_for_read', wraps=self.router.db_for_read) as mock_db_for_read:
            list(user_modle.objects.filter())
            mock_db_for_read.assert_any_call(user_modle)
            self.assertIsNone(self.router.db_for_read(user_modle))
