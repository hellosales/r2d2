# -*- coding: utf-8 -*-
""" insights models """
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save

from r2d2.accounts.models import Account
from r2d2.insights.generators import AverageProductsPerTransactions
from r2d2.insights.generators import AverageTransactionsPerWeek
from r2d2.insights.generators import DataImportedInsight
from r2d2.insights.signals import data_fetched
from r2d2.insights.signals import insight_post_save


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
    generator_class = models.CharField(max_length=100, editable=False)


def validate_file_extension(value):
    """ The file formats accepted should include excel files, csv files, word docs, .txt files, and .jpg files. """
    if not hasattr(value.file, 'content_type'):  # FIXME: detect edit
        return

    if value.file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationError(u'Files allowed: word, excel, csv, text and jpg')


class InsightAttachment(models.Model):
    """ attachment for insight """
    insight = models.ForeignKey(Insight, related_name='attachments')
    content_type = models.CharField(max_length=50, null=True, editable=True)
    file = models.FileField(upload_to='insights_attachments', validators=[validate_file_extension])

    def save(self, *args, **kwargs):
        if self.file and self.file.file and hasattr(self.file.file, 'content_type'):
            self.content_type = self.file.file.content_type
        return super(InsightAttachment, self).save(*args, **kwargs)


post_save.connect(insight_post_save, sender=Insight)

# IMPORTANT! order of connect will be the order of insights
data_fetched.connect(DataImportedInsight.handle_data_fetched)
data_fetched.connect(AverageTransactionsPerWeek.handle_data_fetched)
data_fetched.connect(AverageProductsPerTransactions.handle_data_fetched)
