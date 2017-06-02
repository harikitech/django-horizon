# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model

from horizon.utils import (
    get_metadata_model,
    get_group_from_model,
    get_key_field_name_from_model,
    get_config_from_group,
    get_config_from_model,
    get_db_for_read_from_model_index,
    get_db_for_write_from_model_index,
    get_or_create_index,
)
from .base import HorizontalBaseTestCase
from .models import AnotherGroup, ConcreteModel, HorizonChild, HorizontalMetadata, HorizonParent


user_model = get_user_model()


class UtilsTestCase(HorizontalBaseTestCase):
    def get_metadata_model(self):
        self.assertEqual(get_metadata_model(), HorizontalMetadata)

    def test_get_group_from_model(self):
        self.assertEqual('a', get_group_from_model(HorizonParent))
        self.assertEqual('a', get_group_from_model(HorizonChild))
        self.assertEqual('b', get_group_from_model(AnotherGroup))
        self.assertEqual('b', get_group_from_model(ConcreteModel))

    def test_get_group_from_model_for_none_horizontal_models(self):
        self.assertIsNone(get_group_from_model(user_model))

    def test_get_key_field_name_from_model(self):
        self.assertEqual('user', get_key_field_name_from_model(HorizonParent))
        self.assertEqual('user', get_key_field_name_from_model(HorizonChild))
        self.assertEqual('user', get_key_field_name_from_model(AnotherGroup))
        self.assertEqual('user', get_key_field_name_from_model(ConcreteModel))

    def test_get_key_field_name_from_model_for_none_horizontal_models(self):
        self.assertIsNone(get_key_field_name_from_model(user_model))

    def test_get_config_from_model(self):
        config_for_horizon_parent = get_config_from_model(HorizonParent)
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
            config_for_horizon_parent,
        )

        config_for_horizon_child = get_config_from_model(HorizonParent)
        self.assertDictEqual(config_for_horizon_parent, config_for_horizon_child)
        self.assertDictEqual(config_for_horizon_child, get_config_from_group('a'))

    def test_get_config_from_model_for_none_horizontal_models(self):
        config_for_user = get_config_from_model(user_model)
        self.assertDictEqual({}, config_for_user)

    def test_get_db_for_read_from_model_index(self):
        for model in (HorizonParent, HorizonChild):
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
        for model in (AnotherGroup, ConcreteModel):
            self.assertEqual('b1-primary', get_db_for_write_from_model_index(model, 1))
            self.assertEqual('b2-primary', get_db_for_write_from_model_index(model, 2))
            self.assertEqual('b3', get_db_for_write_from_model_index(model, 3))

    def test_get_or_create_index(self):
        user = user_model.objects.create_user('spam')
        parent_index = get_or_create_index(HorizonParent, user.id)
        self.assertTrue(HorizontalMetadata.objects.get(group='a', key=user.id))

        child_index = get_or_create_index(HorizonChild, user.id)
        self.assertEqual(parent_index, child_index)
