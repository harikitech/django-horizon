from unittest.mock import patch

from django.contrib.auth import get_user_model

from horizon.routers import HorizontalRouter

from .base import HorizontalBaseTestCase
from .models import (
    ConcreteModel,
    HorizontalMetadata,
    ManyModel,
    OneModel,
    ProxiedModel,
    ProxyBaseModel,
)

user_model = get_user_model()


class HorizontalRouterMigrationTestCase(HorizontalBaseTestCase):
    def setUp(self):
        super(HorizontalRouterMigrationTestCase, self).setUp()
        self.router = HorizontalRouter()

    def test_allow_migrate(self):
        for expected_database in ('a1-primary', 'a1-replica-1', 'a1-replica-2', 'a2-primary',
                                  'a2-replica', 'a3'):
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'OneModel',
                                          model=OneModel))
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'ManyModel',
                                          model=OneModel))

        for expected_database in ('b1-primary', 'b1-replica-1', 'b1-replica-2', 'b2-primary',
                                  'b2-replica', 'b3'):
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'ProxyBaseModel',
                                          model=ProxyBaseModel))
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'ProxiedModel',
                                          model=ProxiedModel))
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'ConcreteModel',
                                          model=ConcreteModel))

    def test_allow_migrate_without_hints(self):
        for expected_database in ('a1-primary', 'a1-replica-1', 'a1-replica-2', 'a2-primary',
                                  'a2-replica', 'a3'):
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'OneModel'))
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'ManyModel'))

        for expected_database in ('b1-primary', 'b1-replica-1', 'b1-replica-2', 'b2-primary',
                                  'b2-replica', 'b3'):
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'ProxyBaseModel'))
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'ProxiedModel'))
            self.assertTrue(
                self.router.allow_migrate(expected_database, 'tests', 'ConcreteModel'))

    def test_not_allow_migrate(self):
        for horizontal_model in (OneModel, ManyModel, ProxyBaseModel, ProxiedModel, ConcreteModel):
            self.assertIsNone(
                self.router.allow_migrate('default', 'tests', horizontal_model.__name__,
                                          model=horizontal_model),
                "Other database",
            )

        self.assertIsNone(
            self.router.allow_migrate('a1-primary', user_model._meta.app_label, user_model.__name__,
                                      model=user_model),
            "Not configured for horizontal database groups",
        )
        self.assertIsNone(
            self.router.allow_migrate('a1-primary', 'tests', ProxyBaseModel.__name__,
                                      model=ProxyBaseModel),
            "Another horizontal group",
        )
        self.assertIsNone(
            self.router.allow_migrate('a1-primary', 'tests', ProxiedModel.__name__,
                                      model=ProxiedModel),
            "Another horizontal group",
        )
        self.assertIsNone(
            self.router.allow_migrate('a1-primary', 'tests', ConcreteModel.__name__,
                                      model=ConcreteModel),
            "Another horizontal group",
        )

    def test_not_allow_migrate_without_hints(self):
        for horizontal_model in (
            'OneModel', 'ManyModel', 'ProxyBaseModel', 'ProxiedModel', 'ConcreteModel'
        ):
            self.assertIsNone(
                self.router.allow_migrate('default', 'tests', horizontal_model),
                "Other database",
            )

        self.assertIsNone(
            self.router.allow_migrate(
                'a1-primary', user_model._meta.app_label, 'User', model=user_model),
            "Not configured for horizontal database groups",
        )
        self.assertIsNone(
            self.router.allow_migrate(
                'a1-primary', 'tests', 'ProxyBaseModel', model=ProxyBaseModel),
            "Another horizontal group",
        )
        self.assertIsNone(
            self.router.allow_migrate(
                'a1-primary', 'tests', 'ProxiedModel', model=ProxiedModel),
            "Another horizontal group",
        )
        self.assertIsNone(
            self.router.allow_migrate(
                'a1-primary', 'tests', 'ConcreteModel', model=ConcreteModel),
            "Another horizontal group",
        )


class HorizontalRouterRelationTestCase(HorizontalBaseTestCase):
    def setUp(self):
        super(HorizontalRouterRelationTestCase, self).setUp()
        self.router = HorizontalRouter()
        self.user_a = user_model.objects.create_user('spam')
        self.user_b = user_model.objects.create_user('egg')

    def test_allow_relation_in_same_database(self):
        HorizontalMetadata.objects.create(group='a', key=self.user_a.id, index=1)
        HorizontalMetadata.objects.create(group='a', key=self.user_b.id, index=1)
        one1 = OneModel.objects.create(user=self.user_a, spam='1st')
        one2 = OneModel.objects.create(user=self.user_b, spam='2nd')
        self.assertTrue(self.router.allow_relation(one1, one2))

    def test_disallow_other_database(self):
        HorizontalMetadata.objects.create(group='a', key=self.user_a.id, index=1)
        HorizontalMetadata.objects.create(group='a', key=self.user_b.id, index=2)
        one1 = OneModel.objects.create(user=self.user_a, spam='1st')
        one2 = OneModel.objects.create(user=self.user_b, spam='2nd')
        self.assertIsNone(self.router.allow_relation(one1, one2), "Other shard")

    def test_disallow_other_group(self):
        one = OneModel.objects.create(user=self.user_a, spam='meat?')
        concrete = ConcreteModel.objects.create(
            user=self.user_a,
            pizza='pepperoni',
            potate='head',
            coke='pe*si'
        )
        self.assertIsNone(self.router.allow_relation(one, concrete), "Other group")

    def test_allow_relation_to_forein(self):
        one = OneModel.objects.create(user=self.user_a, spam='meat?')
        many = ManyModel.objects.create(user=self.user_a, one=one)
        self.assertTrue(self.router.allow_relation(one, many))

    def test_disallow_default_database(self):
        one = OneModel.objects.create(user=self.user_a, spam='meat?')
        self.assertFalse(self.router.allow_relation(one, self.user_a))


