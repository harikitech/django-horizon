# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import HorizonA, HorizonB


class HorizontalModelTestCase(TestCase):
    def setUp(self):
        user_modle = get_user_model()
        self.user_a = user_modle.objects.create_user('spam')
        self.user_b = user_modle.objects.create_user('egg')

    def test_set_meta(self):
        self.assertEqual('a', HorizonA._meta.horizontal_group)
        self.assertEqual('user', HorizonA._meta.horizontal_key)
        self.assertEqual('b', HorizonB._meta.horizontal_group)
        self.assertEqual('user', HorizonB._meta.horizontal_key)
