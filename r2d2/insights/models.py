# -*- coding: utf-8 -*-
""" insights models """
from django.db import models

from r2d2.accounts.models import Account


class Insight(models.Model):
    """ model to store insights """
    user = models.ForeignKey(Account)
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    generator_class = models.CharField(max_length=100)
