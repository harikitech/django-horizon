from django.conf import settings
from django.db import models
from horizon.manager import HorizontalManager
from horizon.models import AbstractHorizontalMetadata, AbstractHorizontalModel


class HorizontalMetadata(AbstractHorizontalMetadata):
    pass


class OneModel(AbstractHorizontalModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
    )
    spam = models.CharField(max_length=15)
    egg = models.CharField(max_length=15, null=True, default=None)

    objects = HorizontalManager()  # For Django<1.10

    class Meta(object):
        horizontal_group = 'a'
        horizontal_key = 'user'


class ManyModel(AbstractHorizontalModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
    )
    one = models.ForeignKey(OneModel, on_delete=models.CASCADE)

    objects = HorizontalManager()  # For Django<1.10

    class Meta(object):
        horizontal_group = 'a'
        horizontal_key = 'user'


class ProxyBaseModel(AbstractHorizontalModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
    )
    sushi = models.CharField(max_length=15, unique=True)

    class Meta(object):
        horizontal_group = 'b'
        horizontal_key = 'user'


class ProxiedModel(ProxyBaseModel):
    tempura = models.CharField(max_length=15, unique=True)
    karaage = models.CharField(max_length=15, unique=True)

    class Meta(object):
        unique_together = (
            ('tempura', 'karaage'),
        )


class AbstractModel(AbstractHorizontalModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
    )
    pizza = models.CharField(max_length=15, unique=True)
    potate = models.CharField(max_length=15, unique=True)

    class Meta(object):
        abstract = True
        horizontal_group = 'b'
        horizontal_key = 'user'
        unique_together = (
            ('pizza', 'potate'),
        )


class ConcreteModel(AbstractModel):
    coke = models.CharField(max_length=15, unique=True)

    class Meta(AbstractModel.Meta):
        unique_together = (
            ('pizza', 'coke'),
        )
