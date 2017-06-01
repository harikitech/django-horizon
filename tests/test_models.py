# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model

from .base import HorizontalBaseTestCase
from .models import AnotherGroup, ConcreteModel, HorizonChild, HorizontalMetadata, HorizonParent


user_model = get_user_model()


class HorizontalModelTestCase(HorizontalBaseTestCase):
    def setUp(self):
        super(HorizontalModelTestCase, self).setUp()
        self.user_a = user_model.objects.create_user('spam')
        self.user_b = user_model.objects.create_user('egg')

    def test_get_horizontal_group(self):
        self.assertEqual(
            'a',
            HorizonParent._get_horizontal_group(),
        )
        self.assertEqual(
            'a',
            HorizonChild._get_horizontal_group(),
        )
        self.assertEqual(
            'b',
            AnotherGroup._get_horizontal_group(),
        )
        self.assertEqual(
            'b',
            ConcreteModel._get_horizontal_group(),
        )

    def test_get_horizontal_key(self):
        self.assertEqual(
            'user',
            HorizonParent._get_horizontal_key(),
        )
        self.assertEqual(
            'user',
            HorizonChild._get_horizontal_key(),
        )
        self.assertEqual(
            'user',
            AnotherGroup._get_horizontal_key(),
        )
        self.assertEqual(
            'user',
            ConcreteModel._get_horizontal_key(),
        )

    def test_get_unique_checks(self):
        a = AnotherGroup.objects.create(user=self.user_a, egg='1st')
        unique_checks, date_checks = a._get_unique_checks()
        self.assertSetEqual(
            {
                (AnotherGroup, ('user', 'id')),  # Added horizontal key
                (AnotherGroup, ('user', 'egg')),
                (AnotherGroup, ('user', 'sushi')),  # Added horizontal key
            },
            set(unique_checks),
        )

    def test_horizontal_key(self):
        p = HorizonParent.objects.create(user=self.user_a, spam='1st')
        self.assertEqual(self.user_a.id, p._horizontal_key)

    def test_horizontal_database_index(self):
        p = HorizonParent.objects.create(user=self.user_a, spam='1st')
        c = HorizonChild.objects.create(user=self.user_a, parent=p)
        self.assertEqual(p._horizontal_database_index, c._horizontal_database_index)

    def test_filter(self):
        HorizonParent.objects.create(user=self.user_a, spam='1st')
        self.assertEqual(1, HorizonParent.objects.filter(user=self.user_a).count())

    def test_get_or_create_expected_database(self):
        HorizontalMetadata.objects.create(group='a', key=self.user_a.id, index=1)
        p = HorizonParent.objects.create(user=self.user_a, spam='1st')

        self.assertTrue(HorizonParent.objects.using('a1-primary').get(pk=p.pk))
        self.assertTrue(HorizonParent.objects.using('a1-replica-1').get(pk=p.pk))
        self.assertTrue(HorizonParent.objects.using('a1-replica-2').get(pk=p.pk))

        with self.assertRaises(HorizonParent.DoesNotExist):
            self.assertTrue(HorizonParent.objects.using('a2-primary').get(pk=p.pk))

        with self.assertRaises(HorizonParent.DoesNotExist):
            self.assertTrue(HorizonParent.objects.using('a3').get(pk=p.pk))

    def test_get_or_create_expected_database_for_inherited_model(self):
        HorizontalMetadata.objects.create(group='b', key=self.user_a.id, index=1)
        c = ConcreteModel.objects.create(user=self.user_a, pizza='pepperoni', potate='head')
        self.assertTrue(ConcreteModel.objects.using('b1-primary').get(pk=c.pk))
        self.assertTrue(ConcreteModel.objects.using('b1-replica-1').get(pk=c.pk))
        self.assertTrue(ConcreteModel.objects.using('b1-replica-2').get(pk=c.pk))
