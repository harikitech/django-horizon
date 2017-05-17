# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings

from horizon.models import (
    AbstractHorizontalMetadata,
    AbstractHorizontalModel,
)


class HorizontalMetadata(AbstractHorizontalMetadata):
    pass


class HorizonA(AbstractHorizontalModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    spam = models.CharField(max_length=15)

    class Meta(object):
        horizontal_group = 'a'
        horizontal_key = 'user'


class HorizonB(AbstractHorizontalModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    egg = models.CharField(max_length=15)

    class Meta(object):
        horizontal_group = 'b'
        horizontal_key = 'user'