class HorizontalRouterReadWriteTestCase(HorizontalBaseTestCase):
    def setUp(self):
        super(HorizontalRouterReadWriteTestCase, self).setUp()
        self.router = HorizontalRouter()
        self.user_a = user_model.objects.create_user('spam')
        self.user_b = user_model.objects.create_user('egg')
        self.user_c = user_model.objects.create_user('musubi')
        HorizontalMetadata.objects.create(group='a', key=self.user_a.id, index=1)
        HorizontalMetadata.objects.create(group='a', key=self.user_b.id, index=2)
        HorizontalMetadata.objects.create(group='a', key=self.user_c.id, index=3)

    def test_db_for_write(self):
        with patch.object(
            HorizontalRouter, 'db_for_write', wraps=self.router.db_for_write,
        ) as mock_db_for_write:
            OneModel.objects.create(user=self.user_a, spam='1st')
            mock_db_for_write.assert_any_call(OneModel, horizontal_key=self.user_a.id)
            self.assertEqual(
                'a1-primary',
                self.router.db_for_write(OneModel, horizontal_key=self.user_a.id),
            )

        with patch.object(
            HorizontalRouter, 'db_for_write', wraps=self.router.db_for_write,
        ) as mock_db_for_write:
            OneModel.objects.create(user=self.user_b, spam='2nd')
            mock_db_for_write.assert_any_call(OneModel, horizontal_key=self.user_b.id)
            self.assertEqual(
                'a2-primary',
                self.router.db_for_write(OneModel, horizontal_key=self.user_b.id),
            )

        with patch.object(
            HorizontalRouter, 'db_for_write', wraps=self.router.db_for_write,
        ) as mock_db_for_write:
            OneModel.objects.create(user=self.user_c, spam='1st')
            mock_db_for_write.assert_any_call(OneModel, horizontal_key=self.user_c.id)
            self.assertEqual(
                'a3',
                self.router.db_for_write(OneModel, horizontal_key=self.user_c.id),
            )

    def test_db_for_write_by_id(self):
        with patch.object(
            HorizontalRouter, 'db_for_write', wraps=self.router.db_for_write,
        ) as mock_db_for_write:
            OneModel.objects.create(user_id=self.user_a.id, spam='1st')
            mock_db_for_write.assert_any_call(OneModel, horizontal_key=self.user_a.id)
            self.assertEqual(
                'a1-primary',
                self.router.db_for_write(OneModel, horizontal_key=self.user_a.id),
            )

    def test_db_for_write_other_databases(self):
        with patch.object(
            HorizontalRouter, 'db_for_write', wraps=self.router.db_for_write,
        ) as mock_db_for_write:
            new_user = user_model.objects.create_user('pizza')
            mock_db_for_write.assert_any_call(user_model, instance=new_user)
            self.assertIsNone(self.router.db_for_write(user_model, instance=new_user))

    def test_db_for_read(self):
        with patch.object(
            HorizontalRouter, 'db_for_read', wraps=self.router.db_for_read,
        ) as mock_db_for_read:
            list(OneModel.objects.filter(user=self.user_a))
            mock_db_for_read.assert_any_call(OneModel, horizontal_key=self.user_a.id)
            self.assertIn(
                self.router.db_for_read(OneModel, horizontal_key=self.user_a.id),
                ['a1-replica-1', 'a1-replica-2'],
            )

        with patch.object(
            HorizontalRouter, 'db_for_read', wraps=self.router.db_for_read,
        ) as mock_db_for_read:
            list(OneModel.objects.filter(user=self.user_b))
            mock_db_for_read.assert_any_call(OneModel, horizontal_key=self.user_b.id)
            self.assertIn(
                self.router.db_for_read(OneModel, horizontal_key=self.user_b.id),
                ['a2-replica'],
            )

        with patch.object(
            HorizontalRouter, 'db_for_read', wraps=self.router.db_for_read,
        ) as mock_db_for_read:
            list(OneModel.objects.filter(user=self.user_c))
            mock_db_for_read.assert_any_call(OneModel, horizontal_key=self.user_c.id)
            self.assertIn(
                self.router.db_for_read(OneModel, horizontal_key=self.user_c.id),
                ['a3'],
            )

    def test_db_for_read_by_id(self):
        with patch.object(
            HorizontalRouter, 'db_for_read', wraps=self.router.db_for_read,
        ) as mock_db_for_read:
            list(OneModel.objects.filter(user_id=self.user_a.id))
            mock_db_for_read.assert_any_call(OneModel, horizontal_key=self.user_a.id)
            self.assertIn(
                self.router.db_for_read(OneModel, horizontal_key=self.user_a.id),
                ['a1-replica-1', 'a1-replica-2'],
            )

    def test_db_for_read_other_databases(self):
        with patch.object(
            HorizontalRouter, 'db_for_read', wraps=self.router.db_for_read,
        ) as mock_db_for_read:
            list(user_model.objects.filter())
            mock_db_for_read.assert_any_call(user_model)
            self.assertIsNone(self.router.db_for_read(user_model))
