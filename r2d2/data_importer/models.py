# -*- coding: utf-8 -*-
""" abstract data provider model """
from django.db import models

from r2d2.accounts.models import Account


class AbstractDataProvider(models.Model):
    user = models.ForeignKey(Account)
    name = models.CharField(max_length=255, db_index=True)
    access_token = models.CharField(max_length=255, null=True, blank=True)
    authorization_date = models.DateTimeField(null=True, blank=True)
    last_successfull_call = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        unique_together = ('user', 'name')
        ordering = ('name', )

    def fetch_data(self):
        raise NotImplementedError

    @property
    def is_authorized(self):
        """ if token is set we assume account is authorized """
        return bool(self.access_token)
