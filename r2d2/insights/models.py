# -*- coding: utf-8 -*-
""" insights models """
from django.db import models
from django.core.exceptions import ValidationError

from r2d2.accounts.models import Account
from r2d2.insights.generators import AverageProductsPerTransactions
from r2d2.insights.generators import AverageTransactionsPerWeek
from r2d2.insights.generators import DataImportedInsight
from r2d2.insights.signals import data_fetched


ALLOWED_CONTENT_TYPES = set([
    'application/vnd.ms-excel',
    'application/excel',
    'application/x-msexcel',
    'application/x-excel',
    'application/msword',
    'text/plain',
    'text/csv',
    'image/pjpeg',
    'image/jpeg'
])


class Insight(models.Model):
    """ model to store insights """
    user = models.ForeignKey(Account)
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    generator_class = models.CharField(max_length=100)


def validate_file_extension(value):
    """ The file formats accepted should include excel files, csv files, word docs, .txt files, and .jpg files. """
    if value.file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationError(u'Files allowed: word, excel, csv, text and jpg')


class InsightAttachment(models.Model):
    """ attachment for insight """
    insight = models.ForeignKey(Insight, related_name='attachments')
    file = models.FileField(upload_to='insights_attachments', validators=[validate_file_extension])


# IMPORTANT! order of connect will be the order of insights
data_fetched.connect(DataImportedInsight.handle_data_fetched)
data_fetched.connect(AverageTransactionsPerWeek.handle_data_fetched)
data_fetched.connect(AverageProductsPerTransactions.handle_data_fetched)
