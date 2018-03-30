# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from horizon.utils import (
    get_config,
    get_config_from_group,
    get_config_from_model,
    get_db_for_read_from_model_index,
    get_db_for_write_from_model_index,
    get_group_from_model,
    get_key_field_name_from_model,
    get_metadata_model,
    get_or_create_index,
)

from .models import (
    ConcreteModel,
    HorizontalMetadata,
    ManyModel,
    OneModel,
    ProxiedModel,
    ProxyBaseModel,
)

user_model = get_user_model()


class UtilsTestCase(TestCase):
    def get_metadata_model(self):
        self.assertEqual(get_metadata_model(), HorizontalMetadata)

    @override_settings(HORIZONTAL_CONFIG={'METADATA_MODEL': ':innocent:'})
    def test_get_metadata_failed_when_wrong_format(self):
        with self.assertRaises(ImproperlyConfigured):
            get_config.cache_clear()
            get_metadata_model()
        get_config.cache_clear()

    @override_settings(HORIZONTAL_CONFIG={'METADATA_MODEL': 'where.IsMyModel'})
    def test_get_metadata_failed_when_lookup_failed(self):
        with self.assertRaises(ImproperlyConfigured):
            get_config.cache_clear()
            get_metadata_model()
        get_config.cache_clear()

    def test_get_group_from_model(self):
        self.assertEqual('a', get_group_from_model(OneModel))
        self.assertEqual('a', get_group_from_model(ManyModel))
        self.assertEqual('b', get_group_from_model(ProxyBaseModel))
        self.assertEqual('b', get_group_from_model(ProxiedModel))
        self.assertEqual('b', get_group_from_model(ConcreteModel))

    def test_get_group_from_model_for_none_horizontal_models(self):
        self.assertIsNone(get_group_from_model(user_model))

    def test_get_key_field_name_from_model(self):
        self.assertEqual('user', get_key_field_name_from_model(OneModel))
        self.assertEqual('user', get_key_field_name_from_model(ManyModel))
        self.assertEqual('user', get_key_field_name_from_model(ProxyBaseModel))
        self.assertEqual('user', get_key_field_name_from_model(ProxiedModel))
        self.assertEqual('user', get_key_field_name_from_model(ConcreteModel))

    def test_get_key_field_name_from_model_for_none_horizontal_models(self):
        self.assertIsNone(get_key_field_name_from_model(user_model))

    def test_get_config_from_model(self):
        config_for_mqny = get_config_from_model(OneModel)
        self.assertDictEqual(
            {
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
                        'read': ['a3'],  # Complete db for read
                    },
                },
                'PICKABLES': [1, 2, 3],  # Complete pickables
                'DATABASE_SET': {
                    'a1-primary',
                    'a1-replica-1',
                    'a1-replica-2',
                    'a2-primary',
                    'a2-replica',
                    'a3',
                },
            },
            config_for_mqny,
        )

        config_for_one = get_config_from_model(OneModel)
        self.assertDictEqual(config_for_mqny, config_for_one)
        self.assertDictEqual(config_for_one, get_config_from_group('a'))

    def test_get_config_from_model_for_none_horizontal_models(self):
        config_for_user = get_config_from_model(user_model)
        self.assertDictEqual({}, config_for_user)

    def test_get_db_for_read_from_model_index(self):
        for model in (OneModel, ManyModel):
            self.assertIn(
                get_db_for_read_from_model_index(model, 1),
                ['a1-replica-1', 'a1-replica-2'],
            )
            self.assertIn(
                get_db_for_read_from_model_index(model, 2),
                ['a2-replica'],
            )
            self.assertIn(
                get_db_for_read_from_model_index(model, 3),
                ['a3'],
            )

    def test_get_db_for_write_from_model_index(self):
        for model in (ProxyBaseModel, ProxiedModel, ConcreteModel, ):
            self.assertEqual('b1-primary', get_db_for_write_from_model_index(model, 1))
            self.assertEqual('b2-primary', get_db_for_write_from_model_index(model, 2))
            self.assertEqual('b3', get_db_for_write_from_model_index(model, 3))

    def test_get_or_create_index(self):
        user = user_model.objects.create_user('spam')
        one_index = get_or_create_index(OneModel, user.id)
        self.assertTrue(HorizontalMetadata.objects.get(group='a', key=user.id))

        many_index = get_or_create_index(ManyModel, user.id)
        self.assertEqual(one_index, many_index)
