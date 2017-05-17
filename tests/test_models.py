# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import HorizonA, HorizonB, HorizontalMetadata


class HorizontalModelTestCase(TestCase):
    def setUp(self):
        user_modle = get_user_model()
        self.user_a = user_modle.objects.create_user('spam')
        self.user_b = user_modle.objects.create_user('egg')
        HorizontalMetadata.objects.create(group='a', key=self.user_a.id, index=1)
        HorizontalMetadata.objects.create(group='a', key=self.user_b.id, index=2)

    def test_set_meta(self):
        self.assertEqual('a', HorizonA._meta.horizontal_group)
        self.assertEqual('user', HorizonA._meta.horizontal_key)
        self.assertEqual('b', HorizonB._meta.horizontal_group)
        self.assertEqual('user', HorizonB._meta.horizontal_key)

    def test_horizontal_key(self):
        a1 = HorizonA.objects.create(user=self.user_a, spam='1st')
        a2 = HorizonA.objects.create(user=self.user_b, spam='2nd')
        self.assertEqual(self.user_a.id, a1._horizontal_key)
        self.assertEqual(self.user_b.id, a2._horizontal_key)

    def test_horizontal_database(self):
        a1 = HorizonA.objects.create(user=self.user_a, spam='1st')
        a2 = HorizonA.objects.create(user=self.user_b, spam='2nd')
        self.assertEqual(1, a1._horizontal_database_index)
        self.assertEqual(2, a2._horizontal_database_index)
