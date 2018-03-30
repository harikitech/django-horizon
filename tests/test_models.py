# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.test import TestCase

from horizon.models import AbstractHorizontalModel

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


class HorizontalModelTestCase(HorizontalBaseTestCase):
    def setUp(self):
        super(HorizontalModelTestCase, self).setUp()
        self.user_a = user_model.objects.create_user('spam')
        self.user_b = user_model.objects.create_user('egg')

    def test_get_unique_checks_for_proxied_model(self):
        proxied = ProxiedModel.objects.create(
            user=self.user_a,
            sushi='tsuna',
            tempura='momiji',
            karaage='chicken',
        )
        unique_checks, date_checks = proxied._get_unique_checks()
        self.assertSetEqual(
            {
                (ProxyBaseModel, ('user', 'id')),  # Horizontal key added
                (ProxyBaseModel, ('user', 'sushi')),  # Horizontal key added
                (ProxiedModel, ('user', 'proxybasemodel_ptr')),  # Horizontal key added
                (ProxiedModel, ('user', 'tempura')),  # Horizontal key added
                (ProxiedModel, ('user', 'karaage')),  # Horizontal key added
                (ProxiedModel, ('tempura', 'karaage')),  # Horizontal key added
            },
            set(unique_checks),
        )

    def test_get_unique_checks_for_abstract_model(self):
        concrete = ConcreteModel.objects.create(
            user=self.user_a,
            pizza='pepperoni',
            potate='head',
            coke='pe*si'
        )
        unique_checks, date_checks = concrete._get_unique_checks()
        self.assertSetEqual(
            {
                (ConcreteModel, ('user', 'id')),  # Horizontal key added
                (ConcreteModel, ('user', 'pizza')),  # Horizontal key added
                (ConcreteModel, ('user', 'potate')),  # Horizontal key added
                (ConcreteModel, ('user', 'coke')),  # Horizontal key added
                (ConcreteModel, ('pizza', 'coke')),
            },
            set(unique_checks),
        )

    def test_get_unique_checks_with_exclude(self):
        concrete = ConcreteModel.objects.create(
            user=self.user_a,
            pizza='pepperoni',
            potate='head',
            coke='pe*si'
        )
        unique_checks, date_checks = concrete._get_unique_checks(exclude='coke')
        self.assertSetEqual(
            {
                (ConcreteModel, ('user', 'id')),  # Horizontal key added
                (ConcreteModel, ('user', 'pizza')),  # Horizontal key added
                (ConcreteModel, ('user', 'potate')),  # Horizontal key added
            },
            set(unique_checks),
        )

    def test_horizontal_key(self):
        one = OneModel.objects.create(user=self.user_a, spam='1st')
        self.assertEqual(self.user_a.id, one._horizontal_key)

    def test_horizontal_database_index(self):
        one = OneModel.objects.create(user=self.user_a, spam='1st')
        many = ManyModel.objects.create(user=self.user_a, one=one)
        self.assertEqual(one._horizontal_database_index, many._horizontal_database_index)

    def test_filter(self):
        OneModel.objects.create(user=self.user_a, spam='1st')
        self.assertEqual(1, OneModel.objects.filter(user=self.user_a).count())

    def test_get_or_create_expected_database(self):
        HorizontalMetadata.objects.create(group='a', key=self.user_a.id, index=1)
        one = OneModel.objects.create(user=self.user_a, spam='1st')

        self.assertTrue(OneModel.objects.using('a1-primary').get(pk=one.pk))
        self.assertTrue(OneModel.objects.using('a1-replica-1').get(pk=one.pk))
        self.assertTrue(OneModel.objects.using('a1-replica-2').get(pk=one.pk))

        with self.assertRaises(OneModel.DoesNotExist):
            self.assertTrue(OneModel.objects.using('a2-primary').get(pk=one.pk))

        with self.assertRaises(OneModel.DoesNotExist):
            self.assertTrue(OneModel.objects.using('a3').get(pk=one.pk))

    def test_get_or_create_expected_database_for_inherited_model(self):
        HorizontalMetadata.objects.create(group='b', key=self.user_a.id, index=1)
        concrete = ConcreteModel.objects.create(user=self.user_a, pizza='pepperoni', potate='head')
        self.assertTrue(ConcreteModel.objects.using('b1-primary').get(pk=concrete.pk))
        self.assertTrue(ConcreteModel.objects.using('b1-replica-1').get(pk=concrete.pk))
        self.assertTrue(ConcreteModel.objects.using('b1-replica-2').get(pk=concrete.pk))

    def test_get_or_create_expected_database_for_proxied_model(self):
        HorizontalMetadata.objects.create(group='b', key=self.user_a.id, index=2)
        proxied = ProxiedModel.objects.create(
            user=self.user_a,
            sushi='tsuna',
            tempura='momiji',
            karaage='chicken',
        )
        self.assertTrue(ProxiedModel.objects.using('b2-primary').get(pk=proxied.pk))
        self.assertTrue(ProxiedModel.objects.using('b2-replica').get(pk=proxied.pk))
        self.assertTrue(ProxyBaseModel.objects.using('b2-primary').get(pk=proxied.pk))
        self.assertTrue(ProxyBaseModel.objects.using('b2-replica').get(pk=proxied.pk))


class AbstractHorizontalModelTestCase(TestCase):
    def test_check_horizontal_meta_without_horitontal_group(self):
        class WithoutHorizontalGroupModel(AbstractHorizontalModel):
            user = models.ForeignKey(
                settings.AUTH_USER_MODEL,
                on_delete=models.DO_NOTHING,
                db_constraint=False,
            )

            class Meta(object):
                horizontal_key = 'user'
        errors = WithoutHorizontalGroupModel.check()
        self.assertEqual(1, len(errors))
        self.assertEqual('horizon.E001', errors[0].id)

    def test_check_horizontal_meta_without_horitontal_key(self):
        class WithoutHorizontalKeyModel(AbstractHorizontalModel):
            user = models.ForeignKey(
                settings.AUTH_USER_MODEL,
                on_delete=models.DO_NOTHING,
                db_constraint=False,
            )

            class Meta(object):
                horizontal_group = 'a'
        errors = WithoutHorizontalKeyModel.check()
        self.assertEqual(1, len(errors))
        self.assertEqual('horizon.E001', errors[0].id)

    def test_check_horizontal_meta_wrong_horizontal_group(self):
        class WrongGroupModel(AbstractHorizontalModel):
            user = models.ForeignKey(
                settings.AUTH_USER_MODEL,
                on_delete=models.DO_NOTHING,
                db_constraint=False,
            )

            class Meta(object):
                horizontal_group = 'wrong'
                horizontal_key = 'user'
        errors = WrongGroupModel.check()
        self.assertEqual(1, len(errors))
        self.assertEqual('horizon.E002', errors[0].id)

    def test_check_horizontal_meta_wrong_horizontal_key(self):
        class WrongKeyModel(AbstractHorizontalModel):
            user = models.ForeignKey(
                settings.AUTH_USER_MODEL,
                on_delete=models.DO_NOTHING,
                db_constraint=False,
            )

            class Meta(object):
                horizontal_group = 'a'
                horizontal_key = 'wrong'
        errors = WrongKeyModel.check()
        self.assertEqual(1, len(errors))
        self.assertEqual('horizon.E003', errors[0].id)
