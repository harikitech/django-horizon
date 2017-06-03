# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.contrib.auth import get_user_model
from django.db.utils import ProgrammingError

from horizon.query import HorizontalQuerySet
from .base import HorizontalBaseTestCase
from .models import OneModel


user_model = get_user_model()


class HorizontalQuerySetTestCase(HorizontalBaseTestCase):
    def setUp(self):
        super(HorizontalQuerySetTestCase, self).setUp()
        self.user = user_model.objects.create_user('spam')
        self.queryset = HorizontalQuerySet()

    def test_get(self):
        OneModel.objects.create(user=self.user, spam='1st')
        with patch.object(
            HorizontalQuerySet,
            '_get_horizontal_key_from_lookup_value',
            wraps=self.queryset._get_horizontal_key_from_lookup_value,
        ) as mock_get_horizontal_key_from_lookup_value:
            OneModel.objects.get(user=self.user, spam='1st')
            mock_get_horizontal_key_from_lookup_value.assert_any_call(self.user)
            self.assertEqual(
                self.user.id,
                self.queryset._get_horizontal_key_from_lookup_value(self.user),
            )

    def test_get_by_id(self):
        OneModel.objects.create(user=self.user, spam='1st')
        with patch.object(
            HorizontalQuerySet,
            '_get_horizontal_key_from_lookup_value',
            wraps=self.queryset._get_horizontal_key_from_lookup_value,
        ) as mock_get_horizontal_key_from_lookup_value:
            OneModel.objects.get(user_id=self.user.id, spam='1st')
            mock_get_horizontal_key_from_lookup_value.assert_any_call(self.user.id)
            self.assertEqual(
                self.user.id,
                self.queryset._get_horizontal_key_from_lookup_value(self.user.id),
            )

    def test_create(self):
        with patch.object(
            HorizontalQuerySet,
            '_get_horizontal_key_from_lookup_value',
            wraps=self.queryset._get_horizontal_key_from_lookup_value,
        ) as mock_get_horizontal_key_from_lookup_value:
            OneModel.objects.create(user=self.user, spam='1st')
            mock_get_horizontal_key_from_lookup_value.assert_called_once_with(self.user)
            self.assertEqual(
                self.user.id,
                self.queryset._get_horizontal_key_from_lookup_value(self.user),
            )

    def test_create_by_id(self):
        with patch.object(
            HorizontalQuerySet,
            '_get_horizontal_key_from_lookup_value',
            wraps=self.queryset._get_horizontal_key_from_lookup_value,
        ) as mock_get_horizontal_key_from_lookup_value:
            OneModel.objects.create(user_id=self.user.id, spam='1st')
            mock_get_horizontal_key_from_lookup_value.assert_called_once_with(self.user.id)
            self.assertEqual(
                self.user.id,
                self.queryset._get_horizontal_key_from_lookup_value(self.user.id),
            )

    def test_get_or_create(self):
        # Create
        with patch.object(
            HorizontalQuerySet,
            '_get_horizontal_key_from_lookup_value',
            wraps=self.queryset._get_horizontal_key_from_lookup_value,
        ) as mock_get_horizontal_key_from_lookup_value:
            a1, created = OneModel.objects.get_or_create(user=self.user, spam='1st')
            mock_get_horizontal_key_from_lookup_value.assert_any_call(self.user)
            self.assertEqual(
                self.user.id,
                self.queryset._get_horizontal_key_from_lookup_value(self.user),
            )
            self.assertTrue(created)

        # Get
        with patch.object(
            HorizontalQuerySet,
            '_get_horizontal_key_from_lookup_value',
            wraps=self.queryset._get_horizontal_key_from_lookup_value,
        ) as mock_get_horizontal_key_from_lookup_value:
            a2, created = OneModel.objects.get_or_create(user=self.user, spam='1st')
            mock_get_horizontal_key_from_lookup_value.assert_any_call(self.user)
            self.assertEqual(
                self.user.id,
                self.queryset._get_horizontal_key_from_lookup_value(self.user),
            )
            self.assertFalse(created)
        self.assertEqual(a1.pk, a2.pk)

    def test_get_or_create_by_id(self):
        # Create
        with patch.object(
            HorizontalQuerySet,
            '_get_horizontal_key_from_lookup_value',
            wraps=self.queryset._get_horizontal_key_from_lookup_value,
        ) as mock_get_horizontal_key_from_lookup_value:
            a1, created = OneModel.objects.get_or_create(user_id=self.user.id, spam='1st')
            mock_get_horizontal_key_from_lookup_value.assert_any_call(self.user.id)
            self.assertEqual(
                self.user.id,
                self.queryset._get_horizontal_key_from_lookup_value(self.user.id),
            )
            self.assertTrue(created)

        # Get
        with patch.object(
            HorizontalQuerySet,
            '_get_horizontal_key_from_lookup_value',
            wraps=self.queryset._get_horizontal_key_from_lookup_value,
        ) as mock_get_horizontal_key_from_lookup_value:
            a2, created = OneModel.objects.get_or_create(user_id=self.user.id, spam='1st')
            mock_get_horizontal_key_from_lookup_value.assert_any_call(self.user.id)
            self.assertEqual(
                self.user.id,
                self.queryset._get_horizontal_key_from_lookup_value(self.user.id),
            )
            self.assertFalse(created)
        self.assertEqual(a1.pk, a2.pk)

    def test_update_or_create(self):
        # Create
        with patch.object(
            HorizontalQuerySet,
            '_get_horizontal_key_from_lookup_value',
            wraps=self.queryset._get_horizontal_key_from_lookup_value,
        ) as mock_get_horizontal_key_from_lookup_value:
            a1, created = OneModel.objects.update_or_create(user=self.user, spam='1st',
                                                                 defaults={'egg': 'scrambled'})
            mock_get_horizontal_key_from_lookup_value.assert_any_call(self.user)
            self.assertEqual(
                self.user.id,
                self.queryset._get_horizontal_key_from_lookup_value(self.user),
            )
            self.assertTrue(created)
            self.assertEqual('scrambled', a1.egg)

        # Update
        with patch.object(
            HorizontalQuerySet,
            '_get_horizontal_key_from_lookup_value',
            wraps=self.queryset._get_horizontal_key_from_lookup_value,
        ) as mock_get_horizontal_key_from_lookup_value:
            a2, created = OneModel.objects.update_or_create(user=self.user, spam='1st',
                                                                 defaults={'egg': 'fried'})
            mock_get_horizontal_key_from_lookup_value.assert_any_call(self.user)
            self.assertEqual(
                self.user.id,
                self.queryset._get_horizontal_key_from_lookup_value(self.user),
            )
            self.assertFalse(created)
            self.assertEqual('scrambled', a1.egg)
        self.assertEqual(a1.pk, a2.pk)

    def test_update_or_create_by_id(self):
        # Create
        with patch.object(
            HorizontalQuerySet,
            '_get_horizontal_key_from_lookup_value',
            wraps=self.queryset._get_horizontal_key_from_lookup_value,
        ) as mock_get_horizontal_key_from_lookup_value:
            a1, created = OneModel.objects.update_or_create(user_id=self.user.id, spam='1st',
                                                                 defaults={'egg': 'scrambled'})
            mock_get_horizontal_key_from_lookup_value.assert_any_call(self.user.id)
            self.assertEqual(
                self.user.id,
                self.queryset._get_horizontal_key_from_lookup_value(self.user.id),
            )
            self.assertTrue(created)
            self.assertEqual('scrambled', a1.egg)

        # Update
        with patch.object(
            HorizontalQuerySet,
            '_get_horizontal_key_from_lookup_value',
            wraps=self.queryset._get_horizontal_key_from_lookup_value,
        ) as mock_get_horizontal_key_from_lookup_value:
            a2, created = OneModel.objects.update_or_create(user_id=self.user.id, spam='1st',
                                                                 defaults={'egg': 'fried'})
            mock_get_horizontal_key_from_lookup_value.assert_any_call(self.user.id)
            self.assertEqual(
                self.user.id,
                self.queryset._get_horizontal_key_from_lookup_value(self.user.id),
            )
            self.assertFalse(created)
            self.assertEqual('scrambled', a1.egg)
        self.assertEqual(a1.pk, a2.pk)

    def test_filter(self):
        OneModel.objects.create(user=self.user, spam='1st')
        OneModel.objects.create(user=self.user, spam='2nd')
        with patch.object(
            HorizontalQuerySet,
            '_get_horizontal_key_from_lookup_value',
            wraps=self.queryset._get_horizontal_key_from_lookup_value,
        ) as mock_get_horizontal_key_from_lookup_value:
            q = OneModel.objects.filter(user=self.user)
            mock_get_horizontal_key_from_lookup_value.assert_called_once_with(self.user)
            self.assertEqual(
                self.user.id,
                self.queryset._get_horizontal_key_from_lookup_value(self.user),
            )
            self.assertEqual(2, q.count())

    def test_filter_by_id(self):
        OneModel.objects.create(user=self.user, spam='1st')
        OneModel.objects.create(user=self.user, spam='2nd')
        with patch.object(
            HorizontalQuerySet,
            '_get_horizontal_key_from_lookup_value',
            wraps=self.queryset._get_horizontal_key_from_lookup_value,
        ) as mock_get_horizontal_key_from_lookup_value:
            q = OneModel.objects.filter(user_id=self.user.id)
            mock_get_horizontal_key_from_lookup_value.assert_called_once_with(self.user.id)
            self.assertEqual(
                self.user.id,
                self.queryset._get_horizontal_key_from_lookup_value(self.user.id),
            )
            self.assertEqual(2, q.count())

    def test_raise_value_error_when_lookup_from_foreign(self):
        OneModel.objects.create(user=self.user, spam='1st')
        with self.assertRaises(ValueError):
            list(self.user.onemodel_set.all())

    def test_filter_without_shard_key(self):
        with self.assertRaises(ProgrammingError):
            list(OneModel.objects.all())

    def test_clone(self):
        qs = OneModel.objects.filter(user=self.user)
        qs = qs.exclude(spam='1st')
        list(qs)
