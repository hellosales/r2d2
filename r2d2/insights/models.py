# -*- coding: utf-8 -*-
""" insights models """
from django.db import models

from r2d2.accounts.models import Account
from r2d2.insights.generators import AverageProductsPerTransactions
from r2d2.insights.generators import AverageTransactionsPerWeek
from r2d2.insights.generators import DataImportedInsight
from r2d2.insights.signals import data_fetched


class Insight(models.Model):
    """ model to store insights """
    user = models.ForeignKey(Account)
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    generator_class = models.CharField(max_length=100)


# IMPORTANT! order of connect will be the order of insights
data_fetched.connect(DataImportedInsight.handle_data_fetched)
data_fetched.connect(AverageTransactionsPerWeek.handle_data_fetched)
data_fetched.connect(AverageProductsPerTransactions.handle_data_fetched)
