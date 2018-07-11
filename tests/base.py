from django.test import TransactionTestCase


class HorizontalBaseTestCase(TransactionTestCase):
    """Base test case for horizonta."""

    multi_db = True
