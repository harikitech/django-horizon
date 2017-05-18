# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import HorizonChild, HorizonParent, AnotherGroup


class HorizontalModelTestCase(TestCase):
    def setUp(self):
        user_modle = get_user_model()
        self.user_a = user_modle.objects.create_user('spam')
        self.user_b = user_modle.objects.create_user('egg')

    def test_set_meta(self):
        self.assertEqual('a', HorizonParent._meta.horizontal_group)
        self.assertEqual('user', HorizonParent._meta.horizontal_key)
        self.assertEqual('a', HorizonChild._meta.horizontal_group)
        self.assertEqual('user', HorizonChild._meta.horizontal_key)
        self.assertEqual('b', AnotherGroup._meta.horizontal_group)
        self.assertEqual('user', AnotherGroup._meta.horizontal_key)

    def test_horizontal_key(self):
        p = HorizonParent.objects.create(user=self.user_a, spam='1st')
        self.assertEqual(self.user_a.id, p._horizontal_key)

    def test_horizontal_database_index(self):
        p = HorizonParent.objects.create(user=self.user_a, spam='1st')
        c = HorizonChild.objects.create(user=self.user_a, parent=p)
        self.assertEqual(p._horizontal_database_index, c._horizontal_database_index)

    def test_filter(self):
        list(HorizonParent.objects.filter(user=self.user_a))
